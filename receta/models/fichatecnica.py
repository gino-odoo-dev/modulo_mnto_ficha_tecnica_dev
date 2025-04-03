from odoo import models, fields, api, exceptions, _
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
    
# campos copia ficha tecnica
    part_o = fields.Many2one('cl.product.articulo', string='Articulo Origen', required=False) 
    part_d = fields.Many2one('cl.product.articulo', string='Articulo Destino', required=False)
    m_numero_color = fields.Boolean(string="Copiar Nº", default=True)  
    copia_temporadas = fields.Many2one('cl.product.temporada', string='Temporada', default=False, readonly=True) 
    
    copia = fields.Boolean(string="Copia")
    m_modelo_o = fields.Char(string="Modelo Origen")
    m_modelo_d = fields.Char(string="Modelo Destino")
    no_comb_o = fields.Char(string="Numero Combinaciones Origen")
    no_comb_d = fields.Char(string="Numero Combinaciones Destino")
    xcuero = fields.Char(string="Cuero", size=3)
    xcolor = fields.Char(string="Color", size=3)
    xplnta = fields.Char(string="Plnta", size=3)
    xcolfo = fields.Char(string="Color", size=3)
    sequence = fields.Integer(string="Secuencia", default=10)
    mensaje = fields.Char(string="Mensaje", readonly=True)

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
# Valido si no hay temporada
            if record.articulos_id and not record.temporadas_id:
                return {
                    'warning': {
                        'title': "Temporada requerida",
                        'message': "Debe seleccionar una temporada antes de actualizar los componentes",
                    }
                }
            
# Actualizo componentes si hay articulo
            if record.articulos_id:
                record.with_context(skip_write=True).link_components()
                return {
                    'domain': {'componentes_ids': [('articulo_id', '=', record.articulos_id.id)]}
                }
            
    @api.model
    def create(self, vals):
# Valida que se haya seleccionado una temporada
        if 'temporadas_id' not in vals or not vals['temporadas_id']:
            raise ValidationError("Debe seleccionar una temporada antes de crear una ficha tecnica.")
# Valida que se haya seleccionado un articulo
        if 'articulos_id' not in vals or not vals['articulos_id']:
            raise ValidationError("Debe seleccionar un articulo antes de crear una ficha tecnica.")
# Permite la creacion de multiples fichas tecnicas para el mismo articulo y temporada
# Se agregan un mensaje de advertencia en el log si es necesario
        existing = self.env['receta.fichatecnica'].search([
            ('temporadas_id', '=', vals['temporadas_id']),
            ('articulos_id', '=', vals['articulos_id'])
        ])
        if existing:
            _logger.warning(f"Creando una nueva ficha tecnica para el articulo {vals['articulos_id']} y temporada {vals['temporadas_id']}, aunque ya existe otra ficha tecnica.")

# Llamar al metodo original
        ficha_tecnica = super(FichaTecnica, self).create(vals)
        ficha_tecnica.with_context(skip_link_components=True).link_components()
        return ficha_tecnica

    def write(self, vals):
# Valida cambiar la temporada si ya hay componentes asociados
        if 'temporadas_id' in vals:
            for record in self:
                if record.componentes_ids:
                    raise ValidationError("No puede cambiar la temporada si ya hay componentes asociados.")
# Valida el articulo si ya hay componentes asociados
        if 'articulos_id' in vals:
            for record in self:
                if record.componentes_ids:
                    raise ValidationError("No puede cambiar el artículo si ya hay componentes asociados.")
# Valida articulo y temporada
        if 'temporadas_id' in vals or 'articulos_id' in vals:
            temporadas_id = vals.get('temporadas_id', self.temporadas_id.id)
            articulos_id = vals.get('articulos_id', self.articulos_id.id)
            existing = self.env['receta.fichatecnica'].search([
                ('id', '!=', self.id),
                ('temporadas_id', '=', temporadas_id),
                ('articulos_id', '=', articulos_id)
            ])
            if existing:
                raise ValidationError("Ya existe una ficha técnica para este artículo y temporada.")

