import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList

class TubeBuildingElement(BuildingElement):
    def __init__(self, *args):
        super().__init__(*args)
        self.AddAttribute("Saneamiento", 0)   # 0 = Pluvial, 1 = Fecal/Desagüe
        self.AddAttribute("Diametro", 110)    # Default 110 mm
        self.AddAttribute("Altura", 500.0)    # mm (coincidir con XML)
        self.AddAttribute("Pen", 1)
        self.AddAttribute("Stroke", 1)
        self.AddAttribute("Layer", 1)

def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    return True

def create_element(build_ele: BuildingElement, _doc: AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    # Obtener propiedades comunes (no clonar)
    common_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()

    # Leer tipo de saneamiento
    saneamiento_attr = getattr(build_ele, "Saneamiento", None)
    saneamiento = saneamiento_attr.value if hasattr(saneamiento_attr, "value") else 0

    # Determinar diámetro y color
    if saneamiento == 0:  # Pluvial
        diametro = 110
        color = 7  # Azul
    else:  # Fecal/Desagüe
        diam_attr = getattr(build_ele, "Diametro", None)
        diametro = diam_attr.value if hasattr(diam_attr, "value") else 110
        if diametro is None:
            diametro = 110

        if diametro == 25:
            color = 65  # Verde muy claro
        elif diametro == 40:
            color = 70  # Verde medio
        elif diametro == 110:
            color = 76  # Verde oscuro
        else:
            color = 4  # Verde por defecto

    common_props.Color = color

    # Leer y asignar atributos comunes
    for attr in ["Pen", "Stroke", "Layer"]:
        val = getattr(build_ele, attr, None)
        if hasattr(val, "value"):
            setattr(common_props, attr, val.value)

    # Leer altura del tubo
    height_attr = getattr(build_ele, "Altura", None)
    height = height_attr.value if hasattr(height_attr, "value") else 500.0

    base = diametro
    base_interna = max(base - 6.0, 1.0)
    radio_exterior = base / 2.0
    radio_interior = base_interna / 2.0

    # Definir placement para tubo horizontal en eje X
    placement = AllplanGeo.AxisPlacement3D(
        AllplanGeo.Point3D(0, 0, 0),              # Origen
        AllplanGeo.Vector3D(1, 0, 0),             # Dirección horizontal (X)
        AllplanGeo.Vector3D(0, 0, 1)              # Z local hacia arriba
    )

    # Desplazar el cilindro interno para que atraviese y quede hueco abierto
    placement_interno = AllplanGeo.AxisPlacement3D(
        AllplanGeo.Point3D(-2.5, 0, 0),
        AllplanGeo.Vector3D(1, 0, 0),
        AllplanGeo.Vector3D(0, 0, 1)
    )

    # Crear cilindros y restar para tubo hueco
    cilindro_externo = AllplanGeo.BRep3D.CreateCylinder(placement, radio_exterior, height)
    cilindro_interno = AllplanGeo.BRep3D.CreateCylinder(placement_interno, radio_interior, height + 5.0)

    err, tubo_hueco = AllplanGeo.MakeSubtraction(cilindro_externo, cilindro_interno)
    if err or not tubo_hueco.IsValid:
        return CreateElementResult([AllplanBasisElements.ModelElement3D(common_props, cilindro_externo)])

    # --- Añadir flecha de dirección como polilínea 3D con grosor ---
    flecha_largo = height * 0.15
    flecha_ancho = base * 0.08
    flecha_y = base + 8  # Sobre el tubo

    centro_x = height * 0.7  # Posición hacia el final del tubo
    centro_z = base * 0.5   # Centrado respecto al tubo

    # Crear puntos para la flecha como polilínea
    puntos_flecha = [
        # Línea principal del cuerpo de la flecha
        AllplanGeo.Point3D(centro_x - flecha_largo*0.6, flecha_y, centro_z),
        AllplanGeo.Point3D(centro_x, flecha_y, centro_z),

        # Punta de la flecha (líneas diagonales)
        AllplanGeo.Point3D(centro_x - flecha_ancho*0.5, flecha_y, centro_z - flecha_ancho*0.7),
        AllplanGeo.Point3D(centro_x, flecha_y, centro_z),
        AllplanGeo.Point3D(centro_x - flecha_ancho*0.5, flecha_y, centro_z + flecha_ancho*0.7)
    ]

    # Crear polilínea 3D
    polyline_flecha = AllplanGeo.Polyline3D(puntos_flecha)

    # Crear un grupo geométrico que contenga el tubo
    grupo_geometrias = AllplanGeo.BRep3DList()
    grupo_geometrias.append(tubo_hueco)

    # Unir geometrías del tubo
    err, geometria_tubo = AllplanGeo.MakeUnion(grupo_geometrias)
    if err != 0 or not geometria_tubo.IsValid():
        geometria_tubo = tubo_hueco

    # Crear la flecha como un sólido delgado (BRep3D)
    # Usar los mismos puntos que la superficie, pero extruirlos para darles espesor
    puntos_superficie_flecha = [
        AllplanGeo.Point3D(centro_x - flecha_largo*0.6, flecha_y, centro_z - flecha_ancho*0.15),
        AllplanGeo.Point3D(centro_x - flecha_largo*0.1, flecha_y, centro_z - flecha_ancho*0.15),
        AllplanGeo.Point3D(centro_x - flecha_largo*0.1, flecha_y, centro_z - flecha_ancho*0.4),
        AllplanGeo.Point3D(centro_x + flecha_largo*0.3, flecha_y, centro_z),
        AllplanGeo.Point3D(centro_x - flecha_largo*0.1, flecha_y, centro_z + flecha_ancho*0.4),
        AllplanGeo.Point3D(centro_x - flecha_largo*0.1, flecha_y, centro_z + flecha_ancho*0.15),
        AllplanGeo.Point3D(centro_x - flecha_largo*0.6, flecha_y, centro_z + flecha_ancho*0.15),
        AllplanGeo.Point3D(centro_x - flecha_largo*0.6, flecha_y, centro_z - flecha_ancho*0.15)
    ]

    # Crear superficie base de la flecha
    superficie_flecha = AllplanGeo.Polygon3D(puntos_superficie_flecha)
    print(f"DEBUG: Superficie flecha creada: {superficie_flecha}")

    # Extruir la superficie para crear un sólido delgado (BRep3D)
    # Crear trayectoria de extrusión como Polyline3D
    start_pt = puntos_superficie_flecha[0]
    end_pt = AllplanGeo.Point3D(start_pt.X, start_pt.Y + 0.5, start_pt.Z)
    path = AllplanGeo.Polyline3D([start_pt, end_pt])
    err, flecha_solid = AllplanGeo.CreateSweptBRep3D(superficie_flecha, path, False)
    if err != 0 or not flecha_solid.IsValid():
        print("ERROR: No se pudo crear el sólido de la flecha, se omite la flecha.")
        # Devolver solo el tubo
        return CreateElementResult([AllplanBasisElements.ModelElement3D(common_props, geometria_tubo)])

    # Agrupar tubo y flecha como sólidos
    grupo_geometrias = AllplanGeo.BRep3DList()
    grupo_geometrias.append(geometria_tubo)
    grupo_geometrias.append(flecha_solid)
    err, geometria_unida = AllplanGeo.MakeUnion(grupo_geometrias)
    if err != 0 or not geometria_unida.IsValid():
        print("ERROR: No se pudo unir tubo y flecha, se devuelve solo el tubo.")
        geometria_unida = geometria_tubo

    # Crear un solo ModelElement3D con la geometría unida
    props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    props.Color = color  # Color del tubo
    for attr in ["Pen", "Stroke", "Layer"]:
        val = getattr(build_ele, attr, None)
        if hasattr(val, "value"):
            setattr(props, attr, val.value)

    elemento_final = AllplanBasisElements.ModelElement3D(props, geometria_unida)
    print(f"DEBUG: ModelElement3D único creado con tubo y flecha unidos: {elemento_final}")

    return CreateElementResult([elemento_final])
