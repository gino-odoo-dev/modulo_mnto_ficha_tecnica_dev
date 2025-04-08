import traceback
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
    articulo_origen_id = fields.Many2one('cl.product.componente', string="Modelo Origen", compute='_compute_articulo_origen', store=True)
    articulo_destino_id = fields.Many2one('cl.product.componente', string="Modelo Destino", readonly=False)
    
    temporadas_id_display = fields.Char(string="Temporada (sin ultimos 3 digitos)", compute="_compute_temporadas_id_display", store=True)
    articulos_id_display = fields.Char(string="Articulo Origen (sin ultimos 3 digitos)", compute="_compute_articulos_id_display", store=True)

    @api.depends('temporadas_id')
    def _compute_temporadas_id_display(self):
        for record in self:
            record.temporadas_id_display = record.temporadas_id.name if record.temporadas_id else ''

    @api.depends('articulos_id')
    def _compute_articulos_id_display(self):
        for record in self:
            articulo_name = record.articulos_id.name if record.articulos_id else ''
            record.articulos_id_display = articulo_name[:-3] if len(articulo_name) > 3 else articulo_name

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
        for record in self:
            if record.state == 'done':
                raise exceptions.UserError("No se puede eliminar una Ficha Técnica en estado Done.")
            record.write({'active': False})
        return True
    
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

    def button_duplicar(self):
        """
        Metodo principal llamado desde el frontend que coordina todo el proceso
        """
        self.ensure_one()
        
        try:
            wizard_vals = {
                'ficha_tecnica_id': self.id,
                'temporada_origen_id': self.temporadas_id.id,
                'articulo_origen_id': self.articulos_id.id,
            }
            for field in ['ficha_tecnica_id', 'temporada_origen_id', 'articulo_origen_id']:
                if not wizard_vals[field]:
                    raise ValueError(f"El campo {field} no puede estar vacío")
            
            wizard = self.env['copia.receta.fichatecnica'].create(wizard_vals)
            
            if not wizard.exists():
                raise ValueError("No se pudo crear el wizard de resultados")
            result = wizard.copia_rec_dev()

            if result and result.get('type') == 'ir.actions.act_window':
                return result                

            return wizard._mostrar_resultado(
                exitoso=True,
                mensaje="Exito durante el proceso de copia, Generando resultado"
            )
            
        except Exception as e:
            _logger.error("Error en button_duplicar: %s", traceback.format_exc())
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Exito, copia generada con exito',
                    'message': f'Generando resultado ... ',
                    'sticky': True,
                    'type': 'danger'
                }
            }
