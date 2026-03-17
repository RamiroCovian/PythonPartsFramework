import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_AllplanSettings as AllplanGlobalSettings
import NemAll_Python_BasisElements as AllplanBasisElements

from TypeCollections.ModelEleList import ModelEleList

from copy import deepcopy


class CreateSmartGeo:
    """
    Clase de utilidad para crear geometrías 3D mediante descripciones estructuradas.
    Soporta operaciones booleanas, repeticiones (loop) y rotaciones (rotate).
    """

    def __init__(self):
        self.model_ele_list = ModelEleList()
        self.body = None

    def _new_prop(self, color_index: int):
        """Crear propiedades nuevas sin contaminar otras piezas."""
        prop = AllplanGlobalSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color_index
        return prop

    def _create_cylinder(
        self,
        radius: float,
        height: float,
        base_point: AllplanGeometry.Point3D,
        aux_x_axis: AllplanGeometry.Vector3D = AllplanGeometry.Vector3D(1, 0, 0),
        axis_direction: AllplanGeometry.Vector3D = AllplanGeometry.Vector3D(0, 0, 1),
        rotation_angle_deg: float = 0.0,
    ) -> AllplanGeometry.BRep3D:

        axis_placement = AllplanGeometry.AxisPlacement3D(
            refPoint=base_point, xvector=aux_x_axis, zvector=axis_direction
        )
        cylinder = AllplanGeometry.BRep3D.CreateCylinder(
            placement=axis_placement, radius=radius / 2, height=height
        )

        # Aplicar rotación opcional
        if rotation_angle_deg != 0.0:
            rotation_matrix = AllplanGeometry.Matrix3D()
            eje_rotacion = AllplanGeometry.Line3D(base_point, axis_direction)
            rotation_matrix.SetRotation(
                eje_rotacion, AllplanGeometry.Angle.FromDeg(rotation_angle_deg)
            )
            cylinder = AllplanGeometry.Transform(cylinder, rotation_matrix)

        return cylinder

    def _create_cubo(
        self,
        length: float,
        width: float,
        height: float,
        base_point: AllplanGeometry.Point3D,
        aux_x_axis: AllplanGeometry.Vector3D = AllplanGeometry.Vector3D(1, 0, 0),
        axis_direction: AllplanGeometry.Vector3D = AllplanGeometry.Vector3D(0, 0, 1),
        rotation_angle_deg: float = 0.0,
    ) ->  AllplanGeometry.BRep3D:

        axis_placement = AllplanGeometry.AxisPlacement3D(
            refPoint=base_point, xvector=aux_x_axis, zvector=axis_direction
        )
        cubo = AllplanGeometry.BRep3D.CreateCuboid(
            placement=axis_placement, length=length, width=width, height=height
        )

        # Aplicar rotación opcional
        if rotation_angle_deg != 0.0:
            rotation_matrix = AllplanGeometry.Matrix3D()
            eje_rotacion = AllplanGeometry.Line3D(base_point, axis_direction)
            rotation_matrix.SetRotation(
                eje_rotacion, AllplanGeometry.Angle.FromDeg(rotation_angle_deg)
            )
            cubo = AllplanGeometry.Transform(cubo, rotation_matrix)

        return cubo

    def _apply_boolean(self, op, body, geom):
        if op == "union":
            _, result = AllplanGeometry.MakeUnion(body, geom)
        elif op == "subtract":
            _, result = AllplanGeometry.MakeSubtraction(body, geom)
        elif op == "intersect":
            _, result = AllplanGeometry.MakeIntersection(body, geom)
        else:
            raise ValueError(f"Operación desconocida: {op}")

        if result is None:
            raise RuntimeError(f"Operación {op} falló: cuerpo degenerado.")

        return result

    def _create_shape_from_desc(self, shape_desc: dict):
        """
        Crea una figura desde su descripción.
        Soporta:
        - {"type": ... }
        - {"base": {...}, "operations": [...]}
        """
        # ------------------------------------------------------------
        # CASO 1: es un shape compuesto: tiene base + operations
        # ------------------------------------------------------------
        if "base" in shape_desc:
            base_desc = shape_desc["base"]
            geom, color = self._create_base_shape(base_desc)

            # Aplicar operaciones internas
            for op in base_desc.get("operations", []):
                action = op["action"]
                shape_sub, _ = self._create_shape_from_desc(op["shape"])
                geom = self._apply_boolean(action, geom, shape_sub)

            return geom, color

        # ------------------------------------------------------------
        # CASO 2: shape simple con "type"
        # ------------------------------------------------------------
        return self._create_base_shape(shape_desc)

    def _create_base_shape(self, shape_desc: dict):
        """Crea una figura base a partir de su descripción."""
        shape_type = shape_desc["type"].lower()
        shape_point = AllplanGeometry.Point3D(*shape_desc.get("base_point", (0, 0, 0)))
        color = shape_desc.get("color", 1)

        if shape_type == "cubo":
            geom = self._create_cubo(
                shape_desc["length"],
                shape_desc["width"],
                shape_desc["height"],
                shape_point,
                aux_x_axis=shape_desc.get("x_axis", AllplanGeometry.Vector3D(1, 0, 0)),
                axis_direction=shape_desc.get("direction", AllplanGeometry.Vector3D(0, 0, 1)),
                rotation_angle_deg=shape_desc.get("rotation", 0.0),
            )
        elif shape_type == "cylinder":
            geom = self._create_cylinder(
                shape_desc["radius"],
                shape_desc["height"],
                shape_point,
                aux_x_axis=shape_desc.get("x_axis", AllplanGeometry.Vector3D(1, 0, 0)),
                axis_direction= shape_desc.get("direction", AllplanGeometry.Vector3D(0, 0, 1)),
                rotation_angle_deg=shape_desc.get("rotation", 0.0),
            )
        else:
            raise ValueError(f"Tipo de figura desconocido: {shape_type}")

        return geom, color

    # -------------------------------------------------------------------------
    # CONSTRUCCIÓN GENERAL DESDE DICT
    # -------------------------------------------------------------------------
    def build_from_description(self, description: dict) -> ModelEleList:
        """
        Construye geometrías complejas a partir de una descripción estructurada.
        Soporta múltiples bases, union, subtract, intersect, loop, rotate.
        """
        self.model_ele_list = ModelEleList()

        bases = description.get("bases", [])
        if not bases:
            bases = [{"shape": description["base"], "operations": description.get("operations", [])}]

        # =====================================================================
        #  PROCESAR CADA BASE DE FORMA INDEPENDIENTE
        # =====================================================================
        for base_entry in bases:
            # Asegurar formato uniforme
            base_desc = base_entry.get("shape", base_entry)
            operations = base_entry.get("operations", [])

            # Crear geometría base
            body, base_color = self._create_shape_from_desc(base_desc)

            # ===========================================================
            # BASE SIN OPERACIONES → agregar tal cual
            # ===========================================================
            if len(operations) == 0:
                prop = self._new_prop(base_color)
                self.model_ele_list.append(AllplanBasisElements.ModelElement3D(prop, body))
                continue

            # ===========================================================
            # BASE CON OPERACIONES → aplicar booleanas y loops
            # ===========================================================
            self.body = body  # cuerpo actual sobre el que se aplican booleanas

            for op in operations:
                action = op["action"]

                if action == "loop":
                    shape_desc = op["shape"]
                    count = op.get("count", 1)
                    step = op.get("step", (0, 0, 0))
                    mode = op.get("mode", "union")

                    for i in range(count):
                        offset = AllplanGeometry.Vector3D(step[0]*i, step[1]*i, step[2]*i)
                        shape_copy = deepcopy(shape_desc)

                        # --- 1) mover base_point en distintos lugares posibles ---
                        if "base_point" in shape_copy:
                            bp = AllplanGeometry.Point3D(*shape_copy["base_point"])
                            np = bp + offset
                            shape_copy["base_point"] = (np.X, np.Y, np.Z)

                        # Caso: shape_copy contiene "base" con su base_point
                        if "base" in shape_copy and "base_point" in shape_copy["base"]:
                            bp = AllplanGeometry.Point3D(*shape_copy["base"]["base_point"])
                            np = bp + offset
                            shape_copy["base"]["base_point"] = (np.X, np.Y, np.Z)

                        # --- 2) mover cada operación interna ---
                        inner_ops = []
                        inner_ops.extend(shape_copy.get("operations", []))
                        if "base" in shape_copy:
                            inner_ops.extend(shape_copy["base"].get("operations", []))

                        for sub_op in inner_ops:
                            shp = sub_op.get("shape", {})
                            # Si la operación es una "composite" (tiene "base") también mover su base
                            if "base_point" in shp:
                                bp = AllplanGeometry.Point3D(*shp["base_point"])
                                np = bp + offset
                                shp["base_point"] = (np.X, np.Y, np.Z)
                            if "base" in shp and "base_point" in shp["base"]:
                                bp = AllplanGeometry.Point3D(*shp["base"]["base_point"])
                                np = bp + offset
                                shp["base"]["base_point"] = (np.X, np.Y, np.Z)

                        # --- 3) generar geometría completa ---
                        shape_geom, _ = self._create_shape_from_desc(shape_copy)

                        # --- 4) boolean ---
                        self.body = self._apply_boolean(mode, self.body, shape_geom)

                    continue
                else:
                    geom, _ = self._create_shape_from_desc(op["shape"])
                    self.body = self._apply_boolean(action, self.body, geom)


            prop = self._new_prop(base_color)
            model_elem = AllplanBasisElements.ModelElement3D(prop, self.body)
            self.model_ele_list.append(model_elem)

        return self.model_ele_list
