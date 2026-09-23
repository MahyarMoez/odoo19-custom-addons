from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    is_user_subscribable = fields.Boolean(
        string="User Subscription Possible",
        help="Allow internal users to opt out of this email template.",
    )

    unsubscribed_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="user_email_subscription_optout_rel",
        column1="template_id",
        column2="user_id",
        string="Unsubscribed Users",
        help="Users who explicitly opted out of this template.",
    )

    unsubscribed_user_count = fields.Integer(
        string="Unsubscribed Users",
        compute="_compute_unsubscribed_user_count",
    )

    def _compute_unsubscribed_user_count(self):
        for template in self:
            template.unsubscribed_user_count = len(template.unsubscribed_user_ids)

    def action_view_unsubscribed_users(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Unsubscribed Users",
            "res_model": "res.users",
            "view_mode": "list,form",
            "domain": [("id", "in", self.unsubscribed_user_ids.ids)],
            "context": {"create": False},
        }
