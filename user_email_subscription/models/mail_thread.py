from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_get_recipients(self, message, msg_vals=False, **kwargs):
        recipients_data = super()._notify_get_recipients(
            message, msg_vals=msg_vals, **kwargs
        )
        template_id = self.env.context.get("user_email_subscription_template_id")
        if not template_id or not recipients_data:
            return recipients_data

        template = self.env["mail.template"].sudo().browse(template_id).exists()
        if not template or not template.is_user_subscribable:
            return recipients_data

        partner_ids = [recipient["id"] for recipient in recipients_data if recipient.get("id")]
        recipient_emails = [
            recipient["email_normalized"]
            for recipient in recipients_data
            if recipient.get("email_normalized")
        ]
        opted_out_users = self.env["res.users"].sudo().search([
            ("share", "=", False),
            ("unsubscribed_template_ids", "in", template.id),
            "|",
            ("partner_id", "in", partner_ids),
            ("partner_id.email_normalized", "in", recipient_emails),
        ]) if partner_ids or recipient_emails else self.env["res.users"]
        blocked_partner_ids = set(opted_out_users.mapped("partner_id").ids)
        blocked_emails = {
            email for email in opted_out_users.mapped("partner_id.email_normalized") if email
        }

        for recipient in recipients_data:
            is_opted_out = (
                recipient.get("id") in blocked_partner_ids
                or recipient.get("email_normalized") in blocked_emails
            )
            if is_opted_out and recipient.get("notif") == "email":
                recipient["notif"] = "inbox"
        return recipients_data