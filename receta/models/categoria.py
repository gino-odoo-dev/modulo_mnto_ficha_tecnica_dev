from odoo import models, fields

class ProductCategoria(models.Model):
    _name = 'cl.product.categoria'
    _description = 'Product Categoria'

    codigo = fields.Char(string="Codigo", required=True, unique=True)
    name = fields.Char(string="Nombre", required=True)