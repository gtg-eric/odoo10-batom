# -*- coding: utf-8 -*-
# © 2012 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": "Batom LDAP Populate",
    "version": "10.0.1.0.0",
    "author": (
        "Yong",
        "Batom Co., Ltd.",
    ),
    "license": "AGPL-3",
    "category": 'Tools',
    "description": """
This module allows to prepopulate the user database with all entries in the
LDAP database.

In order to schedule the population of the user database on a regular basis,
create a new scheduled action with the following properties:

- Object: res.company.ldap
- Function: action_populate
- Arguments: [res.company.ldap.id]

Substitute res.company.ldap.id with the actual id of the res.company.ldap
object you want to query.
""",
    "depends": [
        'users_ldap_populate',
		'hr',
    ],
    'external_dependencies': {
        'python': ['ldap'],
    },
    "data": [
    ],
    'installable': True,
}
