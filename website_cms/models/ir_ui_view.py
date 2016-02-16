# -*- coding: utf-8 -*-

from openerp import models
from openerp import fields


class IRUIView(models.Model):
    _inherit = "ir.ui.view"

    cms_view = fields.Boolean('CMS view?')
