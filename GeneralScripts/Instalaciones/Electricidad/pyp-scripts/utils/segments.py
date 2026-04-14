from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum


class ConditionType(Enum):
    """Tipos de condiciones para inserción de elementos"""

    SAME_ANGLE = "same_angle"  # Mismo ángulo (manguitos)
    ANGLE_CHANGE = "angle_change"  # Cambio de ángulo específico (codos)
    ANGLE_RANGE = "angle_range"  # Rango específico de ángulos
    CUSTOM = "custom"  # Función personalizada


class InsertPosition(Enum):
    """Posición de inserción respecto al punto de evaluación"""

    BETWEEN = "between"  # Entre dos segmentos
    BEFORE = "before"  # Antes del elemento que dispara
    AFTER = "after"  # Después del elemento que dispara
    WRAP = "wrap"  # Envuelve (antes y después)
    INCIAL = "inicial"
    FINAL = "final"
    MIDDLE = "middle"
    VERTEX = "vertex"


@dataclass
class ElementConfig:
    """Configuración para un tipo de elemento a insertar"""

    element_3d: Any  # El modelo 3D del elemento
    condition_type: str  # Tipo de condición
    insert_position: str  # Dónde insertar
    name_prefix: str  # Prefijo para el nombre

    # Parámetros específicos según el tipo de condición
    angle_tolerance: float = 1.0  # Tolerancia en grados
    target_angle: Optional[float] = None  # Ángulo objetivo (para ANGLE_CHANGE)
    angle_range: Optional[tuple] = None  # (min, max) para ANGLE_RANGE
    custom_condition: Optional[Callable] = None  # Función personalizada

    # Para elementos tipo WRAP (ej: conexión + codo + conexión)
    wrap_elements: Optional[List[Any]] = (
        None  # [elemento_antes, elemento_central, elemento_después]
    )

    # Metadatos adicionales
    metadata: Dict = field(default_factory=dict)

