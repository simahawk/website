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


class PageViewController(http.Controller, ContextAwareMixin):
    """CMS page view controller."""

    _template = 'website_cms.page_default'

    # `secure_model` is a new converter that check security
    # see `website.security.mixin`.
    @http.route([
        '/cms/<secure_model("cms.page"):main_object>',
        '/cms/<path:path>/<secure_model("cms.page"):main_object>',
        '/cms/<secure_model("cms.page"):main_object>/page/<int:page>',
        '/cms/<path:path>/<secure_model("cms.page"):main_object>/page/<int:page>',
    ], type='http', auth='public', website=True)
    def view_page(self, main_object, **kw):
        """Handle a `page` route."""
        if main_object.redirect_to_id:
            redirect_url = main_object.redirect_to_id.website_url
            redirect = werkzeug.utils.redirect(redirect_url, 301)
            return redirect
        return self.render(main_object, **kw)


class PageCreateController(http.Controller, ContextAwareMixin):
    """CMS page create controller."""

    _template = 'website_cms.page_form'

    def get_render_values(self, parent):
        values = super(PageCreateController, self).get_render_values(parent)
        values.update({
            'name': _('New page title'),
            'parent_id': parent and parent.id,
            'website_published': False,
        })
        if parent:
            for fname in ('type_id', 'view_id'):
                fvalue = getattr(parent, 'sub_page_' + fname)
                values['type_id'] = fvalue and fvalue.id or False
        return values

    @http.route([
        '/cms/add',
        '/cms/<secure_model("cms.page"):parent>/add',
        '/cms/<path:path>/<secure_model("cms.page"):parent>/add',
    ], type='http', auth='user', website=True)
    def add(self, parent=None, **kw):
        import pdb;pdb.set_trace()
        return self.render(parent, **kw)
        # new_page = request.env['cms.page'].create(values)
        # url = new_page.website_url + '?enable_editor=1'
        # return werkzeug.utils.redirect(url)
