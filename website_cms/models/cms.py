# -*- coding: utf-8 -*-

from openerp import models
from openerp import fields
from openerp import api
from openerp.tools.translate import _
from openerp.tools.translate import html_translate
from openerp.addons.website.models.website import slug
# from openerp.addons.website.models.website import unslug


VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    # limit views to "website_cms." prefix
    ('cms_view', '=', True),
]


class CMSPage(models.Model):
    """Model of a CMS page. """
    _name = 'cms.page'
    _description = 'CMS page'
    _order = 'sequence, id'
    _inherit = ['mail.thread',
                'website.seo.metadata',
                'website.published.mixin',
                'website.image.mixin',
                'website.orderable.mixin',
                'website.coremetadata.mixin']

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    description = fields.Html(
        'HTML Description',
        translate=html_translate,
        sanitize=True
    )
    body = fields.Html(
        'HTML Body',
        translate=html_translate,
        sanitize=False
    )

    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='cms.page'
    )
    children_ids = fields.One2many(
        string='Children',
        inverse_name='parent_id',
        comodel_name='cms.page'
    )
    attachment_ids = fields.One2many(
        string='Attachments',
        inverse_name='res_id',
        comodel_name='ir.attachment'
    )
    type_id = fields.Many2one(
        string='Page type',
        comodel_name='cms.page.type',
        default=lambda self: self._default_type()
    )
    view_id = fields.Many2one(
        string='View',
        comodel_name='ir.ui.view',
        domain=lambda self: VIEW_DOMAIN,
    )
    sub_page_type_id = fields.Many2one(
        string='Default page type for sub pages',
        comodel_name='cms.page.type',
        help=(u"You can select a page type to be used "
              u"by default for each contained page."),
    )
    sub_page_view_id = fields.Many2one(
        string='Default page view for sub pages',
        comodel_name='ir.ui.view',
        help=(u"You can select a view to be used "
              u"by default for each contained page."),
        domain=lambda self: VIEW_DOMAIN,
    )
    list_types_ids = fields.Many2many(
        string='Types to list',
        comodel_name='cms.page.type',
        help=(u"You can select types of page to be used "
              u"in `listing` views."),
    )
    nav_include = fields.Boolean(
        'Nav include',
        default=True,
        help=(u"Decide if this item "
              u"should be included in main navigation."),
    )

    @api.model
    def _default_type(self):
        page_type = self.env.ref('website_cms.default_page_type')
        return page_type and page_type.id or False

    @api.model
    def build_public_url(self, item):
        """Walk trough page hierarchy to build its public URL."""
        current = item
        parts = [slug(current), ]
        while current.parent_id:
            parts.insert(0, slug(current.parent_id))
            current = current.parent_id
        public_url = '/cms/' + '/'.join(parts)
        return public_url

    @api.multi
    def _website_url(self, field_name, arg):
        """Override method defined by `website.published.mixin`."""
        res = {}
        for item in self:
            res[item.id] = self.build_public_url(item)
        return res

    @api.model
    def build_hierarchy_name(self, item):
        """Walk trough page hierarchy to build its nested name."""
        current = item
        parts = [current.name, ]
        while current.parent_id:
            parts.insert(0, current.parent_id.name)
            current = current.parent_id
        return ' / '.join(parts)

    @api.multi
    def name_get(self):
        """Format displayed name."""
        # use name and/or country group name
        res = []
        for item in self:
            res.append((item.id, self.build_hierarchy_name(item)))
        return res

    @api.model
    def get_ancestor(self, item):
        """Walk trough page hierarchy to find root ancestor."""
        current = item
        while current.parent_id:
            current = current.parent_id
        return current


class CMSPageType(models.Model):
    """Model of a CMS page type. """
    _name = 'cms.page.type'
    _description = 'CMS page type'

    name = fields.Char('Name', translate=True)
