from odoo import models, fields # type: ignore

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pt_part_type = fields.Char(string="Tipo Parte (PT)")
    pt_pm_code = fields.Char(string="Código PM")
    modelo_corto_id = fields.Many2one('cl.product.modelo', string="Modelo Corto")
