from markupsafe import Markup

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "unsubscribed_template_ids",
            "subscribed_template_ids",
            "unsubscribed_template_count",
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "unsubscribed_template_ids",
            "subscribed_template_ids",
        ]

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

    def write(self, vals):
        tracks_subscriptions = bool({"unsubscribed_template_ids", "subscribed_template_ids"} & vals.keys())
        previous_opt_outs = {
            user.id: user.unsubscribed_template_ids
            for user in self
        } if tracks_subscriptions else {}

        result = super().write(vals)
        if tracks_subscriptions:
            actor_name = self.env.user.display_name
            for user in self:
                previous = previous_opt_outs[user.id]
                current = user.unsubscribed_template_ids
                newly_opted_out = current - previous
                newly_subscribed = previous - current
                if not newly_opted_out and not newly_subscribed:
                    continue

                changed_at = fields.Datetime.context_timestamp(
                    user, fields.Datetime.now()
                ).strftime("%Y-%m-%d %H:%M:%S %Z")
                body = Markup(
                    "<p>Subscription preferences changed by %s at %s.</p>"
                ) % (actor_name, changed_at)
                if newly_opted_out:
                    body += Markup("<p>Unsubscribed from: %s</p>") % ", ".join(
                        newly_opted_out.mapped("display_name")
                    )
                if newly_subscribed:
                    body += Markup("<p>Subscribed to: %s</p>") % ", ".join(
                        newly_subscribed.mapped("display_name")
                    )
                user.partner_id.message_post(
                    body=body,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
        return result

    def action_view_unsubscribed_templates(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Email Subscriptions",
            "res_model": "mail.template",
            "view_mode": "list,form",
            "domain": [
                ("is_user_subscribable", "=", True),
            ],
            "context": {
                "create": False,
                "subscription_user_id": self.id,
            },
        }

    def _is_unsubscribed_from_template(self, template):
        self.ensure_one()
        return bool(
            template
            and template.is_user_subscribable
            and template.id in self.unsubscribed_template_ids.ids
        )
