"""
TØ20|TØ25|TØ32|TØ25-20-25|TØ25-20-20|TØ25-25-20
"""

import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = [
    # TØ20
    {
        # Outer
        "ARM_LEN_X": 110.0,
        "ARM_LEN_Y": 40.0,
        "HEIGHT": 40.0,
        "COLOR": 5,
        "SMALL_ARM_X": 40.0,
        "SMALL_ARM_Y": 35.0,
        # Inner
        "INNER_ARM_X": 54.0,
        "INNER_ARM_Y": 30.0,
        "INNER_HEIGHT": 30.0,
        "INNER_COLOR": 122,
        "SMALL_INNER_ARM_X": 30.0,
        "SMALL_INNER_ARM_Y": 12.0,
        # Caps
        "TOP_CAP_ARM_X": 23.0,
        "TOP_CAP_ARM_Y": 30.0,
        "TOP_CAP_HEIGHT": 31.0,
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 30.0,
        "LEFT_CAP_HEIGHT": 31.0,
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 30.0,
        "RIGHT_CAP_HEIGHT": 31.0,
        # Dif Outer/Inner
        "SPACE": 5.0,
    },
    # TØ25
    {
        # Outer
        "ARM_LEN_X": 155.0,
        "ARM_LEN_Y": 75.0,
        "THICKNESS": 75.0,
        "HEIGHT": 75.0,
        "COLOR": 128,
        "SMALL_ARM_X": 75.0,
        "SMALL_ARM_Y": 40.0,
        # Inner
        "INNER_ARM_X": 69.0,
        "INNER_ARM_Y": 35.0,
        "INNER_THICKNESS": 35.0,
        "INNER_HEIGHT": 35.0,
        "INNER_COLOR": 122,
        "SMALL_INNER_ARM_X": 35.0,
        "SMALL_INNER_ARM_Y": 17.0,
        # Caps
        "TOP_CAP_ARM_X": 23.0,
        "TOP_CAP_ARM_Y": 35.0,
        "TOP_CAP_HEIGHT": 36.0,
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 35.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Dif Outer/Inner
        "SPACE": 20.0,
    },
    # TØ32
    {
        # Outer
        "ARM_LEN_X": 0.0,
        "ARM_LEN_Y": 0.0,
        "HEIGHT": 0.0,
        "COLOR": 5,
        "SMALL_ARM_X": 0.0,
        "SMALL_ARM_Y": 0.0,
        # Inner
        "INNER_ARM_X": 0.0,
        "INNER_ARM_Y": 0.0,
        "INNER_HEIGHT": 0.0,
        "INNER_COLOR": 0,
        "SMALL_INNER_ARM_X": 0.0,
        "SMALL_INNER_ARM_Y": 0.0,
        # Caps
        "TOP_CAP_ARM_X": 0.0,
        "TOP_CAP_ARM_Y": 0.0,
        "TOP_CAP_HEIGHT": 0.0,
        "LEFT_CAP_ARM_X": 0.0,
        "LEFT_CAP_ARM_Y": 0.0,
        "LEFT_CAP_HEIGHT": 0.0,
        "RIGHT_CAP_ARM_X": 0.0,
        "RIGHT_CAP_ARM_Y": 0.0,
        "RIGHT_CAP_HEIGHT": 0.0,
        # Dif Outer/Inner
        "SPACE": 0.0,
    },
    # TØ25-20-25
    {
        # Middle
        "ARM_LEN_X": 64.0,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 122,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 12.0,
        # Left Cap
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        # Right Cap
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 35.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Up Cap
        "TOP_CAP_ARM_X": 23.0,
        "TOP_CAP_ARM_Y": 30.0,
        "TOP_CAP_HEIGHT": 36.0,
    },
    # TØ25-20-20
    {
        # Middle
        "ARM_LEN_X": 59.0,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 122,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 17.0,
        # Left Cap
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        # Right Cap
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 30.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Buttom Cap
        "TOP_CAP_ARM_X": 30.0,
        "TOP_CAP_ARM_Y": 23.0,
        "TOP_CAP_HEIGHT": 36.0,
    },
    # TØ25-25-20
    {
        # Middle
        "ARM_LEN_X": 66.5,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 122,
        "SMALL_ARM_X": 35.0,
        "SMALL_ARM_Y": 17.0,
        # Left Cap
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        # Right Cap
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 30.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Buttom Cap
        "TOP_CAP_ARM_X": 35.0,
        "TOP_CAP_ARM_Y": 23.0,
        "TOP_CAP_HEIGHT": 36.0,
    },
]

