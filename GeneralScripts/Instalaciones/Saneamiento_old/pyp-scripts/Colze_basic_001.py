# -*- coding: utf-8 -*-
"""Codo básico 45° / 90° """

import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult


# ========= Requisito del usuario =========
def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version (se soportan todas las versiones).

    Returns:
        bool: True if the version is supported.
    """
    return True
# ========================================



class CodoBasico:
    """Constructor de codos rectangulares 45°/90° a partir de parámetros de paleta."""

    PARAMS = [
        {
            "DIAMETRO": 32.5, "ANCHO": 40.0, "LARGO_VERTICAL": 40.0, "LARGO_INCLINADA": 33.4,
            "LARGO_HORIZONTAL": 0.0, "ANG_INCL": 45.0, "USE_HORIZONTAL": False
        },
        {
            "DIAMETRO": 32.5, "DIAMETRO_INCLINADA": 38.3, "ANCHO": 40.0, "LARGO_VERTICAL": 42.2,
            "LARGO_INCLINADA": 12.0, "LARGO_HORIZONTAL": 36.8, "LARGO_INCLINADA_INTERIOR": -15.6,
            "ANG_INCL": 45.0, "USE_HORIZONTAL": True
        }
    ]
    COLOR = [24, 24]
    COLOR_COPIA = 5
    PEN = 1
    STROKE = 1
    LAYER = 40148  # IS_CON_SANE_FAB (is cone fab)

    def __init__(self, build_ele, doc=None, rot_x=0.0, rot_y=0.0, rot_z=0.0):
        self.build_ele = build_ele
        self.doc = doc
        self.tipo = self._int_value(getattr(self.build_ele, "TipoSaneamiento", None), 0)
        self.color = self.COLOR[self.tipo]
        self.pen = self.PEN
        self.stroke = self.STROKE
        self.layer = self.LAYER
        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z

    def create_result(self) -> CreateElementResult:
        """Construye el sólido según la paleta y devuelve CreateElementResult."""
        params = self.PARAMS[self.tipo]
        solids = [self._make_solid(params, i) for i in range(3)]

        # Añadir referencias imperceptibles en el centro de las dos salidas/entradas (solo una vez)
        try:
            ref_elems = self._make_outlet_reference_markers(params)
            solids.extend(ref_elems)
        except Exception:
            # No bloquear la creación si hay algún problema con las referencias
            pass
        if any(s is None for s in solids):
            print("Error al crear el codo.")
            return CreateElementResult([])
        return CreateElementResult(solids)

    def _make_solid(self, params, idx):
        params_mod = params.copy()
        if idx == 0:
            params_mod["ANCHO"] -= 7.5
        solid = self._build_elbow(params_mod)
        if solid is None:
            return None
        if self.tipo == 1:
            solid = self._apply_rotations(solid)
        props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        props.Color = self.color if idx == 0 else self.COLOR_COPIA
        props.ColorByLayer = False  # Permitir modificar el color independientemente de la layer
        props.Pen = self.pen
        props.Stroke = self.stroke
        props.Layer = self.layer

        # Crear ModelElement3D
        model_elem = AllplanBasisElements.ModelElement3D(props, solid)

        # Agregar atributos personalizados solo al primer elemento (idx == 0)
        if idx == 0:
            attr_list = []
            if self.tipo == 0:  # 45°
                attr_list.append(AllplanBaseElements.AttributeString(1083, "CS45ºØ25"))
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø25"))
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1896, "25"))
            else:  # 90°
                attr_list.append(AllplanBaseElements.AttributeString(1083, "CSØ25"))
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø25"))
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1896, "25"))

            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes(attr_list)

            # Asignar atributos
            attr_set_list = []
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            model_elem.SetAttributes(attributes)
        else:
            # Agregar atributos a las copias (idx 1 y 2)
            if self.doc:
                attr_list = []
                self._add_copy_attributes(attr_list, idx)
                
                if attr_list:
                    attr_set_list = []
                    attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                    attributes = AllplanBaseElements.Attributes(attr_set_list)
                    model_elem.SetAttributes(attributes)

        return model_elem

    def _apply_rotations(self, solid):
        for axis, angle in zip([(1,0,0), (0,1,0), (0,0,1)], [self.rot_x, self.rot_y, self.rot_z]):
            if angle != 0.0:
                mat = AllplanGeo.Matrix3D()
                mat.SetRotation(AllplanGeo.Line3D(0,0,0,*axis), AllplanGeo.Angle(math.radians(angle)))
                solid = AllplanGeo.Transform(solid, mat)
        return solid

    def _make_outlet_reference_markers(self, base_params):
        """Crea dos pequeñas líneas de referencia en el centro de cada salida del codo.
        Son casi imperceptibles (0.3 mm) pero seleccionables como puntos de referencia.
        """
        import math as _m

        # Importante: usar el ANCHO base (sin el -7.5 de la primera copia) para centrar
        # las referencias en el eje del elemento combinado (sólido + copias)
        params = dict(base_params)
        diam = params.get("DIAMETRO", 40.0)
        diam_inc = params.get("DIAMETRO_INCLINADA", diam)
        ancho_base = params.get("ANCHO", 40.0)
        l_vert = params.get("LARGO_VERTICAL", diam)
        l_h = params.get("LARGO_HORIZONTAL", 0.0)
        ang_i = _m.radians(params.get("ANG_INCL", 45.0))
        use_h = bool(params.get("USE_HORIZONTAL", False))
        l_incl_int = params.get("LARGO_INCLINADA_INTERIOR")
        l_incl = params.get("LARGO_INCLINADA")

        l_incl_ext = (l_incl_int + diam_inc) if (l_incl_int is not None) else (l_incl if l_incl is not None else diam_inc)

        # Punto A (entrada vertical) en coords base, con dirección base -Z
        pA = AllplanGeo.Point3D(ancho_base*0.5, diam*0.5, 0.0)
        dA = AllplanGeo.Point3D(0.0, 0.0, -1.0)

        # Punto B (salida): depende si hay tramo horizontal
        if use_h:
            # Base de horizontal
            dz = l_incl_ext * _m.cos(ang_i)
            dy = l_incl_ext * _m.sin(ang_i)
            base_h = AllplanGeo.Point3D(0.0, dy, l_vert + dz)
            # Centro de la cara final del tramo horizontal tras rotación -90° X y traslación base_h
            pB = AllplanGeo.Point3D(ancho_base*0.5, base_h.Y + l_h, base_h.Z - (diam*0.5))
            # Dirección eje horizontal local (+Y después de rotX -90)
            dB = AllplanGeo.Point3D(0.0, 1.0, 0.0)
        else:
            # Final de la inclinada (rotada -ang alrededor de X y trasladada +Z l_vert)
            y_ = (diam_inc*0.5) * _m.cos(ang_i) + l_incl_ext * _m.sin(ang_i)
            z_ = -(diam_inc*0.5) * _m.sin(ang_i) + l_incl_ext * _m.cos(ang_i) + l_vert
            pB = AllplanGeo.Point3D(ancho_base*0.5, y_, z_)
            # Dirección del eje de la inclinada (rotación de +Z por -ang alrededor de X)
            dB = AllplanGeo.Point3D(0.0, -_m.sin(ang_i), _m.cos(ang_i))

        # Aplicar rotación final del sólido (primero Y 90°, luego Z 225°) a puntos y direcciones
        def rot_y(pt, ang_rad):
            m = AllplanGeo.Matrix3D(); m.SetRotation(AllplanGeo.Line3D(0,0,0, 0,1,0), AllplanGeo.Angle(ang_rad))
            return AllplanGeo.Transform(pt, m)
        def rot_z(pt, ang_rad):
            m = AllplanGeo.Matrix3D(); m.SetRotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle(ang_rad))
            return AllplanGeo.Transform(pt, m)

        def rotate_dir(dir_pt, ang_y, ang_z):
            # rota un vector representado como Point3D
            p = AllplanGeo.Point3D(dir_pt.X, dir_pt.Y, dir_pt.Z)
            p = rot_y(p, ang_y)
            p = rot_z(p, ang_z)
            return p

        ang_y = _m.radians(90.0)
        ang_z = _m.radians(225.0)

        pA = rot_z(rot_y(pA, ang_y), ang_z)
        pB = rot_z(rot_y(pB, ang_y), ang_z)
        dA = rotate_dir(dA, ang_y, ang_z)
        dB = rotate_dir(dB, ang_y, ang_z)

        # Normalizar direcciones
        def norm(v):
            l = (_m.sqrt(v.X*v.X + v.Y*v.Y + v.Z*v.Z)) or 1.0
            return AllplanGeo.Point3D(v.X/l, v.Y/l, v.Z/l)
        dA = norm(dA); dB = norm(dB)

        # Construir endpoints antes de aplicar posibles rotaciones adicionales
        eps = 0.3  # mm, casi imperceptible
        def endpoints_from(p, d, half):
            a = AllplanGeo.Point3D(p.X - d.X*half, p.Y - d.Y*half, p.Z - d.Z*half)
            b = AllplanGeo.Point3D(p.X + d.X*half, p.Y + d.Y*half, p.Z + d.Z*half)
            return a, b

        aA, bA = endpoints_from(pA, dA, eps*0.5)
        aB, bB = endpoints_from(pB, dB, eps*0.5)

        # Aplicar rotaciones adicionales si el tipo 1 las usa en sólidos
        if self.tipo == 1 and any(abs(x) > 1e-9 for x in (self.rot_x, self.rot_y, self.rot_z)):
            def rot_axis(pt, axis, ang_deg):
                if abs(ang_deg) < 1e-9:
                    return pt
                m = AllplanGeo.Matrix3D()
                if axis == 'x':
                    m.SetRotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle(math.radians(ang_deg)))
                elif axis == 'y':
                    m.SetRotation(AllplanGeo.Line3D(0,0,0, 0,1,0), AllplanGeo.Angle(math.radians(ang_deg)))
                else:
                    m.SetRotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle(math.radians(ang_deg)))
                return AllplanGeo.Transform(pt, m)

            def apply_all(pt):
                pt = rot_axis(pt, 'x', self.rot_x)
                pt = rot_axis(pt, 'y', self.rot_y)
                pt = rot_axis(pt, 'z', self.rot_z)
                return pt

            aA, bA = apply_all(aA), apply_all(bA)
            aB, bB = apply_all(aB), apply_all(bB)

        lineA = AllplanGeo.Line3D(aA, bA)
        lineB = AllplanGeo.Line3D(aB, bB)

        # Propiedades discretas para no destacar
        props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        try:
            props.Pen = 1
            props.Stroke = 1
            props.Layer = self.layer  # IS_CON_SANE_FAB (is cone fab)
        except Exception:
            pass

        return [
            AllplanBasisElements.ModelElement3D(props, lineA),
            AllplanBasisElements.ModelElement3D(props, lineB)
        ]

    def _add_user_attributes(self, attr_list):
        """Agrega atributos de usuario adicionales obteniendo sus IDs por nombre."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")
            attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pare")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: según tipo (45°: KN07_001_001, 90°: KN07_001_001)
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                carticulo_value = "KN07_001_001"  # Valor de la foto
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, carticulo_value))

            # pmp_nom: según tipo (45°: CS45ºØ25, 90°: CSØ25)
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                nom_value = "CS45ºØ25" if self.tipo == 0 else "CSØ25"
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, nom_value))

            # pmp_pes_unitari: según tipo (45°: 0.0133, 90°: 0.0133) - valor de la foto
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                pes_value = 0.0133  # Valor de la foto
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, pes_value))

            # pmp_seccio: 25 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                # Intentar como int primero, si falla como string
                try:
                    attr_list.append(AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 25))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "25"))

            # pmp_pare: "IS" (mismo valor que 6_CC_IS)
            if attr_pmp_pare_id and attr_pmp_pare_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_pare_id, "IS"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_basic_001] Advertencia al agregar atributos de usuario: {e}")

    def _add_copy_attributes(self, attr_list, idx):
        """Agrega atributos a las copias según el índice.
        
        Args:
            attr_list: Lista de atributos donde agregar
            idx: Índice de la copia (1 o 2)
        """
        if not self.doc:
            return

        try:
            # Obtener ID de 6_CC_IS (siempre necesario para copias)
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # Para la primera copia (idx == 1) de tipo 45°25 o 90°25, agregar Material = CAVITAT
            if idx == 1:  # Primera copia (tanto 45° como 90°)
                attr_material_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "Material")
                if attr_material_id and attr_material_id > 0:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_material_id, "CAVITAT"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Colze_basic_001] Advertencia al agregar atributos a copia {idx}: {e}")

    @staticmethod
    def _int_value(attr, default=0) -> int:
        if attr is None:
            return default
        v = getattr(attr, "value", attr)
        try:
            return int(v)
        except Exception:
            return default

    @staticmethod
    def _make_cuboid(ax, ay, az, bx, by, bz):
        return AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(ax, ay, az),
            AllplanGeo.Point3D(bx, by, bz)
        )

    def _build_elbow(self, params: dict):
        diam = params["DIAMETRO"]
        diam_inc = params.get("DIAMETRO_INCLINADA", diam)
        ancho = params["ANCHO"]
        l_vert = params.get("LARGO_VERTICAL", diam)
        l_h = params.get("LARGO_HORIZONTAL", diam)
        ang_i = params["ANG_INCL"]
        use_h = params["USE_HORIZONTAL"]
        l_incl_int = params.get("LARGO_INCLINADA_INTERIOR")
        l_incl = params.get("LARGO_INCLINADA")

        l_incl_exterior = l_incl_int + diam_inc if l_incl_int is not None else (l_incl if l_incl is not None else diam_inc)
        seg_vert = self._make_cuboid(0, 0, 0, ancho, diam, l_vert)
        rad_i = math.radians(ang_i)
        seg_inc = self._make_cuboid(0, 0, 0, ancho, diam_inc, l_incl_exterior)
        rot_inc = AllplanGeo.Matrix3D(); rot_inc.SetRotation(AllplanGeo.Line3D(0,0,0,1,0,0), AllplanGeo.Angle(-rad_i))
        seg_inc = AllplanGeo.Transform(seg_inc, rot_inc)
        trn_inc = AllplanGeo.Matrix3D(); trn_inc.SetTranslation(AllplanGeo.Vector3D(0,0,l_vert))
        seg_inc = AllplanGeo.Transform(seg_inc, trn_inc)
        err, solid = AllplanGeo.MakeUnion(seg_vert, seg_inc)
        if err != 0 or not solid.IsValid():
            return None
        if use_h:
            dz = l_incl_exterior * math.cos(rad_i)
            dy = l_incl_exterior * math.sin(rad_i)
            base_h = AllplanGeo.Point3D(0, dy, l_vert + dz)
            seg_h = self._make_cuboid(0, 0, 0, ancho, diam, l_h)
            rot_h = AllplanGeo.Matrix3D(); rot_h.SetRotation(AllplanGeo.Line3D(0,0,0,1,0,0), AllplanGeo.Angle(-math.radians(90.0)))
            seg_h = AllplanGeo.Transform(seg_h, rot_h)
            trn_h = AllplanGeo.Matrix3D(); trn_h.SetTranslation(AllplanGeo.Vector3D(base_h.X, base_h.Y, base_h.Z))
            seg_h = AllplanGeo.Transform(seg_h, trn_h)
            err, solid = AllplanGeo.MakeUnion(solid, seg_h)
            if err != 0 or not solid.IsValid():
                return None
        r_y = AllplanGeo.Matrix3D(); r_y.SetRotation(AllplanGeo.Line3D(0,0,0,0,1,0), AllplanGeo.Angle(math.radians(90)))
        solid = AllplanGeo.Transform(solid, r_y)
        r_z = AllplanGeo.Matrix3D(); r_z.SetRotation(AllplanGeo.Line3D(0,0,0,0,0,1), AllplanGeo.Angle(math.radians(225)))
        solid = AllplanGeo.Transform(solid, r_z)
        return solid


