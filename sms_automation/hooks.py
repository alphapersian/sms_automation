app_name = "sms_automation"
app_title = "SMS Automation"
app_publisher = "alphapersian"
app_description = "SMS automation for Frappe"
app_email = "a.mousavi.bp@gmail.com"
app_license = "mit"

# Every Webhook Endpoint emits this one event. Pick "Webhook received" as the
# Custom Event of an Automation Flow, and narrow it with a condition such as
# `payload.webhook == "my-endpoint"`.
automation_events = [
	{
		"sms_automation.webhook_received": {
			"label": "Webhook received",
			"description": "An external system called a Webhook Endpoint URL",
		}
	},
]
