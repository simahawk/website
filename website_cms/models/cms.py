# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212

from openerp import models
from openerp import fields
from openerp import api
# from openerp.tools.translate import _
from openerp.tools.translate import html_translate
from openerp.addons.website.models.website import slug
# from openerp.addons.website.models.website import unslug


def to_slug(item):
    value = (item.id, item.name)
    return slug(value)


VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    ('cms_view', '=', True),
]
SIDEBAR_VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    ('cms_sidebar', '=', True),
]


class CMSPage(models.Model):
    """Model of a CMS page."""

    _name = 'cms.page'
    _description = 'CMS page'
    _order = 'sequence, id'
    _inherit = ['website.seo.metadata',
                'website.published.mixin',
                'website.image.mixin',
                'website.orderable.mixin',
                'website.coremetadata.mixin',
                'website.security.mixin']

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
    related_ids = fields.Many2many(
        string='Related pages',
        comodel_name='cms.page',
        relation='cms_page_related_rel',
        column1='from_id',
        column2='to_id',
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
    sidebar_view_ids = fields.Many2many(
        string='Sidebar views',
        comodel_name='ir.ui.view',
        help=(u"Each view linked here will be rendered in the sidebar."),
        domain=lambda self: SIDEBAR_VIEW_DOMAIN,
    )
    sidebar_content = fields.Html(
        'Sidebar HTML',
        translate=html_translate,
        sanitize=False,
        help=(u"Each template that enables customization in the sidebar "
              u"must use this field to store content."),
    )
    # sidebar_inherit = fields.Boolean(
    #     'Sidebar Inherit',
    #     help=(u"If turned on, you'll see the same sidebar "
    #           u"into each contained page."),
    # )
    nav_include = fields.Boolean(
        'Nav include',
        default=False,
        help=(u"Decide if this item "
              u"should be included in main navigation."),
    )
    hierarchy = fields.Char(
        string='Hierarchy',
        compute='_compute_hierarchy',
        readonly=True,
        store=True,
        copy=False,
    )
    redirect_to_id = fields.Many2one(
        string='Redirect to',
        comodel_name='cms.page',
        help=(u"If valued, you will be redirected "
              u"to selected page permanently. "
              u"HTTP status 301 will be set. "),
    )

    @api.model
    def _default_type(self):
        page_type = self.env.ref('website_cms.default_page_type')
        return page_type and page_type.id or False

    @api.model
    def build_public_url(self, item):
        """Walk trough page hierarchy to build its public URL."""
        current = item
        parts = [to_slug(current), ]
        while current.parent_id:
            parts.insert(0, to_slug(current.parent_id))
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

    @api.multi
    @api.depends('parent_id')
    def _compute_hierarchy(self):
        for item in self:
            # XXX: would be better to do one write at the end?
            item.hierarchy = self.build_hierarchy_name(item)

    @api.model
    def build_hierarchy_name(self, item):
        """Walk trough page hierarchy to build its nested name."""
        current = item
        parts = [current.name, ]
        while current.parent_id:
            parts.insert(0, current.parent_id.name)
            current = current.parent_id
        # prefix w/ a slash meaning root
        parts.insert(0, '')
        return ' / '.join(parts)

    # XXX: temp disabled because this is used for slugs too
    # repeating each hierarchy item in the url
    # @api.multi
    # def name_get(self):
    #     """Format displayed name."""
    #     # use name and/or country group name
    #     res = []
    #     for item in self:
    #         res.append((item.id, self.build_hierarchy_name(item)))
    #     return res

    @api.model
    def get_root(self, item=None):
        """Walk trough page hierarchy to find root ancestor."""
        current = item or self
        while current.parent_id:
            current = current.parent_id
        return current

    @api.multi
    def update_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})

    @api.multi
    def open_children(self):
        """Action to open tree view of children pages."""
        self.ensure_one()
        domain = [
            ('parent_id', '=', self.id),
        ]
        context = {
            'default_parent_id': self.id,
        }
        for k in ('type_id', 'view_id'):
            fname = 'sub_page_' + k
            value = getattr(self, fname)
            if value:
                context['default_' + k] = value.id
        return {
            'name': 'Children',
            'type': 'ir.actions.act_window',
            'res_model': 'cms.page',
            'target': 'current',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context,
        }

    @api.model
    def get_listing(self, published=True,
                    nav=None, type_ids=None,
                    order=None, item=None):
        """Return items to be listed.

        Tweak filtering by:

        `published` to show published/unpublished items
        `nav` to show nav-included items
        `type_ids` to limit listing to specific page types
        `order` to override ordering by sequence

        By default filter w/ `list_types_ids` if valued.

        """
        item = item or self
        search_args = [
            ('parent_id', '=', item.id),
        ]
        if published is not None:
            search_args.append(('website_published', '=', published))
        if nav is not None:
            search_args.append(('nav_include', '=', nav))

        type_ids = type_ids or (
            item.list_types_ids and item.list_types_ids._ids)
        if type_ids:
            search_args.append(
                ('type_id', 'in', type_ids)
            )
        order = order or 'sequence asc'
        pages = item.search(
            search_args,
            order=order
        )
        return pages


class CMSPageType(models.Model):
    """Model of a CMS page type."""

    _name = 'cms.page.type'
    _description = 'CMS page type'

    name = fields.Char('Name', translate=True)
