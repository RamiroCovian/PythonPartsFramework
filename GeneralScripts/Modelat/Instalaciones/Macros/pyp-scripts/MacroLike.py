# -*- coding: utf-8 -*-
# MacroBloqueMastil.py — 2D simbólico + 3D real (bloque + mástil + cilindro en punta)

import math
import NemAll_Python_Geometry as Geo
import NemAll_Python_BasisElements as Basis
import NemAll_Python_BaseElements as Base
from GeneralScripts.CreateElementResult import CreateElementResult
from GeneralScripts.PythonPartUtil import PythonPartUtil

def check_allplan_version(build_ele, version):
    return True

# -------- helpers --------
def _f(be, name, d):
    try: return float(getattr(getattr(be, name), "value", d))
    except Exception: return float(d)

def _s(be, name, d):
    try: return str(getattr(getattr(be, name), "value", d))
    except Exception: return str(d)

def _rect2d_lines(com, cx, cy, w, h):
    x0, x1 = cx - w/2.0, cx + w/2.0
    y0, y1 = cy - h/2.0, cy + h/2.0
    return [
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x0,y0), Geo.Point2D(x1,y0))),
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x1,y0), Geo.Point2D(x1,y1))),
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x1,y1), Geo.Point2D(x0,y1))),
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x0,y1), Geo.Point2D(x0,y0))),
    ]

# -------- 2D simbólico --------
def _view2d_symbolic(com, sym_side, sym_bowl_r, sym_stem_w, sym_stem_len):
    elems = []
    elems += _rect2d_lines(com, 0.0, 0.0, sym_side, sym_side)
    y_line = sym_side/2.0 - max(1.0, sym_side*0.08)
    elems.append(Basis.ModelElement2D(com, Geo.Line2D(
        Geo.Point2D(-sym_side/2.0, y_line), Geo.Point2D(sym_side/2.0, y_line)
    )))
    c = Geo.Point2D(0.0, 0.0)
    elems.append(Basis.ModelElement2D(com, Geo.Arc2D(c, sym_bowl_r, sym_bowl_r, 0.0, 0.0, math.pi)))
    x0, x1 = -sym_stem_w/2.0, sym_stem_w/2.0
    y0 = -sym_side/2.0; y1 = y0 - sym_stem_len
    elems += [
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x0,y0), Geo.Point2D(x0,y1))),
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x1,y0), Geo.Point2D(x1,y1))),
        Basis.ModelElement2D(com, Geo.Line2D(Geo.Point2D(x0,y1), Geo.Point2D(x1,y1))),
    ]
    return elems

# -------- 3D real --------
def _view3d_real(com, orient, head_side, head_thk,
                 rod_len, rod_w, rod_h,
                 cap_r, cap_len):
    elems = []

    # saneos mínimos
    head_side = max(5.0, head_side)
    head_thk  = max(5.0, head_thk)
    rod_len   = max(5.0, rod_len)
    rod_w     = max(2.0, rod_w)
    rod_h     = max(2.0, rod_h)
    cap_r     = max(1.0, cap_r)
    cap_len   = max(1.0, cap_len)

    # 1) Bloque (cabeza): centrado en XY, de z=0 a z=head_thk
    axis_head = Geo.AxisPlacement3D(
        Geo.Point3D(-head_side/2.0, -head_side/2.0, 0.0),
        Geo.Vector3D(1,0,0),
        Geo.Vector3D(0,0,1)
    )
    head = Geo.BRep3D.CreateCuboid(axis_head, head_side, head_side, head_thk)
    elems.append(Basis.ModelElement3D(com, head))

    if orient.lower().startswith("h"):  # -------- HORIZONTAL (eje X) --------
        # 2) Mástil: desde la cara +X del bloque, hacia +X
        axis_rod = Geo.AxisPlacement3D(
            Geo.Point3D(head_side/2.0, -rod_w/2.0, (head_thk - rod_h)/2.0),
            Geo.Vector3D(1,0,0),   # X local
            Geo.Vector3D(0,0,1)    # Z local
        )
        rod = Geo.BRep3D.CreateCuboid(axis_rod, rod_len, rod_w, rod_h)
        elems.append(Basis.ModelElement3D(com, rod))

        # 3) Cilindro en la punta, eje ALINEADO con el mástil (X)
        cap_axis = Geo.AxisPlacement3D(
            Geo.Point3D(head_side/2.0 + rod_len, 0.0, head_thk/2.0),
            Geo.Vector3D(0,0,1),    # X local (cualquier ortonormal)
            Geo.Vector3D(1,0,0)     # Z local = eje del cilindro (X global)
        )
        cap = Geo.BRep3D.CreateCylinder(cap_axis, cap_r, cap_len)
        elems.append(Basis.ModelElement3D(com, cap))

    else:                               # -------- VERTICAL (eje Z) --------
        # 2) Mástil: desde la cara inferior del bloque, bajando en -Z
        axis_rod = Geo.AxisPlacement3D(
            Geo.Point3D(-rod_w/2.0, -rod_h/2.0, -rod_len),
            Geo.Vector3D(1,0,0),
            Geo.Vector3D(0,0,1)
        )
        rod = Geo.BRep3D.CreateCuboid(axis_rod, rod_w, rod_h, rod_len)
        elems.append(Basis.ModelElement3D(com, rod))

        # 3) Cilindro en la punta, eje ALINEADO con el mástil (−Z)
        cap_axis = Geo.AxisPlacement3D(
            Geo.Point3D(0.0, 0.0, -rod_len),
            Geo.Vector3D(1,0,0),
            Geo.Vector3D(0,0,-1)    # Z local = eje del cilindro (−Z global)
        )
        cap = Geo.BRep3D.CreateCylinder(cap_axis, cap_r, cap_len)
        elems.append(Basis.ModelElement3D(com, cap))

    return elems

# -------- entrypoint --------
def create_element(build_ele, doc):
    # propiedades
    try:
        com = build_ele.CommonProp.value
    except Exception:
        com = Base.CommonProperties(); com.GetGlobalProperties()

    # 3D (reales)
    head_side = _f(build_ele, "HeadSide", 120.0)
    head_thk  = _f(build_ele, "HeadThk",   30.0)
    rod_len   = _f(build_ele, "RodLen",   600.0)  # largo (H) / altura (V)
    rod_w     = _f(build_ele, "RodWidth",  20.0)  # ancho sección
    rod_h     = _f(build_ele, "RodHeight", 20.0)  # alto sección
    cap_r     = _f(build_ele, "CapRadius",  12.0)
    cap_len   = _f(build_ele, "CapLen",     20.0)
    orient    = _s(build_ele, "Orientation", "Horizontal")

    # 2D simbólico
    sym_side     = _f(build_ele, "SymSide",      100.0)
    sym_bowl_r   = _f(build_ele, "SymBowlR",      30.0)
    sym_stem_w   = _f(build_ele, "SymStemW",      10.0)
    sym_stem_len = _f(build_ele, "SymStemLen",    20.0)

    view2d = _view2d_symbolic(com, sym_side, sym_bowl_r, sym_stem_w, sym_stem_len)
    view3d = _view3d_real(com, orient, head_side, head_thk, rod_len, rod_w, rod_h, cap_r, cap_len)

    ppu = PythonPartUtil(com)
    ppu.add_pythonpart_view_2d(view2d)
    ppu.add_pythonpart_view_3d(view3d)
    created = ppu.create_pythonpart(build_ele)
    return CreateElementResult(created)
