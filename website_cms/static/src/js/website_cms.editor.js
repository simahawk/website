odoo.define('website_cms.new_page', function (require) {
"use strict";

var core = require('web.core');
var base = require('web_editor.base');
var Model = require('web.Model');
var website = require('website.website');
var contentMenu = require('website.contentMenu');

var _t = core._t;

contentMenu.TopBar.include({
    new_cms_page: function () {
        var model = new Model('cms.page');
        model.call('name_search', [],
                   { context: base.get_context() }).then(function (page_ids) {
            if (page_ids.length == 0) {
                debugger;
                document.location = '/cms/add';
            } else if (page_ids.length == 1){
                debugger;
                document.location = '/cms/' + page_ids[0][0] + '/add';
            }
            else if (page_ids.length > 1) {
                debugger;
                website.prompt({
                    id: "editor_new_page",
                    window_title: _t("New CMS Page"),
                    select: "Select parent",
                    init: function () {
                        debugger;
                        return page_ids;
                    },
                }).then(function (parent_id) {
                        debugger;
                    if (parent_id){
                        document.location = '/cms/' + parent_id + '/add';
                    }
                });
            }
        });
    },
});

});