# Llamar al metodo original
        result = super(FichaTecnica, self).write(vals)
        if not self.env.context.get('skip_link_components'):
            self.with_context(skip_link_components=True).link_components()
        return result
    
    def success_action(self):
        pass

    def unlink(self):
        """
        Funcion que valida que no se pueda eliminar una ficha tecnica en estado 'Done'.
        """
        for record in self:
            if record.state == 'done':
                raise exceptions.UserError("No se puede eliminar una Ficha Técnica en estado 'Done'.")
        return super(FichaTecnica, self).unlink()
    
    def link_components(self):
        for record in self:
            if not record.articulos_id:
                continue  
            components = self.env['cl.product.componente'].search([
                ('articulo_id', '=', record.articulos_id.id)
            ])
# Reemplazar todos los componentes
            record.componentes_ids = [(6, 0, components.ids)]
            if not self.env.context.get('skip_write') and not record.articulos_id.codigo:
                record.articulos_id.codigo = f"SKU-{record.id:06d}"

    def estructura_sku(self):
        """
        Valida y descompone el SKU solo si cumple con los requisitos.
        """
        if not self.articulos_id:
            raise ValidationError("Debe seleccionar un articulo.")
        
# Verificar si el artículo tiene un SKU asignado
        if not self.articulos_id.name:
            raise ValidationError(f"El artículo '{self.articulos_id.name}' no tiene un SKU asignado.")
        
        if len(self.articulos_id.name) != 18:
            raise ValidationError("El SKU debe tener exactamente 18 caracteres.")

        sku = self.articulos_id.name

# Validar que el nombre del SKU esté bien formado
        mappings = [
            ('marca_name', 'cl.product.marca', sku[:2]),
            ('genero_name', 'cl.product.genero', sku[2]),
            ('correlativo_name', 'cl.product.correlativo', sku[3:7]),
            ('categoria_name', 'cl.product.categoria', sku[7]),
            ('subcategoria_name', 'cl.product.subcategoria', sku[8:10]),
            ('temporada_name', 'cl.product.temporada', sku[10]),
            ('material_name', 'cl.product.material', sku[11:13]),
            ('color_name', 'cl.product.color', sku[13:15]),
            ('tallas_name', 'cl.product.tallas', sku[15:18]),
        ]

        for field_name, _, value in mappings:
            if not value:
                raise ValidationError(f"El campo '{field_name}' no está bien formado en el SKU.")
        
        self.mensaje = "El SKU está correctamente formado."

# Mapeo de campos y modelos para extraer el SKU
        for field_name, model_name, code in mappings:
            record_found = self.env[model_name].search([("codigo", '=', code)], limit=1)
            if not record_found:
                raise ValidationError(f"No se encontro registro para el codigo: {code}.")
            self.write({field_name: record_found.name})

    def copia_rec_dev(self):
        """
        Funcion principal que realiza las validaciones y copia de recetas.
        """
        self.ensure_one()
        try:
# Validar que la temporada exista en la base de datos.
            temporada_existente = self.env['code.mstr'].search([
                ('code_domain', '=', 'global_domain'),
                ('code_fldname', '=', 'TEMPORADA'),
                ('code_value', '=', self.temporadas_id.code_value)
            ], limit=1)
            if not temporada_existente:
                raise ValidationError("La temporada no existe.")

# Validar articulo origen.
            if not self.part_o:
                raise ValidationError("El articulo origen no puede estar vacío.")
            articulo_origen = self.env['product.template'].search([('default_code', '=', self.part_o)], limit=1)
            if not articulo_origen:
                raise ValidationError("El articulo origen no existe.")
            if not articulo_origen.pt_part_type.startswith("PT-"):
                raise ValidationError("El articulo origen debe ser de tipo 'PT-'.")
            if articulo_origen.pt_pm_code != 'M':
                raise ValidationError("El articulo origen debe estar marcado como manufacturado.")

# Validar estructura para la temporada.
            estructura_existente = self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_ref', '=', self.temporadas_id.code_value)
            ], limit=1)
            if not estructura_existente:
                raise ValidationError("El articulo origen no tiene estructura para la temporada.")

# Validar articulo destino (si no es copia de número/color).
            if self.m_numero_color:
                if self.part_d:
                    raise ValidationError("El articulo destino debe estar vacío cuando se copia numeraciones/ficha técnica.")
            else:
                if not self.part_d:
                    raise ValidationError("El articulo destino no puede estar vacío.")
                articulo_destino = self.env['product.template'].search([('default_code', '=', self.part_d)], limit=1)
                if not articulo_destino:
                    raise ValidationError("El articulo destino no existe.")
                if not articulo_destino.pt_part_type.startswith("PT-"):
                    raise ValidationError("El articulo destino debe ser de tipo 'PT-'.")
                if articulo_destino.pt_pm_code != 'M':
                    raise ValidationError("El articulo destino debe estar marcado como manufacturado.")
                if self.part_o == self.part_d:
                    raise ValidationError("El articulo origen y destino no pueden ser iguales.")
                if self.m_modelo_o == self.m_modelo_d:
                    raise ValidationError("El modelo de origen y destino deben ser diferentes.")

