from odoo import fields, models, tools


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

    def _generate_template_recipients(self, res_ids, render_fields,
                                      allow_suggested=False,
                                      find_or_create_partners=False,
                                      render_results=None):
        render_results = super()._generate_template_recipients(
            res_ids,
            render_fields,
            allow_suggested=allow_suggested,
            find_or_create_partners=find_or_create_partners,
            render_results=render_results,
        )
        self.ensure_one()
        if not self.is_user_subscribable:
            return render_results

        opted_out_users = self.env["res.users"].sudo().search([
            ("share", "=", False),
            ("unsubscribed_template_ids", "in", self.id),
        ])
        blocked_partner_ids = set(opted_out_users.mapped("partner_id").ids)
        blocked_emails = {
            email for email in opted_out_users.mapped("partner_id.email_normalized") if email
        }
        if not blocked_partner_ids and not blocked_emails:
            return render_results

        for res_id in res_ids:
            values = render_results.get(res_id, {})
            if "partner_ids" in values:
                values["partner_ids"] = [
                    partner_id for partner_id in values["partner_ids"]
                    if partner_id not in blocked_partner_ids
                ]
            for field_name in ("email_to", "email_cc"):
                raw_emails = values.get(field_name)
                if raw_emails:
                    addresses = tools.mail.email_split_tuples(raw_emails)
                    if addresses:
                        values[field_name] = ", ".join(
                            tools.mail.formataddr((name, email))
                            for name, email in addresses
                            if tools.email_normalize(email) not in blocked_emails
                        )
        return render_results

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
            "context": {"create": False, "subscription_template_id": self.id},
        }
