"""Website mixins."""

# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
# pylint: disable=R0903
# pylint: disable=R0201


from openerp import models
from openerp import fields
from openerp import api
from openerp.tools import image as image_tools


class WebsiteImageMixin(models.AbstractModel):
    """Image mixin for website models.

    Provide fields:

    * `image` (full size image)
    * `image_medium` (`image` resized)
    * `image_thumb` (`image` resized)
    """

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
        """Calculate resized images."""
        for record in self:
            if record.image:
                record.image_medium = self.crop_image(record.image)
                record.image_thumb = self.crop_image(record.image,
                                                     thumbnail_ratio=6)
            else:
                record.image_medium = False
                record.iamge_thumb = False

    @api.model
    def crop_image(self, image, type_='top',
                   ratio=(4, 3), thumbnail_ratio=4):
        """Crop image fields."""
        return image_tools.crop_image(
            image,
            type=type_,
            ratio=ratio,
            thumbnail_ratio=thumbnail_ratio
        )


class WebsiteOrderableMixin(models.AbstractModel):
    """Orderable mixin to allow sorting of objects.

    Add a sequence field that you can use for sorting items
    in tree views. Add the field to a view like this:

        <field name="sequence" widget="handle" />

    Default sequence is calculated as last one + 1.
    """

    _name = "website.orderable.mixin"
    _description = "A mixin for providing sorting features"
    _order = 'sequence, id'

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
    """Expose core fields to be usable in backend and frontend.

    Fields:
    * `create_date`
    * `create_uid`
    * `write_date`
    * `write_uid`
    """

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
