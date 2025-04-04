from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CopiaFichaTecnicaWizard(models.TransientModel):
    _name = 'copia.receta.fichatecnica'
    _description = 'Asistente para Copiar Ficha Técnica'
 
    mensaje = fields.Text(string="Resultado", readonly=True)
    ficha_tecnica_id = fields.Many2one('receta.fichatecnica', string="Ficha Tecnica Origen", required=True, default=lambda self: self._default_ficha_tecnica_id())
    temporada_destino_id = fields.Many2one('cl.temporada', string="Temporada Destino", required=True)
    detalles = fields.Text(string="Detalles de la operacion", readonly=True)
    exitoso = fields.Boolean(string="Operación Exitosa", readonly=True)
    temporada_origen_id = fields.Many2one('cl.temporada', string="Temporada Origen", readonly=True)
    articulo_origen_id = fields.Many2one('cl.product.articulo', string="Artículo Origen", readonly=True)
    componentes_count = fields.Integer(string="Total Componentes", readonly=True)
    componente1_id = fields.Many2one('cl.product.componente', string="Componente 1", readonly=True)
    componente1_name = fields.Char(string="Componente 1 - Nombre", readonly=True)
    componente1_descripcion = fields.Char(string="Componente 1 - Descripcion", readonly=True)
    componente1_umedida = fields.Char(string="Componente 1 - Unidad Medida", readonly=True)
    componente1_codigosecuencia_id = fields.Many2one('cl.secuencia', string="Componente 1 - Codigo Secuencia", readonly=True)
    componente1_compra_manufactura_id = fields.Many2one('cl.product.origen', string="Componente 1 - Compra/Manufactura", readonly=True)
    componente1_compra_manufactura_name = fields.Char(string="Componente 1 - Nombre Compra/Manufactura", readonly=True)
    componente1_cantidad_id = fields.Integer(string="Componente 1 - Cantidad", readonly=True)
    componente1_factor_perdida_id = fields.Float(string="Componente 1 - Factor Perdida (%)", readonly=True)
    componente1_costo_unitario_id = fields.Float(string="Componente 1 - Costo Unitario", readonly=True)
    componente1_costo_ampliado_id = fields.Float(string="Componente 1 - Costo Ampliado", readonly=True)
    componente1_departamento_id = fields.Many2one('cl.departamento', string="Componente 1 - Departamento", readonly=True)
    componente1_departamento_name = fields.Char(string="Componente 1 - Nombre Departamento", readonly=True)
    componente1_articulo_id = fields.Many2one('cl.product.articulo', string="Componente 1 - Articulo", readonly=True)
    
    for i in range(2, 21):
        locals().update({
            f'componente{i}_id': fields.Many2one('cl.product.componente', string=f"Componente {i}", readonly=True),
            f'componente{i}_name': fields.Char(string=f"Componente {i} - Nombre", readonly=True),
            f'componente{i}_descripcion': fields.Char(string=f"Componente {i} - Descripcion", readonly=True),
            f'componente{i}_umedida': fields.Char(string=f"Componente {i} - Unidad Medida", readonly=True),
            f'componente{i}_codigosecuencia_id': fields.Many2one('cl.secuencia', string=f"Componente {i} - Codigo Secuencia", readonly=True),
            f'componente{i}_compra_manufactura_id': fields.Many2one('cl.product.origen', string=f"Componente {i} - Compra/Manufactura", readonly=True),
            f'componente{i}_compra_manufactura_name': fields.Char(string=f"Componente {i} - Nombre Compra/Manufactura", readonly=True),
            f'componente{i}_cantidad_id': fields.Integer(string=f"Componente {i} - Cantidad", readonly=True),
            f'componente{i}_factor_perdida_id': fields.Float(string=f"Componente {i} - Factor Perdida (%)", readonly=True),
            f'componente{i}_costo_unitario_id': fields.Float(string=f"Componente {i} - Costo Unitario", readonly=True),
            f'componente{i}_costo_ampliado_id': fields.Float(string=f"Componente {i} - Costo Ampliado", readonly=True),
            f'componente{i}_departamento_id': fields.Many2one('cl.departamento', string=f"Componente {i} - Departamento", readonly=True),
            f'componente{i}_departamento_name': fields.Char(string=f"Componente {i} - Nombre Departamento", readonly=True),
            f'componente{i}_articulo_id': fields.Many2one('cl.product.articulo', string=f"Componente {i} - Articulo", readonly=True),
        })

    def _default_ficha_tecnica_id(self):
        return self.env.context.get('active_id')

    def cargar_datos_fichatecnica(self):
        """funcion que carga los datos especificos (articulo_id y temporada_id) desde la ficha tecnica"""
        self.ensure_one()
        
        if not self.ficha_tecnica_id:
            raise UserError("No se ha seleccionado una ficha tecnica origen")
        self.write({
            'temporada_origen_id': self.ficha_tecnica_id.temporada_id.id,
            'articulo_origen_id': self.ficha_tecnica_id.articulos_id.id
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
                raise UserError("Debe seleccionar una ficha tecnica origen")
            vals = {
                'temporada_origen_id': self.ficha_tecnica_id.temporada_id.id,
                'articulo_origen_id': self.ficha_tecnica_id.articulos_id.id,
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
            raise UserError(f"Error al cargar componentes: {str(e)}")
        
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
            raise UserError("No hay articulo origen seleccionado")
        
        sku = self.articulo_origen_id.name
        
        if not sku or len(sku) != 18:
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

    def copia_rec_dev(self):
        """
        funcion principal que realiza las validaciones y copia de recetas.
        """
        self.ensure_one()
        try:
            temporada_existente = self.env['code.mstr'].search([
                ('code_domain', '=', 'global_domain'),
                ('code_fldname', '=', 'TEMPORADA'),
                ('code_value', '=', self.temporadas_id.code_value)
            ], limit=1)
            if not temporada_existente:
                raise ValidationError("La temporada no existe.")

            if not self.part_o:
                raise ValidationError("El articulo origen no puede estar vacio.")
            articulo_origen = self.env['product.template'].search([('default_code', '=', self.part_o)], limit=1)
            if not articulo_origen:
                raise ValidationError("El articulo origen no existe.")
            if not articulo_origen.pt_part_type.startswith("PT-"):
                raise ValidationError("El articulo origen debe ser de tipo 'PT-'.")
            if articulo_origen.pt_pm_code != 'M':
                raise ValidationError("El articulo origen debe estar marcado como manufacturado.")

            estructura_existente = self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_ref', '=', self.temporadas_id.code_value)
            ], limit=1)
            if not estructura_existente:
                raise ValidationError("El articulo origen no tiene estructura para la temporada.")

            if self.m_numero_color:
                if self.part_d:
                    raise ValidationError("El articulo destino debe estar vacío cuando se copia numeraciones/ficha tecnica.")
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

                if self.no_comb_o != self.no_comb_d:
                    raise ValidationError("El numero de combinaciones no coincide entre el articulo origen y destino.")

                ficha_tecnica_existente = self.env['ps.mstr'].search([
                    ('ps_domain', '=', 'global_domain'),
                    ('ps_par', '=', self.part_d),
                    ('ps_ref', '=', self.temporadas_id.code_value)
                ], limit=1)
                if ficha_tecnica_existente:
                    raise ValidationError("El articulo destino ya tiene una ficha tecnica para la temporada especificada.")

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
            self.write({'mensaje': f"Error de validacion: {str(e)}"})
            return False
        except Exception as e:
            self.write({'mensaje': f"Error inesperado: {str(e)}"})
            return False

    def obtener_numero_combinaciones(self, codigo_articulo):
        """
        metodo para obtener el numero de combinaciones de un articulo.
        es necesaria para cumplir con la validacion del numero de combinaciones entre el articulo origen y el articulo destino. 
        Esta validacion es crucial para garantizar que los articulos sean compatibles antes de realizar la copia.
        """
        articulo = self.env['product.template'].search([('default_code', '=', codigo_articulo)], limit=1)
        
        if not articulo:
            raise ValidationError(f"El articulo {codigo_articulo} no existe.")
        
        if hasattr(articulo, 'x_numero_combinaciones'):
            return articulo.x_numero_combinaciones
        else:
            raise ValidationError(f"El articulo {codigo_articulo} no tiene un numero de combinaciones definido.")
        
    def _copia_numero(self, part_o, temporadas_id):
        """
        copia las formulas de un articulo origen a otros articulos del mismo modelo.
        """
        articulo_origen = self.env['product.template'].search([('default_code', '=', part_o)], limit=1)
        articulos_mismo_modelo = self.env['product.template'].search([
            ('pt_model', '=', articulo_origen.pt_model),
            ('pt_part_type', '=like', 'PT-%'),
            ('pt_pm_code', '=', 'M'),
            ('default_code', '!=', part_o)
        ])
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
        cambia los componentes de una receta en la base de datos.
        """
        ps_mstr_origin_records = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', part_o),
            ('ps_ref', '=', self.temporadas_id.code_value)
        ])

        if not ps_mstr_origin_records:
            raise ValidationError(f"No se encontraron registros de origen para el articulo {part_o} y la temporada {self.temporadas_id.code_value}.")

        ps_mstr_dest_records = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', part_d),
            ('ps_ref', '=', self.temporadas_id.code_value)
        ])

        if not ps_mstr_dest_records:
            raise ValidationError(f"No se encontraron registros de destino para el articulo {part_d} y la temporada {self.temporadas_id.code_value}.")

        for ps_dest in ps_mstr_dest_records:
            for ps_origin in ps_mstr_origin_records:
                if ps_dest.ps_comp == m_modelo_o:
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
        crea la ficha tecnica del componente destino basada en el componente origen.
        """
        ps_mstr_destino = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', comp_destino),
            ('ps_ref', '=', temporadas_id)
        ], limit=1)

        if ps_mstr_destino:
            raise ValidationError(f"La ficha tecnica del componente destino {comp_destino} ya existe para la temporada {temporadas_id}.")

        ps_mstr_origen_records = self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', comp_origen),
            ('ps_ref', '=', temporadas_id)
        ])

        for ps_origen in ps_mstr_origen_records:
            comp_cambia_num = (
                ps_origen.ps_comp[-3:] == comp_origen[-3:]
            )
            comp_numero = comp_destino[-3:] if comp_cambia_num else ""

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
        copia las formulas de un articulo origen a un articulo destino.
        """
        try:
            formulas_existentes = self.env['ps.mstr'].search([
                ('ps_domain', '=', 'global_domain'),
                ('ps_par', '=', part_d),
                ('ps_ref', '=', temporadas_id)
            ])
            if formulas_existentes:
                formulas_existentes.unlink()

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
            raise ValidationError(f"Error al eliminar las formulas existentes: {str(e)}")

    def _cambia_materia(self, part_o, m_modelo_o, part_d, m_modelo_d):
        """
        cambia las materias primas de un articulo según las reglas definidas.
        """
        articulo_destino = self.env['product.template'].search([
            ('default_code', '=', part_d)
        ], limit=1)

        if not articulo_destino:
            raise ValidationError("El articulo destino no existe.")

        self.xcuero = articulo_destino.pt__chr01  
        self.xcolor = articulo_destino.pt__chr02 
        self.xplnta = articulo_destino.pt__chr06 
        self.xcolfo = articulo_destino.pt__chr07 

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

        for ps_record in self.env['ps.mstr'].search([
            ('ps_domain', '=', 'global_domain'),
            ('ps_par', '=', m_modelo_d),
            ('ps_ref', 'like', 'X%')  
        ]):
            ps_record.write({'ps_ref': ps_record.ps_ref[1:]})  

    def _determinar_nuevo_componente(self, pt_record):
        """
        determina el nuevo componente basado en el componente actual.
        """
        nuevo_componente = self.env['pt.mstr'].search([
            ('pt_domain', '=', 'global_domain'),
            ('pt_group', '=', pt_record.pt_group),  
            ('pt_part', '!=', pt_record.pt_part),  
        ], limit=1)

        if nuevo_componente:
            return nuevo_componente.pt_part

        mapeo_componentes = {
            'COMPONENTE_ANTIGUO_1': 'COMPONENTE_NUEVO_1',
            'COMPONENTE_ANTIGUO_2': 'COMPONENTE_NUEVO_2',
        }

        if pt_record.pt_part in mapeo_componentes:
            return mapeo_componentes[pt_record.pt_part]
        if (pt_record.pt_part.startswith("PT-")):
            return f"PT-NUEVO-{pt_record.pt_part[3:]}"
        return None
    
    def next_button(self):
        """
        ejecuta las funciones cargar_datos_fichatecnica, cargar_datos_componentes, _descomponer_sku y copia_rec_dev.
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

    def close_wizard(self):
        return {'type': 'ir.actions.act_window_close'}