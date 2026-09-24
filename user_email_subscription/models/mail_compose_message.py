from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail_comment(self, res_ids):
        self.ensure_one()
        if self.template_id and self.template_id.is_user_subscribable:
            return super(MailComposeMessage, self.with_context(
                user_email_subscription_template_id=self.template_id.id,
            ))._action_send_mail_comment(res_ids)
        return super()._action_send_mail_comment(res_ids)