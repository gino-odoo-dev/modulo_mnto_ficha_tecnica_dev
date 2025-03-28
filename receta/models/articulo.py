from odoo import models, fields, api

class Articulo(models.Model):
    _name = 'cl.product.articulo'
    _description = 'Artículo'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripción")
    temporada_id = fields.Many2one('cl.product.temporsada', string="Temporada")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    codigo = fields.Char(string="Código SKU", required=False, help="Código SKU del artículo.")