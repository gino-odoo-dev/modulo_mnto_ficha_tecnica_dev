from odoo import models, fields

class ClProductTemporada(models.Model):
    _name = 'cl.product.temporada'
    _description = 'Temporada'

    name = fields.Char(string="Nombre", required=False)
    description = fields.Text(string="Descripción")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    code = fields.Char(string='codigo Temporada')
    active = fields.Boolean(string='Activo', default=True)  
