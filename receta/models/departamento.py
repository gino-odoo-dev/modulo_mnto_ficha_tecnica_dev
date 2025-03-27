from odoo import models, fields

class Departamento(models.Model):
    _name = 'cl.departamento'
    _description = 'Departamento'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripción")
    codigo = fields.Char(string="Código", required=True) 

