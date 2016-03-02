# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
import werkzeug


class ContextAwareMixin(object):
    """`Context` aware mixin klass.

    The `context` in this case is what odoo calls `main_object`.
    """

    # default template
    _template = ''

    def get_template(self, main_object, **kw):
        """Retrieve rendering template."""
        template = self._template

        if getattr(main_object, 'view_id', None):
            template = main_object.view_id.key

        if getattr(main_object, 'default_view_item_id', None):
            view_item = main_object.default_view_item_id
            if view_item.view_id:
                template = view_item.view_id.key

        if not template:
            raise NotImplementedError("You must provide a template!")
        return template

    def get_render_values(self, main_object, **kw):
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
        if getattr(main_object, 'parent_id', None):
            # get the parent if any
            parent = main_object.parent_id

        if getattr(main_object, 'default_view_item_id', None):
            # get a default item if any
            main_object = main_object.default_view_item_id

        values = {
            'main_object': main_object,
            'parent': parent,
        }
        return values

    def render(self, main_object, **kw):
        """Retrieve parameters for rendering and render view template."""
        return request.website.render(
            self.get_template(main_object, **kw),
            self.get_render_values(main_object, **kw),
        )


class PageController(http.Controller, ContextAwareMixin):
    """CMS page controller."""

    _template = 'website_cms.page_default'

    # `secure_model` is a new converter that check security
    # see `website.security.mixin`.
    @http.route([
        '/cms/<secure_model("cms.page"):main_object>',
        '/cms/<path:path>/<secure_model("cms.page"):main_object>',
    ], type='http', auth='public', website=True)
    def page(self, main_object, path=None, **kw):
        """Handle a `page` route."""
        if main_object.redirect_to_id:
            redirect_url = main_object.redirect_to_id.website_url
            redirect = werkzeug.utils.redirect(redirect_url, 301)
            return redirect
        return self.render(main_object, **kw)
