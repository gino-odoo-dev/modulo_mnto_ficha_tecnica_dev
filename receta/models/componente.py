from odoo import models, fields, api # type: ignore

class Componente(models.Model):
    _inherit = 'product.template'
    _description = 'Componente'
    _order = 'id'
    _rec_name = 'default_code'

    numero_seleccionado = fields.Char( string='Numeros Seleccionados', compute='_compute_numeros_badge', store=True)
    compra_manufactura_id = fields.Many2one( 'cl.product.origen', string='Compra/Manufactura', ondelete='set null')
    componentes_id = fields.Many2one('product.template', string='Componente', required=False, ondelete='cascade')
    costo_ampliado_id = fields.Float(string='Costo Ampliado', compute='_compute_costo_ampliado', store=True)
    articulo_id = fields.Many2one('product.template', string='Articulo', required=False, ondelete='cascade')
    origen_copia_id = fields.Many2one('product.template', string="Componente Origen", readonly=True)
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    componente_id = fields.Many2one('product.template', string='Componente Relacionado')
    departamento_id = fields.Many2one('mrp.workcenter', string='Departamento', store=True)
    numeros_seleccionados = fields.Many2one('cl.product.tallas', string='Numeros Talla')
    subcategoria_id = fields.Many2one('cl.product.subcategoria', string="Subcategoría")
    factor_perdida_id = fields.Float(string='Factor de Perdida (%)')
    codigo_componente = fields.Char(string="Codigo Componente")
    default_code = fields.Char(string="Codigo", required=False)
    product_uom_id = fields.Many2one('uom.uom', string="UdM")
    costo_unitario_id = fields.Float(string='Costo Unitario')
    name = fields.Char(string="Nombre", required=False)
    umedida = fields.Char(string="Unidad de Medida")
    descripcion = fields.Char(string="Descripcion")
    cantidad_id = fields.Integer(string='Cantidad')
    product_qty = fields.Float(string="Cantidad")
    sequence = fields.Integer(string="Secuencia")
    cantidad = fields.Float(string="Cantidad")

    @api.depends('default_code')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.default_code or ''

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
