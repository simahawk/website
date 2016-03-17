# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website CMS",
    "summary": "CMS features",
    "version": "1.0.1",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "<AUTHOR(S)>, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        "base",
        'website',
    ],
    "data": [
        # security
        'security/groups.xml',
        'security/ir.model.access.csv',
        # data
        "data/page_types.xml",
        "data/media_categories.xml",
        # "data/form_settings.xml",
        # views
        "views/menuitems.xml",
        "views/cms_page.xml",
        "views/cms_redirect.xml",
        "views/cms_media.xml",
        'views/website_menu.xml',
        # templates
        "templates/assets.xml",
        "templates/actions.xml",
        "templates/page_view.xml",
        "templates/sidebar_view.xml",
        "templates/form.xml",
    ],
}
