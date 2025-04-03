from odoo import models, fields, api

class Modelo(models.Model):
    _name = 'cl.product.modelo'
    _description = 'Articulo'
    _rec_name = "name"

    name = fields.Char(string="Nombre", required=False)
