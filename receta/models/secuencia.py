from odoo import models, fields

class Secuencia(models.Model):
    _name = 'cl.product.secuencia'
    _description = 'Secuencia'

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)