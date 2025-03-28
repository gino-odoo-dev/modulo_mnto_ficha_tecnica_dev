# Modulo Copia Ficha Tecnica (Receta).

## Alcance del modulo

Ingreso de materiales, temporadas y modelos para la creacion de ficha tecnica.
Copia de Ficha tecnica dependiendo de temporada, disponibilidad y disponibilidad de materiales. 

## Modelos 

### `mrp.bom`
- Fields:
  - `name` (Char)
  - `temporadas_id` (Many2one)
  - `temporada_name` (Char)
  - `articulos_id` (Many2one)
  - `articulo_name` (Char)
  - `codigo_departamento` (Char)
  - `descripcion_componente` (Text)
  - `unidadmedida_componente` (Char)
  - `descripcion_departamento` (Text)
  - `cantidad_id` (Integer)
  - `costo_unitarrio_id` (Float)
  - `costo_ampliado_id` (Float)
  - `componente_id` (Many2one)
  - `departamento_id` (Many2one)
  - `factor_perdida_id` (Float)
  - `codigosecuencia_id` (Many2one)
  - `compra_manufactura_id` (Many2one)

### `copia.ficha`
- Fields:
  - `temporadas_id` (Many2one)
  - `temporada_name` (Char)
  - `nombre_receta` (Char)
  - `part_o` (Many2one)
  - `part_d` (Many2one)
  - `m_numero_color` (Boolean)
  - `copia` (Boolean)
  - `m_modelo_o` (Char)
  - `m_modelo_d` (Char)
  - `no_comb_o` (Char)
  - `no_comb_d` (Char)
  - `remplaza` (Char)
  - `mensaje` (Char)
  - `xcuero` (Char)
  - `xcolor` (Char)
  - `xplnta` (Char)
  - `xcolfo` (Char)
  - `sequence` (Integer)
_________________________________________________

### `Funciones Ficha Tecnica`

  - `name_get` ()
  - `_compute_temporada_name` ()
  - `_compute_articulo_name` ()
  - `calcular_costo_ampliado` ()
  - `_onchange_componente_id` ()
  - `next_button` ()


### `Funciones Copia Fich Tecnica`

  - `_compute_nombre_receta` ()
  - `_compute_temporada_name` ()
  - `_check_fields` ()
  - `copia_rec_dev` ()
  - `obtener_numero_combinaciones` ()
  - `_copia_numero` ()
  - `_cambia_componente` ()
  - `_crea_ficha_comp` ()
  - `_copia_color` ()
  - `_cambia_materia` ()
  - `_determinar_nuevo_componente` ()
  - `eliminar_registro` ()

_________________________________________________

### `Cuadro Comparacion "codigo progress-codigo python"`


![Cuadro Comparacion](./cuadro_comparacion.png)
