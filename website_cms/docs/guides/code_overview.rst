.. _code-overview:

#############
Code Overview
#############

Here is an overview of models and their behavior.


********
CMS Page
********

:py:class:`~website_cms.models.cms_page.CMSPage` is the main protagonist of this system. It's the object that you use to create website contents and organize it hierarchically.

Fields
======

Main fields
-----------

* ``name`` is the title of the page. Used for slug generation.
* ``description`` is a short summary of the content. Useful for listings, search results, etc
* ``body`` contains the HTML content of the page (what you edit via website builder)
* ``parent_id`` m2o to parent page
* ``children_ids`` o2m to children pages
* ``media_ids`` o2m to `cms.media` objects
* ``type_id`` m2o to `cms.page.type` object. You can filter pages or use different views based on it. Defaults to `website_cms.default_page_type`.
* ``view_id`` m2o to `ir.ui.view` object. This is the view that is used to display the page.
* ``sub_page_type_id`` m2o to `cms.page.type` object. Set default page type for children pages. You can use this to pre-configure a website section behavior.
* ``sub_page_view_id`` m2o to `ir.ui.view` object. Set default page view for children pages. You can use this to pre-configure a website section look an feel.
* ``list_types_ids`` m2m to `cms.page.type`. Useful to force listed page types.
* ``nav_include`` whether to include or not the page into main navigation building (see ``website.get_nav_pages``).
* ``path`` is a computed field that matches the hierarchy of a page (eg: /A/B/C).

Helper methods
==============

Get the root page
-----------------

The root page is the upper anchestor of a hierarchy of pages.

.. code-block:: python

    >>> page.get_root()


List sub pages
---------------

A page can contain pages, this is how you can list them.

.. code-block:: python

    >>> page.get_listing()

By default it:

* order by sequence (position inside the parent)
* include only published items, unless you are into `website_cms.cms_manager` group
* if `page.list_types_ids` is valued it returns only sub pages matching that types

To learn how to tweak filtering take a look at :doc:`advanced_listing` section.


Mixins and extra features
=========================

The CMS page model rely on several mixins. Namely:

``website.seo.metadata``
    Standard from `web` module. Provides metadata for SEO tuning.

``website.published.mixin``
    Standard from `web` module. Provides basic publishing features.

``website.image.mixin`` (needs improvements)
    New from `website_cms`. Provides image the following image fields:
        * ``image`` full size image
        * ``image_medium`` medium size image
        * ``image_thumb`` thumb size image

``website.orderable.mixin``
    New from `website_cms`. Provides ``sequence`` field used to sort pages.

``website.coremetadata.mixin``
    New from `website_cms`. Provides core metadata.
    Exposes core fields:
        * ``create_date``
        * ``create_uid``
        * ``write_date``
        * ``write_uid``
    Adds extra fields:
        * ``published_date``
        * ``published_uid``

``website.security.mixin``
    New from `website_cms`. Provides per-content security control.
    By using the field ``view_group_ids`` you can decide which group can view the page.
    View permission per-user and edit permission are missing as of today.
    See :doc:`permissions` for further info.

``website.redirect.mixin``
    New from `website_cms`. Provides ability to make a page redirect to another CMS page, an Odoo page (`ir.ui.view` item with `page=True`) or an external link.
    See :doc:`redirects` for further info.
