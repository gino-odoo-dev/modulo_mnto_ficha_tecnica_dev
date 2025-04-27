from odoo import models, fields # type: ignore

class Articulo(models.Model):
    _inherit = 'product.template'
    _description = 'Articulo'
    _rec_name = "name"  

    name = fields.Char(string="Nombre", required=False)
    temporada_id = fields.Many2one('cl.product.temporada', string="Temporada")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)    
    cl_long_model = fields.Char(string="Nombre Largo", store=True)
    cl_short_model = fields.Char(string="Nombre Corto", store=True)
