# SMS Automation

Frappe app that adds **webhook triggers** to the Frappe Automation engine (Frappe v16+).

## How it works

1. Open **Webhook Endpoint** and create one. A key is generated and the full URL is shown at the top of the form.
2. An outside system calls the URL:

   ```bash
   # key in the query string, data in params
   curl "https://your-site/api/method/sms_automation.api.webhook?key=KEY&phone=0912&message=hi"

   # key in a header, data in a JSON body
   curl -X POST https://your-site/api/method/sms_automation.api.webhook \
     -H "X-Webhook-Key: KEY" -H "Content-Type: application/json" \
     -d '{"phone": "0912", "message": "hi"}'
   ```

   The key can be sent as `?key=`, `X-Webhook-Key`, or `Authorization: Bearer`.
3. In an **Automation Flow**, choose trigger **Custom Event** → **Webhook received**. Its actions run when the call arrives.

## Payload available to the flow

| Key | Content |
| --- | --- |
| `payload.webhook` | name of the Webhook Endpoint |
| `payload.params` | query-string params |
| `payload.form` | form fields |
| `payload.body` | parsed JSON body |
| `payload.raw` | raw body when it is neither JSON nor form |
| `payload.headers` | request headers (credentials removed) |
| `payload.data` | params, form and JSON body merged (body wins) |

Use a flow condition like `payload.webhook == "sms-replies"` to react to one endpoint only.

## Optional endpoint settings

- **Allowed Method**: restrict to GET, POST, PUT or PATCH.
- **Link to a Document**: look up a record from the data (e.g. `Lead` where `mobile_no` = `data.from`) and run the flow against it.
- **Correlation Value Path**: resumes flows waiting on this event (*Wait for Event*) with the same key.
- **Regenerate Key** invalidates the old URL.

## Installation

```bash
bench get-app https://github.com/alphapersian/sms_automation --branch main
bench --site your-site install-app sms_automation
```
