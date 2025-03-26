from odoo import models, fields

class ProductTalla(models.Model):
    _name = 'cl.product.talla'
    _description = 'Product Talla'

    codigo = fields.Char(string="Codigo", required=True, unique=True)
    name = fields.Char(string="Nombre", required=True)