from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTalla(models.Model):
    _name = 'cl.product.tallas'
    _description = 'Product Tallas'

    codigo = fields.Char(string="Codigo", required=True)
    name = fields.Char(string="Nombre", required=True)

