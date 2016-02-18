# -*- coding: utf-8 -*-

from openerp import models
from openerp import fields


class IRUIView(models.Model):
    _inherit = "ir.ui.view"

    cms_view = fields.Boolean(
        'CMS view?',
        help=u"This view will be available as a CMS view."
    )
    cms_sidebar = fields.Boolean(
        'CMS sidebar?',
        help=u"This view will be available as a CMS sidebar view."
    )
