from odoo import models, fields

class ProductCorrelativo(models.Model):
    _name = 'cl.product.correlativo'
    _description = 'Product Correlativo'

    code = fields.Char(string="Codigo", required=True)
    name = fields.Char(string="Nombre", required=True)
