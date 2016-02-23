# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212

from openerp import models
from openerp import fields
from openerp import api
# from openerp.addons.web.http import request

# from openerp.tools.translate import _
from openerp.tools.translate import html_translate
# from openerp.addons.website.models.website import slug
# from openerp.addons.website.models.website import unslug


VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    ('cms_portlet', '=', True),
]


class CMSPortletAssignment(models.Model):
    # https://en.wikipedia.org/wiki/Portlet

    _name = 'cms.portlet.assignment'
    _description = 'CMS portlet assignment'
    _inherit = ['website.orderable.mixin', ]

    res_id = fields.Integer('Res')
    portlet_type_id = fields.Reference(
        string='Portlet type',
        selection='_available_portlets',
        required=True,
        domain=[('assignment_id', '=', False)]
    )
    name = fields.Char(
        'Name',
        # related="portlet_type_id.name",
        readonly=True
    )

    @api.model
    def _available_portlets(self):
        search_args = [
            ('model', 'like', 'cms.portlet.%%')
        ]
        _models = self.env['ir.model'].search(search_args)
        available = [
            (model.model, model.name)
            for model in _models
            if 'assignment' not in model.name
        ]
        print available
        return available


class CMSPortlet(models.AbstractModel):
    # https://en.wikipedia.org/wiki/Portlet

    _name = 'cms.portlet'
    _description = 'CMS portlet'

    _template = ''

    assignment_id = fields.Many2one(
        string='Assignment',
        comodel_name='cms.portlet.assignment',
    )
    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    view_id = fields.Many2one(
        string='View',
        comodel_name='ir.ui.view',
        domain=lambda self: VIEW_DOMAIN,
        default=lambda self: self._default_view()
    )

    @api.multi
    def name_get(self):
        """Format displayed name."""
        # use name and/or country group name
        res = []
        for item in self:
            name = '[{}] {}'.format(item._name,
                                    item.name)
            res.append((item.id, name))
        return res

    @api.model
    def _default_view(self):
        # if self._template:
        #     view = self.env.ref(self._template)
        #     return view
        return False

    @property
    def template(self):
        if self.view_id:
            return self.view_id.key
        return self._template


class PortletStatic(models.Model):
    _name = 'cms.portlet.static'
    _description = 'CMS Portlet Static'
    _inherit = 'cms.portlet'

    _template = 'website_cms.portlet_static_editable'

    content = fields.Html(
        # 'HTML content',
        translate=html_translate,
        sanitize=True
    )
