from odoo import models, fields

class Numeracion(models.Model):
    _name = 'cl.product.numeraciones'
    _description = 'Numeraciones de Calzados'
    _rec_name = 'numero' 
    
    name = fields.Char(string="Nombre", required=False)
    numero = fields.Integer(string="Numero Inicio", required=False)
   





