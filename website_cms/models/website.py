# -*- coding: utf-8 -*-

from openerp import models
from openerp import fields
from openerp import api
from openerp.tools import image as image_tools


class WebsiteImageMixin(models.AbstractModel):
    _name = "website.image.mixin"
    _description = "A mixin for providing image features"

    image = fields.Binary('Image', attachment=True)
    image_medium = fields.Binary(
        'Medium',
        compute="_get_image",
        store=True,
        attachment=True
    )
    image_thumb = fields.Binary(
        'Thumbnail',
        compute="_get_image",
        store=True,
        attachment=True
    )

    @api.depends('image')
    @api.multi
    def _get_image(self):
        for record in self:
            if record.image:
                record.image_medium = self.crop_image(record.image)
                record.image_thumb = self.crop_image(record.image,
                                                     thumbnail_ratio=6)
            else:
                record.image_medium = False
                record.iamge_thumb = False

    @api.model
    def crop_image(self, image, type_='top', ratio=(4, 3), thumbnail_ratio=4):
        return image_tools.crop_image(
            image,
            type=type_,
            ratio=ratio,
            thumbnail_ratio=thumbnail_ratio
        )



class WebsiteOrderableMixin(models.AbstractModel):
    _name = "website.orderable.mixin"
    _description = "A mixin for providing sorting features"

    sequence = fields.Integer(
        'Sequence',
        required=True,
        default=lambda self: self._default_sequence()
    )

    @api.model
    def _default_sequence(self):
        last = self.search([], limit=1, order='sequence desc')
        if not last:
            return 0
        return last.sequence + 1



class WebsiteCoreMetadataMixin(models.AbstractModel):
    _name = "website.coremetadata.mixin"
    _description = "A mixin for exposing core metadata fields"

    create_date = fields.Datetime(
        'Created on',
        select=True,
        readonly=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        'Author',
        select=True,
        readonly=True,
    )
    write_date = fields.Datetime(
        'Created on',
        select=True,
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        'Last Contributor',
        select=True,
        readonly=True,
    )
