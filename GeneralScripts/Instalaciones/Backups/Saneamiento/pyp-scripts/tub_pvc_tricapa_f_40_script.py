"""Tub PVC Tricapa fecal Ø40 con anillo y flecha."""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData


# Requisito del usuario: siempre incluir esta función.
def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    """Checks if the Allplan version is compatible with the building element.

    Returns:
        bool: Always returns True, indicating compatibility.
    """
    return True


# Misma capa que tubos tricapa con flecha / saneamiento fabricado (no KN_AIGUA).
LAYER_IS_CON_SANE_FAB = 40148
FLECHA_COLOR = 27
FLECHA_FACTOR_LARGO = 0.7
FLECHA_OFFSET_Z = 0.0
FLECHA_DIST_ANILLO = 20.0


def _build_tube(largo: float) -> AllplanGeo.BRep3D:
    """Construye el tubo Ø40 con anillo."""
    diametro = 40.0
    sobresale_anillo = 6.0
    largo_anillo = 40.0
    diam_anillo = diametro + 2 * sobresale_anillo
    largo_tubo = max(largo - largo_anillo, 0.0)
    eje_x = AllplanGeo.Vector3D(1, 0, 0)
    eje_z = AllplanGeo.Vector3D(0, 0, 1)
    placement = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0), eje_x, eje_z)
    tubo = AllplanGeo.BRep3D.CreateCuboid(placement, diametro, diametro, largo_tubo)
    p_anillo = AllplanGeo.Point3D(-sobresale_anillo, -sobresale_anillo, largo_tubo)
    place_an = AllplanGeo.AxisPlacement3D(p_anillo, eje_x, eje_z)
    anillo = AllplanGeo.BRep3D.CreateCuboid(place_an, diam_anillo, diam_anillo, largo_anillo)
    err, brep = AllplanGeo.MakeUnion(tubo, anillo)
    if err != 0 or not brep.IsValid():
        raise RuntimeError(f"MakeUnion falló (err={err})")
    return brep


def _build_arrow(largo: float) -> AllplanGeo.BRep3D:
    """Construye la flecha direccional superior como sólido (BRep)."""
    diametro = 40.0
    flecha_largo = diametro * FLECHA_FACTOR_LARGO
    z_flecha = diametro * 1.0 + FLECHA_OFFSET_Z
    largo_anillo = 40.0
    largo_tubo = max(largo - largo_anillo, 0.0)

    # Anillo al inicio para saneamiento actual: la flecha apunta hacia el inicio.
    base_x = max(largo_tubo - flecha_largo - FLECHA_DIST_ANILLO, 0.0)
    sentido = -1.0
    y_centro, y_span = diametro * 0.5, diametro * 0.15
    punta_x = base_x + sentido * flecha_largo

    puntos = [
        AllplanGeo.Point3D(base_x, y_centro - y_span, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span * 2, z_flecha),
        AllplanGeo.Point3D(punta_x, y_centro, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span * 2, z_flecha),
        AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span, z_flecha),
        AllplanGeo.Point3D(base_x, y_centro + y_span, z_flecha),
        AllplanGeo.Point3D(base_x, y_centro - y_span, z_flecha),
    ]
    polygon = AllplanGeo.Polygon3D(puntos)
    area = AllplanGeo.PolygonalArea3D()
    area += polygon
    extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
    # Espesor pequeño para que se comporte como sólido transformable.
    extruded_solid.SetDirection(AllplanGeo.Vector3D(0.0, 0.0, 1.0))
    extruded_solid.SetExtrudedArea(area)
    err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
    if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
        raise RuntimeError("CreatePolyhedron flecha falló")
    err, flecha_brep = AllplanGeo.CreateBRep3D(polyhedron)
    if err != AllplanGeo.eGeometryErrorCode.eOK or flecha_brep is None:
        raise RuntimeError("CreateBRep3D flecha falló")
    return flecha_brep

