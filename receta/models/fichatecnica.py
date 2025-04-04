from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class FichaTecnica(models.Model):
    _name = 'receta.fichatecnica'
    _description = 'Ficha Tecnica'
    _rec_name = "nombre_ficha"

    temporadas_id = fields.Many2one('cl.product.temporada', string='Temporada', store=True) 
    articulos_id = fields.Many2one('cl.product.articulo', string='Articulo', store=True)  
    numero = fields.Many2one('cl.product.numeraciones', string='Numero Talla', required=False)
    numeros_seleccionados = fields.Many2many('cl.product.numeraciones', string='Numeros Talla Seleccionados')
    numero_seleccionado = fields.Char( string='Numeros Seleccionados', compute='_compute_numeros_badge', store=True)
    state = fields.Selection([('draft', 'Draft'), ('progress', 'Progress'), ('done', 'Done')], string='State', default='progress') 
    componentes_ids = fields.One2many('cl.product.componente', 'ficha_tecnica_id', string='Componentes')  
    nombre_ficha = fields.Char(string='Nombre de Ficha Tecnica', compute='_compute_nombre_ficha', store=True, readonly=True, default="Sin Nombre")
    
    @api.depends('numeros_seleccionados')
    def _compute_numeros_badge(self):
        for record in self:
            record.numero_seleccionado = ', '.join(
                str(num.numero) for num in record.numeros_seleccionados
            ) if record.numeros_seleccionados else 'Ninguno seleccionado'

    @api.depends('articulos_id')
    def _compute_nombre_ficha(self):
        for record in self:
            record.nombre_ficha = record.articulos_id.name if record.articulos_id else 'Sin Nombre'

    @api.onchange('temporadas_id')
    def _onchange_temporadas_id(self):
        for record in self:
            record.copia_temporadas = record.temporadas_id

    @api.onchange('articulos_id')
    def _onchange_articulos_id(self):
        for record in self:
            if record.articulos_id and not record.temporadas_id:
                return {
                    'warning': {
                        'title': "Temporada requerida",
                        'message': "Debe seleccionar una temporada antes de actualizar los componentes",
                    }
                }       
            if record.articulos_id:
                record.with_context(skip_write=True).link_components()
                return {
                    'domain': {'componentes_ids': [('articulo_id', '=', record.articulos_id.id)]}
                }
            
    @api.model
    def create(self, vals):
        if 'temporadas_id' not in vals or not vals['temporadas_id']:
            raise ValidationError("Debe seleccionar una temporada antes de crear una ficha tecnica.")
        if 'articulos_id' not in vals or not vals['articulos_id']:
            raise ValidationError("Debe seleccionar un articulo antes de crear una ficha tecnica.")
        existing = self.env['receta.fichatecnica'].search([
            ('temporadas_id', '=', vals['temporadas_id']),
            ('articulos_id', '=', vals['articulos_id'])
        ])
        if existing:
            _logger.warning(f"creando una nueva ficha tecnica para el articulo {vals['articulos_id']} y temporada {vals['temporadas_id']}, aunque ya existe otra ficha tecnica.")

        ficha_tecnica = super(FichaTecnica, self).create(vals)
        ficha_tecnica.with_context(skip_link_components=True).link_components()
        return ficha_tecnica

    def write(self, vals):
        if 'temporadas_id' in vals:
            for record in self:
                if record.componentes_ids:
                    raise ValidationError("No puede cambiar la temporada si ya hay componentes asociados.")
        if 'articulos_id' in vals:
            for record in self:
                if record.componentes_ids:
                    raise ValidationError("No puede cambiar el artículo si ya hay componentes asociados.")
        if 'temporadas_id' in vals or 'articulos_id' in vals:
            temporadas_id = vals.get('temporadas_id', self.temporadas_id.id)
            articulos_id = vals.get('articulos_id', self.articulos_id.id)
            existing = self.env['receta.fichatecnica'].search([
                ('id', '!=', self.id),
                ('temporadas_id', '=', temporadas_id),
                ('articulos_id', '=', articulos_id)
            ])
            if existing:
                raise ValidationError("Ya existe una ficha tecnica para este artículo y temporada.")

        result = super(FichaTecnica, self).write(vals)
        if not self.env.context.get('skip_link_components'):
            self.with_context(skip_link_components=True).link_components()
        return result

    def unlink(self):
        """
        funcion que valida que no se pueda eliminar una ficha tecnica en estado Done.
        """
        for record in self:
            if record.state == 'done':
                raise exceptions.UserError("No se puede eliminar una Ficha Técnica en estado Done.")
        return super(FichaTecnica, self).unlink()
    
    def link_components(self):
        for record in self:
            if not record.articulos_id:
                continue  
            components = self.env['cl.product.componente'].search([
                ('articulo_id', '=', record.articulos_id.id)
            ])
            record.componentes_ids = [(6, 0, components.ids)]
            if not self.env.context.get('skip_write') and not record.articulos_id.codigo:
                record.articulos_id.codigo = f"SKU-{record.id:06d}"
