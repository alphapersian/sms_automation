app_name = "sms_automation"
app_title = "SMS Automation"
app_publisher = "alphapersian"
app_description = "SMS automation for Frappe"
app_email = "a.mousavi.bp@gmail.com"
app_license = "mit"

automation_events = [
    {"sms.reply_received": {
        "label": "SMS reply received",
        "description": "Someone replied to a campaign SMS",
    }},
]
