import json

import frappe
from frappe.tests import IntegrationTestCase

from sms_automation.api import build_payload, extract_path


class TestWebhookEndpoint(IntegrationTestCase):
	def test_key_is_generated(self):
		doc = frappe.get_doc({"doctype": "Webhook Endpoint", "title": "t-key"}).insert()
		self.assertTrue(doc.key)

	def test_extract_path(self):
		self.assertEqual(extract_path({"a": {"b": ["x", {"c": 1}]}}, "a.b.1.c"), 1)
		self.assertIsNone(extract_path({"a": 1}, "a.b"))

	def test_payload_merges_sources(self):
		payload = build_payload(
			"ep", "POST", args={"phone": "1", "key": "secret"}, form={}, json_body={"phone": "2", "n": 3}
		)
		self.assertEqual(payload["data"], {"phone": "2", "n": 3})
		self.assertNotIn("key", payload["params"])
		self.assertNotIn("secret", json.dumps(payload))
