import hmac

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

# Headers that never reach the automation payload.
SENSITIVE_HEADERS = {"authorization", "cookie", "x-webhook-key", "x-frappe-csrf-token"}


@frappe.whitelist(allow_guest=True, methods=["GET", "POST", "PUT", "PATCH"])
@rate_limit(limit=300, seconds=60)
def webhook():
	"""Entry point for Webhook Endpoint URLs.

	/api/method/sms_automation.api.webhook?key=<key>
	The key may also come in an `X-Webhook-Key` or `Authorization: Bearer` header. Query
	params, form fields and a JSON body are all passed to the automation as `payload`.
	"""
	request = frappe.request
	key = get_key(request)
	endpoint = get_endpoint(key)

	method = request.method
	if endpoint.allowed_method not in (None, "", "Any") and endpoint.allowed_method != method:
		frappe.throw(_("Method not allowed"), frappe.PermissionError)

	payload = build_payload(
		endpoint.name,
		method,
		args=request.args.to_dict(flat=True),
		form=request.form.to_dict(flat=True),
		json_body=get_json_body(request),
		raw=get_raw_body(request),
		headers=dict(request.headers),
	)
	data = payload["data"]

	doc = None
	if endpoint.link_doctype:
		value = extract_path(data, endpoint.payload_path)
		if value not in (None, ""):
			name = frappe.db.get_value(endpoint.link_doctype, {endpoint.match_field: value}, "name")
			doc = frappe.get_doc(endpoint.link_doctype, name) if name else None

	correlation = extract_path(data, endpoint.correlation_path) if endpoint.correlation_path else None

	from frappe.automation_engine import emit

	result = emit(
		"sms_automation.webhook_received",
		doc=doc,
		payload=payload,
		correlation_key=str(correlation) if correlation not in (None, "") else None,
	)

	frappe.db.set_value(
		"Webhook Endpoint",
		endpoint.name,
		{
			"hit_count": (endpoint.hit_count or 0) + 1,
			"last_received_at": frappe.utils.now(),
			"last_payload": frappe.as_json(payload),
		},
		update_modified=False,
	)
	frappe.db.commit()
	return {"status": "accepted", **result}


def get_key(request) -> str:
	header = request.headers.get("Authorization") or ""
	bearer = header[7:].strip() if header.lower().startswith("bearer ") else ""
	return request.args.get("key") or request.headers.get("X-Webhook-Key") or bearer or ""


def get_endpoint(key: str):
	denied = frappe.PermissionError
	if not key:
		frappe.throw(_("Invalid webhook key"), denied)
	name = frappe.db.get_value("Webhook Endpoint", {"key": key, "enabled": 1}, "name")
	endpoint = frappe.get_doc("Webhook Endpoint", name) if name else None
	if not endpoint or not hmac.compare_digest(endpoint.key, key):
		frappe.throw(_("Invalid webhook key"), denied)
	return endpoint


def get_json_body(request):
	if not request.data:
		return None
	return request.get_json(silent=True)


def get_raw_body(request) -> str | None:
	if request.get_json(silent=True) is not None or request.form:
		return None
	return request.get_data(as_text=True) or None


def build_payload(webhook, method, args=None, form=None, json_body=None, raw=None, headers=None) -> dict:
	"""Collect everything the caller sent. `data` merges params < form < JSON body."""
	args = {k: v for k, v in (args or {}).items() if k != "key"}
	form = {k: v for k, v in (form or {}).items() if k != "key"}
	body = json_body.copy() if isinstance(json_body, dict) else json_body
	if isinstance(body, dict):
		body.pop("key", None)

	data = {**args, **form}
	if isinstance(body, dict):
		data.update(body)
	elif body is not None:
		data["body"] = body

	return {
		"webhook": webhook,
		"method": method,
		"params": args,
		"form": form,
		"body": body,
		"raw": raw,
		"headers": {k: v for k, v in (headers or {}).items() if k.lower() not in SENSITIVE_HEADERS},
		"data": data,
	}


def extract_path(data, path):
	"""Read a dotted path (`customer.phones.0`) out of nested dicts and lists."""
	current = data
	for part in (path or "").split("."):
		if isinstance(current, dict):
			current = current.get(part)
		elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
			current = current[int(part)]
		else:
			return None
	return current
