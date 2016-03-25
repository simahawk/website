# -*- coding: utf-8 -*-

# pylint: disable=E0401

from openerp import models
# from openerp import fields
from openerp import api
from openerp import tools
from openerp.addons.web.http import request

from openerp.addons.website_cms.utils import AttrDict


class Website(models.Model):
    """Override website model."""

    _inherit = "website"

    @api.model
    @tools.ormcache('max_depth', 'pages', 'nav', 'type_ids', 'published')
    def get_nav_pages(self, max_depth=3, pages=None,
                      nav=True, type_ids=None,
                      published=True):
        """Return pages for navigation.

        Given a `max_detph` build a list containing
        a hierarchy of menu and sub menu.
        Only `cms.page` having these flags turned on:
        * `website_published`

        By default consider only `nav_include` items.
        You can alter this behavior by passing
        `nav=False` to list contents non enabled for nav
        or `nav=None` to ignore nav settings.

        * `type_ids`: filter pages by a list of types' ids

        By default consider only `website_cms.default_page_type` type.

        * `published`: filter pages by a publishing state
        """
        type_ids = type_ids or [
            self.env.ref('website_cms.default_page_type').id, ]
        result = []
        if pages is None:
            search_args = [
                ('parent_id', '=', False),
                ('type_id', 'in', type_ids)
            ]
            if published is not None:
                search_args.append(('website_published', '=', published))

            if nav is not None:
                search_args.append(('nav_include', '=', nav))

            sec_model = self.env['cms.page']
            pages = sec_model.search(
                search_args,
                order='sequence asc'
            )
        for item in pages:
            result.append(
                self._build_page_item(item,
                                      max_depth=max_depth,
                                      nav=nav,
                                      type_ids=type_ids,
                                      published=published)
            )
        return result

    @api.model
    def _build_page_item(self, item, max_depth=3,
                         nav=True, type_ids=None,
                         published=True):
        """Recursive method to build main menu items.

        Return a dict-like object containing:
        * `name`: name of the page
        * `url`: public url of the page
        * `children`: list of children pages
        * `nav`: nav_include filtering
        * `type_ids`: filter pages by a list of types' ids
        * `published`: filter pages by a publishing state
        """
        depth = max_depth or 3  # safe default to avoid infinite recursion
        sec_model = self.env['cms.page']
        # XXX: consider to define these args in the main method
        search_args = [
            ('parent_id', '=', item.id),
        ]
        if published is not None:
            search_args.append(('website_published', '=', published))
        if nav is not None:
            search_args.append(('nav_include', '=', nav))
        if type_ids is not None:
            search_args.append(('type_id', 'in', type_ids))
        subs = sec_model.search(
            search_args,
            order='sequence asc'
        )
        while depth != 0:
            depth -= 1
            children = [self._build_page_item(x, max_depth=depth)
                        for x in subs]
        res = AttrDict({
            'id': item.id,
            'name': item.name,
            'url': item.website_url,
            'children': children,
            'website_published': item.website_published,
        })
        return res

    @api.model
    def safe_image_url(self, record, field, size=None, check=True):
        """Return image url if exists."""
        sudo_record = record.sudo()
        if hasattr(sudo_record, field):
            if not getattr(sudo_record, field) and check:
                # no image here yet
                return ''
            return self.image_url(record, field, size=size)
        return ''

    @api.model
    def download_url(self, item, field_name, filename=''):
        if not filename:
            # XXX: we should calculate the filename from the field
            # but in some cases we do not have a proxy for the value
            # like for attachments, so we don't have a way
            # to get the original name of the file.
            filename = 'download'
        url = '/web/content/{model}/{ob_id}/{field_name}/{filename}'
        return url.format(
            model=item._name,
            ob_id=item.id,
            field_name=field_name,
            filename=filename,
        )

    @api.model
    def get_media_categories(self, active=True):
        """Return all available media categories."""
        return self.env['cms.media.category'].search(
            [('active', '=', active)])

    def get_alternate_languages(self, cr, uid, ids,
                                req=None, context=None,
                                main_object=None):
        """Override to drop not available translations."""
        langs = super(Website, self).get_alternate_languages(
            cr, uid, ids, req=req, context=context)

        avail_langs = None
        if main_object and main_object._name == 'cms.page':
            # avoid building URLs for not translated contents
            avail_transl = main_object.get_translations()
            avail_langs = [x.split('_')[0] for x in avail_transl.iterkeys()]

        if avail_langs is not None:
            langs = [lg for lg in langs if lg['short'] in avail_langs]
        return langs
