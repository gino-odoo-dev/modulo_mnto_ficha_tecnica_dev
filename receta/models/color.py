from odoo import models, fields

class ProductColor(models.Model):
    _name = 'cl.product.color'
    _description = 'Product Color'

    codigo = fields.Char(string="Codigo", required=True, unique=True)
    name = fields.Char(string="Nombre", required=True)