# Validar numero de combinaciones.
                if self.no_comb_o != self.no_comb_d:
                    raise ValidationError("El número de combinaciones no coincide entre el articulo origen y destino.")

# Validar si el articulo destino ya tiene ficha tecnica para la temporada.
                ficha_tecnica_existente = self.env['ps.mstr'].search([
                    ('ps_domain', '=', 'global_domain'),
                    ('ps_par', '=', self.part_d),
                    ('ps_ref', '=', self.temporadas_id.code_value)
                ], limit=1)
                if ficha_tecnica_existente:
                    raise ValidationError("El articulo destino ya tiene una ficha técnica para la temporada especificada.")

# Logica de copia.
            if self.m_numero_color:
                self._copia_numero(self.part_o, self.temporadas_id.code_value)
            else:
                self._copia_color(self.part_o, self.part_d, self.temporadas_id.code_value)
                self._cambia_materia(self.part_o, self.m_modelo_o, self.part_d, self.m_modelo_d)
                self._cambia_componente(self.part_o, self.m_modelo_o, self.part_d, self.m_modelo_d)

            mensaje_final = "Proceso de copia completado correctamente."
            self.write({'mensaje': mensaje_final})
            return True
        except ValidationError as e:
            self.write({'mensaje': f"Error de validación: {str(e)}"})
            return False
        except Exception as e:
            self.write({'mensaje': f"Error inesperado: {str(e)}"})
            return False

    def obtener_numero_combinaciones(self, codigo_articulo):
        """
        Metodo para obtener el numero de combinaciones de un articulo.
        es necesaria para cumplir con la validacion del numero de combinaciones 
        entre el articulo origen y el articulo destino. 
        Esta validacion es crucial para garantizar que los articulos sean compatibles 
        antes de realizar la copia.
        """
# Buscar el articulo en la base de datos.
        articulo = self.env['product.template'].search([('default_code', '=', codigo_articulo)], limit=1)
        
        if not articulo:
            raise ValidationError(f"El articulo {codigo_articulo} no existe.")
        
# Suponiendo que el numero de combinaciones esta en un campo personalizado llamado 'x_numero_combinaciones'.
        if hasattr(articulo, 'x_numero_combinaciones'):
            return articulo.x_numero_combinaciones
        else:
            raise ValidationError(f"El articulo {codigo_articulo} no tiene un numero de combinaciones definido.")
           
    def _copia_numero(self, part_o, temporadas_id):
        """
        Copia las formulas de un articulo origen a otros articulos del mismo modelo.
        """
        articulo_origen = self.env['product.template'].search([('default_code', '=', part_o)], limit=1)
        articulos_mismo_modelo = self.env['product.template'].search([
            ('pt_model', '=', articulo_origen.pt_model),
            ('pt_part_type', '=like', 'PT-%'),
            ('pt_pm_code', '=', 'M'),
            ('default_code', '!=', part_o)
        ])

# Copiar formulas.
        for articulo in articulos_mismo_modelo:
            formulas_origen = self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', part_o),
                ('ps_ref', '=', temporadas_id)
            ])
            for formula in formulas_origen:
                self.env['ps.mstr'].create({
                    'ps_par': articulo.default_code,
                    'ps_comp': formula.ps_comp,
                    'ps_ref': formula.ps_ref,
                    'ps_qty_per': formula.ps_qty_per,
                    'ps_scrp_pct': formula.ps_scrp_pct,
                    'ps_ps_code': formula.ps_ps_code,
                    'ps_lt_off': formula.ps_lt_off,
                    'ps_start': formula.ps_start,
                    'ps_end': formula.ps_end,
                    'ps_rmks': formula.ps_rmks,
                    'ps_op': formula.ps_op,
                    'ps_item_no': formula.ps_item_no,
                    'ps_mandatory': formula.ps_mandatory,
                    'ps_exclusive': formula.ps_exclusive,
                    'ps_process': formula.ps_process,
                    'ps_qty_type': formula.ps_qty_type,
                    'ps_user1': formula.ps_user1,
                    'ps_user2': formula.ps_user2,
                    'ps_fcst_pct': formula.ps_fcst_pct,
                    'ps_default': formula.ps_default,
                })

    def _cambia_componente(self, part_o, m_modelo_o, part_d, m_modelo_d):
        """
        Cambia los componentes de una receta en la base de datos.
        """
