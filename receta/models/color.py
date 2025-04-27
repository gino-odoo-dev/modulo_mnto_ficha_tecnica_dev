from odoo import models, fields

class ProductColor(models.Model):
    _name = 'cl.product.color'
    _description = 'Product Color'

    code = fields.Char(string="Codigo", required=True)
    name = fields.Char(string="Nombre", required=True)
