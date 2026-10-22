import frappe
from frappe import _
from frappe.automation_engine.actions.base import AutomationAction, AutomationParamError, render_value


class SendSMS(AutomationAction):
	action_type = "SendSMS"
	label = "Send SMS"
	description = "Send a text message with the gateway set up in SMS Settings."
	requires_document = False
	transactional = False  # an SMS cannot be rolled back
	params_schema = [
		{
			"fieldname": "receiver",
			"label": "Phone Number(s)",
			"fieldtype": "Data",
			"reqd": 1,
			"templatable": True,
			"description": "Separate several numbers with a comma. Example: {{ payload.data.phone }}",
		},
		{
			"fieldname": "message",
			"label": "Message",
			"fieldtype": "Small Text",
			"reqd": 1,
			"templatable": True,
		},
	]

	def validate(self, params, doctype):
		for name in ("receiver", "message"):
			if not params.get(name):
				raise AutomationParamError(_("{0} is required").format(name.title()), fieldname=name)

	def execute(self, doc, params, context):
		from frappe.core.doctype.sms_settings.sms_settings import send_sms

		receiver = render_value(params["receiver"], doc, context)
		message = render_value(params["message"], doc, context)
		numbers = [n.strip() for n in str(receiver).split(",") if n.strip()]
		if not numbers:
			return _("No phone number to send to")

		send_sms(numbers, message)
		return _("SMS sent to {0}").format(", ".join(numbers))
