# Security Notes

The module requires normal users to manage their own subscription choices while administrators can manage users/templates.

Odoo's `res.users` model has special self-write restrictions. The prototype therefore deliberately does not claim that arbitrary normal users can write all user records.

For the final implementation, use Odoo's supported self-service field mechanisms for the exact Odoo 19 target version, and keep administrator access separate.

Also review whether the `mail.template` access CSV is necessary in the target database; existing Mail groups may already govern template access. Do not weaken existing Odoo security.
