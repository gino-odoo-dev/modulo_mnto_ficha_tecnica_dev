from odoo import models, fields, api

class Componente(models.Model):
    _name = 'cl.product.componente'
    _description = 'Componente'
    _order = 'id'

    name = fields.Char(string="Nombre", required=False)
    descripcion = fields.Char(string="Descripcion")  
    umedida = fields.Char(string="Unidad de Medida") 
    componente_id = fields.Many2one('cl.product.componente', string='Componente Relacionado')  

    ficha_tecnica_id = fields.Many2one('receta.fichatecnica', string='Ficha Técnica')
    codigosecuencia_id = fields.Many2one('cl.secuencia', string='Código de Secuencia')  
    compra_manufactura_id = fields.Many2one('cl.product.origen', string='Compra/Manufactura')
    compra_manufactura_name = fields.Char(string='Nombre de Compra/Manufactura', related='compra_manufactura_id.name', store=True)
    cantidad_id = fields.Integer(string='Cantidad')
    factor_perdida_id = fields.Float(string='Factor de Pérdida (%)')
    costo_unitario_id = fields.Float(string='Costo Unitario')
    costo_ampliado_id = fields.Float(string='Costo Ampliado', compute='_compute_costo_ampliado', store=True) 
    departamento_id = fields.Many2one('cl.departamento', string='Departamento')
    departamento_name = fields.Char(string='Nombre del Departamento', related='departamento_id.name', store=True)

    @api.depends('cantidad_id', 'costo_unitario_id', 'factor_perdida_id')
    def _compute_costo_ampliado(self):
        for record in self:
            record.costo_ampliado_id = record.cantidad_id * record.costo_unitario_id * (1 + record.factor_perdida_id / 100)

    @api.onchange('componente_id')
    def _onchange_componentes_ids(self):
        if self.componente_id:
            self.name = self.componente_id.name or '' 
            self.descripcion = self.componente_id.descripcion or ''
            self.umedida = self.componente_id.umedida or ''
        else:
            self.name = ''  
            self.descripcion = ''
            self.umedida = ''

    @api.model
    def create(self, vals):
        if 'componente_id' in vals:
            componente = self.env['cl.product.componente'].browse(vals['componente_id'])
            vals['name'] = vals.get('name', componente.name or '')
            vals['descripcion'] = vals.get('descripcion', componente.descripcion or '')
            vals['umedida'] = vals.get('umedida', componente.umedida or '')
        else:
            vals['name'] = vals.get('name', '')
            vals['descripcion'] = vals.get('descripcion', '')
            vals['umedida'] = vals.get('umedida', '')
        return super(Componente, self).create(vals)

