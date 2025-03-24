from odoo import models, fields

class Temporada(models.Model):
    _name = 'cl.product.temporada'
    _description = 'Temporada'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripción")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)  # Added field