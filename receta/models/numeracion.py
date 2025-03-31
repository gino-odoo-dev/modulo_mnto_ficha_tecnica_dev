from odoo import models, fields

class Numeracion(models.Model):
    _name = 'cl.product.numeraciones'
    _description = 'Numeraciones de Calzados'

    name = fields.Char(string="Nombre", required=False)
    numero_inicio = fields.Char(string="Numero Inicio", required=False)
    numero_fin = fields.Char(string="Numero Fin", required=False)
