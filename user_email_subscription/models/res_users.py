from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    unsubscribed_template_ids = fields.Many2many(
        comodel_name="mail.template",
        relation="user_email_subscription_optout_rel",
        column1="user_id",
        column2="template_id",
        string="Unsubscribed Email Templates",
        domain="[('is_user_subscribable', '=', True)]",
        help="Only templates explicitly opted out from are stored.",
    )

    unsubscribed_template_count = fields.Integer(
        string="Unsubscribed Templates",
        compute="_compute_unsubscribed_template_count",
    )

    @api.depends("unsubscribed_template_ids")
    def _compute_unsubscribed_template_count(self):
        for user in self:
            user.unsubscribed_template_count = len(user.unsubscribed_template_ids)

    def action_view_unsubscribed_templates(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Unsubscribed Email Templates",
            "res_model": "mail.template",
            "view_mode": "list,form",
            "domain": [("id", "in", self.unsubscribed_template_ids.ids)],
            "context": {"create": False},
        }

    def _is_unsubscribed_from_template(self, template):
        self.ensure_one()
        return bool(
            template
            and template.is_user_subscribable
            and template.id in self.unsubscribed_template_ids.ids
        )