# Buscar las formulas del articulo origen.
        ps_mstr_origin_records = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', part_o),
            ('ps_ref', '=', self.temporadas_id.code_value)
        ])

        if not ps_mstr_origin_records:
            raise ValidationError(f"No se encontraron registros de origen para el articulo {part_o} y la temporada {self.temporadas_id.code_value}.")

# Buscar las formulas del articulo destino.
        ps_mstr_dest_records = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', part_d),
            ('ps_ref', '=', self.temporadas_id.code_value)
        ])

        if not ps_mstr_dest_records:
            raise ValidationError(f"No se encontraron registros de destino para el articulo {part_d} y la temporada {self.temporadas_id.code_value}.")

# Cambiar los componentes en las formulas del articulo destino.
        for ps_dest in ps_mstr_dest_records:
            for ps_origin in ps_mstr_origin_records:
                if ps_dest.ps_comp == m_modelo_o:
# Buscar un componente alternativo.
                    nuevo_componente = self._determinar_nuevo_componente(ps_origin.ps_comp)
                    if nuevo_componente:
                        ps_dest.write({
                            'ps_comp': nuevo_componente,
                            'ps_qty_per': ps_origin.ps_qty_per,
                            'ps_scrp_pct': ps_origin.ps_scrp_pct,
                            'ps_ps_code': ps_origin.ps_ps_code,
                            'ps_lt_off': ps_origin.ps_lt_off,
                            'ps_start': ps_origin.ps_start,
                            'ps_end': ps_origin.ps_end,
                            'ps_rmks': ps_origin.ps_rmks,
                            'ps_op': ps_origin.ps_op,
                            'ps_item_no': ps_origin.ps_item_no,
                            'ps_mandatory': ps_origin.ps_mandatory,
                            'ps_exclusive': ps_origin.ps_exclusive,
                            'ps_process': ps_origin.ps_process,
                            'ps_qty_type': ps_origin.ps_qty_type,
                            'ps_user1': ps_origin.ps_user1,
                            'ps_user2': ps_origin.ps_user2,
                            'ps_fcst_pct': ps_origin.ps_fcst_pct,
                            'ps_default': ps_origin.ps_default,
                        })
                    else:
                        raise ValidationError(f"No se pudo determinar un nuevo componente para {ps_origin.ps_comp}.")

    def _crea_ficha_comp(self, comp_origen, comp_destino, temporadas_id):
        """
        Crea la ficha tecnica del componente destino basada en el componente origen.
        """
# Buscar la ficha tecnica del componente destino.
        ps_mstr_destino = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', comp_destino),
            ('ps_ref', '=', temporadas_id)
        ], limit=1)

# Si ya existe la ficha tecnica del componente destino, lanzar una excepcion.
        if ps_mstr_destino:
            raise ValidationError(f"La ficha técnica del componente destino {comp_destino} ya existe para la temporada {temporadas_id}.")

# Si no existe la ficha tecnica del componente destino, se procede a crearla.
        ps_mstr_origen_records = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', comp_origen),
            ('ps_ref', '=', temporadas_id)
        ])

        for ps_origen in ps_mstr_origen_records:
# Determinar si se debe cambiar el numero del componente.
            comp_cambia_num = (
                ps_origen.ps_comp[-3:] == comp_origen[-3:]
            )
            comp_numero = comp_destino[-3:] if comp_cambia_num else ""

