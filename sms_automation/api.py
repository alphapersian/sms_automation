import frappe
from frappe.automation_engine import emit

@frappe.whitelist(allow_guest=True)
def sms_reply(token=None, **data):
    if token != frappe.conf.get("sms_webhook_token"):
        frappe.throw("Not allowed", frappe.PermissionError)

    phone = (data.get("from") or "").strip()
    lead = frappe.db.get_value("Lead", {"mobile_no": phone}, "name")

    emit(
        "sms.reply_received",
        doc=frappe.get_doc("Lead", lead) if lead else None,
        payload={"phone": phone, "message": data.get("message")},
        correlation_key=phone,
    )
    frappe.db.commit()
    return "ok"
