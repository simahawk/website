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
        """Retrieve rendering values."""
        values = {
            'context': context,
        }
        if hasattr(context, 'parent_id'):
            values['parent'] = context.parent_id
        return values

    def render(self, context, **post):
        """Retrieve parameters for rendering and render view template.
        """
        return request.website.render(
            self.get_template(context, **post),
            self.get_render_values(context, **post),
        )


class SectionController(http.Controller, ContextAwareMixin):

    template = 'website_cms.section_default'

    @http.route([
        '/cms/<model("cms.section"):context>',
        '/cms/<path:path>/<model("cms.section"):context>',
    ], type='http', auth='public', website=True)
    def section(self, context, path=None, **post):
        """Handle a `section` route."""
        return self.render(context, **post)


class PageController(http.Controller, ContextAwareMixin):

    template = 'website_cms.page_default'

    @http.route([
        '/cms/<model("cms.page"):context>',
        '/cms/<path:path>/<model("cms.page"):context>',
    ], type='http', auth='public', website=True)
    def page(self, context, path=None, **post):
        """Handle a `section` route."""
        return self.render(context, **post)