# Crear la nueva ficha tecnica para el componente destino.
            self.env['ps.mstr'].create({
                'ps_par': comp_destino,
                'ps_comp': (
                    ps_origen.ps_comp[:-3] + comp_numero
                    if comp_cambia_num else ps_origen.ps_comp
                ),
                'ps_ref': ps_origen.ps_ref,
                'ps_qty_per': ps_origen.ps_qty_per,
                'ps_scrp_pct': ps_origen.ps_scrp_pct,
                'ps_ps_code': ps_origen.ps_ps_code,
                'ps_lt_off': ps_origen.ps_lt_off,
                'ps_start': ps_origen.ps_start,
                'ps_end': ps_origen.ps_end,
                'ps_rmks': ps_origen.ps_rmks,
                'ps_op': ps_origen.ps_op,
                'ps_item_no': ps_origen.ps_item_no,
                'ps_mandatory': ps_origen.ps_mandatory,
                'ps_exclusive': ps_origen.ps_exclusive,
                'ps_process': ps_origen.ps_process,
                'ps_qty_type': ps_origen.ps_qty_type,
                'ps_user1': ps_origen.ps_user1,
                'ps_user2': ps_origen.ps_user2,
                'ps_fcst_pct': ps_origen.ps_fcst_pct,
                'ps_default': ps_origen.ps_default,
                'ps_group': ps_origen.ps_group,
                'ps_critical': ps_origen.ps_critical,
                'ps_qty_per_b': ps_origen.ps_qty_per_b,
                'ps_comp_um': ps_origen.ps_comp_um,
                'ps_um_conv': ps_origen.ps_um_conv,
                'ps_assay': ps_origen.ps_assay,
                'ps_comm_code': ps_origen.ps_comm_code,
                'ps_non_bal': ps_origen.ps_non_bal,
                'ps__qad01': ps_origen.ps__qad01,
                'ps_userid': ps_origen.ps_userid,
                'ps_mod_date': ps_origen.ps_mod_date,
                'ps_batch_pct': ps_origen.ps_batch_pct,
                'ps_cmtindx': ps_origen.ps_cmtindx,
                'ps_start_ecn': ps_origen.ps_start_ecn,
                'ps_end_ecn': ps_origen.ps_end_ecn,
                'ps_joint_type': ps_origen.ps_joint_type,
                'ps_cop_qty': ps_origen.ps_cop_qty,
                'ps_cst_pct': ps_origen.ps_cst_pct,
                'ps_prod_pct': ps_origen.ps_prod_pct,
                'ps_qty_cons': ps_origen.ps_qty_cons,
                'ps_qty_exch': ps_origen.ps_qty_exch,
                'ps_qty_diag': ps_origen.ps_qty_diag,
                'ps__chr01': ps_origen.ps__chr01,
                'ps__chr02': ps_origen.ps__chr02,
                'ps__dte01': ps_origen.ps__dte01,
                'ps__dte02': ps_origen.ps__dte02,
                'ps__dec01': ps_origen.ps__dec01,
                'ps__dec02': ps_origen.ps__dec02,
                'ps__log01': ps_origen.ps__log01,
                'ps__log02': ps_origen.ps__log02,
                'ps__qadc01': ps_origen.ps__qadc01,
                'ps__qadc02': ps_origen.ps__qadc02,
                'ps__qadt01': ps_origen.ps__qadt01,
                'ps__qadt02': ps_origen.ps__qadt02,
                'ps__qadt03': ps_origen.ps__qadt03,
                'ps__qadd01': ps_origen.ps__qadd01,
                'ps__qadd02': ps_origen.ps__qadd02,
                'ps__qadl01': ps_origen.ps__qadl01,
                'ps__qadl02': ps_origen.ps__qadl02,
                'ps_domain': ps_origen.ps_domain,
            })

