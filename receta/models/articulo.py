from odoo import models, fields, api

class Articulo(models.Model):
    _name = 'cl.product.articulo'
    _description = 'Artículo'

    name = fields.Char(string="Nombre", required=False)
    description = fields.Text(string="Descripción")
    temporada_id = fields.Many2one('cl.product.temporada', string="Temporada")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    codigo = fields.Char(string="Codigo SKU", required=False, help="Codigo SKU del articulo.")