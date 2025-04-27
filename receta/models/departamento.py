from odoo import models, fields

class Departamento(models.Model):
    _inherit = 'mrp.workcenter'
    _description = 'Departamento'

    name = fields.Char(string="Nombre", required=True)
  
