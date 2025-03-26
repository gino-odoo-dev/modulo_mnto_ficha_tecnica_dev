from odoo import models, fields

class ProductCorrelativo(models.Model):
    _name = 'cl.product.correlativo'
    _description = 'Product Correlativo'

    codigo = fields.Char(string="Codigo", required=True, unique=True)
    name = fields.Char(string="Nombre", required=True)
