import traceback
from odoo import models, fields, api, exceptions, _ # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
import logging

_logger = logging.getLogger(__name__)

class FichaTecnica(models.Model):
    _name = 'receta.fichatecnica'
    _description = 'Ficha Tecnica'
    _rec_name = "nombre_ficha"

    name = fields.Char(string="Nombre", required=False)
    temporadas_id = fields.Many2one('cl.product.temporada', string='Temporada', required=True) 
    articulos_id = fields.Many2one('product.template', string='Articulo', required=True)
    numeros_seleccionados = fields.Many2one('cl.product.tallas', string='Numeros Talla')
    numero_seleccionado = fields.Char( string='Numeros Seleccionados', compute='_compute_numeros_badge', store=True)
    state = fields.Selection([('draft', 'Draft'), ('progress', 'Progress'), ('done', 'Done')], string='State', default='progress') 
    componentes_ids = fields.One2many('cl.product.componente', 'ficha_tecnica_id', string='Componentes')  
    nombre_ficha = fields.Char(string='Nombre de Ficha Tecnica', compute='_compute_nombre_ficha', store=True, readonly=True)
    articulo_origen_id = fields.Many2one('product.template', string="Modelo Origen", store=True)
    articulo_destino_id = fields.Many2one('product.template', string="Ficha Tecnica Destino", readonly=False)
    temporada_origen_id = fields.Many2one('cl.product.temporada', required=True)
    temporada_destino_id = fields.Many2one('cl.product.temporada', required=True, default=lambda self: self.env.context.get('default_temporada_origen_id'))
    temporadas_id_display = fields.Char(string="Temporada", compute="_compute_temporadas_id_display", store=True)
    marca_id = fields.Many2one('cl.product.marca', string="Marca")
    genero_id = fields.Many2one('cl.product.genero', string="Genero")
    correlativo_id = fields.Many2one('cl.product.correlativo', string="Correlativo")
    categoria_id = fields.Many2one('product.category', string="Categoria")
    subcategoria_id = fields.Many2one('cl.product.subcategoria', string="SubCategoria")
    temporada_sku_id = fields.Many2one('cl.product.temporada', string="temporada")
    material_id = fields.Many2one('cl.product.material', string="Material")
    color_id = fields.Many2one('cl.product.color', string="Color")
  
    @api.depends('componentes_ids')
    def _compute_numeros_badge(self):
        for record in self:
            record.numero_seleccionado = ', '.join(record.componentes_ids.mapped('numeros_seleccionados.name'))

    @api.depends('componentes_ids')
    def _compute_componentes_ids_display(self):
        for record in self:
            record.componentes_ids_display = ', '.join(record.componentes_ids.mapped('name'))

    @api.depends('articulos_id', 'temporadas_id', 'articulos_id.cl_long_model', 'articulos_id.cl_short_model')
    def _compute_nombre_ficha(self):
        for record in self:
            nombre = "Sin Nombre"
            if record.articulos_id:
                model_name = (
                    record.articulos_id.cl_long_model 
                    or record.articulos_id.cl_short_model 
                    or record.articulos_id.name
                )
                nombre = model_name or "Modelo sin nombre"
                
                if record.temporadas_id and record.temporadas_id.name:
                    nombre += f" - {record.temporadas_id.name}"
                    
            record.nombre_ficha = nombre
    
    @api.depends('temporadas_id')
    def _compute_temporadas_id_display(self):
        for record in self:
            record.temporadas_id_display = record.temporadas_id.name if record.temporadas_id else ''

    @api.onchange('articulos_id')
    def _onchange_articulos_id(self):
        for record in self:
            if record.articulos_id and not record.temporadas_id:
                return {
                    'warning': {
                        'title': "Temporada requerida",
                        'message': "Debe seleccionar una temporada antes de actualizar componentes",
                    }
                }       
            if record.articulos_id:
                record.with_context(skip_write=True).link_components()
                return {
                    'domain': {'componentes_ids': [('articulo_id', '=', record.articulos_id.id)]}
                }
            
    def create(self, vals):
        if not vals.get('temporadas_id'):
            raise ValidationError("Debe seleccionar una temporada")
        if not vals.get('articulos_id'):
            raise ValidationError("Debe seleccionar un articulo")
            
        if self.search([
            ('temporadas_id', '=', vals['temporadas_id']),
            ('articulos_id', '=', vals['articulos_id'])
        ]):
            _logger.warning("Duplicado de ficha tecnica")
            
        ficha = super().create(vals)
        ficha._descomponer_sku()
        ficha.link_components()
        return ficha

    def write(self, vals):
        if 'temporadas_id' in vals and any(rec.componentes_ids for rec in self):
            raise ValidationError("No puede cambiar de temporada con componentes existentes")
            
        if 'articulos_id' in vals:
            if any(rec.componentes_ids for rec in self):
                raise ValidationError("No puede cambiar de articulo con componentes existentes")
            if self.search([
                ('id', 'not in', self.ids),
                ('temporadas_id', '=', vals.get('temporadas_id', self.temporadas_id.id)),
                ('articulos_id', '=', vals['articulos_id'])
            ]):
                raise ValidationError("Ya existe una ficha para este articulo y temporada")
        
        res = super().write(vals)
        
        if 'articulos_id' in vals:
            self._descomponer_sku()
            self.link_components()
            
        return res

    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise exceptions.UserError("No se puede eliminar una ficha tecnica en estado Done")
            record.write({'active': False})
        return True
    
    def link_components(self):
        for record in self:
            if not record.articulos_id:
                continue
                
            componentes = self.env['cl.product.componente'].search(
                [('articulo_id', '=', record.articulos_id.id)]
            )
            record.componentes_ids = [(6, 0, componentes.ids)]
            if not record.articulos_id.default_code:
                record.articulos_id.default_code = f"SKU-{record.id:06d}"

    def _descomponer_sku(self):
        for record in self:
            if not record.articulos_id:
                continue    
            sku = (record.articulos_id.cl_long_model or '').strip()
            _logger.info(f"Procesando SKU: {sku} (Longitud: {len(sku)})")
            try:
                estructura = [
                    ('marca_id', 'cl.product.marca', 0, 2),
                    ('genero_id', 'cl.product.genero', 2, 1),
                    ('correlativo_id', 'cl.product.correlativo', 3, 4),
                    ('categoria_id', 'product.category', 7, 1),
                    ('subcategoria_id', 'cl.product.subcategoria', 8, 2),
                    ('temporada_sku_id', 'cl.product.temporada', 10, 1),
                    ('material_id', 'cl.product.material', 11, 2),
                    ('color_id', 'cl.product.color', 13, 2)
                ]
                updates = {}
                for field_name, model_name, start, length in estructura:
                    try:
                        code = sku[start:start+length].strip()
                        
                        if not code:
                            if field_name != 'correlativo_id':  
                                raise ValidationError(
                                    f"Posicion {start}-{start+length-1}: Codigo vacio en SKU"
                                )
                            continue
                        
                        Model = self.env[model_name]
                        
                        if 'code' in Model._fields:
                            domain = [('code', '=', code)]
                        else:
                            domain = [('name', '=ilike', code)]
                            _logger.warning(f"Modelo {model_name} no tiene campo 'code', buscando por 'name'")
                        
                        match = Model.search(domain, limit=1)
                        if not match:
                            if field_name == 'correlativo_id':
                                _logger.warning(f"No se encontro correlativo con codigo '{code}'. Continuando...")
                                continue
                            field = 'code' if 'code' in Model._fields else 'name'
                            existing = Model.search_read(
                                [(field, '!=', False)], 
                                [field], 
                                limit=10
                            )
                            suggestions = ", ".join([str(x[field]) for x in existing if x.get(field)])
                            
                            model_pretty = model_name.split('.')[-1].replace('_', ' ').title()
                            raise ValidationError(
                                f"No se encontro {model_pretty} con codigo '{code}'. "
                                f"Algunos valores validos: {suggestions}"
                            )  
                        updates[field_name] = match.id
                    except IndexError:
                        if field_name != 'correlativo_id': 
                            raise ValidationError(
                                f"El SKU requiere {start+length} caracteres (tiene {len(sku)}). "
                                f"Posicion {start}-{start+length-1} no existe en: '{sku}'"
                            )
                        continue
                if updates:
                    record.write(updates)
                    _logger.info(f"SKU descompuesto exitosamente. Campos actualizados: {updates.keys()}")
            except ValidationError as ve:
                _logger.warning(f"Error con SKU {sku}: {str(ve)}")
                raise ve
            except Exception as e:
                _logger.error(
                    f"Error {sku}. Error: {str(e)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                raise ValidationError(
                    "Error en sistema al procesar SKU."
                ) from e

    def button_duplicar(self):
        self.ensure_one()
        
        try:
            copia_vals = {
                'ficha_tecnica_id': self.id,
                'temporada_origen_id': self.temporadas_id.id,
                'temporada_destino_id': self.temporadas_id.id,  
                'articulo_origen_id': self.articulos_id.id,
                'articulo_destino_id': self.articulo_destino_id.id if self.articulo_destino_id else False,
                'mensaje': f"Copia de {self.articulos_id.display_name or 'Ficha tecnica'}"
            }
            copia = self.env['copia.receta.fichatecnica'].create(copia_vals)
            
            for i, comp in enumerate(self.componentes_ids[:20], 1):
                componente_vals = {
                    f'componente{i}_name': comp.name,
                    f'componente{i}_descripcion': comp.descripcion,
                    f'componente{i}_umedida': comp.umedida,
                    f'componente{i}_cantidad_id': comp.cantidad_id,
                }
                
                if comp.compra_manufactura_id:
                    componente_vals[f'componente{i}_compra_manufactura_id'] = comp.compra_manufactura_id.id
                    
                if comp.articulo_id:
                    componente_vals[f'componente{i}_articulo_id'] = comp.articulo_id.id
                    
                if comp.departamento_id and hasattr(copia, f'componente{i}_departamento_id'):
                    dept = self.env['hr.department'].search(
                        [('name', '=', comp.departamento_id.name)], 
                        limit=1
                    )
                    if dept:
                        componente_vals[f'componente{i}_departamento_id'] = dept.id
                
                copia.write(componente_vals)
            
            return {
                'name': 'Copia Realizada',
                'type': 'ir.actions.act_window',
                'res_model': 'copia.receta.fichatecnica',
                'view_mode': 'form',
                'target': 'new',
                'res_id': copia.id,
                'views': [(False, 'form')],
                'context': {
                    'dialog_size': 'medium', 
                    'create': False,
                    'edit': False
                },
                'flags': {
                    'form': {'action_buttons': True, 'options': {'mode': 'readonly'}},
                    'action_buttons': True
                }
            }
        except Exception as e:
            _logger.error(f"Error duplicando ficha: {e}\n{traceback.format_exc()}")
            raise ValidationError(_("Error al duplicar: %s") % str(e))
            
  
