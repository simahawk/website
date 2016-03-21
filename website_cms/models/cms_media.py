# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
from openerp import models
from openerp import fields
from openerp import api
# from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

from openerp.addons.website_cms.utils import IMAGE_TYPES
from openerp.addons.website_cms.utils import VIDEO_TYPES
from openerp.addons.website_cms.utils import AUDIO_TYPES


class CMSMedia(models.Model):
    """Model of a CMS media."""

    _name = 'cms.media'
    _description = 'CMS Media'
    _order = 'sequence, id'
    _inherit = ['ir.attachment',
                'website.published.mixin',
                'website.orderable.mixin',
                'website.coremetadata.mixin',
                'website.image.mixin',
                'website.security.mixin']

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        'Description',
        translate=True,
    )
    lang_id = fields.Many2one(
        string='Language',
        comodel_name='res.lang',
        domain=lambda self: self._domain_lang_id(),
        select=True,
    )
    category_id = fields.Many2one(
        string='Category',
        comodel_name='cms.media.category',
        compute='_compute_category_id',
        store=True,
        readonly=True,
    )
    force_category_id = fields.Many2one(
        string='Force category',
        comodel_name='cms.media.category',
        domain=[('active', '=', True)],
    )
    icon = fields.Char(
        'Icon',
        compute='_compute_icon',
        readonly=True,
    )
    website_url = fields.Char(
        'Website URL',
        compute='_website_url',
        readonly=True,
    )

    @api.model
    def _domain_lang_id(self):
        """Return options for lang."""
        try:
            website = self.env['website'].get_current_website()
        except RuntimeError:
            # *** RuntimeError: object unbound
            website = None
        if website:
            languages = website.language_ids
        else:
            languages = self.env['res.lang'].search([])
        return [('id', 'in', languages.ids)]

    @api.multi
    @api.depends('force_category_id', 'mimetype', 'url')
    def _compute_category_id(self):
        """Compute media category."""
        default = self.env.ref('website_cms.media_category_document')
        for item in self:
            if item.force_category_id:
                item.category_id = item.force_category_id
                continue
            else:
                guessed = self.guess_category(item.mimetype)
                if guessed:
                    item.category_id = guessed
                    continue
            item.category_id = default

    def guess_category(self, mimetype):
        """Guess media category by mimetype."""
        xmlid = None
        # look for real media first
        if mimetype in IMAGE_TYPES:
            xmlid = 'website_cms.media_category_image'
        if mimetype in VIDEO_TYPES:
            xmlid = 'website_cms.media_category_video'
        if mimetype in AUDIO_TYPES:
            xmlid = 'website_cms.media_category_audio'
        if xmlid:
            return self.env.ref(xmlid)
        # fallback to search by mimetype
        category_model = self.env['cms.media.category']
        cat = category_model.search([
            ('mimetypes', '=like', '%{}%'.format(mimetype)),
            ('active', '=', True)
        ])
        return cat and cat[0] or None

    @api.multi
    @api.depends('category_id', 'mimetype', 'url')
    def _compute_icon(self):
        """Compute media icon."""
        for item in self:
            item.icon = item.get_icon()

    @api.model
    def get_icon(self, mimetype=None):
        """Return a CSS class for icon.

        You can override this to provide different
        icons for your media.
        """
        # TODO: improve this default
        return 'file-text'

    @api.multi
    def _website_url(self):
        """Override method defined by `website.published.mixin`."""
        url_pattern = '/web/content/{model}/{ob_id}/{field_name}/{filename}'
        for item in self:
            url = item.url
            if not url:
                url = url_pattern.format(
                    model=item._name,
                    ob_id=item.id,
                    field_name='datas',
                    filename=item.datas_fname or 'download',
                )
            item.website_url = url

    @api.multi
    def update_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})


class CMSMediaCategory(models.Model):
    """Model of a CMS media category."""

    _name = 'cms.media.category'
    _inherit = 'website.orderable.mixin'
    _description = 'CMS Media Category'

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    mimetypes = fields.Text(
        'Mimetypes',
        help=('Customize mimetypes associated '
              'to this category.')
    )
    icon = fields.Char(
        'Icon',
    )
    active = fields.Boolean('Active?', default=True)

    @api.model
    def public_slug(self):
        """Used to generate relative URL for category."""
        return slug(self)