# Crear la tabla de cabecera (bom_mstr) si no existe.
        bom_mstr_destino = self.env['bom.mstr'].search([
            ('bom_domain', '=', 'global_domain'),
            ('bom_parent', '=', comp_destino)
        ], limit=1)

        if not bom_mstr_destino:
            bom_mstr_origen = self.env['bom.mstr'].search([
                ('bom_domain', '=', 'global_domain'),
                ('bom_parent', '=', comp_origen)
            ], limit=1)

            if bom_mstr_origen:
                self.env['bom.mstr'].create({
                    'bom_parent': comp_destino,
                    'bom_desc': bom_mstr_origen.bom_desc,
                    'bom_batch': bom_mstr_origen.bom_batch,
                    'bom_batch_um': bom_mstr_origen.bom_batch_um,
                    'bom_cmtindx': bom_mstr_origen.bom_cmtindx,
                    'bom_ll_code': bom_mstr_origen.bom_ll_code,
                    'bom_user1': bom_mstr_origen.bom_user1,
                    'bom_user2': bom_mstr_origen.bom_user2,
                    'bom_userid': bom_mstr_origen.bom_userid,
                    'bom_mod_date': bom_mstr_origen.bom_mod_date,
                    'bom__chr01': bom_mstr_origen.bom__chr01,
                    'bom__chr02': bom_mstr_origen.bom__chr02,
                    'bom__chr03': bom_mstr_origen.bom__chr03,
                    'bom__chr04': bom_mstr_origen.bom__chr04,
                    'bom__chr05': bom_mstr_origen.bom__chr05,
                    'bom__dte01': bom_mstr_origen.bom__dte01,
                    'bom__dte02': bom_mstr_origen.bom__dte02,
                    'bom__dec01': bom_mstr_origen.bom__dec01,
                    'bom__dec02': bom_mstr_origen.bom__dec02,
                    'bom__log01': bom_mstr_origen.bom__log01,
                    'bom_formula': bom_mstr_origen.bom_formula,
                    'bom_mthd': bom_mstr_origen.bom_mthd,
                    'bom_fsm_type': bom_mstr_origen.bom_fsm_type,
                    'bom_site': bom_mstr_origen.bom_site,
                    'bom_loc': bom_mstr_origen.bom_loc,
                    'bom__qadc01': bom_mstr_origen.bom__qadc01,
                    'bom__qadc02': bom_mstr_origen.bom__qadc02,
                    'bom__qadc03': bom_mstr_origen.bom__qadc03,
                    'bom__qadd01': bom_mstr_origen.bom__qadd01,
                    'bom__qadi01': bom_mstr_origen.bom__qadi01,
                    'bom__qadi02': bom_mstr_origen.bom__qadi02,
                    'bom__qadt01': bom_mstr_origen.bom__qadt01,
                    'bom__qadt02': bom_mstr_origen.bom__qadt02,
                    'bom__qadl01': bom_mstr_origen.bom__qadl01,
                    'bom__qadl02': bom_mstr_origen.bom__qadl02,
                    'bom_mthd_qtycompl': bom_mstr_origen.bom_mthd_qtycompl,
                    'bom_domain': bom_mstr_origen.bom_domain,
                })

    def _copia_color(self, part_o, part_d, temporadas_id): 
        """
        Copia las formulas de un articulo origen a un articulo destino.
        """
        try:
# Verificar si el articulo destino ya tiene formulas, si tiene formula se eliminan.
            formulas_existentes = self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', part_d),
                ('ps_ref', '=', temporadas_id)
            ])
            if formulas_existentes:
                formulas_existentes.unlink()

# Copiar formulas del articulo origen al destino.
            formulas_origen = self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', part_o),
                ('ps_ref', '=', temporadas_id)
            ])
            for formula in formulas_origen:
                self.env['ps.mstr'].create({
                    'ps_par': part_d,
                    'ps_comp': formula.ps_comp,
                    'ps_ref': formula.ps_ref,
                    'ps_qty_per': formula.ps_qty_per,
                    'ps_scrp_pct': formula.ps_scrp_pct,
                    'ps_ps_code': formula.ps_ps_code,
                    'ps_lt_off': formula.ps_lt_off,
                    'ps_start': formula.ps_start,
                    'ps_end': formula.ps_end,
                    'ps_rmks': formula.ps_rmks,
                    'ps_op': formula.ps_op,
                    'ps_item_no': formula.ps_item_no,
                    'ps_mandatory': formula.ps_mandatory,
                    'ps_exclusive': formula.ps_exclusive,
                    'ps_process': formula.ps_process,
                    'ps_qty_type': formula.ps_qty_type,
                    'ps_user1': formula.ps_user1,
                    'ps_user2': formula.ps_user2,
                    'ps_fcst_pct': formula.ps_fcst_pct,
                    'ps_default': formula.ps_default,
                })
        except Exception as e:
            raise ValidationError(f"Error al eliminar las fórmulas existentes: {str(e)}")

    def _cambia_materia(self, part_o, m_modelo_o, part_d, m_modelo_d):
        """
        Cambia las materias primas de un artículo según las reglas definidas.
        """
# Buscar el artículo destino
        articulo_destino = self.env['product.template'].search([
            ('default_code', '=', part_d)
        ], limit=1)

        if not articulo_destino:
            raise ValidationError("El articulo destino no existe.")

# Asignar valores a xcuero, xcolor, xplnta, y xcolfo
        self.xcuero = articulo_destino.pt__chr01  
        self.xcolor = articulo_destino.pt__chr02 
        self.xplnta = articulo_destino.pt__chr06 
        self.xcolfo = articulo_destino.pt__chr07 