def _create_element(
    tipo_tubo: int,
    doc: AllplanElementAdapter.DocumentAdapter | None,
    largo_total_mm: float | None = None,
) -> CreateElementResult:
    """Crea solo el conjunto fecal Ø40 (1ML/3ML) con flecha."""
    largo = 3000.0 if int(tipo_tubo) == 3 else 1000.0
    if largo_total_mm is not None:
        largo = max(float(largo_total_mm), 41.0)

    brep = _build_tube(largo)
    flecha_brep = _build_arrow(largo)
    z_flecha = 40.0 + FLECHA_OFFSET_Z

    eje_x = AllplanGeo.Axis3D(
        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0)
    )
    rotated = AllplanGeo.Rotate(brep, eje_x, AllplanGeo.Angle(math.radians(180)))
    if isinstance(rotated, tuple):
        err, brep_rot = rotated
        if err != 0 or not brep_rot.IsValid():
            raise RuntimeError(f"Rotate falló (err={err})")
        brep = brep_rot
    else:
        if hasattr(rotated, "IsValid") and not rotated.IsValid():
            raise RuntimeError("Rotate falló: brep no válido")
        brep = rotated

    rot_matrix = AllplanGeo.Matrix3D()
    rot_matrix.SetRotation(
        AllplanGeo.Line3D(0, 0, z_flecha, 1, 0, z_flecha),
        AllplanGeo.Angle(math.radians(180)),
    )
    flecha_brep = AllplanGeo.Transform(flecha_brep, rot_matrix)
    # Recentrar la flecha en origen local para que el ajuste manual XYZ sea intuitivo.
    err_v, verts = flecha_brep.GetVertices()
    if err_v == 0 and verts:
        cx = sum(v.X for v in verts) / len(verts)
        cy = sum(v.Y for v in verts) / len(verts)
        cz = sum(v.Z for v in verts) / len(verts)
        flecha_brep = AllplanGeo.Move(flecha_brep, AllplanGeo.Vector3D(-cx, -cy, -cz))
    # Posicionamiento de flecha solo por distancia al anillo (FLECHA_DIST_ANILLO).
    largo_tubo = max(largo - 40.0, 0.0)
    base_x = max(largo_tubo - (40.0 * FLECHA_FACTOR_LARGO) - FLECHA_DIST_ANILLO, 0.0)
    x_pos = base_x - (largo_tubo * 0.5)
    mat_trasl_flecha = AllplanGeo.Matrix3D()
    mat_trasl_flecha.SetTranslation(
        AllplanGeo.Vector3D(
            x_pos,
            0.0,
            0.0,
        )
    )
    flecha_brep = AllplanGeo.Transform(flecha_brep, mat_trasl_flecha)

    elementos = []
    for i in range(3):
        props_copia = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        props_copia.Color = 66 if i == 0 else 7
        props_copia.ColorByLayer = False
        if i == 0:
            props_copia.Layer = LAYER_IS_CON_SANE_FAB
        elif i == 1:
            props_copia.Layer = 40055
        else:
            props_copia.Layer = 40054

        model_elem = AllplanBasisElements.ModelElement3D(props_copia, brep)
        if i == 0:
            attr_list = []
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-40"))
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1899, "1600"))
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))

            if int(tipo_tubo) == 3 and doc:
                _add_user_attributes_40mm_3ml(attr_list, doc)
            elif doc:
                _add_user_attributes_40mm_1ml(attr_list, doc)

            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            attributes = AllplanBaseElements.Attributes([attr_set])
            model_elem.SetAttributes(attributes)
        elif i == 2 and doc:
            attr_list = []
            try:
                attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(
                    doc, "Material"
                )
                if attr_material_id and attr_material_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT")
                    )
                if attr_list:
                    attr_set = AllplanBaseElements.AttributeSet(attr_list)
                    attributes = AllplanBaseElements.Attributes([attr_set])
                    model_elem.SetAttributes(attributes)
            except Exception as e:
                print(
                    f"[Tub_PVC_Tricapa_005] Advertencia al agregar Material a copia: {e}"
                )

        elementos.append(model_elem)

    flecha_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    flecha_props.Color = FLECHA_COLOR
    flecha_props.ColorByLayer = False
    flecha_props.Layer = LAYER_IS_CON_SANE_FAB
    elementos.append(AllplanBasisElements.ModelElement3D(flecha_props, flecha_brep))
    return CreateElementResult(elementos)