class DynamicSegmentBuilder:
    def __init__(self):
        self.configurations: List[ElementConfig] = []

    def add_configuration(self, config: ElementConfig):
        self.configurations.append(config)
        return self

    def _check_same_angle(self, seg1, seg2, tolerance: float) -> bool:
        """
        Verifica si dos segmentos son colineales (tienen la misma dirección).
        Compara los ángulos XY y Z dentro de un margen de tolerancia.
        """
        # Extraer ángulos
        ang1_xy = seg1.data.angulo_xy
        ang2_xy = seg2.data.angulo_xy
        ang1_z  = seg1.data.angulo_z
        ang2_z  = seg2.data.angulo_z

        # 1. Diferencia en el plano horizontal (XY)
        # Usamos módulo 360 para que 359° y 1° se reconozcan como cercanos
        diff_xy = abs((ang1_xy - ang2_xy + 180) % 360 - 180)

        # 2. Diferencia en inclinación vertical (Z)
        diff_z = abs(ang1_z - ang2_z)

        # Son el mismo ángulo si ambas diferencias están bajo la tolerancia
        return diff_xy <= tolerance and diff_z <= tolerance

    def _check_is_perpendicular(self, seg1, seg2, tolerance: float) -> bool:
        """
        Verifica si dos segmentos son perpendiculares (forman ~90 grados).
        Analiza la relación en el plano horizontal (XY) y vertical (Z).
        """
        # Extraer ángulos
        ang1_xy = seg1.data.angulo_xy
        ang2_xy = seg2.data.angulo_xy
        ang1_z  = seg1.data.angulo_z
        ang2_z  = seg2.data.angulo_z

        # 1. Diferencia en el plano horizontal (XY)
        # Calculamos la diferencia absoluta circular
        diff_xy = abs((ang1_xy - ang2_xy + 180) % 360 - 180)

        # Comprobamos si la diferencia es de 90° (o 270°)
        is_perp_xy = abs(diff_xy - 90) <= tolerance

        # 2. Diferencia en inclinación vertical (Z)
        # Para que sean perpendiculares en 3D, si uno es horizontal y el otro vertical,
        # la diferencia de sus ángulos Z debería ser de 90°.
        diff_z = abs(ang1_z - ang2_z)
        is_perp_z = abs(diff_z - 90) <= tolerance

        # 3. Lógica de combinación
        # Dos segmentos son perpendiculares si:
        # Caso A: Son perpendiculares en el plano horizontal (y mantienen misma inclinación Z)
        # Caso B: Uno es vertical respecto al otro (diferencia de 90 en Z)

        case_horizontal_perp = is_perp_xy and (abs(ang1_z - ang2_z) <= tolerance)
        case_vertical_perp = is_perp_z

        return case_horizontal_perp or case_vertical_perp

    def _evaluate_condition(self, config: ElementConfig, seg_actual, seg_siguiente) -> bool:
        """Evaluación simplificada de condiciones entre segmentos"""
        try:
            # Reutiliza tus funciones de _check_same_angle o _check_angle_change
            if config.condition_type == ConditionType.SAME_ANGLE.value:
                return self._check_same_angle(seg_actual, seg_siguiente, config.angle_tolerance)
            elif config.condition_type == ConditionType.ANGLE_CHANGE.value:
                return self._check_is_perpendicular(seg_actual, seg_siguiente, config.angle_tolerance)
            elif config.condition_type == ConditionType.CUSTOM.value:
                return True
        except:
            return False
        return False

    def create_segment_group(self, segments: list, conducto_3d, element_type: str | None) -> List[Dict]:
        """
        Crea la lista de elementos colocando conexiones en las uniones
        SIN modificar la geometría de los segmentos originales.
        """
        resultado_final = []
        elemento_inicial = None
        elemento_final = None

        # Flags de control
        elemento_inicial = None  # Solo un elemento al inicio
        elemento_final = None    # Solo un elemento al final

        # Flags para insertar solo una vez
        inicial_insertado = False
        final_insertado = False

        i = 0
        for i in range(len(segments)):
            seg_actual = segments[i]

            # 1. AGREGAR CONDUCTO (Mantiene su longitud original)
            resultado_final.append({
                "type": element_type,
                "element3d": conducto_3d,
                "segment": seg_actual,
                # Índice del tubo en la polilínea (0..n-1); coincide con la clave UI seg_*_elem_{N}
                "metadata": {"is_main": True, "path_segment_index": i},
            })

            # 2. EVALUAR CONEXIONES (Entre segmentos o Extremos)
            if i < len(segments) - 1:
                seg_siguiente = segments[i + 1]

                for config in self.configurations:
                    if self._evaluate_condition(config, seg_actual, seg_siguiente):

                        # CASO INICIAL: Se guarda para el principio de la lista
                        if config.insert_position == InsertPosition.INCIAL.value:
                            if not inicial_insertado:
                                    # Usar el primer segmento como referencia
                                elemento_inicial = {
                                    "type": config.name_prefix,
                                    "element3d": config.element_3d,
                                    "segment": seg_actual,
                                    "metadata": config.metadata.copy() if hasattr(config, 'metadata') else {},
                                }
                                inicial_insertado = True
                                print(f"Elemento {config.name_prefix} marcado para inserción INICIAL (UNA VEZ)")
                            else:
                                print(f"Elemento INICIAL ya insertado, se omite {config.name_prefix}")

                        # CASO FINAL: Se guarda para el final de la lista
                        elif config.insert_position == InsertPosition.FINAL.value:
                            if not final_insertado:
                                # Se actualizará al final con el último segmento
                                elemento_final = {
                                    "type": config.name_prefix,
                                    "element3d": config.element_3d,
                                    "segment": segments[-1],  # Se asignará después
                                    "metadata": config.metadata.copy() if hasattr(config, 'metadata') else {},
                                }
                                final_insertado = True
                                print(f"Elemento {config.name_prefix} marcado para inserción FINAL (UNA VEZ)")
                            else:
                                print(f"Elemento FINAL ya insertado, se omite {config.name_prefix}")

                        # CASO MANGUITO / CONEXIÓN INTERMEDIA: Se inserta en el flujo
                        elif config.insert_position == InsertPosition.MIDDLE.value:
                            _md = config.metadata.copy() if hasattr(config, 'metadata') else {}
                            _md["path_segment_index"] = i
                            resultado_final.append({
                                "type": config.name_prefix,
                                "element3d": config.element_3d,
                                "segment": seg_actual, # Usamos el fin de este segmento como posición
                                "metadata": _md,
                            })
                        # CASO CODOS
                        elif config.insert_position == InsertPosition.VERTEX.value:
                            _md = config.metadata.copy() if hasattr(config, 'metadata') else {}
                            _md["path_segment_index"] = i
                            resultado_final.append({
                                "type": config.name_prefix,
                                "element3d": config.element_3d,
                                "segment": seg_actual, # Usamos el fin de este segmento como posición
                                "metadata": _md,
                            })

                        break

        # 3. ENSAMBLAJE FINAL ORDENADO
        lista_completa = []
        if elemento_inicial:
            lista_completa.append(elemento_inicial)

        lista_completa.extend(resultado_final)

        if elemento_final:
            lista_completa.append(elemento_final)

        return lista_completa


