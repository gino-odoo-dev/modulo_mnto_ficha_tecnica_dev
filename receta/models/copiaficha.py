import traceback
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class CopiaFichaTecnicaWizard(models.TransientModel):
    _name = 'copia.receta.fichatecnica'
    _description = 'Asistente para Copiar Ficha Técnica'
 
    mensaje = fields.Text(string="Resultado", readonly=True)
    ficha_tecnica_id = fields.Many2one('receta.fichatecnica', string="Ficha Tecnica Origen", required=True, default=lambda self: self._default_ficha_tecnica_id())
    temporada_destino_id = fields.Many2one('cl.product.temporada', string="Temporada Destino", required=True)
    detalles = fields.Text(string="Detalles de la operacion", readonly=True)
    exitoso = fields.Boolean(string="Operación Exitosa", readonly=True)
    temporada_origen_id = fields.Many2one('cl.product.temporada', string="Temporada Origen", readonly=True)
    temporada_destino_id = fields.Many2one('cl.product.temporada', string="Temporada Destino", required=True)

    articulo_origen_id = fields.Many2one('cl.product.componente', string="Modelo Origen", readonly=True)
    articulo_destino_id = fields.Many2one('cl.product.componente', string="Modelo Destino", readonly=True)
    numeros_seleccionados = fields.Many2many('cl.product.numeraciones', string='Numeros Talla')
    modelo_origen_id = fields.Many2one('cl.product.articulo', string="Artículo Origen", readonly=True)
    modelo_destino_id = fields.Many2one('cl.product.articulo', string="Artículo Destino", readonly=True)

    componentes_count = fields.Integer(string="Total Componentes", readonly=True)
    componente1_id = fields.Many2one('cl.product.componente', string="Componente 1", readonly=True)
    componente1_name = fields.Char(string="Componente 1 - Nombre", readonly=True)
    componente1_descripcion = fields.Char(string="Componente 1 - Descripcion", readonly=True)
    componente1_umedida = fields.Char(string="Componente 1 - Unidad Medida", readonly=True)
    componente1_codigosecuencia_id = fields.Many2one('cl.product.secuencia', string="Componente 1 - Codigo Secuencia", readonly=True)
    componente1_compra_manufactura_id = fields.Many2one('cl.product.origen', string="Componente 1 - Compra/Manufactura", readonly=True)
    componente1_compra_manufactura_name = fields.Char(string="Componente 1 - Nombre Compra/Manufactura", readonly=True)
    componente1_cantidad_id = fields.Integer(string="Componente 1 - Cantidad", readonly=True)
    componente1_factor_perdida_id = fields.Float(string="Componente 1 - Factor Perdida (%)", readonly=True)
    componente1_costo_unitario_id = fields.Float(string="Componente 1 - Costo Unitario", readonly=True)
    componente1_costo_ampliado_id = fields.Float(string="Componente 1 - Costo Ampliado", readonly=True)
    componente1_departamento_id = fields.Many2one('cl.departamento', string="Componente 1 - Departamento", readonly=True)
    componente1_departamento_name = fields.Char(string="Componente 1 - Nombre Departamento", readonly=True)
    componente1_articulo_id = fields.Many2one('cl.product.articulo', string="Componente 1 - Articulo", readonly=True)

    no_comb_o = fields.Integer(string="N° Combinaciones Origen")
    no_comb_d = fields.Integer(string="N° Combinaciones Destino")
    
    # Campos para descomposición SKU
    marca_id = fields.Many2one('cl.product.marca', string="Marca", readonly=True)
    genero_id = fields.Many2one('cl.product.genero', string="Género", readonly=True)
    correlativo_id = fields.Many2one('cl.product.correlativo', string="Correlativo", readonly=True)
    categoria_id = fields.Many2one('cl.product.categoria', string="Categoría", readonly=True)
    subcategoria_id = fields.Many2one('cl.product.subcategoria', string="Subcategoría", readonly=True)
    temporada_sku_id = fields.Many2one('cl.product.temporada', string="Temporada SKU", readonly=True)
    material_id = fields.Many2one('cl.product.material', string="Material", readonly=True)
    color_id = fields.Many2one('cl.product.color', string="Color", readonly=True)
    talla_id = fields.Many2one('cl.product.tallas', string="Talla", readonly=True)

    xcolfo = fields.Char(string="Color", size=3)
    sequence = fields.Integer(string="Secuencia", default=10)
    mensaje = fields.Char(string="Mensaje", readonly=True)
    xcuero = fields.Char(string="Cuero", size=3)
    m_numero_color = fields.Boolean(string="Modo Copia Numeraciones", default=False)
    
    for i in range(2, 21):
        locals().update({
            f'componente{i}_id': fields.Many2one('cl.product.componente', string=f"Componente {i}", readonly=True),
            f'componente{i}_name': fields.Char(string=f"Componente {i} - Nombre", readonly=True),
            f'componente{i}_descripcion': fields.Char(string=f"Componente {i} - Descripcion", readonly=True),
            f'componente{i}_umedida': fields.Char(string=f"Componente {i} - Unidad Medida", readonly=True),
            f'componente{i}_codigosecuencia_id': fields.Many2one('cl.product.secuencia', string=f"Componente {i} - Codigo Secuencia", readonly=True),
            f'componente{i}_compra_manufactura_id': fields.Many2one('cl.product.origen', string=f"Componente {i} - Compra/Manufactura", readonly=True),
            f'componente{i}_compra_manufactura_name': fields.Char(string=f"Componente {i} - Nombre Compra/Manufactura", readonly=True),
            f'componente{i}_cantidad_id': fields.Integer(string=f"Componente {i} - Cantidad", readonly=True),
            f'componente{i}_factor_perdida_id': fields.Float(string=f"Componente {i} - Factor Perdida (%)", readonly=True),
            f'componente{i}_costo_unitario_id': fields.Float(string=f"Componente {i} - Costo Unitario", readonly=True),
            f'componente{i}_costo_ampliado_id': fields.Float(string=f"Componente {i} - Costo Ampliado", readonly=True),
            f'componente{i}_departamento_id': fields.Many2one('cl.product.departamento', string=f"Componente {i} - Departamento", readonly=True),
            f'componente{i}_departamento_name': fields.Char(string=f"Componente {i} - Nombre Departamento", readonly=True),
            f'componente{i}_articulo_id': fields.Many2one('cl.product.articulo', string=f"Componente {i} - Articulo", readonly=True),
        })

    def _default_ficha_tecnica_id(self):
        return self.env.context.get('active_id')

    def cargar_datos_fichatecnica(self):
        """Funcion que carga los datos especificos (articulos_id y temporada_id) desde la ficha tecnica"""
        self.ensure_one()
        
        if not self.ficha_tecnica_id:
            raise ValidationError("No se ha seleccionado una ficha técnica origen")
        self.write({
            'temporada_origen_id': self.ficha_tecnica_id.temporada_id.id,
            'articulo_origen_id': self.ficha_tecnica_id.articulos_id.id,  
            'modelo_origen_id': self.ficha_tecnica_id.articulos_id.modelo_id.id
        })
        return True
    
    def cargar_datos_componentes(self):
        """Carga los datos de componentes desde la ficha tecnica al wizard"""
        self.ensure_one()
        result = {
            'exitoso': False,
            'mensaje': '',
            'detalles': '',
            'componentes_count': 0
        }
        
        try:
            if not self.ficha_tecnica_id:
                raise ValidationError("Debe seleccionar una ficha tecnica origen")
            vals = {
                'temporada_origen_id': self.ficha_tecnica_id.temporada_id.id,
                'articulo_origen_id': self.ficha_tecnica_id.articulos_id.id,
                'modelo_origen_id': self.ficha_tecnica_id.articulos_id.modelo_id.id,
            }
            componentes = self.ficha_tecnica_id.componente_ids.sorted(key=lambda r: r.id)
            vals['componentes_count'] = len(componentes)
            
            for i in range(1, min(21, len(componentes) + 1)): 
                comp = componentes[i-1]
                vals.update({
                    f'componente{i}_id': comp.id,
                    f'componente{i}_name': comp.name,
                    f'componente{i}_descripcion': comp.descripcion,
                    f'componente{i}_umedida': comp.umedida,
                    f'componente{i}_codigosecuencia_id': comp.codigosecuencia_id.id,
                    f'componente{i}_compra_manufactura_id': comp.compra_manufactura_id.id,
                    f'componente{i}_compra_manufactura_name': comp.compra_manufactura_id.name,
                    f'componente{i}_cantidad_id': comp.cantidad_id,
                    f'componente{i}_factor_perdida_id': comp.factor_perdida_id,
                    f'componente{i}_costo_unitario_id': comp.costo_unitario_id,
                    f'componente{i}_costo_ampliado_id': comp.costo_ampliado_id,
                    f'componente{i}_departamento_id': comp.departamento_id.id,
                    f'componente{i}_departamento_name': comp.departamento_id.name,
                    f'componente{i}_articulo_id': comp.articulo_id.id,
                })
            result.update({
                'exitoso': True,
                'mensaje': 'Componentes cargados correctamente',
                'detalles': f"Se cargaron {len(componentes)} componentes desde la ficha tecnica",
            })
            vals.update(result)
            
        except Exception as e:
            result.update({
                'mensaje': 'Error al cargar componentes',
                'detalles': str(e)
            })
            vals.update(result)
            raise ValidationError(f"Error al cargar componentes: {str(e)}")
        
        self.write(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _descomponer_sku(self):
        """
        descompone el SKU del articulo origen y guarda los datos en campos del wizard
        """
        self.ensure_one()
    
        if not self.articulo_origen_id:
            raise ValidationError("No hay artículo origen seleccionado")
        
        sku = self.articulo_origen_id.default_code or ''  
        
        if len(sku) != 18:
            raise ValidationError("El SKU debe tener exactamente 18 caracteres")

        mappings = [
            ('marca_id', 'cl.product.marca', sku[:2]),
            ('genero_id', 'cl.product.genero', sku[2]),
            ('correlativo_id', 'cl.product.correlativo', sku[3:7]),
            ('categoria_id', 'cl.product.categoria', sku[7]),
            ('subcategoria_id', 'cl.product.subcategoria', sku[8:10]),
            ('temporada_sku_id', 'cl.product.temporada', sku[10]),
            ('material_id', 'cl.product.material', sku[11:13]),
            ('color_id', 'cl.product.color', sku[13:15]),
            ('talla_id', 'cl.product.tallas', sku[15:18]),
        ]

        vals = {}
        for field_name, model_name, code in mappings:
            record = self.env[model_name].search([("codigo", '=', code)], limit=1)
            if not record:
                raise ValidationError(f"Codigo {code} no encontrado para {model_name}")
            vals[field_name] = record.id
        
        self.write(vals)
        return True
    
    def obtener_numero_combinaciones(self, codigo_articulo):
        """
        metodo para obtener el numero de combinaciones de un articulo.
        """
        articulo = self.env['cl_product_articulo'].search([('default_code', '=', codigo_articulo)], limit=1)
        
        if not articulo:
            raise ValidationError(f"El articulo {codigo_articulo} no existe.")
        
        if hasattr(articulo, 'x_numero_combinaciones'):
            return articulo.x_numero_combinaciones
        else:
            raise ValidationError(f"El articulo {codigo_articulo} no tiene un numero de combinaciones definido.")

    def copia_rec_dev(self):
        """
        Función principal que realiza la copia de fichas técnicas con todas las reglas de negocio del sistema original.
        """
        self.ensure_one()
        try:
            # =============================================
            # VALIDACIONES COMUNES PARA AMBOS MODOS DE COPIA
            # =============================================
            
            if not self.temporada_destino_id:
                raise ValidationError(_("Debe seleccionar una temporada destino válida"))
                
            if not self.articulo_origen_id:
                raise ValidationError(_("El artículo origen no puede estar vacío"))
                
            if not self.articulo_origen_id.pt_part_type or not self.articulo_origen_id.pt_part_type.startswith("PT-"):
                raise ValidationError(_("El artículo origen debe ser de tipo 'PT-' (Producto Terminado)"))
                
            if not self.articulo_origen_id.pt_pm_code or self.articulo_origen_id.pt_pm_code != 'M':
                raise ValidationError(_("El artículo origen debe estar marcado como manufacturado (M)"))
                
            if not self.env['receta.fichatecnica'].search([
                ('articulos_id', '=', self.articulo_origen_id.id), 
                ('temporada_id', '=', self.temporada_origen_id.id)
            ], limit=1):
                raise ValidationError(_("El artículo origen no tiene estructura para la temporada seleccionada"))
                
            prod_term = self.env['cl_product_terminado'].search([
                ('temporada_id', '=', self.temporada_origen_id.id),
                ('modelo_corto_id', '=', self.articulo_origen_id.modelo_corto_id.id),
                ('material_id', '=', self.articulo_origen_id.material_id.id),
                ('color_id', '=', self.articulo_origen_id.color_id.id)
            ], limit=1)
            
            if not prod_term or (prod_term.planta_id != self.articulo_origen_id.planta_id or 
                                prod_term.color_forro_id != self.articulo_origen_id.color_forro_id):
                raise ValidationError(_("No existe producto terminado para la temporada con estas características")) 
            self.no_comb_o = self.obtener_numero_combinaciones(self.articulo_origen_id.default_code)
            
            # =============================================
            # LÓGICA DE COPIA POR NUMERACIÓN/TALLA
            # =============================================
            if self.m_numero_color:
                if not self.numeros_seleccionados:
                    raise ValidationError(_("Debe seleccionar al menos una numeración/talla"))
                    
                for numeracion in self.numeros_seleccionados:
                    articulo_destino = self.env['cl_product_articulo'].search([
                        ('modelo_id', '=', self.articulo_origen_id.modelo_id.id),
                        ('numeracion_id', '=', numeracion.id),
                        ('pt_part_type', '=like', 'PT-%'),
                        ('pt_pm_code', '=', 'M')
                    ], limit=1)
                    
                    if not articulo_destino:
                        raise ValidationError(_("No se encontró artículo destino válido para la numeración %s") % numeracion.name)
                        
                    self.no_comb_d = self.obtener_numero_combinaciones(articulo_destino.default_code)
                    if self.no_comb_o != self.no_comb_d:
                        raise ValidationError(_("El número de combinaciones no coincide para la numeración %s") % numeracion.name)
                        
                    self._copia_numero(self.articulo_origen_id, articulo_destino, self.temporada_destino_id)
                    self._cambia_componente(articulo_destino, numeracion.numero)
                    
            # =============================================
            # LÓGICA DE COPIA POR COLOR/MODELO
            # =============================================
            else:
                if not self.articulo_destino_id:
                    raise ValidationError(_("Debe seleccionar un artículo destino"))
                    
                if self.articulo_origen_id == self.articulo_destino_id:
                    raise ValidationError(_("El artículo origen y destino no pueden ser iguales"))
                    
                if self.articulo_origen_id.modelo_id == self.articulo_destino_id.modelo_id:
                    raise ValidationError(_("El modelo de origen y destino deben ser diferentes"))
                    
                self.no_comb_d = self.obtener_numero_combinaciones(self.articulo_destino_id.default_code)
                if self.no_comb_o != self.no_comb_d:
                    raise ValidationError(_("El número de combinaciones no coincide entre origen y destino"))
                    
                if self.env['receta.fichatecnica'].search([
                    ('articulos_id', '=', self.articulo_destino_id.id),
                    ('temporada_id', '=', self.temporada_destino_id.id)
                ], limit=1):
                    raise ValidationError(_("El artículo destino ya tiene una ficha técnica para esta temporada"))
                    
                self._copia_color(
                    self.articulo_origen_id, 
                    self.articulo_origen_id.modelo_id,
                    self.articulo_destino_id, 
                    self.articulo_destino_id.modelo_id
                )
                
                self._cambia_materia(
                    self.articulo_origen_id,
                    self.articulo_origen_id.modelo_id,
                    self.articulo_destino_id,
                    self.articulo_destino_id.modelo_id
                )
                
                self._cambia_componente(
                    self.articulo_destino_id, 
                    self.articulo_destino_id.numeracion_id.numero
                )
            
            # =============================================
            # RESULTADO EXITOSO
            # =============================================
            destino = self.articulo_destino_id.default_code if not self.m_numero_color else 'múltiples numeraciones'
            mensaje = _("""
                Proceso de copia completado correctamente:
                - Origen: %s
                - Destino: %s
                - Temporada destino: %s
            """) % (self.articulo_origen_id.default_code, destino, self.temporada_destino_id.display_name)
            
            return self._mostrar_resultado(True, mensaje)
            
        except ValidationError as e:
            return self._mostrar_resultado(False, _("Error de validación: %s") % str(e))
        except Exception as e:
            _logger.error("Error inesperado en copia_rec_dev: %s", traceback.format_exc())
            return self._mostrar_resultado(False, _("Error inesperado: %s") % str(e))

    def _copia_numero(self, articulo_origen, articulo_destino, temporada_destino):
        """
        Copia las fórmulas a otros artículos del mismo modelo (diferente numeración)
        """
        self.env['receta.fichatecnica'].search([
            ('articulos_id', '=', articulo_destino.id),
            ('temporada_id', '=', temporada_destino.id)
        ]).unlink()

        ficha_origen = self.env['receta.fichatecnica'].search([
            ('articulos_id', '=', articulo_origen.id),
            ('temporada_id', '=', self.temporada_origen_id.id)
        ], limit=1)
        
        if not ficha_origen:
            raise ValidationError(_("No se encontró ficha técnica origen"))
        
        nueva_ficha = ficha_origen.copy({
            'articulos_id': articulo_destino.id,
            'temporada_id': temporada_destino.id,
            'origen_copia_id': ficha_origen.id
        })

        for comp_origen in ficha_origen.componente_ids:
            nuevo_comp = comp_origen.copy({
                'ficha_tecnica_id': nueva_ficha.id,
                'origen_copia_id': comp_origen.id
            })

    def _copia_color(self, articulo_origen, modelo_origen, articulo_destino, modelo_destino):
        """
        Copia las fórmulas a un artículo con diferente color/modelo
        """
        self.env['receta.fichatecnica'].search([
            ('articulos_id', '=', articulo_destino.id),
            ('temporada_id', '=', self.temporada_destino_id.id)
        ]).unlink()

        ficha_origen = self.env['receta.fichatecnica'].search([
            ('articulos_id', '=', articulo_origen.id),
            ('temporada_id', '=', self.temporada_origen_id.id)
        ], limit=1)
        
        if not ficha_origen:
            raise ValidationError(_("No se encontró ficha técnica origen"))
        
        nueva_ficha = ficha_origen.copy({
            'articulos_id': articulo_destino.id,
            'temporada_id': self.temporada_destino_id.id,
            'origen_copia_id': ficha_origen.id
        })

        for comp_origen in ficha_origen.componente_ids:
            if comp_origen.articulo_id == articulo_origen:
                continue  
                
            nuevo_comp = comp_origen.copy({
                'ficha_tecnica_id': nueva_ficha.id,
                'origen_copia_id': comp_origen.id
            })

    def _cambia_componente(self, articulo_destino, numero_talla):
        """
        Aplica reglas de negocio a los componentes copiados según la talla/numeración
        """
        ficha_destino = self.env['receta.fichatecnica'].search([
            ('articulos_id', '=', articulo_destino.id),
            ('temporada_id', '=', self.temporada_destino_id.id)
        ], limit=1)
        
        if not ficha_destino:
            raise ValidationError(_("No se encontró ficha técnica destino"))
        
        secuencia = 0
        for componente in ficha_destino.componente_ids.sorted(key=lambda r: r.sequence):
            secuencia += 1
            componente_original = componente.origen_copia_id
            
            if componente_original.subcategoria_id.codigo == '115':
                tipo_copia = self._determinar_tipo_taco(numero_talla)
                correlativo = self._obtener_correlativo(componente_original, tipo_copia)
                if correlativo:
                    nuevo_codigo = f"{componente.codigo[:-3]}{correlativo}"
                    componente.write({'codigo': nuevo_codigo})
            
            if (componente_original.rango_talla_desde and componente_original.rango_talla_hasta and
                not (componente_original.rango_talla_desde <= numero_talla <= componente_original.rango_talla_hasta)):
                
                alternativo = self.env['cl.product.componente'].search([
                    ('subcategoria_id', '=', componente_original.subcategoria_id.id),
                    ('rango_talla_desde', '<=', numero_talla),
                    ('rango_talla_hasta', '>=', numero_talla)
                ], limit=1)
                
                if alternativo:
                    componente.write({'articulo_id': alternativo.id})

    def _cambia_materia(self, articulo_origen, modelo_origen, articulo_destino, modelo_destino):
        """
        Cambia materiales según reglas de color/modelo
        """
        self.xcuero = articulo_destino.material_id.codigo[:3]
        self.xcolor = articulo_destino.color_id.codigo[:3]
        self.xplnta = articulo_destino.planta_id.codigo[:3] if articulo_destino.planta_id else '000'
        self.xcolfo = articulo_destino.color_forro_id.codigo[:3] if articulo_destino.color_forro_id else '000'

        ficha_destino = self.env['receta.fichatecnica'].search([
            ('articulos_id', '=', articulo_destino.id),
            ('temporada_id', '=', self.temporada_destino_id.id)
        ], limit=1)
        
        if not ficha_destino:
            raise ValidationError(_("No se encontró ficha técnica destino"))
        
        secuencia = 0
        for componente in ficha_destino.componente_ids.sorted(key=lambda r: r.sequence):
            secuencia += 1
            componente_original = componente.origen_copia_id
            
            if componente_original.subcategoria_id.codigo == '051':
                nuevo_codigo = f"{componente.codigo[:6]}{self.xcolfo}0{articulo_destino.numeracion_id.numero}"
                componente.write({'codigo': nuevo_codigo})
            
            elif componente_original.subcategoria_id.codigo == '100':
                nuevo_codigo = f"{componente.codigo[:4]}{self.xplnta}{self.xcolor}0{articulo_destino.numeracion_id.numero}"
                componente.write({'codigo': nuevo_codigo})
            
            elif componente_original.subcategoria_id.codigo == '028':
                nuevo_codigo = f"{componente.codigo[:2]}{self.xcuero}{self.xcolor}0{articulo_destino.numeracion_id.numero}"
                componente.write({'codigo': nuevo_codigo})
            
            alternativo = self._obtener_material_alternativo(
                componente_original.subcategoria_id,
                secuencia,
                articulo_destino.modelo_id,
                articulo_destino.material_id,
                articulo_destino.color_id,
                articulo_destino.planta_id
            )
            if alternativo:
                componente.write({'articulo_id': alternativo.id}) 

    def _mostrar_resultado(self, exitoso, mensaje):
        """
        Muestra el resultado de la operación en el wizard de forma segura
        """
        try:
            if not isinstance(self.id, models.NewId) and not isinstance(self.id, int):
                raise ValueError("ID de registro no válido")
            
            self.write({
                'exitoso': exitoso,
                'mensaje': mensaje,
                'detalles': traceback.format_exc() if not exitoso else "Operación completada sin errores"
            })
            if not self.exists():
                raise ValueError("El registro del wizard no existe en la base de datos")
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {'create': False} 
            }
        except Exception as e:
            _logger.error("Error en _mostrar_resultado: %s", str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Ocurrió un error: {str(e)}',
                    'sticky': True,
                    'type': 'danger'
                }
            }
