# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request


class ContextAwareMixin(object):
    """`context` aware mixin klass."""

    template = ''

    def get_template(self, context, **post):
        """Retrieve rendering template."""
        template = self.template
        if hasattr(context, 'view_id') and context.view_id:
            template = context.view_id.get_view_xmlid()[0]
        if not template:
            raise NotImplementedError("You must provide a template!")
        return template

    def get_render_values(self, context, **post):
        """Retrieve rendering values.

        Essentially we need 2 items: ``context`` and ``parent``.

        The context by default is the item being traversed.
        In other words: if you traverse the path to a section
        that section will be the context.

        You can override this behavior by setting a `view_item`.
        If this field is valued the default context for the view
        will become the linked item (usually a page contained in the section).

        The parent - if any - is always the parent of the item being traversed.

        For instance:

            /cms/section-1/section-2

        in this case, `section-2` is the context and `section-1` the parent.
        If `section-1` contains a page `page-1`
        and this page has been linked via `view_item` field,
        the context will be `page-1`.
        """

        parent = None
        if hasattr(context, 'parent_id'):
            # get the parent if any
            parent = context.parent_id

        if hasattr(context, 'view_item') and context.view_item:
            # get view item as context if any
            context = context.view_item

        values = {
            'context': context,
            'parent': parent,
        }
        return values

    def render(self, context, **post):
        """Retrieve parameters for rendering and render view template.
        """
        return request.website.render(
            self.get_template(context, **post),
            self.get_render_values(context, **post),
        )


class PageController(http.Controller, ContextAwareMixin):

    template = 'website_cms.page_default'

    @http.route([
        '/cms/<model("cms.page"):context>',
        '/cms/<path:path>/<model("cms.page"):context>',
    ], type='http', auth='public', website=True)
    def page(self, context, path=None, **post):
        """Handle a `section` route."""
        return self.render(context, **post)
