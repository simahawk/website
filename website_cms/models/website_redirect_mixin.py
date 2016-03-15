"""Website mixins."""

# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
# pylint: disable=R0903
# pylint: disable=R0201


from openerp import models
from openerp import fields
from openerp import api
from openerp import _
from openerp.addons.website_cms.utils import AttrDict


class WebsiteRedirectMixin(models.AbstractModel):
    """Handle redirection for inheriting objects.

    Fields:
    * `redirect_to_id`
    """

    _name = "website.redirect.mixin"
    _description = "Website Redirect Mixin"

    redirect_to_id = fields.Many2one(
        string='Redirect to',
        comodel_name='cms.redirect',
        help=(u"If valued, you will be redirected "
              u"to selected item permanently. "
              u"HTTP status 301 will be set. "),
        domain=[('create_date', '=', False)]
    )

    @api.model
    def has_redirect(self):
        """Return true if we have a redirection."""
        return bool(self.redirect_to_id)

    @api.model
    def get_redirect_data(self):
        """Return redirection data."""
        if not self.redirect_to_id:
            return None
        return AttrDict({
            'url': self.redirect_to_id.website_url,
            'status': int(self.redirect_to_id.status),
        })


class CMSRedirect(models.Model):
    """Add some more features here.

    Fields:
    * `redirect_to_id`
    """

    _name = "cms.redirect"
    _description = "CMS Redirect record"

    source = fields.Reference(
        string='Resource',
        selection='_reference_models',
    )
    name = fields.Char(
        string='Description',
    )
    cms_page_id = fields.Many2one(
        string='CMS Page',
        comodel_name='cms.page',
    )
    view_id = fields.Many2one(
        string='Odoo View',
        comodel_name='ir.ui.view',
        domain=[('page', '=', True)]
    )
    url = fields.Char(
        'Custom URL',
    )
    status = fields.Selection(
        string='Redirect HTTP Status',
        default=u'301',
        selection='_selection_status',
    )
    website_url = fields.Char(
        string='Website URL',
        compute='_compute_website_url',
        readonly=True
    )

    @api.model
    def _reference_models(self):
        _models = self.env['ir.model'].search([])
        # limit to cms.page for now
        return [(model.model, model.name)
                for model in _models
                if model.model == 'cms.page']

    @api.model
    def _selection_status(self):
        return [
            (u'301', _(u"301 Moved Permanently")),
            (u'307', _(u"307 Temporary Redirect")),
        ]

    @api.multi
    def _compute_website_url(self):
        """Compute redirect URL."""
        for item in self:
            if item.url:
                item.website_url = item.url
                continue
            if item.view_id:
                item.website_url = '/page/{}'.format(item.view_id.key)
                continue
            if item.cms_page_id:
                item.website_url = item.cms_page_id.website_url
                continue

    @api.multi
    def name_get(self):
        """Format displayed name."""
        res = []
        for item in self:
            name = [
                'Redirect to >',
            ]
            if self.url:
                name.append(item.url[:50])
            if self.view_id:
                name.append('View:' + item.view_id.name)
            if self.cms_page_id:
                name.append('Page: ' + self.cms_page_id.name)
            name.append('| Status: ' + self.status)
            res.append((item.id, ' '.join(name)))
        return res
