from odoo import models, fields, api

class CopiaFichaTecnicaWizard(models.TransientModel):
    _name = 'copia.ficha.tecnica.wizard'
    _description = 'Copia Ficha Técnica Wizard'

    name = fields.Char(string="Name", readonly=True)