# ====== Punto de entrada estándar de PythonPart ======
def create_element(build_ele, _doc, rot_x=0.0, rot_y=0.0, rot_z=315.0) -> CreateElementResult:
    """Instancia la clase y delega la creación del elemento. Para tipo 90°, permite rotar sobre eje x, y, z."""
    return CodoBasico(build_ele, _doc, rot_x, rot_y, rot_z).create_result()



















    forced_number = None
    current_group_id = 0  # <--- Definida al inicio para evitar UnboundLocalError

    for i, element in enumerate(elements_generated):
        element_type = element.element_type
        element_model = element.element
        seg_idx = element.index

        storage_key = f"seg_{path_idx}_elem_{seg_idx}"
        key_individual = f"seg_{path_idx}_elem_{i}"

        # --- 1. LÓGICA DE NUMERACIÓN ---
        # (Se mantiene la lógica de current_group_id que definimos antes)
        if so.init_storage:
            if so.is_individual_mode:
                # MODO INDIVIDUAL, si ya tiene número en el caché persistente, lo mantenemos
                old_attrs = so.applied_default_attributes.get(key_individual)
                existing_num = _extract_number_from_attrs(old_attrs) if old_attrs else None

                if existing_num:
                    forced_number = existing_num
                elif element_type == so.element_type_core:
                    forced_number = so.init_storage._get_next_number(so.element_type_core)
                else:
                    forced_number = None
            else:
                # MODO GRUPAL (Tu requerimiento principal)
                if element_type == so.element_type_core:
                    group_key = f"path_{path_idx}_group_{current_group_id}"

                    # PASO CRÍTICO: Intentamos recuperar el número del caché global primero
                    if group_key in so.global_group_numbers:
                        forced_number = so.global_group_numbers[group_key]
                    else:
                        # Solo si el grupo es REALMENTE nuevo (ej. tras un manguito nuevo), pedimos número
                        new_num = so.init_storage._get_next_number(so.element_type_core)
                        so.global_group_numbers[group_key] = new_num
                        forced_number = new_num
                        # Guardamos en disco inmediatamente para que otros procesos lo vean
                        so.init_storage._save_numbering_file()
                else:
                    # Es un manguito: actúa como frontera de grupo
                    forced_number = None
                    current_group_id += 1

        # --- 2. OBTENCIÓN DE ATRIBUTOS (CON FILTRO DE SEGURIDAD) ---
        base_attrs = None
        cached_attrs = so.applied_default_attributes.get(key_individual)

        # VALIDACIÓN CRÍTICA:
        # Solo usamos el caché si el atributo "TV" coincide con la naturaleza del elemento actual.
        # Si el caché tiene un "TV-X" pero el elemento actual NO es core, lo ignoramos.
        if cached_attrs:
            has_tv_attr = any(hasattr(a, "Id") and a.Id == 1083 for a in cached_attrs)
            if (element_type == so.element_type_core and has_tv_attr) or \
               (element_type != so.element_type_core and not has_tv_attr):
                base_attrs = cached_attrs

        # Si no hubo coincidencia en el caché (porque el tipo cambió), usamos los default limpios
        if not base_attrs:
            base_attrs = so.default_attributes.get(element_type, [])

        # --- 3. MEZCLA Y PROCESAMIENTO ---
        elem_attrs = so.applied_attributes.get(storage_key, [])
        # Aseguramos que merged_attrs sea una copia para no contaminar el origen
        merged_attrs = _merge_attributes(base_attrs, elem_attrs) if elem_attrs else list(base_attrs)

        # 4. PROCESAR AUTO-NUMBERING
        # Si NO es core, forzamos que forced_number sea None y que se limpie cualquier 1083 residual
        processed_attrs, _ = _process_auto_numbering(
            merged_attrs,
            inst_type=so.element_type_core,
            so=so,
            forced_number=forced_number if element_type == so.element_type_core else None
        )

        # 5. GUARDAR Y APLICAR
        element_model = _apply_attributes_to_model_elem(element_model, processed_attrs)
        so.applied_default_attributes[key_individual] = processed_attrs

        # Capas y finalización
        element_model = _apply_layer_to_element(element_model, storage_key, so) # type: ignore
        element.element = element_model
        elements_generated_final.append(element)

        # --- LÓGICA DE INSERCIÓN DE CUBOIDE ---
        # 1. Al inicio del camino (i == 0)
        # 2. O si el elemento anterior fue un manguito (current_group_id aumentó)
        is_first_in_path = (i == 0)

        # Verificamos si el elemento anterior en el bucle causó un cambio de grupo
        # (Esto implica que el elemento ACTUAL es el primero del nuevo grupo)
        is_first_after_manguito = False
        if i > 0:
            prev_element_type = elements_generated[i-1].element_type
            if prev_element_type != so.element_type_core:
                is_first_after_manguito = True

        if element_type in ["conducto_normal", "conducto_aislado"] and (is_first_in_path or is_first_after_manguito):
            model_base = so.current_inst_config
            diameter = 100
            if model_base:
                if so.diameter_list and so.diameter_type:
                    diameter = so.diameter_type
                else:
                    diameter = model_base["diameter"]
            # Índice real en saved_paths = cantidad de conductos ANTES de posición i
            # (los manguitos intercalados en data_list no consumen puntos en saved_paths)
            pt_idx = sum(1 for j in range(i)
                         if elements_generated[j].element_type in ["conducto_normal", "conducto_aislado"])

            # Creamos el cuboide con pt_idx correcto
            cuboid_model = _create_cuboide_label(diameter, pt_idx, path_idx, so, attr_list=processed_attrs)

            # Guardar attrs para la polilínea: {path_idx: {pt_idx: attrs}}
            if so._polyline_attrs is None:
                so._polyline_attrs = {}
            if path_idx not in so._polyline_attrs:
                so._polyline_attrs[path_idx] = {}
            if pt_idx not in so._polyline_attrs[path_idx]:
                so._polyline_attrs[path_idx][pt_idx] = processed_attrs
            # Lo envolvemos en el formato de diccionario esperado
            # En lugar de crear un diccionario {}, creamos una instancia de la clase
            cuboid_item = GeneratedElement(
                element=cuboid_model,
                element_type="CUBOID_LABEL",
                index=i
            )
            # Lo añadimos a la lista final
            elements_generated_final.append(cuboid_item)

    if so.init_storage:
        so.init_storage._save_numbering_file()