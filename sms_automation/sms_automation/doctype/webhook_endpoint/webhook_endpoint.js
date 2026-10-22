frappe.ui.form.on("Webhook Endpoint", {
	refresh(frm) {
		const url = frm.doc.__onload && frm.doc.__onload.webhook_url;
		if (frm.is_new() || !url) return;

		frm.dashboard.set_headline(
			__("Call this URL from outside Frappe: {0}", [`<code>${frappe.utils.escape_html(url)}</code>`])
		);
		frm.add_custom_button(__("Copy URL"), () => frappe.utils.copy_to_clipboard(url));
		frm.add_custom_button(__("Regenerate Key"), () => {
			frappe.confirm(__("The old URL stops working immediately. Continue?"), () => {
				frm.call("regenerate_key").then(() => frm.reload_doc());
			});
		});
	},
});
