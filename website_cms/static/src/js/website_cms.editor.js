odoo.define('website_cms.new_page', function (require) {
"use strict";

    var core = require('web.core');
    var base = require('web_editor.base');
    var Model = require('web.Model');
    var contentMenu = require('website.contentMenu');
    var ajax = require('web.ajax');

    var _t = core._t;

    contentMenu.TopBar.include({

        getMainObject: function () {
            // barely taken from website.contentMenu.js
            var repr = $('html').data('main-object');
            var m = repr.match(/(.+)\((\d+),(.*)\)/);
            if (!m) {
                return null;
            } else {
                return {
                    model: m[1],
                    id: m[2]|0
                };
            }
        },
        new_cms_page: function () {
            var self = this;
            var main_obj = self.getMainObject();
            var context = base.get_context();
            var create_url = '/cms/add-page';
            // if current context is a cms.page
            // we add the page inside it
            if (main_obj && main_obj.model == 'cms.page'){
                var model = new Model(main_obj.model);
                model.call(
                    'read',
                    [[main_obj.id], ['website_url'],
                    base.get_context()]
                ).then(function (result) {
                    console.log(result);
                    if (result){
                        console.log(result[0].website_url + '/add-page');
                        document.location = result[0].website_url + '/add-page';
                    }
                });
            }
            document.location = create_url;
        }
    });

});
