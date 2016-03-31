# -*- coding: utf-8 -*-

import base64

from openerp import http
from openerp.http import request
import werkzeug
from werkzeug.exceptions import NotFound
from openerp.tools.translate import _


class ContextAwareMixin(object):
    """`Context` aware mixin klass.

    The `context` in this case is what odoo calls `main_object`.
    """

    # default template
    template = ''

    def get_template(self, main_object, **kw):
        """Retrieve rendering template."""
        template = self.template

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

    template = 'website_cms.page_default'

    @http.route(PAGE_VIEW_ROUTES, type='http', auth='public', website=True)
    def view_page(self, main_object, **kw):
        """Handle a `page` route.

        Many optional arguments come from `kw` based on routing match above.
        """
        site = request.website
        # check published
        # XXX: this is weird since it should be done by `website` module itself.
        # Alternatively we can put this in our `secure model` route handler.
        if not site.is_publisher() and not main_object.website_published:
            raise NotFound

        if main_object.has_redirect():
            data = main_object.get_redirect_data()
            redirect = werkzeug.utils.redirect(data.url, data.status)
            return redirect
        if 'edit_translations' in kw:
            # for some reasons here we get an empty string
            # as value, and this breaks translation editor initialization :(
            kw['edit_translations'] = True

        # handle translations switch
        if site and 'edit_translations' not in kw \
                and not site.default_lang_code == request.lang \
                and not site.is_publisher():
            # check if there's any translation for current page in request lang
            if request.lang not in main_object.get_translations():
                raise NotFound
        return self.render(main_object, **kw)


class PageFormMixin(ContextAwareMixin):
    """CMS page Form controller."""

    form_name = ''
    form_title = ''
    form_mode = ''
    form_fields = ('name', 'description', )
    form_file_fields = ('image', )

    def get_template(self, main_object, **kw):
        """Override to force template."""
        return self.template

    def load_defaults(self, main_object):
        """Override to load default values."""
        defaults = {}
        if not main_object:
            return defaults
        for fname in self.form_fields:
            defaults[fname] = getattr(main_object, fname)
        for fname in self.form_file_fields:
            defaults['has_' + fname] = bool(getattr(main_object, fname))
        return defaults

    def get_render_values(self, main_object, parent=None, **kw):
        """Override to preload values."""
        _super = super(PageFormMixin, self)
        values = _super.get_render_values(main_object, **kw)

        base_url = '/cms'
        if main_object:
            base_url = main_object.website_url

        name = request.params.get('name') or kw.get('name')
        values.update({
            'name': name,
            'form_action': base_url + '/' + self.form_name,
        })

        values.update(self.load_defaults(main_object, **kw))

        # make sure we do not allow website builder Form
        values['editable'] = values['translatable'] = False
        # XXX: we should handle this
        # values['errors'] = []
        # values['status_message'] = ''
        values['view'] = self
        return values


class CreatePage(http.Controller, PageFormMixin):
    """CMS page create controller."""

    form_name = 'add-page'
    form_title = _('Add page')
    form_mode = 'create'
    template = 'website_cms.page_form'

    def load_defaults(self, main_object, **kw):
        """Override to preload values."""
        defaults = {}
        if main_object:
            defaults['parent_id'] = main_object.id
            defaults['form_action'] = \
                main_object.website_url + '/' + self.form_name
            for fname in ('type_id', 'view_id'):
                fvalue = getattr(main_object, 'sub_page_' + fname)
                defaults[fname] = fvalue and fvalue.id or False

        return defaults

    @http.route([
        '/cms/add-page',
        '/cms/<secure_model("cms.page"):parent>/add-page',
        '/cms/<path:path>/<secure_model("cms.page"):parent>/add-page',
    ], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def add(self, parent=None, **kw):
        """Handle page add view and form submit."""
        if request.httprequest.method == 'GET':
            return self.render(parent, **kw)

        elif request.httprequest.method == 'POST':
            # handle form submission
            values = self.get_render_values(parent, **kw)
            new_page = request.env['cms.page'].create(values)
            url = new_page.website_url + '?enable_editor=1'
            return werkzeug.utils.redirect(url)


class EditPage(http.Controller, PageFormMixin):
    """CMS page edit controller."""

    form_name = 'edit-page'
    form_title = _('Edit page')
    form_mode = 'write'
    template = 'website_cms.page_form'

    def extract_values(self, request, main_object, **kw):
        """Override to manipulate POST values."""
        # TODO: sanitize user input and add validation!
        if 'image' in kw:
            field_value = kw.pop('image')
            if hasattr(field_value, 'read'):
                image_content = field_value.read()
                image_content = base64.encodestring(image_content)
            else:
                image_content = field_value.split(',')[-1]
            if kw.get('keep_image') != 'yes':
                # empty or not, we want to replace it
                kw['image'] = image_content
        return kw

    @http.route([
        '/cms/<secure_model("cms.page"):main_object>/edit-page',
        '/cms/<path:path>/<secure_model("cms.page"):main_object>/edit-page',
    ], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def edit(self, main_object, **kw):
        """Handle page edit view and form submit."""
        if request.httprequest.method == 'GET':
            # render form
            return self.render(main_object, **kw)
        elif request.httprequest.method == 'POST':
            # handle form submission
            values = self.extract_values(request, main_object, **kw)
            main_object.write(values)
            query = {
                'status_message': _(u'Page updated')
            }
            return http.local_redirect(main_object.website_url,
                                       query=query)
