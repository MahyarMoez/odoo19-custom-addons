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

    subscribed_template_ids = fields.Many2many(
        comodel_name="mail.template",
        string="Email Subscriptions",
        compute="_compute_subscribed_template_ids",
        inverse="_inverse_subscribed_template_ids",
        domain="[('is_user_subscribable', '=', True)]",
        help="Subscribable templates selected here remain enabled; unchecked templates are stored as opt-outs.",
    )

    unsubscribed_template_count = fields.Integer(
        string="Unsubscribed Templates",
        compute="_compute_unsubscribed_template_count",
    )

    @api.depends("unsubscribed_template_ids")
    def _compute_subscribed_template_ids(self):
        templates = self.env["mail.template"].search([
            ("is_user_subscribable", "=", True),
        ])
        for user in self:
            user.subscribed_template_ids = templates - user.unsubscribed_template_ids

    def _inverse_subscribed_template_ids(self):
        templates = self.env["mail.template"].search([
            ("is_user_subscribable", "=", True),
        ])
        for user in self:
            selected_templates = user.subscribed_template_ids & templates
            existing_opt_outs = user.unsubscribed_template_ids
            user.unsubscribed_template_ids = (
                existing_opt_outs - templates
            ) | (templates - selected_templates)

    @api.depends("unsubscribed_template_ids")
    def _compute_unsubscribed_template_count(self):
        for user in self:
            user.unsubscribed_template_count = len(user.unsubscribed_template_ids)

    def action_subscribe_all_templates(self):
        self.ensure_one()
        subscribable_templates = self.env["mail.template"].search([
            ("is_user_subscribable", "=", True),
        ])
        opted_out_templates = self.unsubscribed_template_ids & subscribable_templates
        if opted_out_templates:
            self.write({
                "unsubscribed_template_ids": [
                    (3, template.id) for template in opted_out_templates
                ],
            })
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_unsubscribe_all_templates(self):
        self.ensure_one()
        subscribable_templates = self.env["mail.template"].search([
            ("is_user_subscribable", "=", True),
        ])
        new_opt_outs = subscribable_templates - self.unsubscribed_template_ids
        if new_opt_outs:
            self.write({
                "unsubscribed_template_ids": [
                    (4, template.id) for template in new_opt_outs
                ],
            })
        return {"type": "ir.actions.client", "tag": "reload"}
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