def _add_user_attributes_40mm_1ml(attr_list, doc):
    """Agrega atributos de usuario para tubo de 40mm 1ML (original)."""
    try:
        # Obtener IDs de atributos por nombre
        attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "6_CC_IS")
        attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_CARTICULO")
        attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_nom")
        attr_pmp_area_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_area")
        attr_pmp_densitat_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_densitat")
        attr_pmp_densitat_lineal_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_densitat_lineal")
        attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_diametre")
        attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_seccio")

        # 6_CC_IS: "IS"
        if attr_6_cc_is_id and attr_6_cc_is_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

        # pmp_CARTICULO: "KN07_005_001"
        if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_005_001"))

        # pmp_nom: "TS-40"
        if attr_pmp_nom_id and attr_pmp_nom_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "TS-40"))

        # pmp_area: 1600.000000 (AttributeDouble)
        if attr_pmp_area_id and attr_pmp_area_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_area_id, 1600.000000))

        # pmp_densitat: 0.0000 (AttributeDouble)
        if attr_pmp_densitat_id and attr_pmp_densitat_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_id, 0.0000))

        # pmp_densitat_lineal: 0.2900 (AttributeDouble)
        if attr_pmp_densitat_lineal_id and attr_pmp_densitat_lineal_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_lineal_id, 0.2900))

        # pmp_diametre: 40 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_diametre_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

        # pmp_seccio: 40 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_seccio_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

    except Exception as e:
        # No bloquear la creación si hay problemas con los atributos
        print(f"[Tub_PVC_Tricapa_005] Advertencia al agregar atributos de usuario 40mm 1ML: {e}")

def _add_user_attributes_40mm_3ml(attr_list, doc):
    """Agrega atributos de usuario para tubo de 40mm 3ML (original)."""
    try:
        # Obtener IDs de atributos por nombre
        attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "6_CC_IS")
        attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_CARTICULO")
        attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_nom")
        attr_pmp_area_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_area")
        attr_pmp_densitat_lineal_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_densitat_lineal")
        attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_diametre")
        attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_seccio")

        # 6_CC_IS: "IS"
        if attr_6_cc_is_id and attr_6_cc_is_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

        # pmp_CARTICULO: "KN07_005_002"
        if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_005_002"))

        # pmp_nom: "TS-40"
        if attr_pmp_nom_id and attr_pmp_nom_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "TS-40"))

        # pmp_area: 1600.000000 (AttributeDouble)
        if attr_pmp_area_id and attr_pmp_area_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_area_id, 1600.000000))

        # pmp_densitat_lineal: 0.2900 (AttributeDouble)
        if attr_pmp_densitat_lineal_id and attr_pmp_densitat_lineal_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_lineal_id, 0.2900))

        # pmp_diametre: 40 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_diametre_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

        # pmp_seccio: 40 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_seccio_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

    except Exception as e:
        # No bloquear la creación si hay problemas con los atributos
        print(f"[Tub_PVC_Tricapa_005] Advertencia al agregar atributos de usuario 40mm 3ML: {e}")


# --- Clase Principal del PythonPart ---
class TubPvcTricapaF40Script(BaseScriptObject):
    """PythonPart: tubo PVC tricapa fecal Ø40 (1ML/3ML)."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """Ejecuta la creación del tubo PVC Tricapa."""
        tipo_tubo_raw = kwargs.get("TipoTubo", args[0] if args else 0)
        try:
            tipo_tubo = int(tipo_tubo_raw.value)
        except (AttributeError, TypeError):
            tipo_tubo = int(tipo_tubo_raw)
        lt = kwargs.get("LargoTramoMm")
        largo_total = None
        if lt is not None:
            try:
                largo_total = float(lt.value) if hasattr(lt, "value") else float(lt)
            except (TypeError, ValueError):
                largo_total = None
        return _create_element(tipo_tubo, self.doc, largo_total_mm=largo_total)
