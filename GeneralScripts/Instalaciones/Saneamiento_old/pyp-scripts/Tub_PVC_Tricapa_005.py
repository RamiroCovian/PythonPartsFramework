"""Tub PVC Tricapa bajante"""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

# Requisito del usuario: siempre incluir esta función.
def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    """Checks if the Allplan version is compatible with the building element.

    Returns:
        bool: Always returns True, indicating compatibility.
    """
    return True

def _build_tube(largo: float, diametro: float) -> AllplanGeo.BRep3D:
    """Builds a 3D tube with an attached ring using the specified length and diameter.

    Args:
        largo (float): The length of the tube.
        diametro (float): The diameter of the tube.

    Returns:
        AllplanGeo.BRep3D: The resulting 3D solid representing the tube with the ring.

    Raises:
        RuntimeError: If the union of the tube and ring fails.
    """
    sobresale_anillo = 6.0
    largo_anillo = 40.0 if diametro == 40.0 else 60.0
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

def create_element(build_ele: BuildingElement,
                   _doc: AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Creates the 3D model element for the PVC Tricapa tube based on the building element's properties.

    Args:
        build_ele (BuildingElement): The building element containing tube parameters.

    Returns:
        CreateElementResult: The result containing the created 3D model element(s).

    Raises:
        RuntimeError: If the union of the tube and ring fails, if rotation fails, or if the resulting BRep is not valid.
    """
    props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    tipo_tubo = int(getattr(build_ele, "TipoTubo", 0).value) if hasattr(getattr(build_ele, "TipoTubo", 0), "value") else 0
    opciones = {
        0: (1000.0, 110.0),
        1: (3000.0, 110.0),
        2: (1000.0, 40.0),
        3: (3000.0, 40.0)
    }
    largo, diametro = opciones.get(tipo_tubo, (1000.0, 110.0))
    color = 7 if (tipo_tubo == 2 or (tipo_tubo == 3)) else 67
    props.Color = color
    brep = _build_tube(largo, diametro)
    if diametro == 40.0:
        eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0))
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
        # Crear copias para 40D (tipos 2 y 3)
        elementos = []
        for i in range(3):
            props_copia = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            
            # Colores: ambos tipos 2 y 3 (40mm): original color 66, copias color 7
            props_copia.Color = 66 if i == 0 else 7  # Original 66, copias 7
            props_copia.ColorByLayer = False  # No afectar el color
            
            # Asignar layers para tipos 2 y 3 (40mm 1ML y 3ML)
            if tipo_tubo == 2 or tipo_tubo == 3:
                if i == 0:
                    props_copia.Layer = 40061  # Original
                elif i == 1:
                    props_copia.Layer = 40055  # Primera copia
                elif i == 2:
                    props_copia.Layer = 40054  # Segunda copia
            
            model_elem = AllplanBasisElements.ModelElement3D(props_copia, brep)

            # Add attributes only to original (i == 0) - el original tiene los custom attributes
            if i == 0:
                attr_list = []
                attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-40"))    # Custom attribute 01
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))      # Custom attribute 02
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
                attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))       # Custom attribute 07
                attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
                attr_list.append(AllplanBaseElements.AttributeString(1898, ""))     # Custom attribute 09
                attr_list.append(AllplanBaseElements.AttributeString(1899, "1600"))         # Custom attribute 10
                attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
                attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
                attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
                attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
                attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15

                # Agregar atributos de usuario adicionales según el tipo si hay documento disponible
                if tipo_tubo == 2 and _doc:
                    _add_user_attributes_40mm_1ml(attr_list, _doc)
                elif tipo_tubo == 3 and _doc:
                    _add_user_attributes_40mm_3ml(attr_list, _doc)

                attr_set = AllplanBaseElements.AttributeSet(attr_list)
                attributes = AllplanBaseElements.Attributes([attr_set])
                model_elem.SetAttributes(attributes)
            elif i == 2 and (tipo_tubo == 2 or tipo_tubo == 3) and _doc:
                # Segunda copia (i == 2) de tipos 2 y 3: agregar Material = CAVITAT
                attr_list = []
                try:
                    attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(_doc, "Material")
                    if attr_material_id and attr_material_id > 0:
                        attr_list.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))
                    
                    if attr_list:
                        attr_set = AllplanBaseElements.AttributeSet(attr_list)
                        attributes = AllplanBaseElements.Attributes([attr_set])
                        model_elem.SetAttributes(attributes)
                except Exception as e:
                    print(f"[Tub_PVC_Tricapa_005] Advertencia al agregar Material a copia: {e}")

            elementos.append(model_elem)
        return CreateElementResult(elementos)

    # For 110mm tubes (tipos 0 and 1)
    if not hasattr(brep, "IsValid") or not brep.IsValid():
        raise RuntimeError("El BRep resultante no es válido")

    # Para tubos de 110mm (tipos 0 y 1), asignar layer 40061
    if tipo_tubo == 0 or tipo_tubo == 1:
        props.Layer = 40061  # KN_AIGUA
        props.ColorByLayer = False  # No afectar el color

    model_elem = AllplanBasisElements.ModelElement3D(props, brep)

    # Add attributes for 110mm tubes
    attr_list = []
    attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-110"))   # Custom attribute 01 (sin punto para ambos)
    attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))      # Custom attribute 02
    attr_list.append(AllplanBaseElements.AttributeString(1085, ""))          # Custom attribute 03
    attr_list.append(AllplanBaseElements.AttributeString(1086, ""))          # Custom attribute 04
    attr_list.append(AllplanBaseElements.AttributeString(1087, ""))          # Custom attribute 05
    attr_list.append(AllplanBaseElements.AttributeString(1895, ""))          # Custom attribute 06
    attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))       # Custom attribute 07
    attr_list.append(AllplanBaseElements.AttributeString(1897, ""))          # Custom attribute 08
    attr_list.append(AllplanBaseElements.AttributeString(1898, ""))     # Custom attribute 09
    attr_list.append(AllplanBaseElements.AttributeString(1899, "12100"))          # Custom attribute 10
    attr_list.append(AllplanBaseElements.AttributeString(1900, ""))          # Custom attribute 11
    attr_list.append(AllplanBaseElements.AttributeString(1901, ""))          # Custom attribute 12
    attr_list.append(AllplanBaseElements.AttributeString(1902, ""))          # Custom attribute 13
    attr_list.append(AllplanBaseElements.AttributeString(1903, ""))          # Custom attribute 14
    attr_list.append(AllplanBaseElements.AttributeString(1904, ""))          # Custom attribute 15

    # Agregar atributos de usuario adicionales para tubos de 110mm si hay documento disponible
    if (tipo_tubo == 0 or tipo_tubo == 1) and _doc:
        _add_user_attributes_110mm(attr_list, _doc, tipo_tubo)

    attr_set = AllplanBaseElements.AttributeSet(attr_list)
    attributes = AllplanBaseElements.Attributes([attr_set])
    model_elem.SetAttributes(attributes)

    return CreateElementResult([model_elem])

def _add_user_attributes_110mm(attr_list, doc, tipo_tubo):
    """Agrega atributos de usuario para tubos de 110mm según el tipo (1m o 3m)."""
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

        # pmp_CARTICULO: según tipo (tipo 0 = 1m: KN07_005_003, tipo 1 = 3m: KN07_005_004)
        if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
            carticulo_value = "KN07_005_003" if tipo_tubo == 0 else "KN07_005_004"
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, carticulo_value))

        # pmp_nom: "TS-110"
        if attr_pmp_nom_id and attr_pmp_nom_id > 0:
            attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "TS-110"))

        # pmp_area: 12100.000000 (AttributeDouble)
        if attr_pmp_area_id and attr_pmp_area_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_area_id, 12100.000000))

        # pmp_densitat_lineal: 1.4300 (AttributeDouble)
        if attr_pmp_densitat_lineal_id and attr_pmp_densitat_lineal_id > 0:
            attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_lineal_id, 1.4300))

        # pmp_diametre: 110 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 110))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "110"))

        # pmp_seccio: 110 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 110))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110"))

    except Exception as e:
        # No bloquear la creación si hay problemas con los atributos
        print(f"[Tub_PVC_Tricapa_005] Advertencia al agregar atributos de usuario 110mm: {e}")

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
                attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

        # pmp_seccio: 40 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 40))
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
                attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_diametre_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

        # pmp_seccio: 40 (AttributeInt o AttributeString según el tipo)
        if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
            try:
                attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 40))
            except:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

    except Exception as e:
        # No bloquear la creación si hay problemas con los atributos
        print(f"[Tub_PVC_Tricapa_005] Advertencia al agregar atributos de usuario 40mm 3ML: {e}")
