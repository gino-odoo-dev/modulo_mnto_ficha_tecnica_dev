from odoo import models, fields

class ProductTalla(models.Model):
    _name = 'cl.product.tallas'
    _description = 'Product Tallas'

    code = fields.Char(string="Codigo", required=True)
    name = fields.Char(string="Nombre", required=True)

