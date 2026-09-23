# User Email Subscription

Prototype Odoo 19 add-on for the Cloudunify Developer Mustercase.

## What it implements

- Adds `is_user_subscribable` to `mail.template`.
- Adds an opt-out-only Many2many relation between `res.users` and `mail.template`.
- Adds a Notifications tab to the user form.
- Adds Smart Buttons for unsubscribed users/templates.
- Keeps only explicit opt-outs in the pivot relation.

## Important

This repository is intentionally a **prototype scaffold**. The remaining critical part of the mustercase is the version-specific integration with Odoo's actual mail dispatch path so unsubscribed users are removed from outgoing recipients, including follower notifications.

Before presenting, verify the exact Odoo 19 mail flow in the target environment and implement that dispatch filter with tests/demo evidence.

## Installation

1. Copy `user_email_subscription/` into your Odoo custom addons path.
2. Restart Odoo.
3. Update the Apps list.
4. Install **User Email Subscription**.

## Demo idea

1. Mark a normal mail template as User Subscription Possible.
2. Open an internal user and opt out.
3. Show the opt-out relation.
4. Send the template through the supported Odoo flow.
5. Demonstrate that the opted-out user is excluded.
6. Re-subscribe using the Smart Button/bulk action.
7. Repeat the send.

## Scope

Only `res.users` is supported. Portal users, partners, mailing lists, scheduling, snooze, external integrations, performance tuning and full automated test coverage are outside the mustercase scope.
