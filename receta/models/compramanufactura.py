from odoo import models, fields

class CompraManufactura(models.Model):
    _name = 'cl.product.compramanufactura' 
    _description = 'Compra/Manufactura'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripción")