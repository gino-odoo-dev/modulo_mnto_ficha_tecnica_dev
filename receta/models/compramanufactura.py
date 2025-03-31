from odoo import models, fields

class CompraManufactura(models.Model):
    _name = 'cl.compramanufactura'
    _description = 'Compra/Manufactura'

    name = fields.Char(string="Nombre", required=False)
    description = fields.Text(string="Descripción")