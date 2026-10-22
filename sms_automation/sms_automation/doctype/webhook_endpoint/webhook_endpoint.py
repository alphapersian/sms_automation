import secrets

import frappe
from frappe import _
from frappe.model.document import Document

WEBHOOK_METHOD = "/api/method/sms_automation.api.webhook"


class WebhookEndpoint(Document):
	def validate(self):
		if not self.key:
			self.key = new_key()
		if self.link_doctype and not (self.payload_path and self.match_field):
			frappe.throw(_("Value Path and Match Against Field are required with a Document Type"))
		if self.link_doctype and not frappe.get_meta(self.link_doctype).has_field(self.match_field):
			if self.match_field != "name":
				frappe.throw(_("{0} has no field {1}").format(self.link_doctype, self.match_field))

	def onload(self):
		self.set_onload("webhook_url", get_webhook_url(self.key))

	@frappe.whitelist()
	def regenerate_key(self):
		self.check_permission("write")
		self.key = new_key()
		self.save()
		return get_webhook_url(self.key)


def new_key() -> str:
	return secrets.token_urlsafe(24)


def get_webhook_url(key: str | None) -> str:
	return f"{frappe.utils.get_url()}{WEBHOOK_METHOD}?key={key}" if key else ""
