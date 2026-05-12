"""Tap reduction"""

import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult


# ===== Constantes fijas =====
DIAMETRO = 25.0           # lado del cuerpo principal (mm)
LARGO_PRINCIPAL = 30.0    # longitud del cuerpo principal (mm)
LADO_CUBOIDE_SUP = 40.0   # lado del cuboide superior (mm)
LARGO_ANILLO = 30.0       # longitud del cuboide superior (mm)
COLOR = 7                 # color del elemento

# ===== Parámetros de rotación (hardcodeados) =====
ROT_X = 0.0               # rotación en eje X (grados)
ROT_Y = 0.0               # rotación en eje Y (grados)
ROT_Z = 0.0               # rotación en eje Z (grados)

# ===== Parámetros de traslación (hardcodeados) =====
TRANS_X = -90.0             # traslación en eje X (mm)
TRANS_Y = -25.0             # traslación en eje Y (mm)
TRANS_Z = 0.0             # traslación en eje Z (mm)

def check_allplan_version(_b, _v):
    """Allplan version gate.

    Returns
    -------
    bool
        Always True; this script supports all versions provided by the host.
    """
    return True

def create_element(_be, _doc):
    """Create the main body and an upper cuboid slightly bigger and centered, without branches.

    Allows hardcoded rotation in x, y, z axes.
    """
    base = DIAMETRO
    lado_top = LADO_CUBOIDE_SUP

    # Ejes básicos
    x_dir = AllplanGeo.Vector3D(1, 0, 0)
    z_dir = AllplanGeo.Vector3D(0, 0, 1)

    # Cuerpo principal: colocado desde z=0 con longitud LARGO_PRINCIPAL
    axis_main = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0), x_dir, z_dir)
    cuerpo = AllplanGeo.BRep3D.CreateCuboid(axis_main, base, base, LARGO_PRINCIPAL)


    # Cuboide superior (lado 40 mm, centrado respecto al cuerpo principal)
    offset_xy = (lado_top - base) / 2.0
    cuboide_sup = AllplanGeo.BRep3D.CreateCuboid(
        AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(
                -offset_xy,
                -offset_xy,
                LARGO_PRINCIPAL
            ),
            x_dir,
            z_dir
        ),
        lado_top,
        lado_top,
        LARGO_ANILLO
    )

    # Cuboide adicional 50x50x60 mm centrado respecto al eje central del cuerpo principal
    cuboide_centro_largo = 60.0
    cuboide_centro_lado = 50.0
    # Centro del cuerpo principal
    centro_x = base / 2.0
    centro_y = base / 2.0
    centro_z = LARGO_PRINCIPAL / 2.0
    # Para centrar el cuboide, restamos la mitad de sus dimensiones
    origen_x = centro_x - cuboide_centro_lado / 2.0
    origen_y = centro_y - cuboide_centro_lado / 2.0
    origen_z = centro_z - cuboide_centro_largo / 2.0 + 15.0
    cuboide_centro = AllplanGeo.BRep3D.CreateCuboid(
        AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(origen_x, origen_y, origen_z),
            x_dir,
            z_dir
        ),
        cuboide_centro_lado,
        cuboide_centro_lado,
        cuboide_centro_largo
    )

    # Unión del cuerpo principal y cuboide superior
    err, brep = AllplanGeo.MakeUnion(cuerpo, cuboide_sup)
    if err != 0 or not brep.IsValid():
        print("Error al unir cuerpo y cuboide superior", err)
        return CreateElementResult()

    # Mantener el cuboide adicional como geometría separada.
    # La separación permite manipularlo de forma independiente del tap reductor.

    # Rotación sobre sí mismo (x, y, z) usando los parámetros globales
    if ROT_X != 0.0:
        rot_x_mat = AllplanGeo.Matrix3D()
        rot_x_mat.SetRotation(AllplanGeo.Line3D(0,0,0,1,0,0), AllplanGeo.Angle(math.radians(ROT_X)))
        brep = AllplanGeo.Transform(brep, rot_x_mat)
        cuboide_centro = AllplanGeo.Transform(cuboide_centro, rot_x_mat)
    if ROT_Y != 0.0:
        rot_y_mat = AllplanGeo.Matrix3D()
        rot_y_mat.SetRotation(AllplanGeo.Line3D(0,0,0,0,1,0), AllplanGeo.Angle(math.radians(ROT_Y)))
        brep = AllplanGeo.Transform(brep, rot_y_mat)
        cuboide_centro = AllplanGeo.Transform(cuboide_centro, rot_y_mat)
    if ROT_Z != 0.0:
        rot_z_mat = AllplanGeo.Matrix3D()
        rot_z_mat.SetRotation(AllplanGeo.Line3D(0,0,0,0,0,1), AllplanGeo.Angle(math.radians(ROT_Z)))
        brep = AllplanGeo.Transform(brep, rot_z_mat)
        cuboide_centro = AllplanGeo.Transform(cuboide_centro, rot_z_mat)

    # Rotación para colocar horizontal
    brep = AllplanGeo.Rotate(
        brep,
        AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0)),
        AllplanGeo.Angle(math.radians(90))
    )
    cuboide_centro = AllplanGeo.Rotate(
        cuboide_centro,
        AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(0, 1, 0)),
        AllplanGeo.Angle(math.radians(90))
    )

    # Traslación global para ajustar posicionamiento del conjunto completo
    if abs(TRANS_X) > 1e-9 or abs(TRANS_Y) > 1e-9 or abs(TRANS_Z) > 1e-9:
        trans_mat = AllplanGeo.Matrix3D()
        trans_mat.SetTranslation(AllplanGeo.Vector3D(TRANS_X, TRANS_Y, TRANS_Z))
        brep = AllplanGeo.Transform(brep, trans_mat)
        cuboide_centro = AllplanGeo.Transform(cuboide_centro, trans_mat)

    props_main = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    props_main.Color = 50
    props_main.ColorByLayer = False  # No afectar el color
    props_main.Layer = 40061  # KN_AIGUA
    
    props_copia1 = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    props_copia1.Color = COLOR
    props_copia1.ColorByLayer = False  # No afectar el color
    props_copia1.Layer = 40055  # Primera copia
    
    props_copia2 = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    props_copia2.Color = COLOR
    props_copia2.ColorByLayer = False  # No afectar el color
    props_copia2.Layer = 40054  # Segunda copia

    # Create model element with attributes for the main brep (color 50)
    model_elem_main = AllplanBasisElements.ModelElement3D(props_main, brep)

    # Add attributes to main element (RED.Ø40-25)
    attr_list = []
    attr_list.append(AllplanBaseElements.AttributeString(1083, "RED.Ø40-25"))  # Custom attribute 01
    attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40-25"))     # Custom attribute 02
    attr_list.append(AllplanBaseElements.AttributeString(1085, ""))           # Custom attribute 03
    attr_list.append(AllplanBaseElements.AttributeString(1086, ""))           # Custom attribute 04
    attr_list.append(AllplanBaseElements.AttributeString(1087, ""))           # Custom attribute 05
    attr_list.append(AllplanBaseElements.AttributeString(1895, ""))           # Custom attribute 06
    attr_list.append(AllplanBaseElements.AttributeString(1896, "40-25"))      # Custom attribute 07
    attr_list.append(AllplanBaseElements.AttributeString(1897, ""))           # Custom attribute 08
    attr_list.append(AllplanBaseElements.AttributeString(1898, ""))           # Custom attribute 09
    attr_list.append(AllplanBaseElements.AttributeString(1899, ""))           # Custom attribute 10
    attr_list.append(AllplanBaseElements.AttributeString(1900, ""))           # Custom attribute 11
    attr_list.append(AllplanBaseElements.AttributeString(1901, ""))           # Custom attribute 12
    attr_list.append(AllplanBaseElements.AttributeString(1902, ""))           # Custom attribute 13
    attr_list.append(AllplanBaseElements.AttributeString(1903, ""))           # Custom attribute 14
    attr_list.append(AllplanBaseElements.AttributeString(1904, ""))           # Custom attribute 15

    # Agregar atributos de usuario adicionales si hay documento disponible
    if _doc:
        _add_user_attributes_reduction(attr_list, _doc)

    attr_set = AllplanBaseElements.AttributeSet(attr_list)
    attributes = AllplanBaseElements.Attributes([attr_set])
    model_elem_main.SetAttributes(attributes)

    # Segunda copia del cuboide central
    cuboide_centro_copia = cuboide_centro.Clone() if hasattr(cuboide_centro, 'Clone') else cuboide_centro
    
    # Crear elementos de copias
    model_elem_copia1 = AllplanBasisElements.ModelElement3D(props_copia1, cuboide_centro)
    
    # Segunda copia con Material = CAVITAT
    model_elem_copia2 = AllplanBasisElements.ModelElement3D(props_copia2, cuboide_centro_copia)
    if _doc:
        attr_list_copia2 = []
        try:
            attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(_doc, "Material")
            if attr_material_id and attr_material_id > 0:
                attr_list_copia2.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))
            
            if attr_list_copia2:
                attr_set_copia2 = AllplanBaseElements.AttributeSet(attr_list_copia2)
                attributes_copia2 = AllplanBaseElements.Attributes([attr_set_copia2])
                model_elem_copia2.SetAttributes(attributes_copia2)
        except Exception as e:
            print(f"[Tapreduction_010] Advertencia al agregar Material a copia: {e}")
    
    return CreateElementResult([
        model_elem_main,
        model_elem_copia1,
        model_elem_copia2
    ])

def _add_user_attributes_reduction(attr_list, doc):
    """Agrega atributos de usuario para el reductor (original)."""
    try:
        # Obtener IDs de atributos por nombre
        attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_CARTICULO")
        attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_diametre")
        attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_nom")
        attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_seccio")

        # pmp_CARTICULO: "KN07_0010_001"
        if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_0010_001"))

        # pmp_diametre: "Ø40-25"
        if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "Ø40-25"))

        # pmp_nom: "RED.Ø40-25"
        if attr_pmp_nom_id and attr_pmp_nom_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "RED.Ø40-25"))

        # pmp_seccio: "40-25"
        if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40-25"))

    except Exception as e:
        # No bloquear la creación si hay problemas con los atributos
        print(f"[Tapreduction_010] Advertencia al agregar atributos de usuario: {e}")

__all__ = []
