from odoo import models, fields

class ProductMarca(models.Model):
    _name = 'cl.product.marca'
    _description = 'Product Marca'

    codigo = fields.Char(string="Codigo", required=True)
    name = fields.Char(string="Nombre", required=True)
