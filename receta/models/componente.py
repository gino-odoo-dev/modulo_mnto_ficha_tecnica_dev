from odoo import models, fields, api # type: ignore

class Componente(models.Model):
    _name = 'cl.product.componente'
    _description = 'Componente'
    _order = 'id'

    name = fields.Char(string="Nombre", required=False)
    descripcion = fields.Char(string="Descripcion")  
    umedida = fields.Char(string="Unidad de Medida")
    componente_id = fields.Many2one('cl.product.componente', string='Componente Relacionado')  
    ficha_tecnica_id = fields.Many2one('receta.fichatecnica', string='Ficha Técnica')
    compra_manufactura_id = fields.Many2one( 'cl.product.origen', string='Compra/Manufactura', ondelete='set null')
    cantidad_id = fields.Integer(string='Cantidad')
    factor_perdida_id = fields.Float(string='Factor de Perdida (%)')
    costo_unitario_id = fields.Float(string='Costo Unitario')
    costo_ampliado_id = fields.Float(string='Costo Ampliado', compute='_compute_costo_ampliado', store=True) 
    departamento_id = fields.Many2one('mrp.workcenter', string='Departamento', store=True)
    articulo_id = fields.Many2one('product.template', string='Artículo', required=False, ondelete='cascade')
    componentes_id = fields.Many2one('product.template', string='Componente', required=False, ondelete='cascade')
    numeros_seleccionados = fields.Many2one('cl.product.tallas', string='Numeros Talla')
    numero_seleccionado = fields.Char( string='Numeros Seleccionados', compute='_compute_numeros_badge', store=True)
    origen_copia_id = fields.Many2one('cl.product.componente', string="Componente Origen", readonly=True)
    subcategoria_id = fields.Many2one('cl.product.subcategoria', string="Subcategoría")

    @api.depends('numeros_seleccionados')
    def _compute_numeros_badge(self):
        for record in self:
            record.numero_seleccionado = record.numeros_seleccionados.name if record.numeros_seleccionados else ''

    @api.depends('cantidad_id', 'costo_unitario_id', 'factor_perdida_id')
    def _compute_costo_ampliado(self):
        for record in self:
            record.costo_ampliado_id = record.cantidad_id * record.costo_unitario_id * (1 + record.factor_perdida_id / 100)

    @api.onchange('componentes_id')
    def _onchange_componentes_ids(self):
        if self.componentes_id:
            self.descripcion = self.componentes_id.description or ''
            self.umedida = self.componentes_id.uom_id.name if self.componentes_id.uom_id else ''
            self.name = self.componentes_id.name or ''
        else:
            self.descripcion = ''
            self.umedida = ''
            self.name = ''

    @api.model
    def create(self, vals):
        if 'ficha_tecnica_id' in vals and 'articulo_id' not in vals:
            ficha = self.env['receta.fichatecnica'].browse(vals['ficha_tecnica_id'])
            if ficha.articulos_id:
                vals['articulo_id'] = ficha.articulos_id.id
        return super(Componente, self).create(vals)
    
