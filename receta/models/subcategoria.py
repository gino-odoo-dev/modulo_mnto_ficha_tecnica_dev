from odoo import models, fields

class ProductSubcategoria(models.Model):
    _name = 'cl.product.subcategoria'
    _description = 'Product Subcategoria'

    codigo = fields.Char(string="Codigo", required=True, unique=True)
    name = fields.Char(string="Nombre", required=True)