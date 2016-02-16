# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website CMS",
    "summary": "CMS features",
    "version": "1.0.0dev",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "<AUTHOR(S)>, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        'website',
    ],
    "data": [
        # security
        'security/ir.model.access.csv',
        'security/groups.xml',
        # data
        "data/page_types.xml",
        # views
        "views/menuitems.xml",
        "views/section.xml",
        "views/page.xml",
        # templates
        "templates/section.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ],
    'application': True,
}
