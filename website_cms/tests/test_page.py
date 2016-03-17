# -*- coding: utf-8 -*-

# import unittest
# from lxml import etree as ET, html
# from lxml.html import builder as h


from openerp.tests import common
# from openerp.addons.website.models.website import slug


class TestPage(common.TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestPage, self).setUp()
        self.model = self.env['cms.page']
        self.all_pages = []
        self.page = self.create({
            'name': "Test Page",
            'sub_page_type_id': self.news_type.id,
            'website_published': True,
        })
        # XXX: should find a way to have default type
        # for sub page loaded w/out context
        # but looks like we cannot retrieve that
        # from parent neither w/ @api.depends
        self.sub_page = self.create({
            'name': "Sub Page",
            'parent_id': self.page.id,
            'website_published': True,
        }, default_type_id=self.page.sub_page_type_id.id)
        self.subsub_page = self.create({
            'name': 'Sub Sub',
            'parent_id': self.sub_page.id,
            'website_published': True,
        }, default_type_id=self.page.sub_page_type_id.id)

    def tearDown(self):
        self.registry('cms.page').unlink(
            self.cr, 1, [x.id for x in self.all_pages])

    def create(self, values, **context):
        item = self.model.with_context(**context).create(values)
        self.all_pages.append(item)
        return item

    @property
    def default_type(self):
        return self.env.ref('website_cms.default_page_type')

    @property
    def news_type(self):
        return self.env.ref('website_cms.news_page_type')

    def test_page_default_values(self):
        # check page types
        self.assertEqual(self.page.type_id.id,
                         self.default_type.id)
        self.assertEqual(self.sub_page.type_id.id,
                         self.news_type.id)
        self.assertTrue(
            self.sub_page.id in self.page.children_ids._ids)

        # published date
        new = self.create({'name': 'New'})
        self.assertTrue(not new.published_date)
        new.website_published = True
        self.assertTrue(new.published_date)
        self.all_pages.remove(new)
        new.unlink()

    def test_hierarchy(self):
        # check hierarchy and paths
        self.assertEqual(
            self.page.id, self.sub_page.parent_id.id)
        self.assertEqual(
            self.page.path, '/')
        self.assertEqual(
            self.page.full_path(), '/Test Page')
        self.assertEqual(
            self.sub_page.path, '/Test Page')
        self.assertEqual(
            self.sub_page.full_path(), '/Test Page/Sub Page')
        # check URLs
        self.assertEqual(
            self.page.website_url,
            '/cms/test-page-%s' % self.page.id
        )
        sub_url = '/cms/test-page-%s/sub-page-%s' % (
            self.page.id, self.sub_page.id)
        self.assertEqual(
            self.sub_page.website_url,
            sub_url,
        )
        self.assertEqual(
            self.subsub_page.website_url,
            sub_url + '/sub-sub-%s' % self.subsub_page.id
        )

    def test_get_root(self):
        self.assertEqual(self.page.get_root(),
                         self.page)
        self.assertEqual(self.sub_page.get_root(),
                         self.page)
        self.assertEqual(self.subsub_page.get_root(),
                         self.page)
        self.assertEqual(self.subsub_page.get_root(upper_level=1),
                         self.sub_page)

    def test_get_listing(self):
        # search in root
        root_listing = self.model.get_listing(path='/')
        # all pages must be there
        self.assertEqual(len(root_listing),
                         len(self.model.search([])))
        for page in self.all_pages:
            self.assertTrue(page in root_listing)

        # and ordered by sequence
        for pos, page in enumerate(self.all_pages):
            self.assertEqual(root_listing[pos], page)

        # list a single page's content
        page_listing = self.page.get_listing()
        self.assertEqual(len(page_listing), 1)

        # create a news container
        container = self.create({
            'name': 'News container',
            'parent_id': self.page.id,
            'sub_page_type_id': self.news_type.id,
            'website_published': True,
        })
        # add some news to it
        news = []
        for i in xrange(1, 6):
            news.append(
                self.create({
                    'name': 'News %d' % i,
                    'parent_id': container.id,
                    'type_id': container.sub_page_type_id.id,
                    'website_published': True,
                })
            )

        # check listing
        root_listing = self.page.get_listing(path='/')
        self.assertEqual(len(root_listing), len(self.all_pages))

        # if no path provided: get direct children only
        page_listing = self.page.get_listing()
        self.assertEqual(len(page_listing), 2)

        # container's listing gets direct subpages only
        container_listing = container.get_listing()
        self.assertEqual(len(container_listing), len(news))

        # ordered by sequence
        for i, news_item in enumerate(news):
            self.assertEqual(container_listing[i], news_item)

        # ordered by name
        ordered_name = container.get_listing(order='name asc')
        self.assertEqual(
            ordered_name[0].name,
            'News 1'
        )
        self.assertEqual(
            ordered_name[4].name,
            'News 5'
        )
        ordered_name = container.get_listing(order='name desc')
        self.assertEqual(
            ordered_name[0].name,
            'News 5'
        )
        self.assertEqual(
            ordered_name[4].name,
            'News 1'
        )

        # published/not published
        news[3].website_published = False
        news[4].website_published = False
        # by default list only published
        self.assertEqual(len(container.get_listing()), 3)
        # but we can tweak filters
        self.assertEqual(len(container.get_listing(published=False)), 2)
        self.assertEqual(len(container.get_listing(published=None)), 5)

        # included in nav
        news[1].nav_include = True
        news[2].nav_include = True
        self.assertEqual(
            len(container.get_listing(nav=True, published=None)), 2
        )
        self.assertEqual(
            len(container.get_listing(nav=False, published=None)), 3
        )

        # by type refs
        root_listing = self.model.get_listing(
            path='/', published=None,
            types_ref='website_cms.news_page_type')
        # by type ids
        all_news = self.model.search(
            [('type_id', '=', self.news_type.id)])
        self.assertEqual(len(root_listing),
                         len(all_news))
        root_listing = self.model.get_listing(
            path='/', published=None,
            types_ids=(self.default_type.id, ))
        self.assertEqual(len(root_listing),
                         len(self.all_pages) - len(all_news))

    def test_permissions(self):
        # TODO
        pass
