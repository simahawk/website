# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
import werkzeug
from openerp.tools.translate import _


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

        kw.update({
            'main_object': main_object,
            'parent': parent,
        })
        return kw

    def render(self, main_object, **kw):
        """Retrieve parameters for rendering and render view template."""
        return request.website.render(
            self.get_template(main_object, **kw),
            self.get_render_values(main_object, **kw),
        )


# `secure_model` is our converter that checks security
# see `website.security.mixin`.
PAGE_VIEW_ROUTES = [
    '/cms/<secure_model("cms.page"):main_object>',
    '/cms/<path:path>/<secure_model("cms.page"):main_object>',
    '/cms/<secure_model("cms.page"):main_object>/page/<int:page>',
    '/cms/<path:path>/<secure_model("cms.page"):main_object>/page/<int:page>',
    '/cms/<secure_model("cms.page"):main_object>/media/<model("cms.media.category"):media_categ>',
    '/cms/<secure_model("cms.page"):main_object>/media/<model("cms.media.category"):media_categ>/page/<int:page>',
    '/cms/<path:path>/<secure_model("cms.page"):main_object>/media/<model("cms.media.category"):media_categ>',
    '/cms/<path:path>/<secure_model("cms.page"):main_object>/media/<model("cms.media.category"):media_categ>/page/<int:page>',
]


class PageViewController(http.Controller, ContextAwareMixin):
    """CMS page view controller."""

    _template = 'website_cms.page_default'

    @http.route(PAGE_VIEW_ROUTES, type='http', auth='public', website=True)
    def view_page(self, main_object, **kw):
        """Handle a `page` route.

        Many optional arguments come from `kw` based on routing match above.
        """
        if main_object.has_redirect():
            data = main_object.get_redirect_data()
            redirect = werkzeug.utils.redirect(data.url, data.status)
            return redirect
        return self.render(main_object, **kw)


class PageCreateController(http.Controller, ContextAwareMixin):
    """CMS page create controller."""

    _template = 'website_cms.page_form'

    def get_template(self, main_object, **kw):
        """Override to force template."""
        return self._template

    def get_render_values(self, parent=None, **kw):
        """Override to preload values."""
        values = {
            'name': kw.get('name', 'New page title'),
            'parent_id': parent and parent.id,
            'website_published': False,
        }
        if parent:
            values['form_action'] = parent.website_url + '/add-page'
            for fname in ('type_id', 'view_id'):
                fvalue = getattr(parent, 'sub_page_' + fname)
                values[fname] = fvalue and fvalue.id or False
        return values

    @http.route([
        '/cms/add-page',
        '/cms/<secure_model("cms.page"):parent>/add-page',
        '/cms/<path:path>/<secure_model("cms.page"):parent>/add-page',
    ], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def add(self, parent=None, **kw):
        """Handle page add view and form submit."""
        if request.httprequest.method == 'GET':
            # render form
            return self.render(parent, **kw)
        elif request.httprequest.method == 'POST':
            # handle form submission
            values = self.get_render_values(parent=parent, **kw)
            new_page = request.env['cms.page'].create(values)
            url = new_page.website_url + '?enable_editor=1'
            return werkzeug.utils.redirect(url)