MAP_TES = {
    "TØ20": 0,
    "TØ25": 1,
    "TØ32": 2,
    "TØ25-20-25": 3,
    "TØ25-20-20": 4,
    "TØ25-25-20": 5,
}


class TeModel:
    """Clase que representa los modelos de las diferentes Te"""

    def __init__(self, build_ele):

        tipo_raw = getattr(build_ele, "TipoTe", None)
        tipo_val = getattr(tipo_raw, "value", tipo_raw)

        # Mapear string a índice
        self.type_te = MAP_TES.get(str(tipo_val), 0)
        self.param = PARAMS[self.type_te]

        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def _create_te_brep(self, param: dict):
        """Te externo"""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_te < 3:
            brep_center = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )

            center_x = (param["ARM_LEN_X"] / 2) - (param["SMALL_ARM_X"] / 2)
            origin_top = AllplanGeometry.Point3D(center_x, param["ARM_LEN_Y"], 0)
            placement_top = AllplanGeometry.AxisPlacement3D(origin_top)

            brep_top = AllplanGeometry.BRep3D.CreateCuboid(
                placement_top,
                param["SMALL_ARM_X"],
                param["SMALL_ARM_Y"],
                param["HEIGHT"],
            )

            err, union_brep = AllplanGeometry.MakeUnion(brep_center, brep_top)
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            return union_brep
        if self.type_te >= 3:
            brep_left = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["LEFT_CAP_ARM_X"],
                param["LEFT_CAP_ARM_Y"],
                param["LEFT_CAP_HEIGHT"],
            )
            origin_middle = AllplanGeometry.Point3D(
                param["LEFT_CAP_ARM_X"],
                0,
                0,
            )
            placement_middle = AllplanGeometry.AxisPlacement3D(origin_middle)
            brep_middle = AllplanGeometry.BRep3D.CreateCuboid(
                placement_middle,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )

            err, union_brep = AllplanGeometry.MakeUnion(brep_left, brep_middle)
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            if self.type_te == 4:
                # Medidas del brep a restar
                len_x_sub = 12
                len_y_sub = 5
            elif self.type_te == 5:
                # Medidas del brep a restar
                len_x_sub = 14.5
                len_y_sub = 5

            # Brep para hacer subtraction
            origin_sub = AllplanGeometry.Point3D(
                ((param["LEFT_CAP_ARM_X"] + param["ARM_LEN_X"]) - len_x_sub),
                0,
                0,
            )
            placement_sub = AllplanGeometry.AxisPlacement3D(origin_sub)
            brep_sub = AllplanGeometry.BRep3D.CreateCuboid(
                placement_sub,
                len_x_sub,
                len_y_sub,
                param["LEFT_CAP_HEIGHT"],
            )

            err, sub_brep = AllplanGeometry.MakeSubtraction(union_brep, brep_sub)
            if err != 0:
                raise Exception(f"Error en MakeSubtraction: {err}")

            # Right Cap
            origin_right = AllplanGeometry.Point3D(
                (param["LEFT_CAP_ARM_X"] + param["ARM_LEN_X"]),
                len_y_sub,
                0,
            )
            placement_right = AllplanGeometry.AxisPlacement3D(origin_right)
            brep_right = AllplanGeometry.BRep3D.CreateCuboid(
                placement_right,
                param["RIGHT_CAP_ARM_X"],
                param["RIGHT_CAP_ARM_Y"],
                param["RIGHT_CAP_HEIGHT"],
            )

            err, second_union_brep = AllplanGeometry.MakeUnion(sub_brep, brep_right)
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            # Medidas del brep a restar
            x_len = 17
            y_len = 6

            # Buttom union
            origin_buttom_brep_union = AllplanGeometry.Point3D(
                (param["LEFT_CAP_ARM_X"] + x_len),
                -(param["LEFT_CAP_ARM_Y"] - param["SMALL_ARM_Y"] - y_len),
                0,
            )
            placement_buttom_brep_union = AllplanGeometry.AxisPlacement3D(
                origin_buttom_brep_union
            )
            brep_buttom_brep_union = AllplanGeometry.BRep3D.CreateCuboid(
                placement_buttom_brep_union,
                param["SMALL_ARM_X"],
                param["SMALL_ARM_Y"],
                param["HEIGHT"],
            )

            err, second_union_brep2 = AllplanGeometry.MakeUnion(
                second_union_brep, brep_buttom_brep_union
            )
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            # Buttom Cap
            origin_buttom_brep = AllplanGeometry.Point3D(
                (param["LEFT_CAP_ARM_X"] + 17),
                -(
                    param["LEFT_CAP_ARM_Y"]
                    - param["SMALL_ARM_Y"]
                    - y_len
                    + param["TOP_CAP_ARM_Y"]
                ),
                0,
            )
            placement_buttom_brep = AllplanGeometry.AxisPlacement3D(origin_buttom_brep)
            brep_buttom_brep = AllplanGeometry.BRep3D.CreateCuboid(
                placement_buttom_brep,
                param["TOP_CAP_ARM_X"],
                param["TOP_CAP_ARM_Y"],
                param["TOP_CAP_HEIGHT"],
            )

            err, final_brep = AllplanGeometry.MakeUnion(
                second_union_brep2, brep_buttom_brep
            )
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            return final_brep
        else:
            print("No hemos creado ese Brep todavia!.")

    def _create_te_brep_with_caps(self):
        """Te Interior + Caps"""

        if self.type_te == 3:
            # TØ25-20-25: tiene tapa arriba, no abajo
            inner_param = self.param

            origin = AllplanGeometry.Point3D(0, 0, 0)
            placement = AllplanGeometry.AxisPlacement3D(origin)

            # Cuerpo horizontal
            inner_core = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                inner_param["ARM_LEN_X"],
                inner_param["ARM_LEN_Y"],
                inner_param["HEIGHT"],
            )

            # Brazo vertical (arriba)
            center_x = (inner_param["ARM_LEN_X"] / 2.0) - (
                inner_param["SMALL_ARM_X"] / 2.0
            )
            origin_top = AllplanGeometry.Point3D(
                center_x,
                inner_param["ARM_LEN_Y"],
                0.0,
            )
            placement_top = AllplanGeometry.AxisPlacement3D(origin_top)

            brep_top = AllplanGeometry.BRep3D.CreateCuboid(
                placement_top,
                inner_param["SMALL_ARM_X"],
                inner_param["SMALL_ARM_Y"],
                inner_param["HEIGHT"],
            )

            err, inner_core = AllplanGeometry.MakeUnion(inner_core, brep_top)
            if err != 0:
                raise Exception(f"Error en MakeUnion(inner_core, top): código {err}")

        elif self.type_te >= 4:
            # Estos sí tienen BUTTOM_CAP_* → puedo reutilizar _create_te_brep
            inner_param = self.param
            inner_core = self._create_te_brep(inner_param)

        elif self.type_te < 2:
            inner_param = {
                "ARM_LEN_X": self.param["INNER_ARM_X"],
                "ARM_LEN_Y": self.param["INNER_ARM_Y"],
                "HEIGHT": self.param["INNER_HEIGHT"],
                "COLOR": self.param["INNER_COLOR"],
                "SMALL_ARM_X": self.param["SMALL_INNER_ARM_X"],
                "SMALL_ARM_Y": self.param["SMALL_INNER_ARM_Y"],
                "LEFT_CAP_ARM_X": self.param["LEFT_CAP_ARM_X"],
                "LEFT_CAP_ARM_Y": self.param["LEFT_CAP_ARM_Y"],
                "LEFT_CAP_HEIGHT": self.param["LEFT_CAP_HEIGHT"],
                "RIGHT_CAP_ARM_X": self.param["RIGHT_CAP_ARM_X"],
                "RIGHT_CAP_ARM_Y": self.param["RIGHT_CAP_ARM_Y"],
                "RIGHT_CAP_HEIGHT": self.param["RIGHT_CAP_HEIGHT"],
                "TOP_CAP_ARM_X": self.param["TOP_CAP_ARM_X"],
                "TOP_CAP_ARM_Y": self.param["TOP_CAP_ARM_Y"],
                "TOP_CAP_HEIGHT": self.param["TOP_CAP_HEIGHT"],
            }

            inner_core = self._create_te_brep(inner_param)
        else:
            print("No hemos creado ese Brep todavia!. (_create_te_brep_with_caps)")
        # --- A partir de acá, dejo tu lógica de caps casi igual ---

        # Left Cap
        cap1_origin = AllplanGeometry.Point3D(
            -(inner_param["LEFT_CAP_ARM_X"]), 0.0, 0.0
        )
        cap1_place = AllplanGeometry.AxisPlacement3D(cap1_origin)
        cap1_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap1_place,
            inner_param["LEFT_CAP_ARM_X"],
            inner_param["LEFT_CAP_ARM_Y"],
            inner_param["LEFT_CAP_HEIGHT"],
        )

        err, inner_with_cap1 = AllplanGeometry.MakeUnion(inner_core, cap1_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_core, cap1): código {err}")

        # Right Cap
        cap2_origin = AllplanGeometry.Point3D(inner_param["ARM_LEN_X"], 0.0, 0.0)
        cap2_place = AllplanGeometry.AxisPlacement3D(cap2_origin)

        cap2_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap2_place,
            inner_param["RIGHT_CAP_ARM_X"],
            inner_param["RIGHT_CAP_ARM_Y"],
            inner_param["RIGHT_CAP_HEIGHT"],
        )

        err, inner_with_caps2 = AllplanGeometry.MakeUnion(inner_with_cap1, cap2_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_with_cap1, cap2): código {err}")

        # Top Cap
        center_x = (inner_param["ARM_LEN_X"] / 2) - (inner_param["SMALL_ARM_X"] / 2)
        center_y = inner_param["ARM_LEN_Y"] + inner_param["SMALL_ARM_Y"]
        cap3_origin = AllplanGeometry.Point3D(center_x, center_y, 0.0)
        cap3_place = AllplanGeometry.AxisPlacement3D(cap3_origin)

        cap3_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap3_place,
            inner_param["TOP_CAP_ARM_Y"],
            inner_param["TOP_CAP_ARM_X"],
            inner_param["TOP_CAP_HEIGHT"],
        )

        # Si no hay rotación real, no hace falta transform:
        err, inner_with_caps = AllplanGeometry.MakeUnion(inner_with_caps2, cap3_local)
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(inner_with_caps2, cap3_local): código {err}"
            )

        return inner_with_caps

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_core = None
        inner_centered = None
        if self.type_te < 2:

            outer_core = self._create_te_brep(self.param)
            inner_core = self._create_te_brep_with_caps()

            # CENTRO EL INNER DENTRO DEL OUTER
            # Distancia entre outer e inner
            dx = self.param["SPACE"] + self.param["TOP_CAP_ARM_X"]
            dy = self.param["SPACE"]
            dz = self.param["SPACE"]

            mat_t = AllplanGeometry.Matrix3D()
            mat_t.SetTranslation(AllplanGeometry.Vector3D(dx, dy, dz))
            inner_centered = AllplanGeometry.Transform(inner_core, mat_t)

        elif self.type_te == 3:
            outer_core = self._create_te_brep_with_caps()
        elif self.type_te >= 4:
            # outer_core = self._create_te_brep_with_caps()
            outer_core = self._create_te_brep(self.param)

        else:
            print("No hemos creado este Brep todavia!. (_create_brep)")
        return outer_core, inner_centered

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep, inner_brep = self._create_brep()
        p = self.param

        model_list = []

        # Outer
        if outer_brep is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_model = AllplanBasisElements.ModelElement3D(outer_props, outer_brep)
            model_list.append(outer_model)

        # Inner (solo para type_te < 3)
        if inner_brep is not None and self.type_te < 3:
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p.get("INNER_COLOR", p["COLOR"])
            inner_model = AllplanBasisElements.ModelElement3D(inner_props, inner_brep)
            model_list.append(inner_model)

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    te = TeModel(build_ele)
    model_list = te.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
