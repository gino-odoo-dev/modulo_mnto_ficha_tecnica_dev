from itertools import product
import traceback
from odoo import models, fields, api, exceptions, _ # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class FichaTecnica(models.Model):
    _name = 'receta.fichatecnica'
    _description = 'Ficha Tecnica'
    _rec_name = "nombre_ficha"
    _order = "id asc"

    temporada_destino_id = fields.Many2one('cl.product.temporada', required=True, default=lambda self: self.env.context.get('default_temporada_origen_id'))
    componentes_ids = fields.Many2many('product.template', 'ficha_tecnica_product_template_rel', 'ficha_id', 'product_id', string='Componentes')
    state = fields.Selection([('draft', 'Draft'), ('progress', 'Progress'), ('done', 'Done')], string='State', default='progress') 
    nombre_ficha = fields.Char(string='Nombre de Ficha Tecnica', compute='_compute_nombre_ficha', store=True, readonly=True)
    numero_seleccionado = fields.Char( string='Numeros Seleccionados', compute='_compute_numeros_badge', store=True)
    temporadas_id_display = fields.Char(string="Temporada", compute="_compute_temporadas_id_display", store=True)
    componentes_importados = fields.Boolean(string="componentes Importados", default=False, readonly=True)
    articulo_destino_id = fields.Many2one('product.template', string="Ficha Tecnica Destino", readonly=False)
    orden_compra1_id = fields.Many2one('purchase.order', string="Orden de Compra", compute="_compute_oc_id")
    articulo_origen_id = fields.Many2one('product.template', string="Modelo Origen", store=True)
    temporadas_id = fields.Many2one('cl.product.temporada', string='Temporada', required=True)
    articulos_id = fields.Many2one('product.template', string='Articulo', required=True)
    numeros_seleccionados = fields.Many2one('cl.product.tallas', string='Numeros Talla') 
    subcategoria_id = fields.Many2one('cl.product.subcategoria', string="SubCategoria")
    correlativo_id = fields.Many2one('cl.product.correlativo', string="Correlativo")
    temporada_sku_id = fields.Many2one('cl.product.temporada', string="temporada")
    temporada_origen_id = fields.Many2one('cl.product.temporada', required=True)
    material_id = fields.Many2one('cl.product.material', string="Material")
    categoria_id = fields.Many2one('product.category', string="Categoria")
    genero_id = fields.Many2one('cl.product.genero', string="Genero")
    marca_id = fields.Many2one('cl.product.marca', string="Marca")
    color_id = fields.Many2one('cl.product.color', string="Color")
    name = fields.Char(string="Nombre", required=False)

    for i in range(1, 6):
        locals()[f'componente{i}_id'] = fields.Integer(string=f"Componente {i} - ID", compute='_compute_id_componente', store=True)

    @api.constrains('componentes_ids')
    def _check_components(self):
        for record in self:
            if not record.articulos_id and record.componentes_ids:
                raise ValidationError("No puede agregar componentes sin seleccionar un artículo primero")

    @api.depends('temporadas_id')
    def _compute_temporadas_id_display(self):
        for record in self:
            record.temporadas_id_display = record.temporadas_id.name if record.temporadas_id else ''

    @api.depends('componentes_ids')  
    def _compute_id_componente(self):
        for record in self:
            for i in range(1, 6):
                record[f'componente{i}_id'] = 0
            for i, comp in enumerate(record.componentes_ids[:5], 1):
                if comp:
                    record[f'componente{i}_id'] = comp.id

    def action_importar_componentes(self):
        for record in self:
            if record.componentes_importados:
                continue                  
            if not record.articulos_id:
                raise ValidationError("Debe seleccionar un artículo primero")
                
            try:
                record.componentes_ids = [(5, 0, 0)]  
                bom_lines = self.env['mrp.bom.line'].search([
                    ('bom_id.product_tmpl_id', '=', record.articulos_id.id)
                ])
                if not bom_lines:
                    raise ValidationError("No se encontraron componentes para este artículo")
                
                components = bom_lines.mapped('product_id.product_tmpl_id')
                record.componentes_ids = [(6, 0, components.ids)]
                
                record.componentes_importados = True
                _logger.info(f"Importados {len(components)} componentes para ficha {record.id}")
                
            except Exception as e:
                _logger.error(f"Error importando componentes: {str(e)}\n{traceback.format_exc()}")
                raise ValidationError(f"Error al importar componentes: {str(e)}")
        return True

    @api.model
    def obtener_componentes_por_codigo_producto(self, articulos_id):
        try:
            plantilla_producto = self.env['product.template'].browse(articulos_id)
            if not plantilla_producto.exists():
                _logger.warning(f"No se encontro producto con ID {articulos_id}")
                return []   
            listas_materiales = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', plantilla_producto.id),
                ('active', '=', True)
            ])
            if not listas_materiales:
                _logger.warning(f"No se encontraron listas de materiales activas para el producto {articulos_id}")
                return []   
                
            lineas_ldm = self.env['mrp.bom.line'].search([
                ('bom_id', 'in', listas_materiales.ids)
            ], order="sequence asc") 
            
            resultado = []
            for linea in lineas_ldm:
                componente_data = {
                    'id': linea.id,
                    'codigo_componente': linea.product_id.default_code or '',
                    'company_id': linea.company_id.id if linea.company_id else False,
                    'product_uom_id': linea.product_uom_id.id if linea.product_uom_id else False,
                    'sequence': linea.sequence,
                    'product_qty': linea.product_qty,
                    'id_producto': linea.product_id.id,
                    'nombre_producto': linea.product_id.name,
                }
                resultado.append(componente_data)
                
            return resultado
            
        except Exception as e:
            _logger.error(f"Error obteniendo componentes: {str(e)}\n{traceback.format_exc()}")
            raise ValidationError(f"Error al obtener componentes: {str(e)}")
  
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
            
    @api.model
    def create(self, vals):
        if not vals.get('temporadas_id'):
            raise ValidationError("Debe seleccionar una temporada")
        if not vals.get('articulos_id'):
            raise ValidationError("Debe seleccionar un artículo")
        existing = self.search([
            ('temporadas_id', '=', vals['temporadas_id']),
            ('articulos_id', '=', vals['articulos_id']),
            ('state', '=', 'done')  
        ], limit=1)
        
        if existing:
            raise ValidationError("Ya existe una ficha FINALIZADA para este articulo y temporada. "
                                "Puede crear una nueva versión en estado borrador.")
        
        try:
            ficha = super().create(vals)
            ficha._descomponer_sku()
            
            if ficha.articulos_id.default_code and not ficha.componentes_ids:
                ficha.action_importar_componentes()    
            return ficha
            
        except Exception as e:
            _logger.error(f"Error creando ficha: {str(e)}\n{traceback.format_exc()}")
            raise ValidationError(f"Error al crear ficha: {str(e)}")

    def write(self, vals):
        if 'temporadas_id' in vals and any(rec.componentes_ids for rec in self):
            raise ValidationError("No puede cambiar de temporada con componentes existentes")
        if 'articulos_id' in vals:
            if any(rec.componentes_ids for rec in self):
                raise ValidationError("No puede cambiar de artículo con componentes existentes")            
            existing = self.search([
                ('id', '!=', self.id),
                ('temporadas_id', '=', vals.get('temporadas_id', self.temporadas_id.id)),
                ('articulos_id', '=', vals['articulos_id']),
                ('state', '=', 'done')  
            ], limit=1)
            if existing:
                raise ValidationError("Ya existe una ficha FINALIZADA para este artículo y temporada")
        try:
            res = super().write(vals)
            
            if 'articulos_id' in vals:
                self._descomponer_sku()
                if self.articulos_id.default_code and not self.componentes_ids:
                    self.action_importar_componentes()
            return res
            
        except Exception as e:
            _logger.error(f"Error actualizando ficha: {str(e)}\n{traceback.format_exc()}")
            raise ValidationError(f"Error al actualizar ficha: {str(e)}")

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
            components = self.env['mrp.bom.line'].search([
                ('bom_id.product_tmpl_id', '=', record.articulos_id.id)
            ]).mapped('product_id.product_tmpl_id')
            
            record.componentes_ids = [(6, 0, components.ids)]

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
            