# Cambiar el color del forro
        for ps_record in self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', m_modelo_d),
            ('ps_ref', '=', self.temporadas_id.code_value),
            ('ps_comp', 'like', '051%')  
        ]):
            remplaza = f"{ps_record.ps_comp[:6]}{self.xcolfo}0{ps_record.pt_draw}"
            if not self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', m_modelo_d),
                ('ps_ref', '=', self.temporadas_id.code_value),
                ('ps_comp', '=', remplaza)
            ], limit=1):
                ps_record.write({'ps_comp': remplaza})
            else:
                raise ValidationError(f"Ya existe el forro {remplaza} en la estructura.")

# Cambiar el color de la planta
        for ps_record in self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', part_d),
            ('ps_ref', '=', self.temporadas_id.code_value),
            ('ps_comp', 'like', '100%')  
        ]):
            remplaza = f"{ps_record.ps_comp[:4]}{self.xplnta}{self.xcolor}0{ps_record.pt_draw}"
            if not self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', m_modelo_d),
                ('ps_ref', '=', self.temporadas_id.code_value),
                ('ps_comp', '=', remplaza)
            ], limit=1):
                ps_record.write({'ps_comp': remplaza})
            else:
                raise ValidationError(f"Ya existe la planta {remplaza} en la estructura.")

# Cambiar el color de cueros combinados
        m_seq_tra = 0
        for ps_record in self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', m_modelo_d),
            ('ps_ref', '=', self.temporadas_id.code_value),
            ('ps_comp', 'like', '028%')  
        ]):
            m_seq_tra += 1
            remplaza = f"{ps_record.ps_comp[:2]}{self.xcuero}{self.xcolor}0{ps_record.pt_draw}"
            if not self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', m_modelo_d),
                ('ps_ref', '=', self.temporadas_id.code_value),
                ('ps_comp', '=', remplaza)
            ], limit=1):
                ps_record.write({'ps_comp': remplaza})
            else:
                ps_record.write({'ps_ref': f"X{ps_record.ps_ref}", 'ps_comp': remplaza})

# Regresar el dato que estaba repetido por cueros combinados
        for ps_record in self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', m_modelo_d),
            ('ps_ref', 'like', 'X%')  
        ]):
            ps_record.write({'ps_ref': ps_record.ps_ref[1:]})  

    def _determinar_nuevo_componente(self, pt_record):
        """
        Determina el nuevo componente basado en el componente actual.
        """
# Caso 1: Buscar un componente alternativo en el mismo grupo.
        nuevo_componente = self.env['pt.mstr'].search([
            ('pt_domain', '=', 'global_domain'),
            ('pt_group', '=', pt_record.pt_group),  
            ('pt_part', '!=', pt_record.pt_part),  
        ], limit=1)

        if nuevo_componente:
            return nuevo_componente.pt_part

# Caso 2: Usar un mapeo predefinido.
        mapeo_componentes = {
            'COMPONENTE_ANTIGUO_1': 'COMPONENTE_NUEVO_1',
            'COMPONENTE_ANTIGUO_2': 'COMPONENTE_NUEVO_2',
        }

        if pt_record.pt_part in mapeo_componentes:
            return mapeo_componentes[pt_record.pt_part]
# Caso 3: Generar el nuevo componente.
# Agregar un sufijo o prefijo al código original.
        if (pt_record.pt_part.startswith("PT-")):
            return f"PT-NUEVO-{pt_record.pt_part[3:]}"
# Si no se encuentra un nuevo componente, devolver None.
        return None
    
    def next_button(self):
        """
        Execute the copy function and return a wizard action.
        """
        try:
            self.copia_rec_dev()
            wizard = self.env['copia.receta.fichatecnica'].create({
                'mensaje': self.mensaje or _("Proceso completado"),
                'ficha_tecnica_id': self.id,
                'detalles': _("Copia realizada de %s a %s") % (self.part_o, self.part_d),
                'exitoso': True if _("correctamente") in (self.mensaje or "") else False
            })
        except Exception as e:
            wizard = self.env['copia.receta.fichatecnica'].create({
                'mensaje': _("Error: %s") % str(e),
                'ficha_tecnica_id': self.id,
                'detalles': _("Error durante el proceso de copia"),
                'exitoso': False
            })
        return {
            'name': _('Resultado de Copia'),
            'type': 'ir.actions.act_window',
            'res_model': 'copia.receta.fichatecnica',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context
        }

