from odoo import models, fields

class CopiaFichaTecnicaWizard(models.TransientModel):
    _name = 'copia.receta.fichatecnica'
    _description = 'Resultados de Copia de Ficha Tecnica'

    mensaje = fields.Text(string="Resultado", readonly=True)
    ficha_tecnica_id = fields.Many2one('receta.fichatecnica', string="Ficha Tecnica Origen")
    detalles = fields.Text(string="Detalles de la operacion")
    exitoso = fields.Boolean(string="Operacion Exitosa")

    def close_wizard(self):
        return {'type': 'ir.actions.act_window_close'}