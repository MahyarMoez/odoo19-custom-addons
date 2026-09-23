{
    "name": "User Email Subscription",
    "version": "19.0.1.0.0",
    "summary": "Centralized opt-out management for user email subscriptions",
    "description": '''
Centralized User Email Subscription Management.

Administrators can mark mail templates as user-subscribable.
Users can opt out of those templates from their user profile.
Only opt-out relationships are stored.
''',
    "category": "Tools",
    "author": "Cloudunify Mustercase Prototype",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_template_views.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
    "application": False,
}
