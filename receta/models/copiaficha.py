from odoo import models, fields, _, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore
import logging

_logger = logging.getLogger(__name__)

class CopiaFichaTecnicaWizard(models.TransientModel):
    _name = 'copia.receta.fichatecnica'
    _description = 'Copia Ficha Tecnica'
 
    mensaje = fields.Text(string="Resultado", readonly=True)
    ficha_tecnica_id = fields.Many2one('receta.fichatecnica', string="Ficha Tecnica Origen", required=True, default=lambda self: self._default_ficha_tecnica_id())
    temporada_destino_id = fields.Many2one('cl.product.temporada', string="Temporada Destino", required=True)
    detalles = fields.Text(string="Ficha Tecnica Destino", readonly=True)
    temporada_origen_id = fields.Many2one('cl.product.temporada', string="Temporada Origen", readonly=True)
    temporada_destino_id = fields.Many2one('cl.product.temporada', string="Temporada Destino", required=True)

    articulo_origen_id = fields.Many2one('product.template', string="Modelo Origen", readonly=True)
    articulo_destino_id = fields.Many2one('product.template', string="Ficha tecnica Destino", readonly=True)
    numeros_seleccionados = fields.Many2many('cl.product.tallas', string='Numeros Talla')
    modelo_origen_id = fields.Many2one('product.template', string="Artículo Origen", readonly=True)
    modelo_destino_id = fields.Many2one('product.template', string="Artículo Destino", readonly=True)

    componentes_count = fields.Integer(string="Total Componentes", readonly=True)
    componente1_id = fields.Many2one('product.template', string="Componente 1", readonly=True)
    componente1_name = fields.Char(string="Componente 1 - Nombre", readonly=True)
    componente1_descripcion = fields.Char(string="Componente 1 - Descripcion", readonly=True)
    componente1_umedida = fields.Char(string="Componente 1 - Unidad Medida", readonly=True)
    componente1_compra_manufactura_id = fields.Many2one('cl.product.origen', string="Componente 1 - Compra/Manufactura", readonly=True)
    componente1_compra_manufactura_name = fields.Char(string="Componente 1 - Nombre Compra/Manufactura", readonly=True)
    componente1_cantidad_id = fields.Integer(string="Componente 1 - Cantidad", readonly=True)
    componente1_factor_perdida_id = fields.Float(string="Componente 1 - Factor Perdida (%)", readonly=True)
    componente1_costo_unitario_id = fields.Float(string="Componente 1 - Costo Unitario", readonly=True)
    componente1_costo_ampliado_id = fields.Float(string="Componente 1 - Costo Ampliado", readonly=True)
    componente1_departamento_id = fields.Many2one('hr.department', string="Componente 1 - Departamento", readonly=True)
    componente1_departamento_name = fields.Char(string="Componente 1 - Nombre Departamento", readonly=True)
    componente1_articulo_id = fields.Many2one('product.template', string="Componente 1 - Articulo", readonly=True)
    no_comb_o = fields.Integer(string="N° Combinaciones Origen")
    no_comb_d = fields.Integer(string="N° Combinaciones Destino")
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
    no_comb_o = fields.Integer(string="N° Combinaciones Origen")
    no_comb_d = fields.Integer(string="N° Combinaciones Destino")
    xcolor = fields.Char(string="Código de color (XCOLOR)", size=3)
    xplnta = fields.Char(string="Código de planta (XPLNTA)", size=3)
    ficha_destino = fields.Char(string="ficha_destino", readonly=True)

    
    for i in range(2, 6):
        locals().update({
            f'componente{i}_id': fields.Many2one('product.template', string=f"Componente {i}", readonly=True),
            f'componente{i}_name': fields.Char(string=f"Componente {i} - Nombre", readonly=True),
            f'componente{i}_descripcion': fields.Char(string=f"Componente {i} - Descripcion", readonly=True),
            f'componente{i}_umedida': fields.Char(string=f"Componente {i} - Unidad Medida", readonly=True),
            f'componente{i}_compra_manufactura_id': fields.Many2one('cl.product.origen', string=f"Componente {i} - Compra/Manufactura", readonly=True),
            f'componente{i}_compra_manufactura_name': fields.Char(string=f"Componente {i} - Nombre Compra/Manufactura", readonly=True),
            f'componente{i}_cantidad_id': fields.Integer(string=f"Componente {i} - Cantidad", readonly=True),
            f'componente{i}_factor_perdida_id': fields.Float(string=f"Componente {i} - Factor Perdida (%)", readonly=True),
            f'componente{i}_costo_unitario_id': fields.Float(string=f"Componente {i} - Costo Unitario", readonly=True),
            f'componente{i}_costo_ampliado_id': fields.Float(string=f"Componente {i} - Costo Ampliado", readonly=True),
            f'componente{i}_departamento_id': fields.Many2one('cl.product.departamento', string=f"Componente {i} - Departamento", readonly=True),
            f'componente{i}_departamento_name': fields.Char(string=f"Componente {i} - Nombre Departamento", readonly=True),
            f'componente{i}_articulo_id': fields.Many2one('product.template', string=f"Componente {i} - Articulo", readonly=True),
        })

    @api.depends('articulo_origen_id')
    def _compute_modelo_origen(self):
        for record in self:
            if record.articulo_origen_id and record.articulo_origen_id.cl_long_model:
                record.modelo_origen_id = record.articulo_origen_id.cl_long_model.id
            else:
                record.modelo_origen_id = False

    def _default_ficha_tecnica_id(self):
        return self.env.context.get('active_id')

    def cargar_datos_fichatecnica(self):
        self.ensure_one()
        
        if not self.ficha_tecnica_id:
            raise ValidationError("No se ha seleccionado una ficha tecnica origen")

        articulo_origen = self.ficha_tecnica_id.articulos_id
        
        self.write({
            'temporada_origen_id': self.ficha_tecnica_id.temporadas_id.id,
            'articulo_origen_id': articulo_origen.id,
            'modelo_origen_id': articulo_origen.cl_long_model.id if articulo_origen.cl_long_model else False,
            'detalles': articulo_origen.cl_long_model if articulo_origen.cl_long_model else 'Sin codigo',
        })
        return True

    def cargar_datos_componentes(self):
        self.ensure_one()
        result = {
            'mensaje': '',
            'detalles': '',
            'componentes_count': 0
        }
        
        try:
            if not self.ficha_tecnica_id:
                raise ValidationError("Debe seleccionar una ficha tecnica origen")
                
            articulo_origen = self.ficha_tecnica_id.articulos_id
            vals = {
                'temporada_origen_id': self.ficha_tecnica_id.temporadas_id.id,
                'articulo_origen_id': articulo_origen.id,
                'modelo_origen_id': articulo_origen.cl_long_model.id if articulo_origen.cl_long_model else False,
                'detalles': f"Copia de [{articulo_origen.cl_long_model or 'Sin codigo'}] {articulo_origen.cl_long_model}",
                'mensaje': f"Copia de [{articulo_origen.default_code or 'Sin codigo'}] {articulo_origen.name}",
            }
            
            componentes = self.ficha_tecnica_id.componente_ids.sorted(key=lambda r: r.id)
            vals['componentes_count'] = len(componentes)
            
            for i in range(1, min(6, len(componentes) + 1)): 
                comp = componentes[i-1]
                vals.update({
                    f'componente{i}_id': comp.id,
                    f'componente{i}_name': comp.name,
                    f'componente{i}_descripcion': comp.descripcion,
                    f'componente{i}_umedida': comp.umedida,
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
                'mensaje': 'Componentes cargados correctamente',
                'detalles': f"Se cargaron {len(componentes)} componentes desde la ficha tecnica",
            })
            vals.update(result)
            
        except Exception as e:
            result.update({
                'mensaje': 'Error',
                'detalles': str(e)
            })
            vals.update(result)
            raise ValidationError(f"Error: {str(e)}")
        
        self.write(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }