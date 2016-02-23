# -*- coding: utf-8 -*-

# pylint: disable=E0401

from openerp import models
from openerp import fields
from openerp import api

from openerp.addons.website_cms.utils import AttrDict


class Website(models.Model):
    """Override website model."""

    _inherit = "website"

    social_instagram = fields.Char('Instagram account')

    # NOTE: we could move this as a base feature in website_cms

    @api.model
    def get_public_nav_pages(self, max_depth=3, pages=None, nav=True):
        """Return public pages for navigation.

        Given a `max_detph` build a list containing
        a hierarchy of menu and sub menu.
        Only `cms.page` having these flags turned on:
        * `website_published`

        By default consider only `nav_include` items.
        You can alter this behavior by passing
        `nav=False` to list contents non enabled for nav
        or `nav=None` to ignore nav settings.
        """
        result = []
        if pages is None:
            search_args = [
                ('parent_id', '=', False),
                ('website_published', '=', True),
            ]
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
                                      nav=nav)
            )
        # Find the best way to cache this? Or just rely on varnish & co.?
        # Odoo dispatcher already do cache: let's see if this is enough!
        return result

    @api.model
    def _build_page_item(self, item, max_depth=3, nav=True):
        """Recursive method to build main menu items.

        Return a dict-like object containing:
        * `name`: name of the page
        * `url`: public url of the page
        * `children`: list of children pages
        * `nav`: nav_include filtering
        """
        depth = max_depth or 3  # safe default to avoid infinite recursion
        sec_model = self.env['cms.page']
        # XXX: consider to define these args in the main method
        search_args = [
            ('parent_id', '=', item.id),
            ('website_published', '=', True),
        ]
        if nav is not None:
            search_args.append(('nav_include', '=', nav))
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
        })
        return res
