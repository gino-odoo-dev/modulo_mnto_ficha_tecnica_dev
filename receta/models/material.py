
from odoo import models, fields # type: ignore

class ProductMaterial(models.Model):
    _inherit = 'cl.product.material'

    code = fields.Char(string='Código', required=True, index=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    