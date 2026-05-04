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
    LAYER = 1

    def __init__(self, build_ele, rot_x=0.0, rot_y=0.0, rot_z=0.0):
        self.build_ele = build_ele
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

            # Asignar atributos
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
        except Exception:
            pass

        return [
            AllplanBasisElements.ModelElement3D(props, lineA),
            AllplanBasisElements.ModelElement3D(props, lineB)
        ]

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
    return CodoBasico(build_ele, rot_x, rot_y, rot_z).create_result()
