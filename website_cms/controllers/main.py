# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request


class ContextAwareMixin(object):
    """`Context` aware mixin klass.

    The `context` in this case is what odoo calls `main_object`.
    """

    template = ''

    def get_template(self, main_object, **post):
        """Retrieve rendering template."""
        template = self.template
        if hasattr(main_object, 'view_id') and main_object.view_id:
            template = main_object.view_id.key
        if not template:
            raise NotImplementedError("You must provide a template!")
        return template

    def get_render_values(self, main_object, **post):
        """Retrieve rendering values.

        Essentially we need 2 items: ``main_object`` and ``parent``.

        The main_object by default is the item being traversed.
        In other words: if you traverse the path to a page
        that page will be the main_object.

        The parent - if any - is always the parent of the item being traversed.

        For instance:

            /cms/page-1/page-2

        in this case, `page-2` is the main_object and `page-1` the parent.
        """

        parent = None
        if hasattr(main_object, 'parent_id'):
            # get the parent if any
            parent = main_object.parent_id

        values = {
            'main_object': main_object,
            'parent': parent,
        }
        return values

    def render(self, main_object, **post):
        """Retrieve parameters for rendering and render view template.
        """
        return request.website.render(
            self.get_template(main_object, **post),
            self.get_render_values(main_object, **post),
        )


class PageController(http.Controller, ContextAwareMixin):

    template = 'website_cms.page_default'

    @http.route([
        '/cms/<model("cms.page"):main_object>',
        '/cms/<path:path>/<model("cms.page"):main_object>',
    ], type='http', auth='public', website=True)
    def page(self, main_object, path=None, **post):
        """Handle a `page` route."""
        return self.render(main_object, **post)
