# User Email Subscription

Prototype Odoo 19 add-on for the Cloudunify Developer sample case.

## What it implements

* Adds `is_user_subscribable` to `mail.template`.
* Adds a Many2many opt-out relation between `res.users` and `mail.template`.
* Adds a **Notifications** tab to the user form.
* Adds **Smart buttons** showing the total number of unsubscribed users and templates.
* Adds a Resubscribe Selected _action_ to Email Templates.
* Adds Subscribe to Selected Templates and Unsubscribe from Selected Templates _actions_ to the User form.
* Logs subscription and unsubscription changes in the user's chatter.
* Filters emails based on the user's subscription status for subscribable email templates.


## Installation

1. Copy `user_email_subscription/` into your Odoo custom addons path.
2. Restart Odoo.
3. Update the Apps list.
4. Install **User Email Subscription**.

## Usage

1. Mark a regular mail template as **User Subscription Possible**.
2. Open an internal user and opt out of the template from the **Notifications** tab.
3. Send the template through a supported Odoo flow. The email will be sent or filtered based on the user's subscription status.
4. For administrators, use the **Smart Button** or **bulk action** to resubscribe users.


## Scope

Only `res.users` is supported. Portal users, partners, mailing lists, scheduling, snooze, external integrations, performance tuning and full automated test coverage are outside the scope.
