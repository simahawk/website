# -*- coding: utf-8 -*-

from openerp import models
from openerp import fields
from openerp import api
from openerp.tools.translate import _
from openerp.tools.translate import html_translate
from openerp.addons.website.models.website import slug
# from openerp.addons.website.models.website import unslug


@api.model
def build_public_url(item):
    """Walk trough section hierarchy to build its public URL."""
    current = item
    parts = [slug(current), ]
    while current.parent_id:
        parts.insert(0, slug(current.parent_id))
        current = current.parent_id
    public_url = '/cms/' + '/'.join(parts)
    return public_url


VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    # limit views to "website_cms." prefix
    ('cms_view', '=', True),
]


class CMSSection(models.Model):
    """Model of a CMS section. """
    _name = 'cms.section'
    _description = 'CMS section'
    _order = 'sequence, id'
    _inherit = ['mail.thread',
                'website.seo.metadata',
                'website.published.mixin',
                'website.orderable.mixin']

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    description = fields.Html(
        'Description',
        translate=html_translate,
        sanitize=True
    )
    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='cms.section'
    )
    children_ids = fields.One2many(
        string='Children',
        inverse_name='parent_id',
        comodel_name='cms.section'
    )
    page_ids = fields.One2many(
        string='Pages',
        inverse_name='parent_id',
        comodel_name='cms.page'
    )
    attachment_ids = fields.One2many(
        string='Attachments',
        inverse_name='res_id',
        comodel_name='ir.attachment'
    )
    view_item = fields.Many2one(
        string='View item',
        comodel_name='cms.page',
        help=(u"To be used to set a default item "
              u"to display when displaying the section."),
        domain=lambda self: [('parent_id', '=', self.id)],
    )
    view_id = fields.Many2one(
        string='View',
        comodel_name='ir.ui.view',
        domain=lambda self: VIEW_DOMAIN,
    )
    page_type_id = fields.Many2one(
        string='Default page type for section',
        comodel_name='cms.page.type',
    )
    page_view_id = fields.Many2one(
        string='Page view',
        comodel_name='ir.ui.view',
        help=(u"You can select a view to be used "
              u"by default for each page contained in this section."),
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

    @api.multi
    def _website_url(self, field_name, arg):
        """Override method defined by `website.published.mixin`."""
        res = super(CMSSection, self)._website_url(field_name, arg)
        for item in self:
            res[item.id] = build_public_url(item)
        return res


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
        'Description',
        translate=html_translate,
        sanitize=True
    )
    parent_id = fields.Many2one(
        string='Parent section',
        comodel_name='cms.section'
    )
    body = fields.Html(
        'HTML Body',
        translate=html_translate,
        sanitize=False
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

    @api.model
    def _default_type(self):
        page_type = self.env.ref('website_cms.default_page_type')
        return page_type and page_type.id or False


class CMSPageType(models.Model):
    """Model of a CMS page type. """
    _name = 'cms.page.type'
    _description = 'CMS page type'

    name = fields.Char('Name', translate=True)
