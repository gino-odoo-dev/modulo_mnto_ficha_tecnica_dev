from odoo import models, fields

class CompraManufactura(models.Model):
    _inherit = 'cl.product.origen' 
    _description = 'Compra/Manufactura'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripcion")