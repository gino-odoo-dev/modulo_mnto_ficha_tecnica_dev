from odoo import models, fields

class ProductCategoria(models.Model):
    _name = 'cl.product.categoria'
    _description = 'Product Categoria'

    code = fields.Char(string="Codigo", required=True)
    name = fields.Char(string="Nombre", required=True)
