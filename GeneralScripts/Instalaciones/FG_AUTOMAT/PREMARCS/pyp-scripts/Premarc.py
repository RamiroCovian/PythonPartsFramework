import ast
from PythonPartTransaction import PythonPartTransaction
from TypeCollections.ModificationElementList import ModificationElementList
import NemAll_Python_ArchElements as AllplanArchElements
from Utils.Architecture.OpeningPointsUtil import OpeningPointsUtil
import NemAll_Python_Utility as PythonUtility
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
from NemAll_Python_Geometry import Vector3D  # para normales y utilidades
from NemAll_Python_Geometry import PolyhedronUtil  # puntos de cara (2025+)
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseEle
from ScriptObjectInteractors.BaseScriptObjectInteractor import (
    BaseScriptObjectInteractor,
)
from BuildingElementTupleUtil import BuildingElementTupleUtil
import subprocess
import os
from GeneralScripts.BaseScriptObject import (
    BaseScriptObject,
    BaseScriptObjectData,
)  # base del contrato
from GeneralScripts.CreateElementResult import (
    CreateElementResult,
)  # wrapper del resultado
from ScriptObjectInteractors.PointInteractor import (
    PointInteractor,
    PointInteractorResult,
)
from TypeCollections import ModelEleList, Curve3DList
import hashlib
import math
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from PythonPartUtil import PythonPartUtil
from BuildingElementAttributeList import BuildingElementAttributeList
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import random
import subprocess
import json
from typing import Any, List
from HandleDirection import HandleDirection
from HandleParameterData import HandleParameterData
from HandleParameterType import HandleParameterType
from HandleProperties import HandleProperties
from HandlePropertiesService import HandlePropertiesService
import NemAll_Python_Utility as AllplanUtil
from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from Utils.BaseElementAdapterFilter import BaseElementAdapterFilter
from .opening_creation_util import OpeningCreationUtil, WindowOpeningCreationUtil
from .solid_opening import SolidOpening

import requests

ZERO_MODEL_GUID = "00000000-0000-0000-0000-000000000000"


def resolve_attribute_id(document, *candidate_names: str) -> int:
    """Devuelve el primer ID de atributo válido probando varios nombres."""
    if not document:
        return 0

    for attr_name in candidate_names:
        try:
            attr_id = AllplanBaseElements.AttributeService.GetAttributeID(
                document, attr_name
            )
            if attr_id and attr_id > 0:
                return attr_id
        except Exception:
            continue

    return 0


def install_packages(package):
    prg_path = AllplanSettings.AllplanPaths.GetPrgPath() + "\\"
    target_dir = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
    print("target_dir ETC: ")
    print(target_dir)
    subprocess.check_call(
        [
            prg_path + "Python\\Python.exe",
            "-m",
            "pip",
            "install",
            "--target",
            target_dir,
            "--upgrade",
            package,
        ]
    )

    target_dir = (
        f"{AllplanSettings.AllplanPaths.GetUsrPath()}Local\\PythonParts-site-packages"
    )
    print("target_dir USR: ")
    print(target_dir)
    subprocess.check_call(
        [
            prg_path + "Python\\Python.exe",
            "-m",
            "pip",
            "install",
            "--target",
            target_dir,
            "--upgrade",
            package,
        ]
    )


import sys as _sys

_site_etc = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
_site_usr = f"{AllplanSettings.AllplanPaths.GetUsrPath()}Local\\PythonParts-site-packages"
for _p in (_site_etc, _site_usr):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

try:
    import numpy as np
except ImportError:
    install_packages("numpy")
    print("instalando paquetes: numpy")
    import numpy as np

try:
    import urllib3 as urllib3
except ImportError:
    install_packages("formulas")
    print("instalando paquetes: formulas")
    import urllib3 as urllib3

XPS_LAYER = "XPS_PREMARCS"
FRAME_LAYER = "PREMARCS"
WINDOW_LAYER = "PMP_FUSTERIES"
AMPIT_LAYER = "PMP_AMPITS"
IMPERM_LAYER = "PMP_IMPERMEABILITZACIONS"
ENCAIX_LAYER = "PMP_ENCAIX"
SPACE_LAYER_REAL = "PMP_PREM_VOL_A"
SPACE_LAYER_INNER = "PMP_PREM_VOL_B"
BOX_SHUTTER_LAYER = "PMP_PREM_CALAIX_PERSIANA"
TUBS_REA_LAYER = "MP_PREM_TUB_REA"
TUBS_HORIZONTAL_VERTICAL_LAYER = "PMP_PREM_TUB"
ESCAIRE_LAYER = "PMP_PREM_ESCAIRE"
FALCAS_LAYER = "PMP_PREM_FALCA"
RETALL_GANXO_LAYER = "PMP_PREM_RETALL_GANXO"
LAYER_AMPIT_EIX_FORMIGO = "PMP_AMPITS_EIX_FG"
LAYER_AMPIT_EIX_AFEGIT = "PMP_AMPITS_EIX_ADD"
MOSQUITERA_LAYER = "PMP_MOSQUITERA"
ACCESSORIS_PREMARCS = "ACCESSORIS_PREMARCS"
ACCESSORIS_PREMARCS_LAYER = "ACCESSORIS_PREMARCS"
# Bottom U-channel accessory (catalog 115×30×3 sheet metal). Profile runs along X (sill length); U opens toward +Z.
# Physical dimensions: 115 mm opening (Y), 30 mm legs (Z), 3 mm wall. One leg hangs 24 mm past sill outer face (Y).
# Optional Y shift after anchor (mm); 0 = none.
U_SILL_EDGE_HANG_SHIFT_Y_MM = 0.0
# Whole U translated after geometry (mm); rigid move, not stretch.
U_PROFILE_SHIFT_X_MM = 0.0
U_PROFILE_SHIFT_Z_MM = 0.0
U_PROTRUSION_MM = 115  # catalog "115" = total depth in Y
U_OUTER_WIDTH_MM = 115  # same meaning as U_PROTRUSION_MM (readable alias)
U_LEG_HEIGHT_MM = 30  # physical leg height from catalog (115×30×3)
U_WALL_THICKNESS_MM = 3
U_OVERHANG_Y_MM = (
    24.0  # one leg of the U hangs 24 mm past the sill outer face (Y direction)
)
U_SILL_CONTACT_Z_EPSILON_MM = 0
# Lower z0 by this much (mm) to sit in the premarc "dip" below the opening plane; matches frame_bottom extrude step.
U_PROFILE_Z_INTO_AMPIT_DIP_MM = 3.0
U_ACCESSOR_COLOR_INT = 2  # Allplan yellow (same index as COLOR_THICKNESS_MAP for 160)
# Y placement: sill top spans y in [-self.thickness, 0]; inner opening y=0 (window side); y=-thickness = outer/back lip.
# The U profile is hard-anchored to y0 = -thickness - overhang in _u_channel_bottom (equivalent to legacy "pit_span_from_outer_lip" mode).
U_Y_OFFSET_FROM_INNER_FACE_MM = 0.01
U_PROFILE_EXTRA_Y_SHIFT_MM = 0.0
# Fine trim (mm) added to z0 after sill top is chosen. Prefer fixing sill first.
U_PROFILE_BASE_Z_ADJUST_MM = 0.0
# If not None: IGNORE bbox cache entirely. z_top = (-heigh + this offset) in premarc local Z (+Z up).
# None = automatic (cached max Z from base + finish bottom).
U_PROFILE_SILL_TOP_OFFSET_FROM_OPENING_MM = (
    None  # None = auto-detect; set a number (mm) to override
)
# create_premarc_window: cuboid_bottom_frame uses local Z span 0..63 then Move(0,-thickness,-heigh).
# U must sit at or above this plane or it occupies the same volume as the simplified bottom rail.
WINDOW_BOTTOM_RAIL_Z_EXTENT_MM = 63.0

STOPPED = 0
# RUNNING = 1
SELECTING_WALL = 1
PLACING_POINT = 2
SELECTING_EXISTING_PREMARC = 3
SELECTING_PENDING_PREMARC = 4
PREMARC_SELECTION_AUX_COLOR = 3
PREMARC_SELECTION_AUX_PEN = 15
PREMARC_SELECTION_AUX_CROSS_HALF_MM = 300.0
PREMARC_SELECTION_AUX_OFFSET_MM = 80.0
THICKNESS_MM = 3
SQUARE_THICKNESS = 60
SQUARE_VERTEX_OFFSET = math.sqrt(
    SQUARE_THICKNESS**2 + SQUARE_THICKNESS**2
)  # c= sqrt(60^2 + 60^2)
DISTANCE_FROM_ORIGIN = 230
LENGTH_CENTER_FOR_WALL = 50
WIDTH_CONCRETE = 160
TUB_WIDTH_LENGTH = 60
TUBS_NUMBER = 4  # number of tubs
FOLD_WIDTH_MM = 34
FOLD_SPACING_MM = 3
# TOP_FALCAS = False
# BOTTOM_FALCAS = False
HEIGHT_FALCA = 60
MINUS_HEIGHT_FALCA = 19
THICKNESS_FALCA = 132
MINUS_THICKNESS_FALCA = 25
# HEIGHT_EDGE_FALCA = 107
# LEFT_EDGE_FALCA = 19
LENGTH_SIDE_HEXAGON = 40
TUB_DELTA_Y_OPEN_PREMARC = 40
TUB_DELTA_X_OPEN_PREMARC = 80
BOX_SHUTTER_HEIGHT = 263
BOX_SHUTTER_WIDTH = 136
OFFSET_FRONT_BOX_SHUTTER = 0
OFFSET_FALCA = 25
DISTANCE_BETWEEN_FALCAS = 250
FIX_FEMELLA_Y = 40  # = 160/2- (80/2). 80 mm es el ancho de la femella.
VERTICAL_TUB = 1
HORIZONTAL_TUB = 2
REA_Z_ORIGIN = 50
REA_Z_FINAL = 700
LENGTH_REBAJES_MM = 19

PREMARC_USE_COMANDES_OT = True

# API_URL ="https://localhost:5050/ComandesOT/GetAllDenConfigsByAT1Value"
# API_URL ="http://localhost:5000/ComandesOT/GetAllDenConfigsByAT1Value"
API_URL ="https://192.168.30.227:8311/ComandesOT/GetAllDenConfigsByAT1Value"

# API_URL_AT1 = "https://localhost:5050/ComandesOT/GetAllValuesForConfig?den=PREM&config=1"
# API_URL_AT1 ="http://localhost:5000/ComandesOT/GetAllValuesForConfig?den=PREM&config=1"
API_URL_AT1 ="https://192.168.30.227:8311/ComandesOT/GetAllValuesForConfig?den=PREM&config=1"

# API_URL_DEFAULT = "https://localhost:5050/ComandesOT/GetAllValuesForAllConfigs?den=PREM"
# API_URL_DEFAULT = "http://localhost:5000/ComandesOT/GetAllValuesForAllConfigs?den=PREM"
API_URL_DEFAULT = "https://192.168.30.227:8311/ComandesOT/GetAllValuesForAllConfigs?den=PREM"

# LOGIN_URL_DEFAULT = "https://localhost:5050/Usuari/Login"
# LOGIN_URL_DEFAULT = "http://localhost:5000/Usuari/Login"
LOGIN_URL_DEFAULT = "https://192.168.30.227:8311/Usuari/Login"

COLOR_THICKNESS_MAP = {
    160: 2,  # amarillo
    310: 6,  # rojo
    295: 15,  # morado
}


def _premarc_comandes_ot_enabled() -> bool:
    """ComandesOT (localhost) is opt-in so Allplan runs without that backend."""
    return PREMARC_USE_COMANDES_OT


def _premarc_empty_data_endpoint() -> dict:
    """Shape expected by get_description_by_position when there is no API data."""
    return {"options": []}


def _premarc_fallback_config_values() -> dict:
    """Thickness keys for valueListaGrosor when ComandesOT is off or unreachable."""
    return {
        str(i + 1): str(th)
        for i, th in enumerate(sorted(COLOR_THICKNESS_MAP.keys()))
    }


_premarc_comandes_ot_warned = False


def _warn_comandes_ot_once(message: str) -> None:
    global _premarc_comandes_ot_warned
    if _premarc_comandes_ot_warned:
        return
    _premarc_comandes_ot_warned = True
    print(message)


FALCAS_MAP_NO_SLOPE = {
    "NO": "0",
    "PASSAMÀ LATERALS": "1-2",
    "PASSAMÀ INF/SUP": "3-4",
    "PASSAMÀ 4 COSTATS": "1-2-3-4",
    "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)": "8",
    "PASSAMÀ FALCA INF. (+ de 4 m)": "7",
    "PASSAMÀ FALCA SUP./INF. (+ de 6m)": "8-9",
}

FALCAS_MAP_SLOPE = {
    "NO": "0",
    "PASSAMÀ LATERALS": "1-2",
    "PASSAMÀ INF/SUP": "3-10",
    "PASSAMÀ 4 COSTATS": "1-2-3-10",
    "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)": "8",
    "PASSAMÀ FALCA INF. (+ de 4 m)": "11",
    "PASSAMÀ FALCA SUP./INF. (+ de 6m)": "8-12",
}

PASSAMA_FALCA_OPTIONS = {
    "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)",
    "PASSAMÀ FALCA INF. (+ de 4 m)",
    "PASSAMÀ FALCA SUP./INF. (+ de 6m)",
}

PASSAMA_PASAMANO_OPTIONS = {
    "PASSAMÀ LATERALS",
    "PASSAMÀ INF/SUP",
    "PASSAMÀ 4 COSTATS",
}

PASSAMA_SEPARATION_CM = DISTANCE_BETWEEN_FALCAS // 10  # 25 cm — fixed passamà spacing used in the XPS detail attribute

ESCUADRAS_MAP_NO_SLOPE = {
    "NO": "0",
    "35*30": "1",
    "40*30": "1",
    "70*30": "3",
    "PLEC INFERIOR": "4",
    "30*80": "2",
}

ESCUADRAS_MAP_SLOPE = {
    "NO": "5",
    "35*30": "6",
    "40*30": "6",
    "70*30": "8",
    "PLEC INFERIOR": "9",
    "30*80": "7",
}

ESCUADRAS_MAP_MANUAL_NO_SLOPE = {
    "cuadrado": "1",
    "largo": "3",
    "alto": "2",
}

ESCUADRAS_MAP_MANUAL_SLOPE = {
    "cuadrado": "6",
    "largo": "8",
    "alto": "7",
}

MAP_PERSIANAS = {
    "LAMISOL VIST": "5",
    "METALUNIC VIST": "6",
}

# WALL_ID_ATTRIBUTE = 1084
# DEN = 2103
# Matias
# PMP_FG_WALL_NAME = 2028
# DEN = 2029

# PMP_XPS_PREMARC_DETAIL = 2574
# PMP_XPS_PREMARC_DETAIL_TEXT     = 2600

# Matias
# PMP_XPS_PREMARC_DETAIL = 2002
# PMP_XPS_PREMARC_DETAIL_TEXT     = 2003

# Name attribute's
SIZES_ATTRIBUTE = "SIZES_ATTRIBUTE"
DEN = "DEN"

PMP_XPS_PREMARC_DETAIL_TEXT = "PMP_XPS_PREMARC_DETAIL_TEXT"
PMP_ID_PREMARC = "PMP_ID_PREMARC"
PMP_FG_WALL_NAME = "PMP_FG_WALL_NAME"
PMP_TIPUS_PREMARC = "PMP_TIPUS_PREMARC"
PMP_PREMARC_LABELS = "PMP_PREMARC_LABELS"
PMP_PREMARC_ELEMENT_LABELS = "PMP_PREMARC_ELEMENT_LABELS"

PMP_XPS_PREMARC_DETAIL = "PMP_XPS_PREMARC_DETAIL"

PMP_TIPUS_IMPERMEABILITZACIO = "PMP_TIPUS_IMPERMEABILITZACIO"

PMP_FG_FUS_CODI_PANELL = "PMP_FG_FUS_CODI_PANELL"
PMP_FG_FUS_CODI = "PMP_FG_FUS_CODI"
PMP_FG_FUS_UNITATS = "PMP_FG_FUS_UNITATS"
PMP_FG_FUS_MATERIAL = "PMP_FG_FUS_MATERIAL"
PMP_FG_FUS_COLOR = "PMP_FG_FUS_COLOR"
PMP_FG_FUS_MIDES = "PMP_FG_FUS_MIDES"
PMP_FG_FUS_MODEL_PERFIL = "PMP_FG_FUS_MODEL_PERFIL"
PMP_FG_FUS_FULLES = "PMP_FG_FUS_FULLES"
PMP_FG_FUS_TIPUS_FULLES = "PMP_FG_FUS_TIPUS_FULLES"
PMP_FG_FUS_POSICIO_MANETA = "PMP_FG_FUS_POSICIO_MANETA"
PMP_FG_FUS_VIDRIERA = "PMP_FG_FUS_VIDRIERA"
PMP_FG_FUS_COMP_VIDRIERA = "PMP_FG_FUS_COMP_VIDRIERA"
PMP_FG_FUS_PERSIANA = "PMP_FG_FUS_PERSIANA"
PMP_FG_FUS_AMPIT = "PMP_FG_FUS_AMPIT"
PMP_FG_FUS_APLACAT_FA = "PMP_FG_FUS_APLACAT_FA"
PMP_FG_FUS_COMP_FUST = "PMP_FG_FUS_COMP_FUST"
PMP_FG_FUS_VOLADA_FUST = "PMP_FG_FUS_VOLADA_FUST"
PMP_FG_FUS_PINTURA_OBRA = "PMP_FG_FUS_PINTURA_OBRA"
PMP_FG_FUS_BARANA = "PMP_FG_FUS_BARANA"
PMP_FG_FUS_MOSQUITERA = "PMP_FG_FUS_MOSQUITERA"
PMP_FG_FUS_MARGE = "PMP_FG_FUS_MARGE"
PMP_FG_FUS_DETAIL = "PMP_FG_FUS_DETAIL"
PMP_FG_FUS_TAPAJUNTS = "PMP_FG_FUS_TAPAJUNTS"
PMP_FG_AMPIT_DETAIL = "PMP_FG_AMPIT_DETAIL"
PMP_FG_FUSTERIA_TIPUS_MUNTATGE = "PMP_FG_FUSTERIA_TIPUS_MUNTATGE"
PMP_FG_MUNTATGE = "PMP_FG_MUNTATGE"
PMP_FG_AMPIT_ESQ = "PMP_FG_AMPIT_ESQ"
PMP_FG_AMPIT_DRE = "PMP_FG_AMPIT_DRE"
PMP_FG_AMPIT_SUP = "PMP_FG_AMPIT_SUP"
PMP_FG_AMPIT_INF = "PMP_FG_AMPIT_INF"
PMP_FG_AMPIT_REF_1 = "PMP_FG_AMPIT_REF_1"
PMP_FG_AMPIT_REF_2 = "PMP_FG_AMPIT_REF_2"
PMP_FG_AMPIT_PARTS = "PMP_FG_AMPIT_PARTS"
PMP_FG_AMPIT_MUNTATGE = "PMP_FG_AMPIT_MUNTATGE"
PMP_FG_AMPIT_AFEGIT = "PMP_FG_AMPIT_AFEGIT"
PMP_FG_AMPIT_RETALL = "PMP_FG_AMPIT_RETALL"
PMP_WALL_NAME = "PMP_WALL_NAME"
PMP_ID_PREMARC = "PMP_ID_PREMARC"
PMP_FG_FUS_ACCESORI = "PMP_FG_FUS_ACCESORI"
PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO = "PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO"
PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL = "PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO"
PMP_FG_AMPIT_DETAIL_GENERAL     = "PMP_FG_AMPIT_DETAIL_GENERAL"
PMP_FG_AMPIT_DETAIL_MATERIAL    = "PMP_FG_AMPIT_DETAIL_MATERIAL"
PMP_FG_AMPIT_MATERIAL           = "PMP_FG_AMPIT_MATERIAL"
PMP_FG_AMPIT_APLACAT            = "PMP_FG_AMPIT_APLACAT"
PMP_FG_AMPIT_SOBRESALIENTE      = "PMP_FG_AMPIT_SOBRESALIENTE"
PMP_WALL_ID                     = "PMP_WALL_ID"
PMP_PREM_ENCAJE_ALTURA          = "PMP_PREM_ENCAJE_ALTURA"
PMP_PREM_ENCAJE_BASE            = "PMP_PREM_ENCAJE_BASE"
PMP_PREM_MURO                   = "PMP_PREM_MURO"
PMP_PREM_COLOR                  = "PMP_PREM_COLOR"
PMP_PREM_XPS_TYPE               = "PMP_PREM_XPS_TYPE"
PMP_TIPUS_PREMARC = "PMP_TIPUS_PREMARC"
PMP_PREMARC_LABELS = "PMP_PREMARC_LABELS"
PMP_PREMARC_TIPO = "PMP_PREMARC_TIPO"
PMP_PREM_FONDO = "PMP_PREM_FONDO"
PMP_PARE = "PMP_PARE"


VAL_PMP_XPS_PREMARC_DETAIL_TEXT = "PIR"
VAL_PMP_ID_PREMARC = "HM1102 (HC-4)"
VAL_PMP_WALL_NAME = "HM1102"
VAL_PMP_PARE = "HM1102"
VAL_PMP_TIPUS_PREMARC = "FONS 415 mm"
VAL_PMP_PREMARC_LABELS = ""
VAL_PMP_PREMARC_ELEMENT_LABELS_TUB_VERTICAL = "$<bold, color(6)>TUB VERTICAL$"
VAL_PMP_PREMARC_ELEMENT_LABELS_TUB_HORITZONTAL = "$<bold, color(6)>TUB HORITZONTAL$"
VAL_PMP_PREMARC_ELEMENT_LABELS_ESCAIRE = "$<bold, color(6)>ESCAIRES$"
VAL_PMP_PREMARC_ELEMENT_LABELS_FALCA = "$<bold, color(4)>FALCA$"
VAL_PMP_PREMARC_ELEMENT_LABELS_REA = "$<bold, color(6)>TUB ESTRUCTURAL$"

VAL_PMP_TIPUS_IMPERMEABILITZACIO = "A"

VAL_PMP_XPS_PREMARC_DETAIL = "TIPUS_7;XPS;0.25;0.04;0.415,25.5;25;25;283;290;;"

VAL_PMP_FG_FUS_CODI_PANELL = "PANELL AC1299"
VAL_PMP_FG_FUS_CODI = "F1-SOT"
VAL_PMP_FG_FUS_UNITATS = 1
VAL_PMP_FG_FUS_MATERIAL = "ALUMINI HYDRO CIRCAL 75R"
VAL_PMP_FG_FUS_COLOR = "GRIS NEGRUZCO RAIL 7021 TEXTURITZAT"
VAL_PMP_FG_FUS_MIDES = "1992 X 592 mm"
VAL_PMP_FG_FUS_MODEL_PERFIL = "TECHNAL-SOLEAL FY-76 NEXT"
VAL_PMP_FG_FUS_FULLES = "1+1"
VAL_PMP_FG_FUS_TIPUS_FULLES = "OSCIL·LOBATENT H.0 + FIX LATERAL"
VAL_PMP_FG_FUS_POSICIO_MANETA = "MANETA VISTA DES DE L'INTERIOR DRETA"
VAL_PMP_FG_FUS_VIDRIERA = (
    "4+16+4+14+4 mm (42 mm);TRIPLE VIDRE;VIDRE CENTRAL TERMOENDURIT"
)
VAL_PMP_FG_FUS_COMP_VIDRIERA = "BAIX EMISSIU / TRANSPARENT;FOAM PERIMETRAL VIDRE;VÀLVULA ARGÓ AUTORREGULABLE;INTERCALADOR NEGRE"
VAL_PMP_FG_FUS_PERSIANA = "NO"
VAL_PMP_FG_FUS_AMPIT = "D'ALUMINI GRIS NEGRUZCO TEXTURITZAT RAIL 7021"
VAL_PMP_FG_FUS_AMPIT += ";VISTA DES DE D'ALT, VOLADA 8 cm. GRUIX 1.5mm;DETALL 4.1.2 (XAPA + APLACAT)    A OBRA"
VAL_PMP_FG_FUS_APLACAT_FA = "SI. PEDRA"
VAL_PMP_FG_FUS_COMP_FUST = "MANETA I ACCESSORIS COLOR NEGRE"
VAL_PMP_FG_FUS_VOLADA_FUST = "DES DE PREMARC 18mm"
VAL_PMP_FG_FUS_PINTURA_OBRA = "BRANCALS I DINTELL RAIL 7021"
VAL_PMP_FG_FUS_BARANA = "AMB PERFIL AMB FORMA DE 'U' DE INOX"
VAL_PMP_FG_FUS_MOSQUITERA = "MOSQUITERA CLICK-CLACK"
VAL_PMP_FG_FUS_MARGE = "30;15"
VAL_PMP_FG_FUS_DETAIL = 1
VAL_PMP_FG_FUS_TAPAJUNTS = "text 1;text 2"
VAL_PMP_FG_FUSTERIA_TIPUS_MUNTATGE = "FABRICA"
VAL_PMP_FG_MUNTATGE = "(FUSTERIA) FABRICA"
VAL_PMP_FG_FUS_ACCESORI = "ACCESORI_1"
VAL_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO = "TIPUS_IMP_1"
VAL_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL = "TIPUS_IMP_1_DETAIL"

VAL_PMP_FG_AMPIT_DETAIL = 1
VAL_PMP_FG_AMPIT_ESQ = '2"JUNTA DE 2MM"(0),409.2'
VAL_PMP_FG_AMPIT_DRE = '2"JUNTA DE 2MM"(P),409.2'
VAL_PMP_FG_AMPIT_SUP = '2"JUNTA DE 2MM"(O),409.2'
VAL_PMP_FG_AMPIT_INF = '2"JUNTA DE 2MM"(P),409.2'
VAL_PMP_FG_AMPIT_REF_1 = "HG-1"
VAL_PMP_FG_AMPIT_REF_2 = "HG067"
VAL_PMP_FG_AMPIT_PARTS = "BB-1;3"
VAL_PMP_FG_AMPIT_MUNTATGE = "FABRICA"
VAL_PMP_FG_AMPIT_AFEGIT = 0.0
VAL_PMP_FG_AMPIT_RETALL = 0.0
VAL_PMP_FG_AMPIT_DETAIL_GENERAL = "TIPUS_AMPIT_1"
VAL_PMP_FG_AMPIT_DETAIL_MATERIAL = "MATERIAL_1"
VAL_PMP_FG_AMPIT_APLACAT = "NO"

# Per-type ampit geometry specs. All dimensions in mm. Color codes are this
# codebase's verified Allplan palette indices (cross-checked against
# NEOPRENO/Solido3DNeoprenoPP.py and PREMARCS' own usages):
#   3 = turquesa, 4 = verde, 8 = naranja, 19 = gris negruc (see
#   get_color_by_thickness fallback), 91 = rosa.
# Note: color 7 in Allplan's standard palette is cyan/blue, NOT grey — use
#       19 ("gris negruc") for PAVIMENTO to match the rest of this file.
#   - grosor:               Z thickness of the top slab
#   - grosor_tope:          Y depth of the front drip lip
#   - tope:                 Z height of the front drip lip (0 = no lip)
#   - sobresaliente:        Y projection of the lip OUTER face beyond the slab OUTER face
#   - baseline_protrusion:  Y projection of the slab OUTER face beyond the wall interior face
#                           (CERAMIC / CERAMICA_MAYOR / LEGACY keep the historic 14 mm "into the
#                           room" baseline; XAPA / PAVIMENTO sit flush with the interior face)
#   - remate:               Xapa-only horizontal return at the bottom of the lip pointing inward
# LEGACY is kept here ONLY for state migration; it is no longer exposed in the UI.
AMPIT_TYPE_SPECS = {
    # "LEGACY":         {"grosor": 11, "grosor_tope": 11, "tope": 34, "sobresaliente": 0,  "baseline_protrusion": 14, "remate": 0, "color": 91, "layer": AMPIT_LAYER},
    "CERAMIC":        {"grosor": 11, "grosor_tope": 30, "tope": 30, "sobresaliente": 5,  "baseline_protrusion": 14, "remate": 0, "color": 91, "layer": AMPIT_LAYER},
    "CERAMICA_MAYOR": {"grosor": 11, "grosor_tope": 14, "tope": 34, "sobresaliente": 10, "baseline_protrusion": 14, "remate": 0, "color": 8,  "layer": AMPIT_LAYER},
    "XAPA":           {"grosor": 2,  "grosor_tope": 2,  "tope": 40, "sobresaliente": 12, "baseline_protrusion": 0,  "remate": 6, "color": 3,  "layer": AMPIT_LAYER},
    "PAVIMENTO":      {"grosor": 11, "grosor_tope": 0,  "tope": 0,  "sobresaliente": 0,  "baseline_protrusion": 0,  "remate": 0, "color": 19, "layer": AMPIT_LAYER},
}

# IMP IMPERMEABILIZACIONES — 3 tipos. grosor en mm (Z), color de la paleta
# del proyecto Allplan (6=rojo, 4=verde, 3=cyan/turquesa según paleta enviada
# por el dev). code A/B/C es el valor legacy del atributo
# PMP_TIPUS_IMPERMEABILITZACIO ya serializado en archivos viejos: mantener
# para backward compat.
IMPERM_TYPE_SPECS = {
    "Water-Stop":     {"grosor": 1.0, "color": 6, "code": "C", "layer": IMPERM_LAYER},
    "PVC":            {"grosor": 1.5, "color": 4, "code": "B", "layer": IMPERM_LAYER},
    "Tela Asfàltica": {"grosor": 3.0, "color": 3, "code": "A", "layer": IMPERM_LAYER},
}

IFC_ID_ATTRIBUTE_ID = 683

def create_element_hash(element_type: str, stable: bool = False, **params) -> str:
    # En modificacion debe ser estable para no perder relaciones del PPG.
    param_items = sorted(params.items())
    if stable:
        param_string = element_type + "_" + "_".join(f"{k}={v}" for k, v in param_items)
    else:
        random_number = random.randint(10**15, 10**16 - 1)
        param_string = f"{element_type}_random{random_number}_" + "_".join(
            f"{k}={v}" for k, v in param_items
        )

    # Generar hash
    hash_val = hashlib.sha224(param_string.encode("utf-8")).hexdigest()
    return hash_val


def create_params_list_from_dict(params: dict) -> List[str]:
    """
    Convierte un diccionario de parámetros en una lista de strings para PythonPart.

    Args:
        params: Diccionario con parámetros del elemento

    Returns:
        Lista de strings en formato "clave = valor\n"
    """
    param_list = []
    for key, value in sorted(params.items()):
        if key == "z_unique":
            try:
                value = int(float(value))
            except (TypeError, ValueError):
                value = 0
        param_list.append(f"{key} = {value}\n")
    return param_list


def z_unique_as_int(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def parse_params_list_to_dict(param_list: List[str]) -> dict:
    params = {}
    for param_str in param_list or []:
        if "=" not in param_str:
            continue
        key, value = param_str.split("=", 1)
        key = key.strip()
        value = value.strip().rstrip("\n").strip()
        if not key:
            continue
        try:
            params[key] = ast.literal_eval(value)
            continue
        except (ValueError, SyntaxError):
            pass
        if value.lower() in ("true", "false"):
            params[key] = value.lower() == "true"
            continue
        try:
            params[key] = float(value) if "." in value else int(value)
        except ValueError:
            params[key] = value
    return params


def parse_saved_state_value(raw_value: Any) -> dict:
    if isinstance(raw_value, dict):
        return dict(raw_value)

    if raw_value in (None, "", b""):
        return {}

    raw_text = str(raw_value).strip()
    if not raw_text:
        return {}

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    try:
        parsed = ast.literal_eval(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except Exception as exc:
        print(f"[SELECT][PREMARC] No se pudo parsear SavedState del PPG: {exc}")

    return {}


def _make_premarc_selection_aux_properties(
    color: int = PREMARC_SELECTION_AUX_COLOR,
    pen: int = PREMARC_SELECTION_AUX_PEN,
):
    props = AllplanBaseElements.CommonProperties()
    try:
        props.GetGlobalProperties()
    except Exception:
        pass
    props.Color = color
    props.Pen = pen
    props.ColorByLayer = False
    props.PenByLayer = False
    props.StrokeByLayer = False
    props.Construction = True
    return props


def _append_premarc_aux_line(elements, props, p0, p1) -> None:
    try:
        if AllplanGeo.CalcLength(AllplanGeo.Line3D(p0, p1)) < 0.5:
            return
    except Exception:
        return
    elements.append(
        AllplanBasisElements.ModelElement3D(props, AllplanGeo.Line3D(p0, p1))
    )


def check_allplan_version(build_ele, version):
    return True


def create_element(build_ele, doc):
    return ([], [])


def create_script_object(
    build_ele: BuildingElement, script_object_data: BaseScriptObjectData
) -> BaseScriptObject:
    """Creation of the script object (Allplan 2025 ScriptObject)"""
    return PremarcScriptObject(build_ele, script_object_data)


def _geometry_from_model_element(model_element: Any):
    if model_element is None:
        return None
    geo = getattr(model_element, "GeometryObject", None) or getattr(
        model_element, "Geometry", None
    )
    if geo is not None:
        return geo
    if hasattr(model_element, "GetGeometry"):
        try:
            return model_element.GetGeometry()
        except Exception:
            return None
    return None


def _common_props_from_model_element(model_element: Any):
    props = AllplanBaseElements.CommonProperties()
    try:
        if hasattr(model_element, "GetCommonProperties"):
            props = model_element.GetCommonProperties()
        else:
            props.GetGlobalProperties()
    except Exception:
        props.GetGlobalProperties()
    return props


class WallSelectResult:
    def __init__(self):
        self.element = None
        self.element_guid = None
        self.is_selected = False


class WallSelectInteractor(BaseScriptObjectInteractor):

    def __init__(
        self, result: WallSelectResult, prompt_msg: str = "Seleccione el muro"
    ):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg

        self.sel_query = AllplanIFW.SelectionQuery(
            [
                AllplanIFW.QueryTypeID(AllplanEleAdapter.Wall_TypeUUID),
                AllplanIFW.QueryTypeID(AllplanEleAdapter.WallTier_TypeUUID),
            ]
        )
        self.element_filter = AllplanIFW.ElementSelectFilterSetting(
            self.sel_query, True
        )

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        coord_input.InitFirstElementInput(
            AllplanIFW.InputStringConvert(self.prompt_msg)
        )

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info
    ) -> bool:
        if not self.coord_input:
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            self.coord_input.SelectElement(
                mouse_msg, pnt, msg_info, True, True, True, self.element_filter
            )
            return True

        self.coord_input.SelectElement(
            mouse_msg, pnt, msg_info, True, True, True, self.element_filter
        )
        selected_element = self.coord_input.GetSelectedElement()

        if selected_element.IsNull():
            return True

        self.result.element = selected_element
        self.result.element_guid = str(selected_element.GetModelElementUUID())
        self.result.is_selected = True
        return False  # señal a Allplan: "terminé, llama a start_next_input"

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


class PremarcSelectResult:
    def __init__(self):
        self.element = None
        self.element_guid = ""
        self.param_list: list = []
        self.saved_state: dict = {}
        self.is_selected = False


class PendingPremarcSelectResult:
    def __init__(self):
        self.selected_index = None
        self.selected_item = None
        self.input_point = None
        self.selection_source = ""
        self.element = None
        self.param_list: list = []
        self.saved_state: dict = {}
        self.is_selected = False


class ExistingPremarcSelectInteractor(BaseScriptObjectInteractor):
    def __init__(
        self,
        result: PremarcSelectResult,
        prompt_msg: str = "Seleccione el premarco (PPG) en el dibujo",
        owner=None,
    ):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg
        self.owner = owner

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        coord_input.InitFirstElementInput(
            AllplanIFW.InputStringConvert(self.prompt_msg)
        )

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info
    ) -> bool:
        if not self.coord_input or self.owner is None:
            return True

        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, False, False)

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        selected_element = self.coord_input.GetSelectedElement()
        if selected_element is None or selected_element.IsNull():
            print("[SELECT][PREMARC] Clic sin elemento: seleccione la geometria del premarco")
            return True

        clicked_name, clicked_type, clicked_guid = self.owner._get_adapter_debug_values(
            selected_element
        )
        print(
            "[SELECT][PREMARC] Click elemento -> "
            f"name={clicked_name}, type={clicked_type}, model_guid={clicked_guid or '<sin-guid>'}"
        )

        pyp_element, param_list = self.owner._resolve_premarc_ppg_from_adapter(
            selected_element
        )
        if pyp_element is None:
            print("[SELECT][PREMARC] No se identifico el PPG Premarcs en el dibujo")
            return True

        params = parse_params_list_to_dict(param_list)
        saved_state = parse_saved_state_value(params.get("SavedState", {}))
        ppg_name, ppg_type, ppg_guid = self.owner._get_adapter_debug_values(pyp_element)
        print(
            "[SELECT][PREMARC] PPG resuelto -> "
            f"clicked_guid={clicked_guid or '<sin-guid>'}, "
            f"ppg_name={ppg_name}, ppg_type={ppg_type}, ppg_guid={ppg_guid or '<sin-guid>'}, "
            f"params={len(param_list) if param_list else 0}, "
            f"saved_state_keys={sorted(saved_state.keys()) if saved_state else []}"
        )
        if not saved_state:
            print(
                "[SELECT][PREMARC] PPG sin SavedState utilizable: no se puede dibujar el marco de seleccion"
            )
            return True

        self.result.element = pyp_element
        try:
            self.result.element_guid = str(pyp_element.GetModelElementUUID())
        except Exception:
            self.result.element_guid = ""
        self.result.param_list = list(param_list) if param_list else []
        self.result.saved_state = saved_state
        self.result.is_selected = True
        print(
            f"[SELECT][PREMARC] PPG seleccionado params={len(self.result.param_list)}"
        )
        return False

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


class PendingPremarcSelectInteractor(BaseScriptObjectInteractor):
    def __init__(
        self,
        result: PendingPremarcSelectResult,
        prompt_msg: str = "Seleccione el premarco preview a editar",
        owner=None,
    ):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg
        self.owner = owner

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        coord_input.InitFirstPointInput(
            AllplanIFW.InputStringConvert(self.prompt_msg)
        )
        if self.owner is not None:
            self.owner._draw_session_selection_preview_context(clear_before=False)

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info
    ) -> bool:
        if not self.coord_input or self.owner is None:
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        try:
            input_point = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info
            ).GetPoint()
        except Exception:
            input_point = None

        if input_point is None:
            print("[SELECT][PREMARC] No se pudo leer el punto de seleccion preview")
            return True

        idx, item = self.owner._find_pending_premarc_candidate_near_point(input_point)
        if item is not None:
            self.owner._clear_session_selection_preview_context()
            self.result.selected_index = idx
            self.result.selected_item = item
            self.result.input_point = input_point
            self.result.selection_source = "preview"
            self.result.is_selected = True
            print(f"[SELECT][PREMARC] Preview seleccionado indice={idx}")
            return False

        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, False, False)
        selected_element = self.coord_input.GetSelectedElement()
        if selected_element is None or selected_element.IsNull():
            print(
                "[SELECT][PREMARC] Clic fuera del premarco activo; "
                "seleccione un preview o un PPG ya creado"
            )
            return True

        pyp_element, param_list = self.owner._resolve_premarc_ppg_from_adapter(
            selected_element
        )
        if pyp_element is None:
            print("[SELECT][PREMARC] No se identifico el PPG Premarcs en el dibujo")
            return True

        params = parse_params_list_to_dict(param_list)
        selected_z = z_unique_as_int(params.get("z_unique", 0))
        current_z = z_unique_as_int(getattr(self.owner.build_ele.z_unique, "value", 0))
        if selected_z <= 0 or current_z <= 0 or selected_z != current_z:
            self.owner._warn_premarc_from_other_execution()
            return True

        saved_state = parse_saved_state_value(params.get("SavedState", {}))

        self.result.element = pyp_element
        try:
            self.result.element_guid = str(pyp_element.GetModelElementUUID())
        except Exception:
            self.result.element_guid = ""
        self.result.param_list = list(param_list) if param_list else []
        self.result.saved_state = saved_state
        self.result.input_point = input_point
        self.result.selection_source = "existing"
        self.result.is_selected = True
        self.owner._clear_session_selection_preview_context()
        print("[SELECT][PREMARC] PPG seleccionado desde selector combinado")
        return False

    def on_cancel_function(self):
        if self.owner is not None:
            self.owner._clear_session_selection_preview_context()
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


class PremarcScriptObject(BaseScriptObject):
    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        # 1) inicializa la base y guarda el building element (acceso a parámetros)
        super().__init__(script_object_data)

        self.build_ele = build_ele
        if hasattr(self.build_ele, "ShowSessionControls"):
            self.build_ele.ShowSessionControls.value = not self.is_modification_mode
        if hasattr(self.build_ele, "ShowModificationControls"):
            self.build_ele.ShowModificationControls.value = self.is_modification_mode

        z_unique = z_unique_as_int(getattr(self.build_ele.z_unique, "value", 0))
        if z_unique <= 0 or not self.is_modification_mode:
            z_unique = int(random.random() * 3600)
        self.build_ele.z_unique.value = z_unique

        self.placement_mat = AllplanGeo.Matrix3D()
        self.placement_pnt = AllplanGeo.Point3D()
        self.point_result = PointInteractorResult()
        self.wall_select_result = WallSelectResult()
        self.premarc_select_result = PremarcSelectResult()
        self.pending_premarc_select_result = PendingPremarcSelectResult()
        self.selected_wall = None  # guardará el BaseElementAdapter
        self.detected_wall_thickness = 0
        self._opening_baseline_width = None
        self._opening_baseline_height = None
        self._opening_baseline_point = None
        self._loaded_saved_state = {}
        self._opening_recreated_during_cancel = False
        self._opening_sync_requires_direct_update = False
        self._opening_deleted_on_modification_entry = False
        self._modification_ppg_guid_str = ""
        self._modification_ppg_adapter = None
        self._delete_current_premarc_requested = False

        self.val_pmp_wall_id = self.build_ele.wall_id.value

        project_name, host_name = (
            AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
        )
        error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(
            project_name, host_name
        )
        if error != 0:
            base_path = AllplanSettings.AllplanPaths.GetCurPrjPath()

        self.color_file = os.path.join(
            base_path,
            "Premarcs",
            "color_premacs.txt",
        )

        self.encaje_file = os.path.join(
            base_path,
            "Premarcs",
            "encaje_premacs.txt",
        )

        self.wall_guid_str = ""
        raw_state = self.build_ele.SavedState.value
        if raw_state:
            # SavedState puede venir como JSON string o ya como dict
            if isinstance(raw_state, str):
                self._loaded_saved_state = json.loads(raw_state)
            elif isinstance(raw_state, dict):
                self._loaded_saved_state = raw_state

        if self.is_modification_mode:
            print(
                "[Premarc] Reingreso modificacion -> "
                f"saved_state={'si' if bool(self._loaded_saved_state) else 'no'}, "
                f"opening_guid={str(getattr(self.build_ele.opening_guid, 'value', '') or '<sin-opening>')}"
            )
            if self._loaded_saved_state:
                self.wall_guid_str = self._loaded_saved_state.get("wall_guid", "")
                print(
                    "[Premarc] Reingreso modificacion -> "
                    f"wall_guid_saved={self.wall_guid_str or '<sin-wall-guid>'}"
                )
                self._apply_premarc_saved_state(self._loaded_saved_state)
                self._opening_baseline_width = float(
                    self._loaded_saved_state.get("width", self.width)
                )
                self._opening_baseline_height = float(
                    self._loaded_saved_state.get("height", self.heigh)
                )
                self._opening_baseline_point = self._copy_point3d(self.placement_pnt)

            self._reset_wall_selection_for_modification(self.wall_guid_str)
            self._cache_modification_ppg_guid()
            if self.build_ele.opening_guid.value:
                deleted = self._delete_wall_opening()
                if deleted:
                    self._opening_deleted_on_modification_entry = True
                    print(
                        "[Premarc] Opening eliminado al reingresar a la PPG "
                        "de modificacion"
                    )

            # self.detected_wall_thickness = self.build_ele.SavedWallThickness.value

        self.session = requests.Session()
        # self.login_to_api()   #TODO descomentar en producción

        self.build_ele.SelectionWall.value = (
            "Seleccionado" if self.selected_wall else "No seleccionado"
        )
        self.thickness_premarc = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )
        self.values_for_config = self.get_values_for_config_API()
        self.list_color = self.load_color_thickness_list()
        if self.build_ele.enable_manual_thickness.value:
            self.load_color_manual_thickness()
        else:
            self.load_color_thickness_api()
        self.color_premarc = (
            self.build_ele.color_manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else COLOR_THICKNESS_MAP[self.thickness_premarc]
        )

        self.socket_width = 30
        self.socket_height = 30

        self.build_ele.id_premarc.value = VAL_PMP_ID_PREMARC
        # self.build_ele.wall_id.value                                = VAL_PMP_WALL_NAME
        self.build_ele.wall_id.value = VAL_PMP_PARE

        self.build_ele.INPUT_PMP_ID_PREMARC.value = VAL_PMP_ID_PREMARC

        self.disable_save_encaje = False
        self._user_label_override: str | None = (
            None  # set by modify_element_property when user edits INPUT_PMP_PREMARC_LABELS
        )

        # self.build_ele.INPUT_PMP_XPS_PREMARC_DETAIL.value = VAL_PMP_XPS_PREMARC_DETAIL
        # self.build_ele.INPUT_PMP_FG_FUS_CODI_PANELL.value = VAL_PMP_FG_FUS_CODI_PANELL
        # self.build_ele.INPUT_PMP_FG_FUS_CODI.value = VAL_PMP_FG_FUS_CODI
        # self.build_ele.INPUT_PMP_FG_FUS_UNITATS.value = VAL_PMP_FG_FUS_UNITATS
        # self.build_ele.INPUT_PMP_FG_FUS_MATERIAL.value = VAL_PMP_FG_FUS_MATERIAL
        # self.build_ele.INPUT_PMP_FG_FUS_COLOR.value = VAL_PMP_FG_FUS_COLOR
        # self.build_ele.INPUT_PMP_FG_FUS_MIDES.value = VAL_PMP_FG_FUS_MIDES
        # self.build_ele.INPUT_PMP_FG_FUS_MODEL_PERFIL.value = VAL_PMP_FG_FUS_MODEL_PERFIL
        # self.build_ele.INPUT_PMP_FG_FUS_FULLES.value = VAL_PMP_FG_FUS_FULLES
        # self.build_ele.INPUT_PMP_FG_FUS_TIPUS_FULLES.value = VAL_PMP_FG_FUS_TIPUS_FULLES
        # self.build_ele.INPUT_PMP_FG_FUS_POSICIO_MANERA.value = VAL_PMP_FG_FUS_POSICIO_MANERA
        # self.build_ele.INPUT_PMP_FG_FUS_VIDRIERA.value = VAL_PMP_FG_FUS_VIDRIERA
        # self.build_ele.INPUT_PMP_FG_FUS_COMP_VIDRIERA.value = VAL_PMP_FG_FUS_COMP_VIDRIERA
        # self.build_ele.INPUT_PMP_FG_FUS_PERSIANA.value = VAL_PMP_FG_FUS_PERSIANA
        # self.build_ele.INPUT_PMP_FG_FUS_AMPIT.value = VAL_PMP_FG_FUS_AMPIT
        # self.build_ele.INPUT_PMP_FG_FUS_APLACAT_FA.value = VAL_PMP_FG_FUS_APLACAT_FA
        # self.build_ele.INPUT_PMP_FG_FUS_COMP_FUST.value = VAL_PMP_FG_FUS_COMP_FUST
        # self.build_ele.INPUT_PMP_FG_FUS_VOLADA_FUST.value = VAL_PMP_FG_FUS_VOLADA_FUST
        # self.build_ele.INPUT_PMP_FG_FUS_PINTURA_OBRA.value = VAL_PMP_FG_FUS_PINTURA_OBRA
        # self.build_ele.INPUT_PMP_FG_FUS_BARANA.value = VAL_PMP_FG_FUS_BARANA
        # self.build_ele.INPUT_PMP_FG_FUS_MOSQUITERA.value = VAL_PMP_FG_FUS_MOSQUITERA

        # self.build_ele.INPUT_PMP_XPS_PREMARC_DETAIL_TEXT.value      = VAL_PMP_XPS_PREMARC_DETAIL_TEXT
        # self.build_ele.INPUT_PMP_FG_FUS_MARGE.value                 = VAL_PMP_FG_FUS_MARGE
        # self.build_ele.INPUT_PMP_FG_FUS_DETAIL.value                = VAL_PMP_FG_FUS_DETAIL
        # self.build_ele.INPUT_PMP_FG_FUS_TAPAJUNTS.value             = VAL_PMP_FG_FUS_TAPAJUNTS
        # self.build_ele.INPUT_PMP_FG_AMPIT_DETAIL.value              = VAL_PMP_FG_AMPIT_DETAIL
        # self.build_ele.INPUT_PMP_FG_AMPIT_ESQ.value                 = VAL_PMP_FG_AMPIT_ESQ
        # self.build_ele.INPUT_PMP_FG_AMPIT_DRE.value                 = VAL_PMP_FG_AMPIT_DRE
        # self.build_ele.INPUT_PMP_FG_AMPIT_SUP.value                 = VAL_PMP_FG_AMPIT_SUP
        # self.build_ele.INPUT_PMP_FG_AMPIT_INF.value                 = VAL_PMP_FG_AMPIT_INF
        # self.build_ele.INPUT_PMP_FG_AMPIT_REF_1.value               = VAL_PMP_FG_AMPIT_REF_1
        # self.build_ele.INPUT_PMP_FG_AMPIT_REF_2.value               = VAL_PMP_FG_AMPIT_REF_2
        # self.build_ele.INPUT_PMP_FG_AMPIT_PARTS.value               = VAL_PMP_FG_AMPIT_PARTS
        # self.build_ele.INPUT_PMP_FG_AMPIT_MUNTATGE.value            = VAL_PMP_FG_AMPIT_MUNTATGE
        # self.build_ele.INPUT_PMP_FG_FUSTERIA_TIPUS_MUNTATGE.value   = VAL_PMP_FG_FUSTERIA_TIPUS_MUNTATGE
        # self.build_ele.INPUT_PMP_FG_MUNTATGE.value                  = VAL_PMP_FG_MUNTATGE
        # self.build_ele.INPUT_PMP_FG_AMPIT_AFEGIT.value              = VAL_PMP_FG_AMPIT_AFEGIT
        # self.build_ele.INPUT_PMP_FG_AMPIT_RETALL.value              = VAL_PMP_FG_AMPIT_RETALL
        # self.build_ele.INPUT_PMP_FG_WALL_NAME.value                 = VAL_PMP_FG_WALL_NAME
        # self.build_ele.INPUT_PMP_FG_FUS_ACCESORI.value              = VAL_PMP_FG_FUS_ACCESORI
        # self.build_ele.INPUT_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO.value = VAL_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO
        # self.build_ele.INPUT_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL.value = VAL_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL
        # self.build_ele.INPUT_PMP_FG_AMPIT_DETAIL_GENERAL.value = VAL_PMP_FG_AMPIT_DETAIL_GENERAL
        # self.build_ele.INPUT_PMP_FG_AMPIT_MATERIAL.value = VAL_PMP_FG_AMPIT_MATERIAL

        self.update_params()

        self.afegit_ampits_manual = False
        self.retall_ampits_manual = False

        self.interactor_state = STOPPED
        self.handle_list = []
        self._pending_premarcs = []
        self._session_created_premarcs = []
        self._active_session_source_guid = ""
        self._has_confirmed_placement = False
        self._final_creation_cancelled_by_user = False
        self._create_union_frames = False  # Flag para controlar el comportamiento
        self._should_recreate_opening_after_handle = False
        self._placement_handle_start_pnt = None
        self._selected_premarc_overlay_active = False
        self._selected_premarc_overlay_state = {}
        self._selected_premarc_overlay_elements = []
        self._session_selection_preview_elements = []
        self._palette_reposition_active = False
        self._palette_reposition_has_new_point = False
        self._palette_reposition_original_point = None
        self._palette_reposition_original_state = {}
        self._palette_reposition_deleted_root = False
        self._palette_reposition_deleted_opening = False
        self._in_placement_preview = (
            False  # True solo durante preview del punto (sin XPS/accesorios/ampits)
        )
        self.data_endpoint = self.get_data_endpoint(self.get_thickness_for_api())
        self.crearListaPendiente()
        # print(f"AT9 list elements: {self.get_description_by_position(self.data_endpoint, 6)}")
        self.crearListaAbiertoCerrado()
        # self.load_pendent()
        # print(f"AT4 list elements: {self.get_description_by_position(self.data_endpoint, 3)}")
        self.load_passama_checkboxes()
        self.load_rebajes_checkboxes()
        self.default_options_rebajes()
        self.crearListaEncajes()
        self.crearListaEscuadras()
        self.crearListaTubos()
        self.crearListaPerianas()
        self.crearListaConfiguraciones()
        self.load_premarc_PE_checkbox()
        self.prem_encaje = "0 * 0"
        self.prem_encaje_base = (
            self.build_ele.EncajeBase.value
            if self.build_ele.EnableManualEncaje.value
            else 0
        )
        self.prem_encaje_altura = (
            self.build_ele.EncajeAltura.value
            if self.build_ele.EnableManualEncaje.value
            else 0
        )

        # load attributes IDs (returns -1 when attribute not defined in project)
        self._missing_attrs = set()

        #each AllplanBaseElements.AttributeService.GetAttributeID + parameters need one line
        self.sizes_attribute_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, SIZES_ATTRIBUTE
        )
        self.den_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, DEN
        )
        self.pmp_xps_premarc_detail_text_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_XPS_PREMARC_DETAIL_TEXT
            )
        )
        self.pmp_id_premarc_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_ID_PREMARC
        )
        self.pmp_pare_id = resolve_attribute_id(
            self.document, "pmp_pare", "PMP_PARE"
        )
        self.pmp_wall_id_attr_id = resolve_attribute_id(
            self.document, "PMP_WALL_ID"
        )
        self.pmp_tipus_premarc_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_TIPUS_PREMARC
        )
        self.pmp_premarc_type_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_PREMARC_TIPO
        )
        self.pmp_prem_fondo_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_PREM_FONDO
        )
        self.pmp_premarc_labels_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_PREMARC_LABELS
            )
        )
        self.pmp_premarc_element_labels_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_PREMARC_ELEMENT_LABELS
            )
        )
        self.pmp_xps_premarc_detail_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_XPS_PREMARC_DETAIL
            )
        )
        self.pmp_tipus_impermeabilitzacio_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_TIPUS_IMPERMEABILITZACIO
            )
        )
        self.pmp_fg_fus_codipanell_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_CODI_PANELL
            )
        )
        self.pmp_fg_fus_codi_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_CODI
        )
        self.pmp_fg_fus_unitats_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_UNITATS
            )
        )
        self.pmp_fg_fus_material_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_MATERIAL
            )
        )
        self.pmp_fg_fus_color_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_COLOR
        )
        self.pmp_fg_fus_mides_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_MIDES
        )
        self.pmp_fg_fus_model_perfil_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_MODEL_PERFIL
            )
        )
        self.pmp_fg_fus_fulles_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_FULLES
        )
        self.pmp_fg_fus_fulles_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_FULLES
        )
        self.pmp_fg_fus_tipus_fulles_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_TIPUS_FULLES
            )
        )
        self.pmp_fg_fus_posicio_maneta_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_POSICIO_MANETA
            )
        )
        self.pmp_fg_fus_vidriera_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_VIDRIERA
            )
        )
        self.pmp_fg_fus_comp_vidriera_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_COMP_VIDRIERA
            )
        )
        self.pmp_fg_fus_persiana_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_PERSIANA
            )
        )
        self.pmp_fg_fus_ampit_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_AMPIT
        )
        self.pmp_fg_fus_aplacat_fa_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_APLACAT_FA
            )
        )
        self.pmp_fg_fus_comp_fust_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_COMP_FUST
            )
        )
        self.pmp_fg_fus_volada_fust_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_VOLADA_FUST
            )
        )
        self.pmp_fg_fus_pintura_obra_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_PINTURA_OBRA
            )
        )
        self.pmp_fg_fus_barana_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_BARANA
        )
        self.pmp_fg_fus_mosquitera_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_MOSQUITERA
            )
        )
        self.pmp_fg_fus_marge_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_MARGE
        )
        self.pmp_fg_fus_detail_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_FUS_DETAIL
        )
        self.pmp_fg_fus_tapajunts_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_TAPAJUNTS
            )
        )
        self.pmp_fg_ampit_detail_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_DETAIL
            )
        )  #
        self.pmp_fg_fusteria_tipus_muntatge_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUSTERIA_TIPUS_MUNTATGE
            )
        )
        self.pmp_fg_muntatge_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_MUNTATGE
        )
        self.pmp_fg_ampit_esq_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_AMPIT_ESQ
        )
        self.pmp_fg_ampit_dre_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_AMPIT_DRE
        )
        self.pmp_fg_ampit_sup_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_AMPIT_SUP
        )
        self.pmp_fg_ampit_inf_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_FG_AMPIT_INF
        )
        self.pmp_fg_ampit_ref_1_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_REF_1
            )
        )
        self.pmp_fg_ampit_ref_2_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_REF_2
            )
        )
        self.pmp_fg_ampit_parts_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_PARTS
            )
        )
        self.pmp_fg_ampit_muntatge_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_MUNTATGE
            )
        )
        self.pmp_fg_ampit_afegit_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_AFEGIT
            )
        )
        self.pmp_fg_ampit_retall_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_RETALL
            )
        )
        self.pmp_fg_fus_accesori_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_ACCESORI
            )
        )
        self.pmp_fg_fus_tipus_impermeabilitzacio_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO
            )
        )
        self.pmp_fg_fus_tipus_impermeabilitzacio_detail_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL
            )
        )
        self.pmp_fg_ampit_detail_general_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_DETAIL_GENERAL
            )
        )
        self.pmp_fg_ampit_material_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_MATERIAL
            )
        )
        self.pmp_prem_encaje_altura_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_PREM_ENCAJE_ALTURA
            )
        )
        self.pmp_prem_encaje_base_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_PREM_ENCAJE_BASE
            )
        )
        self.pmp_prem_muro_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_PREM_MURO
        )
        self.pmp_prem_color_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_PREM_COLOR
        )
        self._debug_log_attribute_resolution()
        # self.pmp_prem_xps_type_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, PMP_PREM_XPS_TYPE)

    def login_to_api(self):
        payload = {
            "username": "allplan_app",
            "password": "T0jB@u3^o#",
            "empresaId": 1,
            "aplicacioId": 1007,
        }

        response = self.session.post(LOGIN_URL_DEFAULT, json=payload, verify=False)

        response.raise_for_status()

        if response.status_code == 200:
            print("LOGIN OK")
            return

        print("ERROR LOGIN")

    #     # Obtener la lista de valores dinámicos
    # def load_pendent(self):
    #     lista_pendiente = self.get_description_by_position(self.data_endpoint, 2)
    #     # lista_pendiente = ['NO', 'SI']

    #     # Crear el namedtuple desde la definición
    #     if (file_selection_tuple := BuildingElementTupleUtil.create_namedtuple_from_definition(self.build_ele.ImportPendentSelection)) is not None:
    #         # Crear la lista de namedtuples
    #         # RowText: texto a mostrar, FileSelection: valor del radio button (índice)
    #         self.build_ele.ImportPendentSelection.value = [
    #             file_selection_tuple(value, index)  # RowText=value ("NO"/"SI"), FileSelection=index (0/1)
    #             for index, value in enumerate(lista_pendiente)
    #         ]
    #         # Resultado: [ImportPendent(RowText='NO', FileSelection=0), ImportPendent(RowText='SI', FileSelection=1)]

    #     print(f"ImportPendentSelection: {self.build_ele.ImportPendentSelection.value}")

    def get_wall_material_name(self, wall_element) -> str | None:
        """Obtiene el nombre del muro desde el atributo Material (id 508) o buscando en todos los atributos."""

        if not wall_element:
            return ""

        try:
            from DocumentManager import DocumentManager

            doc = DocumentManager.get_instance().document

            attrs = wall_element.GetAttributes(
                AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
            )
            material_value_from_508 = None
            for attr in attrs:
                try:
                    attr_id = getattr(attr, "Id", None)
                    if (
                        attr_id is None
                        and isinstance(attr, (tuple, list))
                        and len(attr) >= 2
                    ):
                        attr_id = attr[0]
                        attr_value = attr[1]
                    else:
                        attr_value = getattr(attr, "Value", None)

                    if attr_id == 508:
                        # TEST
                        if not attr_value:
                            attr_value = "AP$PV_10"
                        material_value_from_508 = (
                            str(attr_value).strip() if attr_value else ""
                        )

                        if (
                            material_value_from_508
                            and material_value_from_508 != "<undefiniert>"
                        ):
                            if "$" in material_value_from_508:
                                wall_name = material_value_from_508.split("$")[
                                    0
                                ].strip()
                                return wall_name if wall_name else None
                            else:
                                return material_value_from_508
                except Exception:
                    continue

            for attr in attrs:
                try:
                    attr_id = getattr(attr, "Id", None)
                    if (
                        attr_id is None
                        and isinstance(attr, (tuple, list))
                        and len(attr) >= 2
                    ):
                        attr_id = attr[0]
                        attr_value = attr[1]
                    else:
                        attr_value = getattr(attr, "Value", None)

                    if attr_value:
                        attr_value_str = str(attr_value).strip()
                        if "$" in attr_value_str and attr_value_str != "<undefiniert>":
                            try:
                                wall_name = attr_value_str.split("$")[0].strip()
                                if wall_name:
                                    return wall_name
                            except Exception:
                                pass
                except Exception:
                    continue

        except Exception:
            pass

        return None

    def get_wall_internal_id(self, wall_element) -> str:
        """Return the Allplan Wal element internal id (e.g. '7034Wal000000334').

        Falls back to the typed `wall_id` field when no wall is selected or when
        the Allplan API on the current version does not expose a UUID accessor.
        """
        if wall_element is None:
            return self.build_ele.wall_id.value or ""
        for getter_name in ("GetModelElementUUID", "GetElementUUID", "GetUUID"):
            try:
                getter = getattr(wall_element, getter_name, None)
                if getter is None:
                    continue
                value = getter()
                if value:
                    return str(value)
            except Exception:
                continue
        return self.build_ele.wall_id.value or ""

    def compute_ampit_detail_general(self) -> str:
        """Compute PMP_FG_AMPIT_DETAIL_GENERAL based on ampit material, premarc/wall
        thickness comparison and the `is_puerta_entrada` flag.

        Returns an empty string when no material has been chosen by the user.
        """
        material = (self.build_ele.ampit_material.value or "").upper()
        is_pe = bool(self.build_ele.is_puerta_entrada.value)
        try:
            grosor_premarc = float(self.thickness_premarc or 0)
        except Exception:
            grosor_premarc = 0.0
        try:
            grosor_pared = float(self.detected_wall_thickness or 0)
        except Exception:
            grosor_pared = 0.0
        is_thicker = grosor_premarc > grosor_pared

        if material == "CERAMICA_MAYOR":
            if is_pe:
                return "DG_A_PE_CM_1"
            return "DG_A_CM_1" if is_thicker else "DG_A_CM_2"
        if material == "CERAMIC":
            if is_pe:
                return "DG_A_PE_C_2"
            return "DG_A_C_1" if is_thicker else "DG_A_C_2"
        return ""

    def get_wall_ifc_id(self, wall_element) -> str:
        """Obtiene el IFC ID del muro host desde el atributo 683."""
        if not wall_element:
            return ""

        try:
            attrs = wall_element.GetAttributes(
                AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
            )
            for attr in attrs:
                try:
                    attr_id = getattr(attr, "Id", None)
                    if (
                        attr_id is None
                        and isinstance(attr, (tuple, list))
                        and len(attr) >= 2
                    ):
                        attr_id = attr[0]
                        attr_value = attr[1]
                    else:
                        attr_value = getattr(attr, "Value", None)

                    if attr_id == IFC_ID_ATTRIBUTE_ID:
                        return str(attr_value).strip() if attr_value else ""
                except Exception:
                    continue
        except Exception:
            pass

        return ""

    def _get_current_pmp_pare_value(self) -> str:
        """Valor legible de pmp_pare: nombre/material del muro host."""
        if self.selected_wall:
            wall_name = self.get_wall_material_name(self.selected_wall) or ""
            if wall_name:
                return str(wall_name).strip()
        return str(getattr(self.build_ele.wall_id, "value", "") or "").strip()

    def _get_current_wall_ifc_id_value(self) -> str:
        """Valor técnico de PMP_WALL_ID: IFC ID del muro host."""
        if self.selected_wall:
            return self.get_wall_ifc_id(self.selected_wall)
        return ""

    def _get_current_premarc_id_value(self) -> str:
        """PMP_ID_PREMARC debe salir del input de paleta del premarco."""
        input_value = str(
            getattr(self.build_ele.INPUT_PMP_ID_PREMARC, "value", "") or ""
        ).strip()
        if input_value:
            return input_value
        return str(getattr(self.build_ele.id_premarc, "value", "") or "").strip()

    def _add_shared_generated_element_attributes(
        self, attribute_list: BuildingElementAttributeList
    ) -> None:
        """Aplica atributos comunes a todos los subelementos del premarco."""
        premarc_id = self._get_current_premarc_id_value()
        if premarc_id:
            attribute_list.add_attribute(self.pmp_id_premarc_id, premarc_id)

        wall_name = self._get_current_pmp_pare_value()
        if self.pmp_pare_id <= 0:
            print("[Premarc] PMP_PARE no resuelto: attr_id<=0")
        elif wall_name:
            attribute_list.add_attribute(self.pmp_pare_id, wall_name)
        else:
            print("[Premarc] PMP_PARE vacío: no se añade atributo")

        wall_ifc_id = self._get_current_wall_ifc_id_value()
        if getattr(self, "pmp_wall_id_attr_id", 0) <= 0:
            print("[Premarc] PMP_WALL_ID no resuelto: attr_id<=0")
        elif wall_ifc_id:
            attribute_list.add_attribute(self.pmp_wall_id_attr_id, wall_ifc_id)
        else:
            print("[Premarc] PMP_WALL_ID vacío: no se añade atributo")

    def _add_ampit_identity_attributes(
        self, attribute_list: BuildingElementAttributeList
    ) -> None:
        """Identidad tecnica minima para ampits y sus ejes."""
        premarc_id = self._get_current_premarc_id_value()
        if premarc_id:
            attribute_list.add_attribute(self.pmp_id_premarc_id, premarc_id)

        wall_ifc_id = self._get_current_wall_ifc_id_value()
        if getattr(self, "pmp_wall_id_attr_id", 0) <= 0:
            print("[Premarc] PMP_WALL_ID no resuelto: attr_id<=0")
        elif wall_ifc_id:
            attribute_list.add_attribute(self.pmp_wall_id_attr_id, wall_ifc_id)
        else:
            print("[Premarc] PMP_WALL_ID vacío: no se añade atributo")

    def _debug_log_attribute_resolution(self) -> None:
        """
        Traza acotada de los atributos clave para diagnosticar IDs no definidos
        en el proyecto actual.
        """
        debug_attrs = [
            ("PMP_ID_PREMARC", getattr(self, "pmp_id_premarc_id", -1)),
            ("PMP_PARE", getattr(self, "pmp_pare_id", -1)),
            ("PMP_WALL_ID", getattr(self, "pmp_wall_id_attr_id", -1)),
            ("PMP_FG_AMPIT_AFEGIT", getattr(self, "pmp_fg_ampit_afegit_id", -1)),
            ("PMP_FG_AMPIT_RETALL", getattr(self, "pmp_fg_ampit_retall_id", -1)),
            ("PMP_FG_AMPIT_MATERIAL", getattr(self, "pmp_fg_ampit_material_id", -1)),
            ("PMP_FG_AMPIT_MUNTATGE", getattr(self, "pmp_fg_ampit_muntatge_id", -1)),
            ("PMP_FG_AMPIT_PARTS", getattr(self, "pmp_fg_ampit_parts_id", -1)),
            ("PMP_FG_AMPIT_REF_1", getattr(self, "pmp_fg_ampit_ref_1_id", -1)),
            ("PMP_FG_AMPIT_REF_2", getattr(self, "pmp_fg_ampit_ref_2_id", -1)),
        ]

        print("[Premarc][ATTR] Resolucion de atributos clave:")
        for attr_name, attr_id in debug_attrs:
            status = "OK" if isinstance(attr_id, int) and attr_id > 0 else "MISSING"
            print(f"[Premarc][ATTR]   {attr_name}: id={attr_id} status={status}")

    def _build_window_attribute_list(self) -> BuildingElementAttributeList:
        """Atributos propios de la fusteria, sin contaminar con los del ampit."""
        attribute_list = BuildingElementAttributeList()
        attribute_list.add_attribute(
            self.pmp_fg_fus_codipanell_id, VAL_PMP_FG_FUS_CODI_PANELL
        )
        attribute_list.add_attribute(self.pmp_fg_fus_codi_id, VAL_PMP_FG_FUS_CODI)
        attribute_list.add_attribute(
            self.pmp_fg_fus_unitats_id, VAL_PMP_FG_FUS_UNITATS
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_material_id, VAL_PMP_FG_FUS_MATERIAL
        )
        attribute_list.add_attribute(self.pmp_fg_fus_color_id, VAL_PMP_FG_FUS_COLOR)
        attribute_list.add_attribute(self.pmp_fg_fus_mides_id, VAL_PMP_FG_FUS_MIDES)
        attribute_list.add_attribute(
            self.pmp_fg_fus_model_perfil_id, VAL_PMP_FG_FUS_MODEL_PERFIL
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_fulles_id, VAL_PMP_FG_FUS_FULLES
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_tipus_fulles_id, VAL_PMP_FG_FUS_TIPUS_FULLES
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_posicio_maneta_id, VAL_PMP_FG_FUS_POSICIO_MANETA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_vidriera_id, VAL_PMP_FG_FUS_VIDRIERA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_comp_vidriera_id, VAL_PMP_FG_FUS_COMP_VIDRIERA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_persiana_id, VAL_PMP_FG_FUS_PERSIANA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_aplacat_fa_id, VAL_PMP_FG_FUS_APLACAT_FA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_comp_fust_id, VAL_PMP_FG_FUS_COMP_FUST
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_volada_fust_id, VAL_PMP_FG_FUS_VOLADA_FUST
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_pintura_obra_id, VAL_PMP_FG_FUS_PINTURA_OBRA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_barana_id, VAL_PMP_FG_FUS_BARANA
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_mosquitera_id, VAL_PMP_FG_FUS_MOSQUITERA
        )
        attribute_list.add_attribute(self.pmp_fg_fus_marge_id, VAL_PMP_FG_FUS_MARGE)
        attribute_list.add_attribute(
            self.pmp_fg_fus_detail_id, VAL_PMP_FG_FUS_DETAIL
        )
        attribute_list.add_attribute(
            self.pmp_fg_fus_tapajunts_id, VAL_PMP_FG_FUS_TAPAJUNTS
        )
        attribute_list.add_attribute(
            self.pmp_fg_fusteria_tipus_muntatge_id,
            VAL_PMP_FG_FUSTERIA_TIPUS_MUNTATGE,
        )
        attribute_list.add_attribute(self.pmp_fg_muntatge_id, VAL_PMP_FG_MUNTATGE)
        self._add_shared_generated_element_attributes(attribute_list)
        return attribute_list

    def _get_build_ele_value(self, *candidate_names: str, default="") -> str:
        """Lee el primer parametro existente en build_ele y devuelve su valor como texto."""
        for name in candidate_names:
            param = getattr(self.build_ele, name, None)
            if param is None:
                continue
            value = getattr(param, "value", param)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return str(default).strip() if default is not None else ""

    def _get_ampit_parts_value(self) -> str:
        """ID de fusteria definido por el usuario para el ampit."""
        return self._get_build_ele_value(
            "INPUT_PMP_FG_AMPIT_PARTS",
            "INPUT_PMP_FG_FUS_CODI",
            default=VAL_PMP_FG_AMPIT_PARTS,
        )

    def _get_ampit_muntatge_value(self) -> str:
        """
        Tipo de montaje del ampit segun la seleccion actual de TypeTubos.
        """
        type_tubos = str(getattr(self.build_ele.TypeTubos, "value", "") or "").strip()
        if type_tubos in {"OBRA", "FABRICA"}:
            return type_tubos

        return VAL_PMP_FG_AMPIT_MUNTATGE

    def _get_ampit_afegit_value(self) -> float:
        """
        Longitud añadida si el ampit es mas estrecho que el ancho a cubrir.
        La fuente persistida es build_ele.afegit_ampits.
        """
        build_ele_value = float(
            getattr(self.build_ele.afegit_ampits, "value", 0.0) or 0.0
        )
        computed_value = float(getattr(self, "afegit_ampits", 0.0) or 0.0)
        if computed_value > 0 and abs(build_ele_value - computed_value) > 1e-9:
            self.build_ele.afegit_ampits.value = computed_value
            return computed_value
        return build_ele_value

    def _get_ampit_material_value(self) -> str:
        """
        Material del ampit seleccionado por el usuario.
        Solo debe informarse para opciones tipo ceramic / ceramica mayor;
        en el resto se devuelve vacio.
        """
        material_value = self._get_build_ele_value(
            "INPUT_PMP_FG_AMPIT_MATERIAL",
            "INPUT_PMP_FG_AMPIT_DETAIL_MATERIAL",
            "INPUT_PMP_FG_FUS_AMPIT",
        )
        if not material_value:
            return ""

        normalized = material_value.lower()
        if "ceramic" in normalized or "ceramica" in normalized:
            return material_value
        return ""

    def _build_ampit_attribute_list(self) -> BuildingElementAttributeList:
        """Atributos visibles para los elementos 3D de ampit."""
        attribute_list = BuildingElementAttributeList()
        self._add_ampit_identity_attributes(attribute_list)
        attribute_list.add_attribute(
            self.pmp_fg_ampit_afegit_id, self._get_ampit_afegit_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_retall_id, self.build_ele.retall_ampits.value
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_detail_general_id, VAL_PMP_FG_AMPIT_DETAIL_GENERAL
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_material_id, self._get_ampit_material_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_muntatge_id, self._get_ampit_muntatge_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_parts_id, self._get_ampit_parts_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_1_id, self._get_current_premarc_id_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_2_id, self._get_current_pmp_pare_value()
        )
        return attribute_list

    def _build_ampit_edge_fg_attribute_list(self) -> BuildingElementAttributeList:
        """Atributos visibles para PMP_AMPITS_EIX_FG."""
        attribute_list = BuildingElementAttributeList()
        self._add_ampit_identity_attributes(attribute_list)
        return attribute_list

    def _build_ampit_edge_add_attribute_list(self) -> BuildingElementAttributeList:
        """Atributos visibles para PMP_AMPITS_EIX_ADD."""
        attribute_list = BuildingElementAttributeList()
        self._add_ampit_identity_attributes(attribute_list)
        attribute_list.add_attribute(
            self.pmp_fg_ampit_parts_id, self._get_ampit_parts_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_1_id, self._get_current_premarc_id_value()
        )
        attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_2_id, self._get_current_pmp_pare_value()
        )
        return attribute_list

    def get_thickness_for_api(self):
        if self.build_ele.enable_manual_thickness.value:
            return None
        return self.build_ele.thickness.value

    # def get_thickness_for_api(self):
    #     """Espesor usado solo para consultar la API (listas/combos). Siempre un valor de catálogo."""
    #     if self.build_ele.enable_manual_thickness.value:
    #         # Manual activo: la API puede no conocer el valor manual → usar un valor por defecto de catálogo
    #         return self.build_ele.thickness.value  # el del combo, que sí está en la API
    #     return self.build_ele.thickness.value

    def load_color_thickness_list(self) -> list[tuple[float, int]]:
        """return list of tuples (thickness, color)"""
        if not os.path.exists(self.color_file):
            return []
        list_color = []
        try:
            with open(self.color_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) != 2:
                        continue
                    thickness, color = parts[0].strip(), parts[1].strip()
                    list_color.append((thickness, color))
        except (OSError, IOError):
            return []

        return list_color

    def load_color_thickness_api(self) -> str:
        """return color for thickness"""
        for thickness, color in self.list_color:
            if float(thickness) == self.build_ele.thickness.value:
                self.build_ele.color_manual_thickness.value = color
                return color
        return None

    def load_color_manual_thickness(self) -> int:
        """
        load color for thickness and set visibility for color_manual_thickness
        """

        # check if thickness is in colors default for premarcs api
        if self.build_ele.manual_thickness.value in COLOR_THICKNESS_MAP:
            self.build_ele.color_manual_thickness.value = COLOR_THICKNESS_MAP.get(
                self.build_ele.manual_thickness.value
            )
            self.build_ele.color_manual_thickness_visible.value = False
            return self.build_ele.color_manual_thickness.value

        for thickness, color in self.list_color:
            if float(thickness) == self.build_ele.manual_thickness.value:
                self.build_ele.color_manual_thickness.value = color
                self.build_ele.color_manual_thickness_visible.value = False
                return color

        self.build_ele.color_manual_thickness_visible.value = True
        # Manage first manual color
        if not self.list_color:
            self.build_ele.color_manual_thickness.value = 4
            # self.build_ele.color_manual_thickness_visible.value = False
            return self.build_ele.color_manual_thickness.value

        # Propors colors for values in [4, 7, 5]
        values = [color for thickness, color in self.list_color]
        for propors_color in ["4", "7", "5"]:
            if propors_color not in values:
                self.build_ele.color_manual_thickness.value = propors_color
                # self.list_color.append((self.build_ele.manual_thickness.value, color))
                self.build_ele.color_manual_thickness.visible = True
                return propors_color
        # Random color, except colors already used
        values_set = [int(color) for color in values]
        allowed = [n for n in range(1, 256) if n not in values_set]
        rnd = random.choice(allowed) if allowed else -1
        self.build_ele.color_manual_thickness.value = rnd
        # self.build_ele.color_manual_thickness.visible = True
        return rnd

    def load_premarc_PE_checkbox(self):
        """load premarc PE checkbox"""
        if self.build_ele.premarc_PE.value:
            self.build_ele.ComboBoxEncajes.value = "PLEC INFERIOR"
            self.build_ele.EnableEncajes.value = False
            self.build_ele.ComboBoxPendiente.value = "SI"
            self.build_ele.EnablePendiente.value = False
            self.build_ele.ComboBoxPersianas.value = "NO"
            self.build_ele.EnablePersianas.value = False
        else:
            self.build_ele.EnableEncajes.value = True
            self.build_ele.EnablePendiente.value = True
            self.build_ele.EnablePersianas.value = True

        return

    def save_color_manual_thickness(self):
        """save color for thickness"""
        premarcs_saved = [float(thickness) for thickness, _ in self.list_color]
        # Check if thickness is in list_color
        # TODO cahnge to new requirement
        if (self.build_ele.manual_thickness.value) in premarcs_saved:
            return
        # Not save if color is in colors default for premarcs api
        if self.build_ele.color_manual_thickness.value in COLOR_THICKNESS_MAP:
            return

        color_dir = os.path.dirname(self.color_file)
        os.makedirs(color_dir, exist_ok=True)
        with open(self.color_file, "a") as file:
            file.write(
                f"{self.thickness_premarc},{self.build_ele.color_manual_thickness.value}\n"
            )
        return

    def save_manual_encaje(self):
        """save color for thickness"""
        base = self.build_ele.EncajeBase.value
        altura = self.build_ele.EncajeAltura.value

        encaje_dir = os.path.dirname(self.encaje_file)
        os.makedirs(encaje_dir, exist_ok=True)
        with open(self.encaje_file, "a") as file:
            file.write(f"{base}x{altura}\n")
        return

    def color_id_to_rgb_or_hex(self):
        """Convierte color_manual_thickness.value (ID) a RGB y/o hex."""
        default_rgb = "(0,0,0)"
        default_hex = "#000000"
        color_id = int(self.build_ele.color_manual_thickness.value)
        if color_id is None or color_id < 0:
            return default_rgb, default_hex

        argb = AllplanBaseElements.GetColorById(int(color_id))
        r, g, b = argb.Red, argb.Green, argb.Blue
        rgb = f"({r},{g},{b})"
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        return rgb, hex_color

    def load_passama_checkboxes(self):
        """Carga los valores dinámicos para los CheckBox"""
        data = self.data_endpoint
        lista_passama = self.get_description_by_position(data, 3)

        if not lista_passama:
            lista_passama = [
                "NO",
                "PASSAMÀ LATERALS",
                "PASSAMÀ INF/SUP",
                "PASSAMÀ 4 COSTATS",
                "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)",
                "PASSAMÀ FALCA INF. (+ de 4 m)",
                "PASSAMÀ FALCA SUP./INF. (+ de 6m)",
            ]

        # Regla de negocio: para fondo 310 no existen opciones de falca.
        # Se filtra en UI para no depender de que la API o el mock estén
        # perfectamente alineados con ese catálogo.
        if self.get_thickness_for_api() == 310:
            lista_passama = [
                option_name
                for option_name in lista_passama
                if "FALCA" not in str(option_name).upper()
            ]

        previous_names = list(self.build_ele.valueListaPassama.value or [])
        previous_values = list(self.build_ele.PassamaOptions.value or [])
        previous_state_by_name = {
            str(name): bool(value)
            for name, value in zip(previous_names, previous_values)
        }

        # Allplan no siempre recompone bien una lista dinámica si solo cambia
        # el texto de las filas. Forzamos sincronización completa de nombres y
        # estados, preservando únicamente las opciones que siguen existiendo.
        self.build_ele.valueListaPassama.value = lista_passama
        self.build_ele.PassamaOptions.value = [
            previous_state_by_name.get(option_name, False)
            for option_name in lista_passama
        ]

    def load_rebajes_checkboxes(self):
        """Carga los valores dinámicos para los CheckBox"""
        data = self.data_endpoint
        lista_rebajes = self.get_description_by_position(data, 5)

        if not lista_rebajes:
            lista_rebajes = [
                "NO",
                "REB. DRETA",
                "REB. ESQUERRA",
                "REB. BAIXS",
                "REB. DALT",
            ]

        # Actualizar la lista de valores
        self.build_ele.valueListaRebajes.value = lista_rebajes

        # Inicializar los CheckBox si no están inicializados
        if (
            len(self.build_ele.RebajesOptions.value) != len(lista_rebajes)
            and not self.is_modification_mode
        ):
            self.build_ele.RebajesOptions.value = [False] * len(lista_rebajes)

    def default_options_rebajes(self):
        """Default options: enable NO option"""

        index_no = self.build_ele.valueListaRebajes.value.index("NO")
        self.build_ele.RebajesOptions.value[index_no] = 1
        return

    def start_input(self):
        """start the input"""

        self.update_params()

        if self.is_modification_mode:
            self.interactor_state = STOPPED
            self.script_object_interactor = None
            return

        # Reiniciar selección de muro
        self.wall_select_result = WallSelectResult()
        self.selected_wall = None

        self.interactor_state = SELECTING_WALL
        self.script_object_interactor = WallSelectInteractor(
            self.wall_select_result, "Seleccione el muro donde colocar el premarco"
        )

        # self.interactor_state = RUNNING
        # self.script_object_interactor = PointInteractor(
        #     interactor_result=self.point_result,
        #     is_first_input=True,
        #     request_text="Posicionar Premarco",
        #     preview_function=self.draw_placement_preview
        # )

        # Recupera la selección hecha por el usuario (lista de adaptadores)
        # Si en el futuro usas filtros, pásalos aquí con `selection_filter=...`

    # --- Entrada de datos (paso interactivo opcional) ---

    # def start_next_input(self):
    #     """
    #     Es llamado cuando termina la interacción actual.
    #     Si no hay más pasos, anula el interactor.
    #     """
    #     self.update_params()

    #     if self.point_result.input_point != PointInteractorResult():
    #         self.placement_pnt = self.point_result.input_point
    #         self.placement_mat.SetRotation(AllplanGeo.Line3D(AllplanGeo.Point3D(self.placement_pnt.X,self.placement_pnt.Y,self.placement_pnt.Z), AllplanGeo.Point3D(self.placement_pnt.X,self.placement_pnt.Y,self.placement_pnt.Z + 100)), AllplanGeo.Angle.FromDeg(self.rotation))
    #         self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.placement_pnt))

    #         self.script_object_interactor = None
    #         self.interactor_state = STOPPED
    def start_next_input(self):
        self.update_params()

        if self.interactor_state == SELECTING_WALL:
            if self.wall_select_result.is_selected:
                # Guardar adapter del muro — disponible en execute()
                self._set_selected_wall_adapter(
                    self.wall_select_result.element,
                    self.wall_select_result.element_guid,
                )
                print(
                    f"[Premarc] Muro seleccionado: {self.wall_select_result.element_guid}"
                )

                try:
                    wall_angle = self._get_wall_rotation_deg(self.selected_wall)
                except Exception as e:
                    print(f"[Premarc] _get_wall_rotation_deg fallo: {e}")
                    wall_angle = 0.0
                self.rotation = wall_angle
                self.build_ele.rotation.value = wall_angle
                print(f"[Premarc] Rotation set to wall angle: {wall_angle} deg")

                try:
                    self._debug_wall_attrs(self.selected_wall)
                except Exception as e:
                    print(f"[Premarc] _debug_wall_attrs fallo: {e}")

                if self.selected_wall:
                    try:
                        mat_raw = self.get_wall_material_name(self.selected_wall)
                        self.wall_name = mat_raw
                        self.build_ele.wall_id.value = mat_raw or ""

                    except Exception as e:
                        pass

                # Pasar al segundo interactor
                self._start_placement_point_input()
            else:
                # El usuario canceló sin seleccionar muro
                self.script_object_interactor = None
                self.interactor_state = STOPPED

        elif self.interactor_state == PLACING_POINT:
            if self.point_result.input_point != PointInteractorResult():
                self.placement_pnt = self.point_result.input_point
                self._sync_placement_point_parameter()
                self._rebuild_placement_mat()
                self._has_confirmed_placement = True
                if self._palette_reposition_active:
                    self._palette_reposition_has_new_point = True

                # self.build_ele.PlacementPntX.value = self.placement_pnt.X
                # self.build_ele.PlacementPntY.value = self.placement_pnt.Y
                # self.build_ele.PlacementPntZ.value = self.placement_pnt.Z
                self.build_ele.SavedWallThickness.value = self.detected_wall_thickness
                # self.build_ele.PlacementPnt.value = f"{self.placement_pnt.X},{self.placement_pnt.Y},{self.placement_pnt.Z}"

                # state = {
                #     "X": self.placement_pnt.X,
                #     "Y": self.placement_pnt.Y,
                #     "Z": self.placement_pnt.Z,
                #     "thickness": self.detected_wall_thickness
                # }
                # self.build_ele.SavedState.value = json.dumps(state)

                if not self.is_modification_mode and not self._palette_reposition_active:
                    print(
                        "[Premarc] Punto confirmado en creacion -> "
                        "materializando premarco inmediatamente"
                    )
                    self._create_current_premarc_ppg_without_opening(
                        register_session_item=True,
                        reset_active_after_create=True,
                    )
                elif (
                    not self.is_modification_mode
                    and self._palette_reposition_active
                    and self._palette_reposition_has_new_point
                ):
                    print(
                        "[Premarc][SESSION] Punto confirmado en reubicacion -> "
                        "materializando PPG reubicado inmediatamente"
                    )
                    source_guid = str(self._active_session_source_guid or "")
                    if self._create_current_premarc_ppg_without_opening(
                        register_session_item=True,
                        reset_active_after_create=True,
                    ):
                        self._reset_reposition_state()

            self.script_object_interactor = None
            self.interactor_state = STOPPED
        elif self.interactor_state == SELECTING_EXISTING_PREMARC:
            self._clear_session_selection_preview_context()
            self.script_object_interactor = None
            self.interactor_state = STOPPED
            if self.premarc_select_result.is_selected:
                if not self._select_session_created_premarc_for_edit(
                    self.premarc_select_result.saved_state,
                    self.premarc_select_result.element_guid,
                ):
                    self._activate_selected_premarc_overlay(
                        self.premarc_select_result.saved_state
                    )
        elif self.interactor_state == SELECTING_PENDING_PREMARC:
            self._clear_session_selection_preview_context()
            self.script_object_interactor = None
            self.interactor_state = STOPPED
            if self.pending_premarc_select_result.is_selected:
                if self.pending_premarc_select_result.selection_source == "preview":
                    self._select_pending_premarc_for_edit(
                        self.pending_premarc_select_result.selected_item
                    )
                elif (
                    self.pending_premarc_select_result.selection_source == "existing"
                ):
                    if not self._select_session_created_premarc_for_edit(
                        self.pending_premarc_select_result.saved_state,
                        self.pending_premarc_select_result.element_guid,
                    ):
                        self._activate_selected_premarc_overlay(
                            self.pending_premarc_select_result.saved_state
                        )

    def _start_placement_point_input(self):
        """Inicia el input de punto conservando el muro seleccionado."""
        self.point_result = PointInteractorResult()
        self._has_confirmed_placement = False
        self.interactor_state = PLACING_POINT
        self.script_object_interactor = PointInteractor(
            interactor_result=self.point_result,
            is_first_input=True,
            request_text="Posicionar Premarco",
            preview_function=self.draw_placement_preview,
        )

    def _start_palette_reposition_input(self) -> bool:
        """Start explicit point-pick to relocate an existing premarc from the PPG."""
        if not self.selected_wall and self.is_modification_mode:
            self._reset_wall_selection_for_modification(self.wall_guid_str)

        if not self.selected_wall:
            PythonUtility.ShowMessageBox(
                "Seleccione o restaure el muro del premarco antes de reubicarlo.",
                PythonUtility.MB_OK,
            )
            return False

        if self.placement_pnt == AllplanGeo.Point3D():
            PythonUtility.ShowMessageBox(
                "Primero debe existir un premarco posicionado para poder moverlo.",
                PythonUtility.MB_OK,
            )
            return False

        self._clear_selected_premarc_overlay()
        self._palette_reposition_original_point = self._copy_point3d(self.placement_pnt)
        self._palette_reposition_original_state = self._build_premarc_saved_state_dict(
            self.placement_pnt
        )
        self._palette_reposition_deleted_root = False
        self._palette_reposition_deleted_opening = False

        if self.is_modification_mode:
            self._prepare_modification_reposition_preview()
        else:
            source_guid = str(self._active_session_source_guid or "")
            if source_guid:
                self._remove_session_created_premarc_item(source_guid)
                deleted_now = self._delete_session_premarc_ppg(source_guid)
                self._palette_reposition_deleted_root = deleted_now
                print(
                    "[Premarc][SESSION] Reubicar desde sesion -> "
                    f"source_guid={source_guid}, "
                    f"deleted_now={'si' if deleted_now else 'no'}"
                )
                self._log_session_created_premarcs(
                    "Despues de borrar PPG seleccionado para reubicar",
                    selected_guid=source_guid,
                )

        self._palette_reposition_active = True
        self._palette_reposition_has_new_point = False
        self._start_placement_point_input()
        return True

    def _prepare_modification_reposition_preview(self) -> bool:
        """Hide the edited PPG while dragging so only the live preview remains."""
        wall_guid = ""
        try:
            if self.selected_wall and not self.selected_wall.IsNull():
                wall_guid = str(self.selected_wall.GetModelElementUUID())
        except Exception:
            wall_guid = str(self.wall_guid_str or "")

        print(
            "[Premarc] Reubicar -> estado previo: "
            f"wall_guid={wall_guid or '<sin-guid>'}, "
            f"opening_guid={str(getattr(self.build_ele.opening_guid, 'value', '') or '<sin-opening>')}, "
            f"placement=({self.placement_pnt.X:.1f}, {self.placement_pnt.Y:.1f}, {self.placement_pnt.Z:.1f})"
        )

        # No borrar el PPG aqui. Allplan puede cerrar la sesion si se llama
        # DeleteElements() sobre el elemento activo mientras la PPG esta en modo
        # modificacion. La actualizacion real se hace al confirmar/cerrar.
        self._palette_reposition_deleted_root = False
        self._palette_reposition_deleted_opening = False
        print("[Premarc] Reubicar -> modo seguro: no se borra PPG durante el drag")

        wall_guid_after = ""
        try:
            if self.selected_wall and not self.selected_wall.IsNull():
                wall_guid_after = str(self.selected_wall.GetModelElementUUID())
        except Exception:
            wall_guid_after = str(self.wall_guid_str or "")

        print(
            "[Premarc] Reubicar -> estado posterior: "
            f"wall_guid={wall_guid_after or '<sin-guid>'}, "
            f"opening_deleted={self._palette_reposition_deleted_opening}, "
            f"ppg_deleted={self._palette_reposition_deleted_root}"
        )

        return True

    def _commit_current_premarc_before_next_placement(self) -> bool:
        """Materializa el premarco configurado antes de pedir una nueva posicion."""
        self.update_params()

        if self.placement_pnt == AllplanGeo.Point3D():
            print("[Premarc] No hay premarco posicionado para confirmar")
            return True

        if not self.selected_wall:
            PythonUtility.ShowMessageBox(
                "Seleccione un muro antes de posicionar otro premarco.",
                PythonUtility.MB_OK,
            )
            return False

        if self.build_ele.enable_manual_thickness.value:
            self.save_color_manual_thickness()
        if self.build_ele.EnableManualEncaje.value and not self.disable_save_encaje:
            self.save_manual_encaje()

        if self.check_falcas_and_persianas():
            resp = PythonUtility.ShowMessageBox(
                f"Selecciono Falcas, pero no hay persianas.\n" "¿Desea continuar?",
                PythonUtility.MB_OKCANCEL,
            )
            if resp == PythonUtility.IDCANCEL:
                return False

        self._create_wall_opening()
        self._create_union_frames = True
        self._execute()

        # El siguiente ciclo debe empezar sin punto activo ni GUID de opening heredado.
        self.placement_pnt = AllplanGeo.Point3D()
        self._has_confirmed_placement = False
        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""
        self._loaded_saved_state = {}

        print("[Premarc] Premarco confirmado; habilitando nueva posicion")
        return True

    def _extract_created_premarc_ppg_guid(self, created_elements) -> str:
        for element in created_elements or []:
            ppg_element, _ = self._resolve_premarc_ppg_from_adapter(element)
            if ppg_element is None:
                continue
            try:
                if ppg_element.IsNull():
                    continue
            except Exception:
                pass
            try:
                return str(ppg_element.GetModelElementUUID())
            except Exception:
                continue
        return ""

    def _format_point3d_for_log(self, point: Any) -> str:
        if point is None or not hasattr(point, "X"):
            return "<sin-point>"
        try:
            return f"({float(point.X):.1f}, {float(point.Y):.1f}, {float(point.Z):.1f})"
        except Exception:
            return "<sin-point>"

    def _log_session_created_premarcs(
        self, reason: str, selected_guid: str = ""
    ) -> None:
        selected_guid_str = str(selected_guid or "")
        active_guid_str = str(self._active_session_source_guid or "")
        active_point_str = (
            self._format_point3d_for_log(self.placement_pnt)
            if self.placement_pnt != AllplanGeo.Point3D()
            else "<sin-point>"
        )
        print(
            "[Premarc][SESSION] "
            f"{reason} -> count={len(self._session_created_premarcs)}, "
            f"selected_guid={selected_guid_str or '<sin-guid>'}, "
            f"active_guid={active_guid_str or '<sin-guid>'}, "
            f"active_point={active_point_str}, "
            f"has_confirmed={'si' if self._has_confirmed_placement else 'no'}"
        )

        if not self._session_created_premarcs:
            print("[Premarc][SESSION]   <vacio>")
            return

        selected_found = False
        non_selected_guids = []

        for idx, item in enumerate(self._session_created_premarcs):
            guid_str = str(item.get("ppg_guid", "") or "")
            wall_guid_str = str(
                item.get("wall_guid", "") or item.get("state", {}).get("wall_guid", "") or ""
            )
            role = (
                "SELECTED"
                if selected_guid_str and guid_str == selected_guid_str
                else "OTHER"
            )
            if role == "SELECTED":
                selected_found = True
            else:
                non_selected_guids.append(guid_str or f"idx={idx}")

            print(
                "[Premarc][SESSION]   "
                f"idx={idx}, role={role}, guid={guid_str or '<sin-guid>'}, "
                f"point={self._format_point3d_for_log(item.get('point'))}, "
                f"wall_guid={wall_guid_str or '<sin-guid>'}"
            )

        if selected_guid_str and not selected_found:
            print(
                "[Premarc][SESSION]   "
                f"selected_guid_not_in_queue={selected_guid_str}"
            )
        print(
            "[Premarc][SESSION]   "
            f"non_selected_guids={non_selected_guids if non_selected_guids else []}"
        )

    def _create_current_premarc_ppg_without_opening(
        self, *, register_session_item: bool, reset_active_after_create: bool
    ) -> bool:
        if self.placement_pnt == AllplanGeo.Point3D():
            print("[Premarc] No hay premarco posicionado para crear PPG sin opening")
            return True

        if not self.selected_wall:
            PythonUtility.ShowMessageBox(
                "Seleccione un muro antes de crear el premarco.",
                PythonUtility.MB_OK,
            )
            return False

        self.update_params()
        if self.build_ele.enable_manual_thickness.value:
            self.save_color_manual_thickness()
        if self.build_ele.EnableManualEncaje.value and not self.disable_save_encaje:
            self.save_manual_encaje()

        if self.check_falcas_and_persianas():
            resp = PythonUtility.ShowMessageBox(
                f"Selecciono Falcas, pero no hay persianas.\n" "Â¿Desea continuar?",
                PythonUtility.MB_OKCANCEL,
            )
            if resp == PythonUtility.IDCANCEL:
                return False

        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""

        session_state = self._build_premarc_saved_state_dict(self.placement_pnt)
        session_wall_guid = str(
            session_state.get("wall_guid", "")
            or self.wall_select_result.element_guid
            or getattr(self, "wall_guid_str", "")
            or ""
        )

        self._create_union_frames = True
        created_elements = self._execute() or []
        created_ppg_guid = self._extract_created_premarc_ppg_guid(created_elements)
        print(
            "[Premarc][SESSION] Materializacion sin opening -> "
            f"created_ppg_guid={created_ppg_guid or '<sin-guid>'}, "
            f"point={self._format_point3d_for_log(self.placement_pnt)}, "
            f"created_elements={len(created_elements) if created_elements else 0}"
        )

        if register_session_item:
            session_item = {
                "point": self._copy_point3d(self.placement_pnt),
                "state": dict(session_state),
                "ppg_guid": created_ppg_guid,
                "wall_guid": session_wall_guid,
            }
            replaced_existing = False
            if self._active_session_source_guid:
                for idx, item in enumerate(self._session_created_premarcs):
                    if str(item.get("ppg_guid", "") or "") == str(
                        self._active_session_source_guid
                    ):
                        self._session_created_premarcs[idx] = session_item
                        replaced_existing = True
                        break
            if not replaced_existing:
                self._session_created_premarcs.append(session_item)
            print(
                "[Premarc] PPG de sesion creado sin opening: "
                f"{len(self._session_created_premarcs)} pendiente(s) de opening"
            )
            self._log_session_created_premarcs(
                "Despues de materializar PPG sin opening",
                selected_guid=self._active_session_source_guid,
            )

        if reset_active_after_create:
            self.placement_pnt = AllplanGeo.Point3D()
            self._has_confirmed_placement = False
            self._loaded_saved_state = {}
            self._active_session_source_guid = ""
            if hasattr(self.build_ele, "opening_guid"):
                self.build_ele.opening_guid.value = ""

        return True

    def _replace_session_premarc_ppg(self, ppg_guid_str: str) -> bool:
        if not ppg_guid_str:
            self._create_union_frames = True
            created = self._execute()
            return bool(created)

        try:
            old_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                AllplanEleAdapter.GUID.FromString(ppg_guid_str),
                self.coord_input.GetInputViewDocument(),
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo recuperar PPG de sesion: {exc}")
            self._create_union_frames = True
            created = self._execute()
            return bool(created)

        if old_adapter is None or old_adapter.IsNull():
            print(
                "[Premarc] PPG de sesion no encontrado; "
                "recreando premarco final desde el estado de sesion"
            )
            self._create_union_frames = True
            created = self._execute()
            return bool(created)

        self._rebuild_placement_mat()
        premarc_elements = self.create_premarcs_group()
        if not premarc_elements:
            print("[Premarc] Actualizacion de PPG cancelada: sin geometria")
            return False

        trans_mat = AllplanGeo.Matrix3D()
        trans_mat.SetTranslation(AllplanGeo.Vector3D(self.placement_pnt))

        try:
            old_list = AllplanEleAdapter.BaseElementAdapterList()
            old_list.append(old_adapter)
            AllplanBaseElements.DeleteElements(self.document, old_list)
        except Exception as exc:
            print(f"[Premarc] No se pudo borrar PPG previo antes de actualizar: {exc}")
            return False

        try:
            created_elements = AllplanBaseElements.CreateElements(
                self.document,
                trans_mat,
                premarc_elements,
                [],
                None,
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo recrear PPG con opening: {exc}")
            return False

        print(
            "[Premarc] PPG de sesion actualizado con opening "
            f"({len(created_elements) if created_elements else 0} elementos)"
        )
        return bool(created_elements)

    def _finalize_session_created_premarcs(self) -> bool:
        if not self._validate_before_final_creation():
            return False

        active_session_item_to_replace = None
        if self._has_confirmed_placement:
            active_session_item = self._build_current_active_session_final_item()
            if active_session_item is not None:
                active_guid = str(active_session_item.get("ppg_guid", "") or "")
                if active_guid:
                    active_session_item_to_replace = active_session_item
                    print(
                        "[Premarc][SESSION] Premarco activo finalizado como reemplazo -> "
                        f"source_guid={active_guid}, "
                        f"target_point={self._format_point3d_for_log(active_session_item.get('point'))}"
                    )
                else:
                    self._session_created_premarcs.append(active_session_item)
                self._log_session_created_premarcs(
                    "Premarco activo preparado para finalizacion",
                    selected_guid=active_guid,
                )
                self.placement_pnt = AllplanGeo.Point3D()
                self._has_confirmed_placement = False
                self._loaded_saved_state = {}
                self._active_session_source_guid = ""
                if hasattr(self.build_ele, "opening_guid"):
                    self.build_ele.opening_guid.value = ""
            else:
                if not self._create_current_premarc_ppg_without_opening(
                    register_session_item=True,
                    reset_active_after_create=True,
                ):
                    return False

        if not self._session_created_premarcs:
            if active_session_item_to_replace is None:
                print("[Premarc] No hay PPGs de premarco pendientes de opening")
                return False

        session_items = list(self._session_created_premarcs)
        self._session_created_premarcs = []

        if active_session_item_to_replace is not None:
            session_items.insert(0, active_session_item_to_replace)

        for index, item in enumerate(session_items, start=1):
            point = item["point"]
            state = dict(item["state"])
            wall_guid = str(item.get("wall_guid", "") or state.get("wall_guid", "") or "")

            self._apply_premarc_saved_state(state)
            self.placement_pnt = self._copy_point3d(point)
            self._sync_placement_point_parameter()
            self._rebuild_placement_mat()
            self._has_confirmed_placement = True

            if wall_guid:
                self._try_restore_wall_from_guid(wall_guid)

            if hasattr(self.build_ele, "opening_guid"):
                self.build_ele.opening_guid.value = ""

            print(
                f"[Premarc] Generando opening final {index}/{len(session_items)} en "
                f"({point.X:.1f}, {point.Y:.1f}, {point.Z:.1f})"
            )
            if self.selected_wall:
                self._create_wall_opening()

            self._replace_session_premarc_ppg(str(item.get("ppg_guid", "") or ""))

        self.placement_pnt = AllplanGeo.Point3D()
        self._has_confirmed_placement = False
        self._loaded_saved_state = {}
        self._active_session_source_guid = ""
        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""

        return True

    def _copy_point3d(self, point: AllplanGeo.Point3D) -> AllplanGeo.Point3D:
        return AllplanGeo.Point3D(point.X, point.Y, point.Z)

    def _normalize_pyp_display_name(self, name: Any) -> str:
        return str(name or "").strip().strip("'\"")

    def _parameter_to_param_list(self, parameter: Any) -> list:
        if isinstance(parameter, str):
            return parameter.splitlines()
        if isinstance(parameter, (list, tuple)):
            return list(parameter)
        return []

    def _is_premarc_pyp_params(self, name: Any, parameter: Any) -> bool:
        if self._normalize_pyp_display_name(name) == "Premarcs":
            return True
        param_list = self._parameter_to_param_list(parameter)
        if not param_list:
            return False
        params = parse_params_list_to_dict(param_list)
        return bool(params.get("SavedState")) and params.get("z_unique") not in (
            None,
            0,
            0.0,
        )

    def _read_premarc_param_list_from_element(self, pyp_element) -> list:
        if pyp_element is None:
            return []
        try:
            if pyp_element.IsNull():
                return []
        except Exception:
            pass
        try:
            success, name, parameter = AllplanBaseElements.PythonPartService.GetParameter(
                pyp_element
            )
            if success and self._is_premarc_pyp_params(name, parameter):
                return self._parameter_to_param_list(parameter)
        except Exception as exc:
            print(f"[SELECT][PREMARC] Error leyendo param_list del PPG: {exc}")
        return []

    def _get_parent_adapter(self, adapter):
        if adapter is None:
            return None
        try:
            return AllplanEleAdapter.BaseElementAdapterParentElementService.GetParentElement(
                adapter
            )
        except Exception:
            return None

    def _resolve_premarc_ppg_from_adapter(self, adapter):
        current = adapter
        visited = set()
        for _ in range(16):
            if current is None:
                break
            try:
                if current.IsNull():
                    break
            except Exception:
                break

            name, _type_guid, model_guid = self._get_adapter_debug_values(current)
            if self._is_invalid_modification_adapter(name, model_guid):
                print(
                    "[Premarc] Resolucion PPG detenida: adapter invalido "
                    f"name={name}, model_guid={model_guid or '<sin-guid>'}"
                )
                break

            param_list = self._read_premarc_param_list_from_element(current)
            if param_list:
                return current, param_list
            try:
                key = str(current.GetNOIGUID())
            except Exception:
                key = str(id(current))
            if key in visited:
                break
            visited.add(key)
            current = self._get_parent_adapter(current)
        return None, []

    def _warn_premarc_from_other_execution(self) -> None:
        print(
            "[SELECT][PREMARC] Rechazado: premarco de otra ejecucion "
            "(solo premarcos colocados en esta sesion)"
        )
        try:
            PythonUtility.ShowMessageBox(
                "No se puede seleccionar un premarco colocado en otra ejecución.\n\n"
                "Solo puede seleccionar premarcos colocados en la ejecución actual.",
                PythonUtility.MB_OK,
            )
        except Exception:
            pass

    def _build_premarc_selection_overlay(self, state: dict) -> list[Any]:
        if not state:
            return []

        try:
            width = float(state.get("width", 0.0))
            height = float(state.get("height", 0.0))
            depth = float(state.get("depth", 0.0))
            rotation = float(state.get("rotation", 0.0))
            base_point = AllplanGeo.Point3D(
                float(state.get("X", 0.0)),
                float(state.get("Y", 0.0)),
                float(state.get("Z", 0.0)),
            )
        except (TypeError, ValueError):
            return []

        props = _make_premarc_selection_aux_properties()
        mat = AllplanGeo.Matrix3D()
        mat.SetRotation(
            AllplanGeo.Line3D(
                base_point,
                AllplanGeo.Point3D(base_point.X, base_point.Y, base_point.Z + 100),
            ),
            AllplanGeo.Angle.FromDeg(rotation),
        )
        mat.SetTranslation(AllplanGeo.Vector3D(base_point))

        def tp(x, y, z):
            return AllplanGeo.Transform(AllplanGeo.Point3D(x, y, z), mat)

        offset = float(PREMARC_SELECTION_AUX_OFFSET_MM)
        x_min = -offset
        x_max = width + offset
        y_front = offset
        y_back = -depth - offset
        z_top = offset
        z_bottom = -height - offset
        mid_x = width / 2.0
        mid_y = -depth / 2.0
        mid_z = -height / 2.0

        p0 = tp(x_min, y_front, z_top)
        p1 = tp(x_max, y_front, z_top)
        p2 = tp(x_max, y_front, z_bottom)
        p3 = tp(x_min, y_front, z_bottom)
        p4 = tp(x_min, y_back, z_top)
        p5 = tp(x_max, y_back, z_top)
        p6 = tp(x_max, y_back, z_bottom)
        p7 = tp(x_min, y_back, z_bottom)

        overlay = []
        for a, b in (
            (p0, p1),
            (p1, p2),
            (p2, p3),
            (p3, p0),
            (p4, p5),
            (p5, p6),
            (p6, p7),
            (p7, p4),
            (p0, p4),
            (p1, p5),
            (p2, p6),
            (p3, p7),
            (
                tp(mid_x - PREMARC_SELECTION_AUX_CROSS_HALF_MM / 2.0, mid_y, mid_z),
                tp(mid_x + PREMARC_SELECTION_AUX_CROSS_HALF_MM / 2.0, mid_y, mid_z),
            ),
            (
                tp(mid_x, mid_y, mid_z - PREMARC_SELECTION_AUX_CROSS_HALF_MM / 2.0),
                tp(mid_x, mid_y, mid_z + PREMARC_SELECTION_AUX_CROSS_HALF_MM / 2.0),
            ),
        ):
            _append_premarc_aux_line(overlay, props, a, b)
        return overlay

    def _draw_selected_premarc_overlay(self, clear_before: bool = False) -> bool:
        if not self._selected_premarc_overlay_active or not self._selected_premarc_overlay_state:
            return False
        overlay = self._build_premarc_selection_overlay(
            self._selected_premarc_overlay_state
        )
        if not overlay:
            return False
        self._selected_premarc_overlay_elements = list(overlay)
        try:
            AllplanBaseElements.DrawElementPreview(
                self.document, AllplanGeo.Matrix3D(), overlay, clear_before, None
            )
            return True
        except Exception as exc:
            print(f"[SELECT][PREMARC] Error dibujando marco auxiliar: {exc}")
            return False

    def _clear_selected_premarc_overlay(self) -> None:
        if not self._selected_premarc_overlay_elements:
            self._selected_premarc_overlay_active = False
            self._selected_premarc_overlay_state = {}
            return
        try:
            AllplanBaseElements.DrawElementPreview(
                self.document,
                AllplanGeo.Matrix3D(),
                list(self._selected_premarc_overlay_elements),
                True,
                None,
            )
        except Exception as exc:
            print(f"[SELECT][PREMARC] Error limpiando marco auxiliar: {exc}")
        self._selected_premarc_overlay_elements = []
        self._selected_premarc_overlay_active = False
        self._selected_premarc_overlay_state = {}

    def _activate_selected_premarc_overlay(self, state: dict) -> bool:
        self._clear_selected_premarc_overlay()
        if not state:
            return False
        self._selected_premarc_overlay_state = dict(state)
        self._selected_premarc_overlay_active = True
        return self._draw_selected_premarc_overlay(clear_before=False)

    def _get_active_selected_premarc_overlay(self) -> list[Any]:
        """Marco auxiliar del premarco seleccionado, actualizado con el estado activo."""
        if (
            not self._selected_premarc_overlay_active
            or self.placement_pnt == AllplanGeo.Point3D()
        ):
            return []

        state = self._build_premarc_saved_state_dict(self.placement_pnt)
        if not state:
            state = dict(self._selected_premarc_overlay_state or {})
        if not state:
            return []

        self._selected_premarc_overlay_state = dict(state)
        return self._build_premarc_selection_overlay(state)

    def _build_current_active_premarc_item(self) -> dict | None:
        if not self._has_confirmed_placement or self.placement_pnt == AllplanGeo.Point3D():
            return None
        return {
            "point": self._copy_point3d(self.placement_pnt),
            "state": self._build_premarc_saved_state_dict(self.placement_pnt),
            "is_active": True,
            "pending_index": None,
        }

    def _build_current_active_session_final_item(self) -> dict | None:
        if not self._has_confirmed_placement or self.placement_pnt == AllplanGeo.Point3D():
            return None

        session_state = self._build_premarc_saved_state_dict(self.placement_pnt)
        if not session_state:
            return None

        session_wall_guid = str(
            session_state.get("wall_guid", "")
            or self.wall_select_result.element_guid
            or getattr(self, "wall_guid_str", "")
            or ""
        )
        return {
            "point": self._copy_point3d(self.placement_pnt),
            "state": dict(session_state),
            "ppg_guid": str(self._active_session_source_guid or ""),
            "wall_guid": session_wall_guid,
        }

    def _is_session_guid_in_queue(self, ppg_guid_str: str) -> bool:
        if not ppg_guid_str:
            return False
        for item in self._session_created_premarcs:
            if str(item.get("ppg_guid", "") or "") == str(ppg_guid_str):
                return True
        return False

    def _build_selectable_pending_premarc_items(self) -> list[dict]:
        items = []
        for idx, item in enumerate(self._pending_premarcs):
            items.append(
                {
                    "point": self._copy_point3d(item["point"]),
                    "state": dict(item["state"]),
                    "is_active": False,
                    "pending_index": idx,
                }
            )
        active_item = self._build_current_active_premarc_item()
        if active_item is not None:
            items.append(active_item)
        return items

    def _find_pending_premarc_candidate_near_point(
        self, input_point: AllplanGeo.Point3D, tolerance_mm: float = 600.0
    ) -> tuple[int | None, dict | None]:
        items = self._build_selectable_pending_premarc_items()
        if input_point is None or not hasattr(input_point, "X"):
            return None, None

        best_idx = None
        best_item = None
        best_dist_sq = None
        tol_sq = float(tolerance_mm) ** 2

        for idx, item in enumerate(items):
            point = item.get("point")
            if point is None:
                continue
            dx = float(point.X) - float(input_point.X)
            dy = float(point.Y) - float(input_point.Y)
            dz = float(getattr(point, "Z", 0.0)) - float(getattr(input_point, "Z", 0.0))
            dist_sq = dx * dx + dy * dy + dz * dz
            if dist_sq <= tol_sq and (best_dist_sq is None or dist_sq < best_dist_sq):
                best_idx = idx
                best_item = item
                best_dist_sq = dist_sq
        return best_idx, best_item

    def _select_pending_premarc_for_edit(self, selected_item: dict) -> bool:
        if not selected_item:
            return False

        current_active = self._build_current_active_premarc_item()
        selected_pending_index = selected_item.get("pending_index")

        if selected_item.get("is_active"):
            self._apply_premarc_saved_state(selected_item["state"])
            self.placement_pnt = self._copy_point3d(selected_item["point"])
            self._sync_placement_point_parameter()
            self._rebuild_placement_mat()
            self._has_confirmed_placement = True
            return self._activate_selected_premarc_overlay(selected_item["state"])

        if selected_pending_index is None:
            return False

        if selected_pending_index < 0 or selected_pending_index >= len(self._pending_premarcs):
            return False

        selected_pending = self._pending_premarcs.pop(selected_pending_index)

        if current_active is not None:
            self._pending_premarcs.append(
                {
                    "point": self._copy_point3d(current_active["point"]),
                    "state": dict(current_active["state"]),
                }
            )

        self._apply_premarc_saved_state(selected_pending["state"])
        self.placement_pnt = self._copy_point3d(selected_pending["point"])
        self._sync_placement_point_parameter()
        self._rebuild_placement_mat()
        self._has_confirmed_placement = True
        return self._activate_selected_premarc_overlay(selected_pending["state"])

    def _delete_session_premarc_ppg(self, ppg_guid_str: str) -> bool:
        if not ppg_guid_str:
            return False
        print(
            "[Premarc][SELECT] Borrado temporal de PPG de sesion para editar -> "
            f"ppg_guid={ppg_guid_str}"
        )
        try:
            ppg_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                AllplanEleAdapter.GUID.FromString(ppg_guid_str),
                self.coord_input.GetInputViewDocument(),
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo recuperar PPG de sesion para editar: {exc}")
            return False

        if ppg_adapter is None or ppg_adapter.IsNull():
            print("[Premarc] PPG de sesion ya no existe al intentar editarlo")
            return False

        try:
            name, type_guid, model_guid = self._get_adapter_debug_values(ppg_adapter)
            resolved_guid = str(model_guid or "")
            print(
                "[Premarc][SESSION] Adapter PPG recuperado para borrado -> "
                f"name={name}, type={type_guid}, "
                f"model_guid={resolved_guid or '<sin-guid>'}, "
                f"requested_guid={ppg_guid_str}"
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo inspeccionar PPG de sesion: {exc}")
            resolved_guid = ""

        if resolved_guid and resolved_guid != str(ppg_guid_str):
            print(
                "[Premarc][SESSION] Borrado cancelado: el adapter resuelto "
                "no coincide con el GUID solicitado"
            )
            return False

        try:
            delete_list = AllplanEleAdapter.BaseElementAdapterList()
            delete_list.append(ppg_adapter)
            transaction = PythonPartTransaction(self.document)
            transaction.execute(
                AllplanGeo.Matrix3D(),
                AllplanIFW.ViewWorldProjection(),
                [],
                ModificationElementList(),
                elements_to_delete=delete_list,
            )
            print(
                "[Premarc][SESSION] PPG de sesion borrado en transaccion OK -> "
                f"ppg_guid={ppg_guid_str}"
            )
            return True
        except Exception as exc:
            print(f"[Premarc] No se pudo borrar PPG de sesion seleccionado: {exc}")
            return False

    def _remove_session_created_premarc_item(self, ppg_guid_str: str) -> dict | None:
        if not ppg_guid_str:
            return None

        for idx, item in enumerate(self._session_created_premarcs):
            if str(item.get("ppg_guid", "") or "") == str(ppg_guid_str):
                removed_item = self._session_created_premarcs.pop(idx)
                print(
                    "[Premarc] Premarco de sesion retirado de la cola -> "
                    f"ppg_guid={ppg_guid_str}, pendientes={len(self._session_created_premarcs)}"
                )
                return removed_item

        print(
            "[Premarc] Premarco de sesion no encontrado en la cola para borrar -> "
            f"ppg_guid={ppg_guid_str}"
        )
        return None

    def _discard_active_session_premarc_from_creation(self) -> bool:
        """Delete the selected premarc during the same creation session."""
        active_guid = str(self._active_session_source_guid or "")
        print(
            "[Premarc] Eliminar en sesion -> "
            f"active_guid={active_guid or '<sin-guid>'}, "
            f"placement_is_zero={self.placement_pnt == AllplanGeo.Point3D()}, "
            f"pending_queue={len(self._pending_premarcs)}, "
            f"session_queue={len(self._session_created_premarcs)}"
        )

        if active_guid:
            removed_item = self._remove_session_created_premarc_item(active_guid)
            deleted_ppg = self._delete_session_premarc_ppg(active_guid)
            self._clear_selected_premarc_overlay()
            self._clear_session_selection_preview_context()
            self._loaded_saved_state = {}
            self._active_session_source_guid = ""
            self._has_confirmed_placement = False
            self.placement_pnt = AllplanGeo.Point3D()
            self._sync_placement_point_parameter()
            if hasattr(self.build_ele, "opening_guid"):
                self.build_ele.opening_guid.value = ""
            if hasattr(self.build_ele, "SavedState"):
                self.build_ele.SavedState.value = ""
            print(
                "[Premarc] Premarco seleccionado de la sesion eliminado desde UI -> "
                f"found_in_queue={'si' if removed_item else 'no'}, "
                f"deleted_ppg_now={'si' if deleted_ppg else 'no'}"
            )
            self._redraw_session_created_premarcs_context()
            return True

        if self._has_confirmed_placement and self.placement_pnt != AllplanGeo.Point3D():
            self._clear_selected_premarc_overlay()
            self._clear_session_selection_preview_context()
            self._loaded_saved_state = {}
            self._has_confirmed_placement = False
            self.placement_pnt = AllplanGeo.Point3D()
            self._sync_placement_point_parameter()
            if hasattr(self.build_ele, "opening_guid"):
                self.build_ele.opening_guid.value = ""
            if hasattr(self.build_ele, "SavedState"):
                self.build_ele.SavedState.value = ""
            print("[Premarc] Premarco activo no materializado descartado desde UI")
            self._redraw_session_created_premarcs_context()
            return True

        print("[Premarc] Eliminacion en sesion cancelada: no hay premarco activo seleccionado")
        PythonUtility.ShowMessageBox(
            "Seleccione un premarco de esta misma ejecucion antes de eliminarlo.",
            PythonUtility.MB_OK,
        )
        return False

    def _select_session_created_premarc_for_edit(
        self, saved_state: dict, ppg_guid_str: str
    ) -> bool:
        if not saved_state or not ppg_guid_str:
            return False

        print(
            "[Premarc][SELECT] Solicitud seleccionar PPG de sesion -> "
            f"requested_guid={ppg_guid_str}, "
            f"saved_state_keys={sorted(saved_state.keys()) if saved_state else []}"
        )
        self._log_session_created_premarcs(
            "Antes de seleccionar PPG de sesion", selected_guid=ppg_guid_str
        )

        selected_index = None
        selected_item = None
        for idx, item in enumerate(self._session_created_premarcs):
            if str(item.get("ppg_guid", "") or "") == str(ppg_guid_str):
                selected_index = idx
                selected_item = item
                break

        if selected_item is None:
            return False

        selected_point = self._copy_point3d(selected_item["point"])
        current_is_same = (
            self._has_confirmed_placement
            and abs(self.placement_pnt.X - selected_point.X) <= 0.01
            and abs(self.placement_pnt.Y - selected_point.Y) <= 0.01
            and abs(self.placement_pnt.Z - selected_point.Z) <= 0.01
        )
        print(
            "[Premarc][SELECT] Match en cola -> "
            f"selected_index={selected_index}, "
            f"selected_point={self._format_point3d_for_log(selected_point)}, "
            f"current_point={self._format_point3d_for_log(self.placement_pnt)}, "
            f"current_is_same={'si' if current_is_same else 'no'}"
        )

        self._log_session_created_premarcs(
            "Premarco de sesion marcado como activo",
            selected_guid=ppg_guid_str,
        )
        self._active_session_source_guid = str(ppg_guid_str)

        self._apply_premarc_saved_state(dict(selected_item["state"]))
        self.placement_pnt = self._copy_point3d(selected_item["point"])
        self._sync_placement_point_parameter()
        self._rebuild_placement_mat()
        self._has_confirmed_placement = True
        self._loaded_saved_state = dict(selected_item["state"])

        wall_guid = str(
            selected_item.get("wall_guid", "")
            or selected_item["state"].get("wall_guid", "")
            or ""
        )
        if wall_guid:
            self._try_restore_wall_from_guid(wall_guid)

        print(
            "[Premarc] PPG de sesion cargado como premarco activo editable -> "
            f"restantes_en_contexto={len(self._session_created_premarcs)}"
        )
        return self._activate_selected_premarc_overlay(selected_item["state"])

    def _transform_model_element_list(
        self, elements_list: list, matrix: AllplanGeo.Matrix3D
    ) -> list:
        """Transforma elementos locales a coordenadas reales para modificar PPG."""
        transformed = []
        for element in elements_list or []:
            geo = _geometry_from_model_element(element)
            if geo is None:
                continue
            try:
                geo = AllplanGeo.Transform(geo, matrix)
            except Exception as exc:
                print(f"[Premarc] No se pudo transformar geometria en edicion: {exc}")
                continue
            transformed.append(
                AllplanBasisElements.ModelElement3D(
                    _common_props_from_model_element(element), geo
                )
            )
        return transformed

    def _set_selected_wall_adapter(self, wall_adapter, wall_guid_str: str = "") -> bool:
        """Restaura la seleccion del muro y mantiene la relacion con el PPG."""
        if wall_adapter is None or wall_adapter.IsNull():
            return False

        guid_str = wall_guid_str or str(wall_adapter.GetModelElementUUID())
        self.wall_guid_str = guid_str
        self.wall_select_result.element = wall_adapter
        self.wall_select_result.element_guid = guid_str
        self.wall_select_result.is_selected = True
        self.selected_wall = wall_adapter
        self.detected_wall_thickness = self._get_wall_thickness(wall_adapter)
        self.build_ele.SelectionWall.value = "Seleccionado"
        self.build_ele.SavedWallThickness.value = self.detected_wall_thickness
        print(f"[Premarc] Muro restaurado/seleccionado: {guid_str}")
        return True

    def _try_restore_wall_from_guid(self, wall_guid_str: str) -> bool:
        if not wall_guid_str:
            print("[Premarc] Restore muro -> wall_guid vacio")
            return False
        try:
            wall_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                AllplanEleAdapter.GUID.FromString(wall_guid_str),
                self.coord_input.GetInputViewDocument(),
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo leer wall_guid guardado: {exc}")
            return False
        if wall_adapter is None or wall_adapter.IsNull():
            print(
                "[Premarc] Restore muro -> wall_guid no resolvio un adaptador valido: "
                f"{wall_guid_str}"
            )
            return False
        return self._set_selected_wall_adapter(wall_adapter, wall_guid_str)

    def _try_restore_wall_from_opening(self) -> bool:
        opening_guid_str = str(getattr(self.build_ele.opening_guid, "value", "") or "")
        if not opening_guid_str:
            print("[Premarc] Restore muro -> opening_guid vacio")
            return False
        try:
            opening_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                AllplanEleAdapter.GUID.FromString(opening_guid_str),
                self.coord_input.GetInputViewDocument(),
            )
            if opening_adapter.IsNull():
                print(
                    "[Premarc] Restore muro -> opening_guid sin adaptador valido: "
                    f"{opening_guid_str}"
                )
                return False
            wall_adapter = AllplanEleAdapter.BaseElementAdapterParentElementService.GetParentElement(
                opening_adapter
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo restaurar muro desde opening: {exc}")
            return False
        return self._set_selected_wall_adapter(wall_adapter)

    def _get_saved_placement_reference_point(self):
        point = getattr(self, "placement_pnt", None)
        if isinstance(point, AllplanGeo.Point3D):
            return self._copy_point3d(point)

        if hasattr(self.build_ele, "PlacementPnt"):
            raw_point = getattr(self.build_ele.PlacementPnt, "value", None)
            if isinstance(raw_point, AllplanGeo.Point3D):
                return self._copy_point3d(raw_point)

        return None

    def _get_axis_projection_metrics(self, point: AllplanGeo.Point3D, wall_adapter):
        try:
            axis_ele = AllplanEleAdapter.AxisElementAdapter(wall_adapter)
            if axis_ele.IsNull():
                return None

            wall_axis = axis_ele.GetAxis()
            p0 = wall_axis.StartPoint
            p1 = wall_axis.EndPoint
            dx = p1.X - p0.X
            dy = p1.Y - p0.Y
            axis_length = math.sqrt(dx * dx + dy * dy)
            if axis_length < 1e-9:
                return None

            ux = dx / axis_length
            uy = dy / axis_length
            rel_x = point.X - p0.X
            rel_y = point.Y - p0.Y
            axis_pos = rel_x * ux + rel_y * uy
            normal_dist = abs((-uy * rel_x) + (ux * rel_y))

            if axis_pos < 0.0:
                outside_axis = -axis_pos
            elif axis_pos > axis_length:
                outside_axis = axis_pos - axis_length
            else:
                outside_axis = 0.0

            return {
                "normal_dist": normal_dist,
                "outside_axis": outside_axis,
                "axis_length": axis_length,
                "thickness": float(axis_ele.GetThickness()),
            }
        except Exception:
            return None

    def _try_restore_wall_from_geometry(self) -> bool:
        ref_point = self._get_saved_placement_reference_point()
        if ref_point is None:
            print("[Premarc] Restore muro geometria -> sin punto de referencia")
            return False

        try:
            active_doc = self.coord_input.GetInputViewDocument()
            all_elements = AllplanBaseElements.ElementsSelectService.SelectAllElements(active_doc)
            wall_candidates = BaseElementAdapterFilter.get_wall_tiers(all_elements)
        except Exception as exc:
            print(f"[Premarc] Restore muro geometria -> no se pudieron leer muros: {exc}")
            return False

        if not wall_candidates:
            print("[Premarc] Restore muro geometria -> sin muros candidatos")
            return False

        best_wall = None
        best_guid = ""
        best_score = None
        best_metrics = None

        for wall_adapter in wall_candidates:
            metrics = self._get_axis_projection_metrics(ref_point, wall_adapter)
            if metrics is None:
                continue

            axis_tolerance = max(float(self.width) * 0.5, 500.0)
            normal_tolerance = max(metrics["thickness"] * 1.5, 500.0)
            if metrics["outside_axis"] > axis_tolerance:
                continue
            if metrics["normal_dist"] > normal_tolerance:
                continue

            score = (metrics["outside_axis"] * 10000.0) + metrics["normal_dist"]
            if best_score is None or score < best_score:
                best_score = score
                best_wall = wall_adapter
                best_guid = str(wall_adapter.GetModelElementUUID())
                best_metrics = metrics

        if best_wall is None:
            print(
                "[Premarc] Restore muro geometria -> sin candidato valido "
                f"para point=({ref_point.X:.1f}, {ref_point.Y:.1f}, {ref_point.Z:.1f})"
            )
            return False

        print(
            "[Premarc] Restore muro geometria -> candidato "
            f"{best_guid} con dist_normal={best_metrics['normal_dist']:.1f} mm, "
            f"fuera_eje={best_metrics['outside_axis']:.1f} mm"
        )
        return self._set_selected_wall_adapter(best_wall, best_guid)

    def _reset_wall_selection_for_modification(self, wall_guid_str: str) -> None:
        self.wall_select_result = WallSelectResult()
        self.selected_wall = None

        print(
            "[Premarc] Restore muro modificacion -> "
            f"wall_guid_input={wall_guid_str or '<sin-wall-guid>'}, "
            f"opening_guid_input={str(getattr(self.build_ele.opening_guid, 'value', '') or '<sin-opening>')}"
        )

        if self._try_restore_wall_from_guid(wall_guid_str):
            return

        if self._try_restore_wall_from_opening():
            return

        if self._try_restore_wall_from_geometry():
            return

        self.build_ele.SelectionWall.value = "No seleccionado"
        if self.build_ele.SavedWallThickness.value:
            self.detected_wall_thickness = self.build_ele.SavedWallThickness.value
        print("[Premarc] No se pudo restaurar el muro del premarco")

    def _get_existing_group_hash(self) -> str:
        if hasattr(self.build_ele, "get_hash"):
            try:
                existing_hash = self.build_ele.get_hash()
                if existing_hash:
                    return str(existing_hash)
            except Exception as exc:
                print(f"[Premarc] No se pudo leer hash existente: {exc}")
        return ""

    def _sync_placement_point_parameter(self) -> None:
        """Keep the hidden handle parameter aligned with the active insertion point."""
        if hasattr(self.build_ele, "PlacementPnt"):
            self.build_ele.PlacementPnt.value = self._copy_point3d(self.placement_pnt)

    def _did_opening_placement_change(self, tolerance: float = 0.01) -> bool:
        """Compare current placement against the persisted opening baseline."""
        if self._opening_baseline_point is None:
            return False

        current = self.placement_pnt
        baseline = self._opening_baseline_point

        return (
            abs(current.X - baseline.X) > tolerance
            or abs(current.Y - baseline.Y) > tolerance
            or abs(current.Z - baseline.Z) > tolerance
        )

    def _did_point_change_from_state(
        self,
        state: dict,
        point: AllplanGeo.Point3D,
        tolerance: float = 0.01,
    ) -> bool:
        """Compare a point against the XYZ stored in a SavedState-like dict."""
        if not state:
            return False

        try:
            old_x = float(state.get("X", point.X))
            old_y = float(state.get("Y", point.Y))
            old_z = float(state.get("Z", point.Z))
        except (TypeError, ValueError):
            return False

        return (
            abs(point.X - old_x) > tolerance
            or abs(point.Y - old_y) > tolerance
            or abs(point.Z - old_z) > tolerance
        )

    def _delete_previous_opening_for_reinserted_premarc(
        self, source_state: dict, new_point: AllplanGeo.Point3D
    ) -> bool:
        """When Allplan reinserts an existing premarc after drag, remove the old opening."""
        if not source_state:
            return False

        source_opening_guid = str(source_state.get("opening_guid", "") or "")
        if not source_opening_guid:
            return False

        if not self._did_point_change_from_state(source_state, new_point):
            return False

        previous_guid = str(getattr(self.build_ele.opening_guid, "value", "") or "")
        self.build_ele.opening_guid.value = source_opening_guid

        try:
            deleted = self._delete_wall_opening()
            if deleted:
                print(
                    "[Premarc] Opening anterior eliminado antes de recrear "
                    "premarco reinsertado"
                )
            return deleted
        finally:
            self.build_ele.opening_guid.value = previous_guid

    def _build_premarc_saved_state_dict(
        self, placement_pnt: AllplanGeo.Point3D | None = None
    ) -> dict:
        """Snapshot de configuración de un premarco (misma forma que SavedState)."""
        self.update_params()
        pnt = placement_pnt if placement_pnt is not None else self.placement_pnt
        passama_vals = self.build_ele.PassamaOptions.value
        rebajes_vals = self.build_ele.RebajesOptions.value
        passama_01 = (
            [self._saved_checkbox_01(x) for x in passama_vals] if passama_vals else []
        )
        rebajes_01 = (
            [self._saved_checkbox_01(x) for x in rebajes_vals] if rebajes_vals else []
        )
        encaje = self.build_ele.ComboBoxEncajes.value
        return {
            "X": pnt.X,
            "Y": pnt.Y,
            "Z": pnt.Z,
            "thickness": self.detected_wall_thickness,
            "height": self.heigh,
            "width": self.width,
            "depth": self.thickness_premarc,
            "thickness_wall": self.build_ele.thickness_wall.value,
            "rotation": self.rotation,
            "encaje": encaje,
            "encaje_manual": self.build_ele.EnableManualEncaje.value,
            "encaje_altura": self.build_ele.EncajeAltura.value,
            "encaje_base": self.build_ele.EncajeBase.value,
            "disable_top_xps": self.build_ele.DisableTopXPS.value,
            "disable_bottom_xps": self.build_ele.DisableBottomXPS.value,
            "disable_left_xps": self.build_ele.DisableLeftXPS.value,
            "disable_right_xps": self.build_ele.DisableRightXPS.value,
            "xps_thickness_index": self.build_ele.XPSthicknessInd.value,
            "xps_thickness": self.build_ele.XPSthickness.value,
            "thickness_manual": self.build_ele.thickness.value,
            "enable_manual_thickness": self.build_ele.enable_manual_thickness.value,
            "manual_thickness": self.build_ele.manual_thickness.value,
            "color_manual_thickness": self.build_ele.color_manual_thickness.value,
            "xps_type": self.build_ele.xps_type.value,
            "wall_id": self.build_ele.wall_id.value,
            "fondo_ampits": self.build_ele.fondo_ampits.value,
            "llarg_ampits": self.build_ele.llarg_ampits.value,
            "afegit_ampits": self.build_ele.afegit_ampits.value,
            "retall_ampits": self.build_ele.retall_ampits.value,
            "ComboBoxAbiertoCerrado": self.build_ele.ComboBoxAbiertoCerrado.value,
            "EnableRetallGanxo": self.build_ele.EnableRetallGanxo.value,
            "Z_RetallGanxo": self.build_ele.Z_RetallGanxo.value,
            "ComboBoxPendiente": self.build_ele.ComboBoxPendiente.value,
            "PassamaOptions": passama_01,
            "ComboBoxEncajes": encaje,
            "EnableManualEncaje": self.build_ele.EnableManualEncaje.value,
            "EncajeBase": self.build_ele.EncajeBase.value,
            "EncajeAltura": self.build_ele.EncajeAltura.value,
            "RebajesOptions": rebajes_01,
            "ComboBoxPersianas": self.build_ele.ComboBoxPersianas.value,
            "PersianaHeight": self.build_ele.PersianaHeight.value,
            "PersianaWidth": self.build_ele.PersianaWidth.value,
            "ComboBoxEscuadras": self.build_ele.ComboBoxEscuadras.value,
            "ComboBoxTubos": self.build_ele.ComboBoxTubos.value,
            "TypeTubos": self.build_ele.TypeTubos.value,
            "CheckBoxRealSpace": self.build_ele.CheckBoxRealSpace.value,
            "CheckBoxInnerSpace": self.build_ele.CheckBoxInnerSpace.value,
            "opening_guid": self.build_ele.opening_guid.value,
            "wall_guid": (
                self.wall_select_result.element_guid
                or getattr(self, "wall_guid_str", "")
                or (
                    str(self.selected_wall.GetModelElementUUID())
                    if self.selected_wall
                    else ""
                )
            ),
            "pmp_pare": (
                self.get_wall_material_name(self.selected_wall)
                if self.selected_wall
                else ""
            ),
            "ShowAccessorUPerimeter": self.build_ele.ShowAccessorUPerimeter.value,
        }

    def _apply_premarc_saved_state(self, state: dict) -> None:
        """Restaura paleta e instancia desde un snapshot SavedState."""
        if not state:
            return

        saved_pnt = AllplanGeo.Point3D(state["X"], state["Y"], state["Z"])
        self.placement_pnt = saved_pnt
        self.rotation = state["rotation"]
        self.build_ele.rotation.value = self.rotation
        self.heigh = state["height"]
        self.width = state["width"]
        self.build_ele.heigh.value = state["height"]
        self.build_ele.width.value = state["width"]
        self.thickness = state["depth"]
        self.thickness_premarc = state["depth"]
        self.thickness_wall = state["thickness_wall"]
        self.build_ele.thickness_wall.value = state["thickness_wall"]
        self.detected_wall_thickness = state.get(
            "thickness", self.detected_wall_thickness
        )

        encaje = state.get("ComboBoxEncajes", state.get("encaje", ""))
        self.build_ele.ComboBoxEncajes.value = encaje
        self.build_ele.EnableManualEncaje.value = state.get(
            "EnableManualEncaje", state.get("encaje_manual", False)
        )
        self.build_ele.EncajeBase.value = state.get(
            "EncajeBase", state.get("encaje_base", 0)
        )
        self.build_ele.EncajeAltura.value = state.get(
            "EncajeAltura", state.get("encaje_altura", 0)
        )
        self.build_ele.DisableTopXPS.value = state["disable_top_xps"]
        self.build_ele.DisableBottomXPS.value = state["disable_bottom_xps"]
        self.build_ele.DisableLeftXPS.value = state["disable_left_xps"]
        self.build_ele.DisableRightXPS.value = state["disable_right_xps"]
        self.build_ele.XPSthicknessInd.value = state["xps_thickness_index"]
        self.build_ele.XPSthickness.value = state["xps_thickness"]
        self.build_ele.ComboBoxAbiertoCerrado.value = state["ComboBoxAbiertoCerrado"]
        self.build_ele.EnableRetallGanxo.value = state["EnableRetallGanxo"]
        self.build_ele.Z_RetallGanxo.value = state["Z_RetallGanxo"]
        self.build_ele.ComboBoxPendiente.value = state["ComboBoxPendiente"]
        self.build_ele.ShowAccessorUPerimeter.value = state["ShowAccessorUPerimeter"]
        self.build_ele.PassamaOptions.value = [
            int(x) for x in state.get("PassamaOptions", [])
        ]
        self.build_ele.RebajesOptions.value = [
            int(x) for x in state.get("RebajesOptions", [])
        ]
        self.build_ele.ComboBoxPersianas.value = state["ComboBoxPersianas"]
        self.build_ele.PersianaHeight.value = state.get(
            "PersianaHeight", self.build_ele.PersianaHeight.value
        )
        self.build_ele.PersianaWidth.value = state.get(
            "PersianaWidth", self.build_ele.PersianaWidth.value
        )
        self.build_ele.ComboBoxEscuadras.value = state["ComboBoxEscuadras"]
        self.build_ele.ComboBoxTubos.value = state["ComboBoxTubos"]
        self.build_ele.TypeTubos.value = state["TypeTubos"]
        self.build_ele.CheckBoxRealSpace.value = state["CheckBoxRealSpace"]
        self.build_ele.CheckBoxInnerSpace.value = state["CheckBoxInnerSpace"]
        self.build_ele.thickness.value = state["thickness_manual"]
        self.build_ele.enable_manual_thickness.value = state["enable_manual_thickness"]
        self.build_ele.manual_thickness.value = state["manual_thickness"]
        self.build_ele.color_manual_thickness.value = state["color_manual_thickness"]
        self.build_ele.xps_type.value = state["xps_type"]
        self.build_ele.fondo_ampits.value = state["fondo_ampits"]
        self.build_ele.llarg_ampits.value = state["llarg_ampits"]
        self.build_ele.afegit_ampits.value = state["afegit_ampits"]
        self.build_ele.retall_ampits.value = state["retall_ampits"]
        self.build_ele.wall_id.value = state.get(
            "pmp_pare", state.get("wall_id", "")
        )
        self.build_ele.opening_guid.value = state.get("opening_guid", "")

        if self.build_ele.enable_manual_thickness.value:
            self.load_color_manual_thickness()
            self.color_premarc = self.build_ele.color_manual_thickness.value
        else:
            thickness_key = int(self.thickness_premarc)
            self.color_premarc = COLOR_THICKNESS_MAP[thickness_key]

        self.update_params()
        self._rebuild_placement_mat()
        self._sync_placement_point_parameter()

    def _queue_current_premarc_for_later_creation(self) -> bool:
        """Guarda el punto confirmado y deja la creacion real para el cierre."""
        if not self._has_confirmed_placement:
            print("[Premarc] No hay premarco confirmado para agregar a la cola")
            return True

        if not self.selected_wall:
            PythonUtility.ShowMessageBox(
                "Seleccione un muro antes de posicionar otro premarco.",
                PythonUtility.MB_OK,
            )
            return False

        if self.placement_pnt == AllplanGeo.Point3D():
            print("[Premarc] Punto confirmado invalido; no se agrega a la cola")
            return True

        self.update_params()
        self.thickness_premarc = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )
        self._pending_premarcs.append(
            {
                "point": self._copy_point3d(self.placement_pnt),
                "state": self._build_premarc_saved_state_dict(self.placement_pnt),
                "source_state": (
                    dict(self._loaded_saved_state) if self._loaded_saved_state else {}
                ),
            }
        )
        self.placement_pnt = AllplanGeo.Point3D()
        self._has_confirmed_placement = False
        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""

        print(
            f"[Premarc] Premarco agregado a la cola: {len(self._pending_premarcs)} pendiente(s)"
        )
        return True

    def _validate_before_final_creation(self) -> bool:
        self._final_creation_cancelled_by_user = False
        self.update_params()

        if not self.selected_wall and not self.is_modification_mode:
            PythonUtility.ShowMessageBox(
                "Seleccione un muro antes de generar los premarcos.",
                PythonUtility.MB_OK,
            )
            return False

        if self.build_ele.enable_manual_thickness.value:
            self.save_color_manual_thickness()
        if self.build_ele.EnableManualEncaje.value and not self.disable_save_encaje:
            self.save_manual_encaje()

        if self.check_falcas_and_persianas():
            resp = PythonUtility.ShowMessageBox(
                f"Selecciono Falcas, pero no hay persianas.\n" "Â¿Desea continuar?",
                PythonUtility.MB_OKCANCEL,
            )
            if resp == PythonUtility.IDCANCEL:
                self._final_creation_cancelled_by_user = True
                return False

        return True

    def _create_pending_premarcs(self) -> bool:
        if self._has_confirmed_placement:
            if not self._queue_current_premarc_for_later_creation():
                return False

        if not self._pending_premarcs:
            print("[Premarc] No hay premarcos pendientes para generar")
            return False

        if not self._validate_before_final_creation():
            return False

        pending_items = list(self._pending_premarcs)
        self._pending_premarcs = []

        for index, item in enumerate(pending_items, start=1):
            point = item["point"]
            self._apply_premarc_saved_state(item["state"])
            self.placement_pnt = self._copy_point3d(point)
            self._delete_previous_opening_for_reinserted_premarc(
                item.get("source_state", {}), point
            )
            if hasattr(self.build_ele, "opening_guid"):
                self.build_ele.opening_guid.value = ""

            print(
                f"[Premarc] Generando premarco {index}/{len(pending_items)} en "
                f"({point.X:.1f}, {point.Y:.1f}, {point.Z:.1f})"
            )
            if self.selected_wall:
                self._create_wall_opening()
            self._create_union_frames = True
            self._execute()

        self.placement_pnt = AllplanGeo.Point3D()
        self._has_confirmed_placement = False
        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""
        self._loaded_saved_state = {}

        return True

    def _append_preview_model_at_current_matrix(self, preview_elements, local_model):
        for element in local_model or []:
            geo = _geometry_from_model_element(element)
            if geo is None:
                continue
            try:
                geo = AllplanGeo.Transform(geo, self.placement_mat)
            except Exception as e:
                print(f"[Premarc] No se pudo transformar preview acumulado: {e}")
                continue
            preview_elements.append(
                AllplanBasisElements.ModelElement3D(
                    _common_props_from_model_element(element), geo
                )
            )

    def _make_preview_relative_to_point(self, preview_elements, point):
        """Convert global preview geometry to the local space used by placement_point."""
        if not preview_elements or point is None or point == AllplanGeo.Point3D():
            return preview_elements

        offset_mat = AllplanGeo.Matrix3D()
        offset_mat.SetTranslation(
            AllplanGeo.Vector3D(-point.X, -point.Y, -point.Z)
        )

        relative_elements = []
        for element in preview_elements:
            geo = _geometry_from_model_element(element)
            if geo is None:
                continue
            try:
                geo = AllplanGeo.Transform(geo, offset_mat)
            except Exception as e:
                print(f"[Premarc] No se pudo relativizar preview de contexto: {e}")
                continue
            relative_elements.append(
                AllplanBasisElements.ModelElement3D(
                    _common_props_from_model_element(element), geo
                )
            )
        return relative_elements

    def _append_session_created_premarcs_preview(
        self, preview_elements, exclude_point: AllplanGeo.Point3D | None = None
    ):
        rendered = 0
        active_guid = str(self._active_session_source_guid or "")
        for item in self._session_created_premarcs:
            point = item.get("point")
            state = item.get("state", {})
            item_guid = str(item.get("ppg_guid", "") or "")
            if point is None or not state:
                continue
            if active_guid and item_guid == active_guid:
                continue
            if (
                exclude_point is not None
                and abs(point.X - exclude_point.X) <= 0.01
                and abs(point.Y - exclude_point.Y) <= 0.01
                and abs(point.Z - exclude_point.Z) <= 0.01
            ):
                continue
            self._apply_premarc_saved_state(state)
            self.placement_pnt = self._copy_point3d(point)
            self._rebuild_placement_mat()
            local_model = self._create_premarc_placement_preview_only()
            self._append_preview_model_at_current_matrix(preview_elements, local_model)
            rendered += 1
        if rendered:
            print(f"[Premarc] Contexto visual de sesion dibujado: {rendered} premarco(s)")

    def _build_session_selection_preview_elements(self) -> list[Any]:
        """Build preview geometry for session selection: stored premarcs + active one."""
        saved_pnt = self.placement_pnt
        saved_mat = self.placement_mat
        saved_preview_flag = self._in_placement_preview
        saved_state = None
        if saved_pnt != AllplanGeo.Point3D() and self._has_confirmed_placement:
            saved_state = self._build_premarc_saved_state_dict(saved_pnt)

        preview_elements = []
        try:
            self._in_placement_preview = True
            self._append_session_created_premarcs_preview(preview_elements)

            if self._has_confirmed_placement and saved_pnt != AllplanGeo.Point3D():
                if saved_state:
                    self._apply_premarc_saved_state(saved_state)
                else:
                    self.placement_pnt = self._copy_point3d(saved_pnt)
                self._rebuild_placement_mat()
                local_model = self._create_premarc_placement_preview_only()
                self._append_preview_model_at_current_matrix(
                    preview_elements, local_model
                )
        finally:
            self._in_placement_preview = saved_preview_flag
            if saved_state:
                self._apply_premarc_saved_state(saved_state)
            else:
                self.placement_pnt = saved_pnt
                self.placement_mat = saved_mat

        return preview_elements

    def _clear_session_selection_preview_context(self) -> None:
        if not self._session_selection_preview_elements:
            return
        try:
            AllplanBaseElements.DrawElementPreview(
                self.document,
                AllplanGeo.Matrix3D(),
                list(self._session_selection_preview_elements),
                True,
                None,
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo limpiar preview de seleccion de sesion: {exc}")
        self._session_selection_preview_elements = []

    def _draw_session_selection_preview_context(self, clear_before: bool = False) -> bool:
        self._log_session_created_premarcs(
            "Antes de dibujar preview de seleccion",
            selected_guid=self._active_session_source_guid,
        )
        preview_elements = self._build_session_selection_preview_elements()
        if not preview_elements:
            print("[Premarc] Preview de seleccion de sesion vacio")
            return False

        if clear_before:
            self._clear_session_selection_preview_context()

        self._session_selection_preview_elements = list(preview_elements)
        try:
            print(
                "[Premarc][SESSION] Preview seleccion construido -> "
                f"preview_elements={len(preview_elements)}"
            )
            AllplanBaseElements.DrawElementPreview(
                self.document,
                AllplanGeo.Matrix3D(),
                preview_elements,
                False,
                None,
            )
            print(
                "[Premarc] Preview de seleccion de sesion dibujado -> "
                f"session_queue={len(self._session_created_premarcs)}, "
                f"has_active={'si' if self._has_confirmed_placement and self.placement_pnt != AllplanGeo.Point3D() else 'no'}"
            )
            return True
        except Exception as exc:
            print(f"[Premarc] No se pudo dibujar preview de seleccion de sesion: {exc}")
            self._session_selection_preview_elements = []
            return False

    def _redraw_session_created_premarcs_context(self) -> bool:
        """Clear transient selection previews.

        Session premarcs are already materialized as real PPGs in the model, so
        they must not be redrawn as auxiliary previews here.
        """
        self._log_session_created_premarcs(
            "Antes de refrescar contexto de sesion",
            selected_guid=self._active_session_source_guid,
        )
        self._clear_session_selection_preview_context()
        if not self._session_created_premarcs:
            print("[Premarc] Contexto visual de sesion vacio tras eliminar")
            return False
        print(
            "[Premarc] Contexto visual de sesion materializado; no se dibuja preview auxiliar "
            f"({len(self._session_created_premarcs)} premarco(s))"
        )
        return True

    def _build_session_created_premarcs_context_preview(self) -> list[Any]:
        """Construye el contexto visual de los premarcos de sesion restantes en coordenadas globales."""
        if not self._session_created_premarcs:
            return []

        saved_pnt = self.placement_pnt
        saved_mat = self.placement_mat
        saved_preview_flag = self._in_placement_preview
        saved_state = None
        if saved_pnt != AllplanGeo.Point3D() and self._has_confirmed_placement:
            saved_state = self._build_premarc_saved_state_dict(saved_pnt)

        preview_elements = []
        try:
            self._in_placement_preview = True
            self._append_session_created_premarcs_preview(preview_elements)
        finally:
            self._in_placement_preview = saved_preview_flag
            if saved_state:
                self._apply_premarc_saved_state(saved_state)
            else:
                self.placement_pnt = saved_pnt
                self.placement_mat = saved_mat

        return preview_elements

    def _create_accumulated_placement_preview(self, active_point):
        """Preview del activo/pendientes no materializados.

        Los PPGs de `_session_created_premarcs` ya existen en el modelo y no se
        deben volver a dibujar como preview auxiliar durante una recolocacion.
        """
        saved_pnt = self.placement_pnt
        saved_mat = self.placement_mat
        saved_preview_flag = self._in_placement_preview
        working_state = None
        if saved_pnt != AllplanGeo.Point3D():
            working_state = self._build_premarc_saved_state_dict(saved_pnt)
        preview_elements = []
        active_preview_point = None
        if active_point is not None and hasattr(active_point, "X"):
            active_preview_point = self._copy_point3d(active_point)
        elif saved_pnt != AllplanGeo.Point3D():
            active_preview_point = self._copy_point3d(saved_pnt)

        try:
            self._in_placement_preview = True

            for item in self._pending_premarcs:
                self._apply_premarc_saved_state(item["state"])
                self.placement_pnt = self._copy_point3d(item["point"])
                local_model = self._create_premarc_placement_preview_only()
                self._append_preview_model_at_current_matrix(
                    preview_elements, local_model
                )

            if working_state:
                self._apply_premarc_saved_state(working_state)
                if active_preview_point is not None:
                    self.placement_pnt = self._copy_point3d(active_preview_point)
                    self._rebuild_placement_mat()
                local_model = self._create_premarc_placement_preview_only()
                self._append_preview_model_at_current_matrix(
                    preview_elements, local_model
                )
            elif active_preview_point is not None:
                self.placement_pnt = self._copy_point3d(active_preview_point)
                self._rebuild_placement_mat()
                local_model = self._create_premarc_placement_preview_only()
                self._append_preview_model_at_current_matrix(
                    preview_elements, local_model
                )
        finally:
            self._in_placement_preview = saved_preview_flag
            if working_state:
                self._apply_premarc_saved_state(working_state)
            else:
                self.placement_pnt = saved_pnt
                self.placement_mat = saved_mat

        return preview_elements

    def on_control_event(self, event_id: int):
        # Reiniciar vector_length para recalcular con los nuevos puntos
        if event_id == 1000:
            self.build_ele.SelectionWall.value = "No seleccionado"
            self.wall_select_result = WallSelectResult()
            self.selected_wall = None
            self._pending_premarcs = []
            self._active_session_source_guid = ""
            self._has_confirmed_placement = False
            self.interactor_state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result, "Seleccione el muro donde colocar el premarco"
            )
            self.script_object_interactor.start_input(self.coord_input)
            return True
        elif event_id == 1001:
            if self.is_modification_mode:
                return False

            if not self._create_current_premarc_ppg_without_opening(
                register_session_item=True,
                reset_active_after_create=True,
            ):
                return True

            if not self.selected_wall:
                self.start_input()
            else:
                self.build_ele.SelectionWall.value = "Seleccionado"
                self._start_placement_point_input()

            if self.script_object_interactor:
                self.script_object_interactor.start_input(self.coord_input)
            return True
        elif event_id == 1002:
            if not self._start_palette_reposition_input():
                return True

            if self.script_object_interactor:
                self.script_object_interactor.start_input(self.coord_input)
            return True
        elif event_id == 1003:
            if not self.is_modification_mode:
                print(
                    "[Premarc] Click boton Eliminar (sesion) -> "
                    f"active_guid={self._active_session_source_guid or '<sin-guid>'}, "
                    f"placement=({self.placement_pnt.X:.1f}, {self.placement_pnt.Y:.1f}, {self.placement_pnt.Z:.1f}), "
                    f"session_queue={len(self._session_created_premarcs)}"
                )
                self._discard_active_session_premarc_from_creation()
                return True
            previous_delete_requested = self._delete_current_premarc_requested
            self._delete_current_premarc_requested = True
            self._clear_selected_premarc_overlay()
            print(
                "[Premarc] Click boton Eliminar -> "
                f"delete_requested={self._delete_current_premarc_requested}, "
                f"previous_delete_requested={previous_delete_requested}, "
                f"placement=({self.placement_pnt.X:.1f}, {self.placement_pnt.Y:.1f}, {self.placement_pnt.Z:.1f}), "
                f"opening_guid={str(getattr(getattr(self.build_ele, 'opening_guid', None), 'value', '') or '<sin-opening>')}, "
                f"cached_ppg_guid={self._modification_ppg_guid_str or '<sin-guid>'}"
            )
            print("[Premarc] Intentando eliminar premarco inmediatamente desde el boton")
            deleted_now = self._delete_modified_premarc_direct()
            if deleted_now:
                self._delete_current_premarc_requested = False
                self.script_object_interactor = None
                self.interactor_state = STOPPED
                print("[Premarc] Premarco eliminado inmediatamente desde el boton")
            else:
                print(
                    "[Premarc] Eliminacion inmediata no confirmada; "
                    "se reintentara al cerrar la PPG"
                )
            return True
        elif event_id == 1055:
            print(
                "[Premarc][SELECT] Click boton seleccionar -> "
                f"session_queue={len(self._session_created_premarcs)}, "
                f"active_guid={self._active_session_source_guid or '<sin-guid>'}, "
                f"placement={self._format_point3d_for_log(self.placement_pnt)}"
            )
            self._log_session_created_premarcs(
                "Click boton seleccionar",
                selected_guid=self._active_session_source_guid,
            )
            self._clear_selected_premarc_overlay()
            self._clear_session_selection_preview_context()
            self.premarc_select_result = PremarcSelectResult()
            self.pending_premarc_select_result = PendingPremarcSelectResult()

            has_active_preview = (
                self._has_confirmed_placement
                and self.placement_pnt != AllplanGeo.Point3D()
            )
            active_guid = str(self._active_session_source_guid or "")
            active_guid_in_queue = self._is_session_guid_in_queue(active_guid)
            has_only_active_preview = (
                has_active_preview and not active_guid_in_queue
            )

            if has_only_active_preview:
                print(
                    "[Premarc][SELECT] Seleccion directa del activo preview -> "
                    f"active_guid={self._active_session_source_guid or '<sin-guid>'}, "
                    f"point={self._format_point3d_for_log(self.placement_pnt)}"
                )
                active_state = self._build_premarc_saved_state_dict(self.placement_pnt)
                self._activate_selected_premarc_overlay(active_state)
                return True

            if self._session_created_premarcs:
                self.interactor_state = SELECTING_EXISTING_PREMARC
                self.script_object_interactor = ExistingPremarcSelectInteractor(
                    self.premarc_select_result,
                    "Seleccione el premarco (PPG) materializado en el dibujo",
                    owner=self,
                )
            elif has_active_preview:
                self._draw_session_selection_preview_context(clear_before=False)
                self.interactor_state = SELECTING_PENDING_PREMARC
                self.script_object_interactor = PendingPremarcSelectInteractor(
                    self.pending_premarc_select_result,
                    "Seleccione el premarco preview o materializado a editar",
                    owner=self,
                )
            else:
                self._active_session_source_guid = ""
                self.interactor_state = SELECTING_EXISTING_PREMARC
                self.script_object_interactor = ExistingPremarcSelectInteractor(
                    self.premarc_select_result,
                    "Seleccione el premarco (PPG) materializado en el dibujo",
                    owner=self,
                )
            self.script_object_interactor.start_input(self.coord_input)
            return True
        elif event_id == 1056:
            print("[Premarc] Evento 1056 ignorado: selector de premarco deshabilitado temporalmente")
            return True
        else:
            return False

    def modify_element_property(self, name: str, _value: Any) -> bool:
        """modify the element property

        Args:
            name:   name
            _value: value

        Returns:
            update palette state
        """

        if name == "INPUT_PMP_PREMARC_LABELS":
            value = str(_value).strip()
            if value and "$<" not in value:
                self._user_label_override = value
            else:
                self._user_label_override = None
            return False

        if name == "id_premarc":
            self.build_ele.INPUT_PMP_ID_PREMARC.value = str(_value).strip()
            return False

        if name == "INPUT_PMP_ID_PREMARC":
            self.build_ele.id_premarc.value = str(_value).strip()
            return False

        if name == "afegit_ampits":
            self.afegit_ampits = self.build_ele.afegit_ampits.value
            # self.build_ele.INPUT_PMP_FG_AMPIT_AFEGIT.value = self.afegit_ampits
            self.afegit_ampits_manual = True
            return False
        # if name == "INPUT_PMP_FG_AMPIT_AFEGIT":
        #     self.afegit_ampits = self.build_ele.INPUT_PMP_FG_AMPIT_AFEGIT.value
        #     self.build_ele.afegit_ampits.value = self.afegit_ampits
        #     self.afegit_ampits_manual = True
        #     return False

        if name == "retall_ampits":
            self.retall_ampits = self.build_ele.retall_ampits.value
            # self.build_ele.INPUT_PMP_FG_AMPIT_RETALL.value = self.retall_ampits
            self.retall_ampits_manual = True
            return False
        if name == "INPUT_PMP_FG_AMPIT_RETALL":
            # self.retall_ampits = self.build_ele.INPUT_PMP_FG_AMPIT_RETALL.value
            self.build_ele.retall_ampits.value = self.retall_ampits
            self.retall_ampits_manual = True
            return False

        if name == "enable_manual_thickness":
            self.update_pallete_values()
            if _value == True:
                self.load_color_manual_thickness()  # delegate to visblility control for color
                self.thickness_premarc = self.build_ele.manual_thickness.value
                self.thickness = self.build_ele.manual_thickness.value
            else:
                self.load_color_thickness_api()
                self.build_ele.color_manual_thickness_visible.value = False
                self.thickness_premarc = self.build_ele.thickness.value
                self.thickness = self.build_ele.thickness.value
            return True

        if name == "color_manual_thickness":
            # Check if color is used

            # Check if color is used in colors default for premarcs api
            list_colors = list(COLOR_THICKNESS_MAP.items()) + self.list_color
            for thickness, color in list_colors:
                if int(_value) == int(color):
                    results = PythonUtility.ShowMessageBox(
                        f"El color {_value} ya está siendo usado para el fondo de {thickness}. \n ¿Desea seleccionar otro color?\n",
                        PythonUtility.MB_YESNO,
                    )
                    if results == PythonUtility.IDYES:
                        self.load_color_manual_thickness()
                        return True
                    else:
                        return False
            return True

        if name == "rotation":
            self.rotation = float(_value)
            return True

        if name == "manual_thickness":
            self.load_color_manual_thickness()
            self.thickness_premarc = _value  # manage value
            self.thickness = _value
            return True

        if name == "thickness":
            self.load_color_thickness_api()
            self.thickness_premarc = _value
            self.thickness = _value
            self.update_pallete_values()
            return True

        if name == "premarc_PE":
            self.load_premarc_PE_checkbox()
            return True

        # if self.interactor_state == RUNNING:
        #     self.start_input()

        #     if self.script_object_interactor:
        #         self.script_object_interactor.start_input(self.coord_input)

        elif self.interactor_state == STOPPED:
            self.start_next_input()

        return False

    def move_handle(
        self, handle_prop: HandleProperties, input_pnt: AllplanGeo.Point3D
    ) -> CreateElementResult:

        if handle_prop.handle_id == "PlacementHandle":
            if self._placement_handle_start_pnt is None:
                self._placement_handle_start_pnt = self._copy_point3d(
                    self.placement_pnt
                )

            self.placement_pnt = self._placement_handle_start_pnt + AllplanGeo.Vector3D(
                input_pnt
            )
            self._sync_placement_point_parameter()
            self._rebuild_placement_mat()
            self._should_recreate_opening_after_handle = self.is_modification_mode
            return self.execute()

        HandlePropertiesService.update_property_value(
            self.build_ele, handle_prop, input_pnt
        )

        return self.execute()

    def on_handle_input_done(self, handle_prop: HandleProperties) -> bool:
        if handle_prop.handle_id != "PlacementHandle":
            return False

        self._placement_handle_start_pnt = None

        if not self._should_recreate_opening_after_handle:
            return False

        self._should_recreate_opening_after_handle = False
        self._recreate_wall_opening()
        return True

    def _create_union_frame_elements(self):
        """
        Crea solo la unión de frames (lógica extraída de on_cancel_function)
        """
        model_ele_list = ModelEleList()

        layer_frame_id = AllplanBaseElements.LayerService.GetIDByShortName(
            FRAME_LAYER, self.document
        )
        props_frame = AllplanBaseElements.CommonProperties()
        props_frame.Color = self.get_color_by_thickness(int(self.thickness_premarc))
        print(f"Color frame: {props_frame.Color}")
        props_frame.Layer = layer_frame_id

        polyhedrons = self.create_premarc_frame()
        valid_polyhedrons = []
        for i, poly in enumerate(polyhedrons):
            if poly and poly.IsValid():
                valid_polyhedrons.append(poly)
            else:
                print(f"Poliedro {i} no es válido en on_cancel_function")

        if len(valid_polyhedrons) > 1:
            polyhedron_list = AllplanGeo.Polyhedron3DList()
            for poly in valid_polyhedrons:
                polyhedron_list.append(poly)

            success, union_final = AllplanGeo.MakeUnion(polyhedron_list)

            if success and union_final.IsValid():
                model_ele_list.append_geometry_3d(union_final, props_frame)

        return model_ele_list

    def _rebuild_placement_mat(self):
        """Rebuild placement_mat from current rotation + placement_pnt.
        Called before every execute/preview so the matrix is never stale."""
        self.placement_mat = AllplanGeo.Matrix3D()
        self.placement_mat.SetRotation(
            AllplanGeo.Line3D(
                AllplanGeo.Point3D(
                    self.placement_pnt.X, self.placement_pnt.Y, self.placement_pnt.Z
                ),
                AllplanGeo.Point3D(
                    self.placement_pnt.X,
                    self.placement_pnt.Y,
                    self.placement_pnt.Z + 100,
                ),
            ),
            AllplanGeo.Angle.FromDeg(self.rotation),
        )
        self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.placement_pnt))

    def execute(self) -> CreateElementResult:
        print(
            "[Premarc][EXECUTE] execute -> "
            f"session_queue={len(self._session_created_premarcs)}, "
            f"active_guid={self._active_session_source_guid or '<sin-guid>'}, "
            f"placement={self._format_point3d_for_log(self.placement_pnt)}, "
            f"has_confirmed={'si' if self._has_confirmed_placement else 'no'}, "
            f"overlay_active={'si' if self._selected_premarc_overlay_active else 'no'}"
        )
        # if self._should_create_opening:
        #     PythonUtility.ShowMessageBox(
        #         f"Creando opening en muro: {self.selected_wall}?",
        #         PythonUtility.MB_OK
        #     )
        #     self._create_wall_opening()
        #     self._should_create_opening = False

        # TODO Delete this
        # if self.selected_wall:
        #     print(f"[Premarc] execute() tiene muro: {self.wall_select_result.element_guid}")
        #     PythonUtility.ShowMessageBox("Tiene muro seleccionado",  PythonUtility.MB_OK)
        # else:
        #     print("[Premarc] execute() sin muro seleccionado")
        #     PythonUtility.ShowMessageBox("No tiene muro seleccionado", PythonUtility.MB_OK)

        # input_data = self.getValuesFromInputDataPallet()
        # print(f"Input data: {input_data}")
        # self.crearListaAbiertoCerrado()
        # self.load_radio_buttons_pendent()
        z_unique = z_unique_as_int(self.build_ele.z_unique.value)
        if z_unique <= 0:
            z_unique = int(random.random() * 3600)
            self.build_ele.z_unique.value = z_unique
        self.thickness_premarc = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )

        if not self.selected_wall and not self.is_modification_mode:
            return CreateElementResult([])

        if self._palette_reposition_active and not self._palette_reposition_has_new_point:
            return CreateElementResult(
                elements=[],
                handles=[],
                placement_point=AllplanGeo.Point3D(),
            )

        if not self.is_modification_mode and self._pending_premarcs:
            active_point = (
                self.placement_pnt
                if self.placement_pnt != AllplanGeo.Point3D()
                else None
            )
            preview_elements = self._create_accumulated_placement_preview(active_point)
            return CreateElementResult(
                elements=preview_elements,
                handles=[],
                placement_point=AllplanGeo.Point3D(),
            )

        if self.placement_pnt == AllplanGeo.Point3D():
            return CreateElementResult([])

        preview_elements = []

        self._rebuild_placement_mat()

        premarc_elements = self.create_premarcs_group()
        preview_elements = self._make_preview_relative_to_point(
            preview_elements, self.placement_pnt
        )
        selection_overlay = self._make_preview_relative_to_point(
            self._get_active_selected_premarc_overlay(), self.placement_pnt
        )
        if selection_overlay:
            print(
                "[Premarc][EXECUTE] Overlay de seleccion adjuntado al execute -> "
                f"selection_overlay={len(selection_overlay)}"
            )

        return CreateElementResult(
            elements=preview_elements + premarc_elements,
            handles=self.handle_list,
            preview_elements=selection_overlay,
            placement_point=self.placement_pnt,
        )

    def _execute(self):
        """Fuerza la creación final de elementos directamente en el documento.
        Solo llamar desde on_cancel_function, no desde el bucle de preview.
        Permite que el opening_guid (y cualquier otro estado post-ESC) quede
        guardado en el PythonPart que escribe el framework al confirmar.

        IMPORTANTE: usa solo traslación en CreateElements. La rotación ya está
        embebida en placement_matrix de cada PythonPart individual (igual que
        hace el framework en execute() vía insert_matrix + placement_matrix).
        Usar placement_mat aquí causaría doble rotación."""
        z_unique = z_unique_as_int(self.build_ele.z_unique.value)
        if z_unique <= 0:
            z_unique = int(random.random() * 3600)
            self.build_ele.z_unique.value = z_unique
        self.thickness_premarc = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )

        if self.placement_pnt == AllplanGeo.Point3D():
            return
        if not self.selected_wall and not self.is_modification_mode:
            return

        self._rebuild_placement_mat()
        premarc_elements = self.create_premarcs_group()

        # Geometria local: tanto creacion como modificacion necesitan la matriz de insercion.
        trans_mat = AllplanGeo.Matrix3D()
        trans_mat.SetTranslation(AllplanGeo.Vector3D(self.placement_pnt))

        return AllplanBaseElements.CreateElements(
            self.document,
            trans_mat,
            premarc_elements,
            self.modification_ele_list if self.is_modification_mode else [],
            None,
        )

    def _get_adapter_debug_values(self, adapter):
        name = "<sin-name>"
        type_guid = "<sin-type>"
        model_guid = ""

        try:
            name = str(adapter.GetDisplayName())
        except Exception:
            pass

        try:
            type_guid = str(adapter.GetElementAdapterType().GetGuid())
        except Exception:
            pass

        try:
            model_guid = str(adapter.GetModelElementUUID())
        except Exception:
            pass

        return name, type_guid, model_guid

    def _is_invalid_modification_adapter(self, name: str, model_guid: str) -> bool:
        normalized_name = str(name or "").strip().lower()
        normalized_guid = str(model_guid or "").strip().lower().strip("{}")

        return (
            not normalized_guid
            or normalized_guid.startswith(ZERO_MODEL_GUID)
            or normalized_name == "undefined element"
        )

    def _cache_modification_ppg_guid(self) -> None:
        """Guarda el GUID del PPG activo antes de tocar openings/muro."""
        if self._modification_ppg_guid_str:
            return

        ppg_adapter = self._get_modification_root_adapter()
        if ppg_adapter is None or ppg_adapter.IsNull():
            ppg_adapter = self._get_document_manager_modification_root_adapter()
        if ppg_adapter is None or ppg_adapter.IsNull():
            print("[Premarc] No se pudo cachear GUID del PPG en modificacion")
            return

        name, _type_guid, model_guid = self._get_adapter_debug_values(ppg_adapter)
        if self._is_invalid_modification_adapter(name, model_guid):
            print(
                "[Premarc] GUID del PPG no cacheado: adapter invalido "
                f"name={name}, model_guid={model_guid or '<sin-guid>'}"
            )
            return

        self._modification_ppg_adapter = ppg_adapter
        self._modification_ppg_guid_str = model_guid
        print(f"[Premarc] PPG original cacheado: {self._modification_ppg_guid_str}")

    def _get_cached_modification_adapter_object(self):
        adapter = getattr(self, "_modification_ppg_adapter", None)
        if adapter is None:
            print("[Premarc] Sin adapter PPG cacheado en memoria")
            return None

        try:
            if adapter.IsNull():
                print("[Premarc] Adapter PPG cacheado en memoria es nulo")
                return None
        except Exception as exc:
            print(f"[Premarc] Adapter PPG cacheado en memoria invalido: {exc}")
            return None

        try:
            model_guid = str(adapter.GetModelElementUUID())
        except Exception:
            model_guid = ""

        print(
            "[Premarc] Adapter PPG cacheado en memoria reutilizado -> "
            f"model_guid={model_guid or '<sin-guid>'}"
        )
        return adapter

    def _get_document_manager_pythonpart_adapter(self):
        try:
            from DocumentManager import DocumentManager

            adapter = DocumentManager.get_instance().pythonpart_element
        except Exception as exc:
            print(f"[Premarc] No se pudo leer pythonpart_element del DocumentManager: {exc}")
            return None

        if adapter is None:
            print("[Premarc] DocumentManager.pythonpart_element = None")
            return None
        try:
            if adapter.IsNull():
                print("[Premarc] DocumentManager.pythonpart_element es nulo")
                return None
        except Exception:
            return None

        name, type_guid, model_guid = self._get_adapter_debug_values(adapter)
        print(
            "[Premarc] DocumentManager pythonpart_element -> "
            f"name={name}, type={type_guid}, model_guid={model_guid or '<sin-guid>'}"
        )
        if self._is_invalid_modification_adapter(name, model_guid):
            print("[Premarc] DocumentManager pythonpart_element invalido")
            return None
        return adapter

    def _get_document_manager_modification_root_adapter(self):
        base_adapter = self._get_document_manager_pythonpart_adapter()
        if base_adapter is None:
            return None

        ppg_adapter, param_list = self._resolve_premarc_ppg_from_adapter(base_adapter)
        if ppg_adapter is None or ppg_adapter.IsNull():
            print("[Premarc] DocumentManager pythonpart_element no resolvio PPG Premarcs")
            return None

        params = parse_params_list_to_dict(param_list)
        selected_z = z_unique_as_int(params.get("z_unique", 0))
        current_z = z_unique_as_int(getattr(self.build_ele.z_unique, "value", 0))
        if selected_z > 0 and current_z > 0 and selected_z != current_z:
            print(
                "[Premarc] PPG desde DocumentManager rechazado por z_unique: "
                f"{selected_z} != {current_z}"
            )
            return None

        print("[Premarc] PPG original recuperado desde DocumentManager")
        return ppg_adapter

    def _get_cached_modification_root_adapter(self):
        guid_str = str(self._modification_ppg_guid_str or "")
        if not guid_str:
            print("[Premarc] Sin GUID cacheado del PPG original")
            return None

        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            doc = self.document

        try:
            adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                AllplanEleAdapter.GUID.FromString(guid_str),
                doc,
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo recuperar PPG por GUID cacheado: {exc}")
            return None

        if adapter is None or adapter.IsNull():
            print(
                "[Premarc] GUID cacheado del PPG original no resolvio adapter: "
                f"{guid_str}"
            )
            return None

        name, type_guid, model_guid = self._get_adapter_debug_values(adapter)
        print(
            "[Premarc] Adapter PPG cacheado -> "
            f"name={name}, type={type_guid}, model_guid={model_guid or '<sin-guid>'}"
        )
        if self._is_invalid_modification_adapter(name, model_guid):
            print("[Premarc] Adapter PPG cacheado invalido; no se usa")
            return None

        ppg_adapter, param_list = self._resolve_premarc_ppg_from_adapter(adapter)
        if ppg_adapter is None or ppg_adapter.IsNull():
            print("[Premarc] GUID cacheado no corresponde a un PPG Premarcs")
            return None

        params = parse_params_list_to_dict(param_list)
        selected_z = z_unique_as_int(params.get("z_unique", 0))
        current_z = z_unique_as_int(getattr(self.build_ele.z_unique, "value", 0))
        if selected_z > 0 and current_z > 0 and selected_z != current_z:
            print(
                "[Premarc] PPG cacheado rechazado por z_unique: "
                f"{selected_z} != {current_z}"
            )
            return None

        print("[Premarc] PPG original recuperado por GUID cacheado")
        return ppg_adapter

    def _get_modification_root_adapter(self):
        """Devuelve el adaptador raiz del PythonPartGroup Premarcs en edicion."""
        modification_list = getattr(self, "modification_ele_list", None)
        if not modification_list:
            return None

        try:
            if not modification_list.is_modification_element():
                return None
        except Exception:
            pass

        base_adapter = None
        try:
            first = modification_list[0]
            if isinstance(first, AllplanEleAdapter.BaseElementAdapter):
                base_adapter = first
        except Exception:
            pass

        if base_adapter is None:
            try:
                base_adapter = modification_list.get_base_element_adapter(self.document)
            except Exception as exc:
                print(f"[Premarc] No se pudo obtener el PythonPart original: {exc}")
                return None

        if base_adapter is None or base_adapter.IsNull():
            print("[Premarc] Adapter base de modificacion nulo")
            return None

        name, type_guid, model_guid = self._get_adapter_debug_values(base_adapter)
        print(
            "[Premarc] Adapter base modificacion -> "
            f"name={name}, type={type_guid}, model_guid={model_guid or '<sin-guid>'}"
        )

        if self._is_invalid_modification_adapter(name, model_guid):
            print(
                "[Premarc] Adapter base modificacion invalido; "
                "se evita resolver PPG para no llamar servicios C++ "
                "sobre undefined element"
            )
            return None

        ppg_adapter, param_list = self._resolve_premarc_ppg_from_adapter(base_adapter)
        if ppg_adapter is None or ppg_adapter.IsNull():
            print("[Premarc] Adapter base no pertenece a un PythonPartGroup Premarcs")
            return None

        try:
            is_pyp = AllplanBaseElements.PythonPartService.IsPythonPartElement(ppg_adapter)
            is_ppg = AllplanBaseElements.PythonPartService.IsPythonPartGroupElement(
                ppg_adapter
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo validar tipo PythonPart: {exc}")
            return None

        if not (is_pyp or is_ppg):
            print("[Premarc] Adapter resuelto no es PythonPart/PythonPartGroup")
            return None

        params = parse_params_list_to_dict(param_list)
        selected_z = z_unique_as_int(params.get("z_unique", 0))
        current_z = z_unique_as_int(getattr(self.build_ele.z_unique, "value", 0))
        if selected_z > 0 and current_z > 0 and selected_z != current_z:
            print(
                "[Premarc] Adapter resuelto rechazado por z_unique: "
                f"{selected_z} != {current_z}"
            )
            return None

        try:
            print(
                "[Premarc] PythonPartGroup Premarcs resuelto para borrado -> "
                f"name={ppg_adapter.GetDisplayName()}, "
                f"model_guid={ppg_adapter.GetModelElementUUID()}, "
                f"is_group={is_ppg}"
            )
        except Exception:
            pass

        return ppg_adapter

    def _reset_reposition_state(self) -> None:
        self._palette_reposition_active = False
        self._palette_reposition_has_new_point = False
        self._palette_reposition_original_point = None
        self._palette_reposition_original_state = {}
        self._palette_reposition_deleted_root = False
        self._palette_reposition_deleted_opening = False

    def _refresh_selected_wall_after_delete(self, wall_guid_str: str) -> None:
        if not wall_guid_str:
            return
        if self._try_restore_wall_from_guid(wall_guid_str):
            print("[Premarc] Muro revalidado tras borrar PPG temporal")
            return
        print(
            "[Premarc] Muro no revalidado por GUID tras borrar PPG; "
            "se intentara fallback geometrico"
        )
        self._try_restore_wall_from_geometry()

    def _build_safe_premarc_delete_list(self, ppg_adapter):
        """Build a delete list from the PPG child tree, skipping the host wall."""
        empty_list = AllplanEleAdapter.BaseElementAdapterList()
        if ppg_adapter is None or ppg_adapter.IsNull():
            print("[Premarc] Delete list segura cancelada: adapter PPG nulo")
            return empty_list, 0

        child_list = None
        try:
            child_list = (
                AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildModelElementsFromTree(
                    ppg_adapter
                )
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo leer arbol hijo del PPG: {exc}")

        if child_list is None:
            try:
                child_list = (
                    AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildModelElements(
                        ppg_adapter, True
                    )
                )
            except Exception as exc:
                print(f"[Premarc] No se pudo leer hijos directos del PPG: {exc}")
                child_list = None

        if child_list is None:
            print("[Premarc] Delete list segura vacia: no hay hijos recuperables del PPG")
            return empty_list, 0

        delete_list = AllplanEleAdapter.BaseElementAdapterList()
        seen_guids = set()
        wall_guid = str(self.wall_guid_str or "")
        opening_guid = str(
            getattr(getattr(self.build_ele, "opening_guid", None), "value", "") or ""
        )
        kept_wall = False
        included_opening = False
        candidate_count = 0

        for child_adapter in child_list:
            if child_adapter is None or child_adapter.IsNull():
                continue

            name, type_guid, model_guid = self._get_adapter_debug_values(child_adapter)
            guid_str = str(model_guid or "")
            candidate_count += 1

            if self._is_invalid_modification_adapter(name, guid_str):
                print(
                    "[Premarc] Delete list segura ignora child invalido -> "
                    f"name={name}, type={type_guid}, model_guid={guid_str or '<sin-guid>'}"
                )
                continue

            if wall_guid and guid_str == wall_guid:
                kept_wall = True
                print(
                    "[Premarc] Delete list segura conserva muro host -> "
                    f"model_guid={guid_str}"
                )
                continue

            dedupe_key = guid_str or f"{name}|{type_guid}|{candidate_count}"
            if dedupe_key in seen_guids:
                continue

            if opening_guid and guid_str == opening_guid:
                included_opening = True

            seen_guids.add(dedupe_key)
            delete_list.append(child_adapter)

        delete_count = len(seen_guids)
        print(
            "[Premarc] Delete list segura construida -> "
            f"candidates={candidate_count}, delete_count={delete_count}, "
            f"wall_preserved={kept_wall}, opening_included={included_opening}"
        )
        return delete_list, delete_count

    def _clear_runtime_state_after_direct_delete(self) -> None:
        print(
            "[Premarc] Limpiando estado runtime tras borrado directo -> "
            f"active_guid={self._active_session_source_guid or '<sin-guid>'}, "
            f"cached_ppg_guid={self._modification_ppg_guid_str or '<sin-guid>'}"
        )
        self._clear_selected_premarc_overlay()
        self._loaded_saved_state = {}
        self._active_session_source_guid = ""
        self._modification_ppg_guid_str = ""
        self._modification_ppg_adapter = None
        self._has_confirmed_placement = False
        self.placement_pnt = AllplanGeo.Point3D()
        self._sync_placement_point_parameter()
        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""
        if hasattr(self.build_ele, "SavedState"):
            self.build_ele.SavedState.value = ""

    def _delete_modified_premarc_direct(self) -> bool:
        """Borra el PPG en modificacion sin pasar por CREATE_ELEMENTS."""
        print(
            "[Premarc] Inicio borrado directo -> "
            f"placement=({self.placement_pnt.X:.1f}, {self.placement_pnt.Y:.1f}, {self.placement_pnt.Z:.1f}), "
            f"opening_guid={str(getattr(getattr(self.build_ele, 'opening_guid', None), 'value', '') or '<sin-opening>')}, "
            f"wall_guid={self.wall_guid_str or '<sin-wall-guid>'}, "
            f"cached_ppg_guid={self._modification_ppg_guid_str or '<sin-guid>'}"
        )
        opening_deleted = False
        opening_prop = getattr(self.build_ele, "opening_guid", None)
        if opening_prop and str(getattr(opening_prop, "value", "") or ""):
            opening_deleted = self._delete_wall_opening()
            print(f"[Premarc] Resultado borrado opening previo: {opening_deleted}")
        else:
            print("[Premarc] Eliminar premarco -> sin opening persistido para borrar")

        old_adapter = self._get_modification_root_adapter()
        if old_adapter is None or old_adapter.IsNull():
            print(
                "[Premarc] Eliminar premarco -> adapter actual no validado; "
                "probando adapter cacheado, DocumentManager y GUID cacheado del PPG original"
            )
            old_adapter = self._get_cached_modification_adapter_object()
            if old_adapter is None or old_adapter.IsNull():
                old_adapter = self._get_document_manager_modification_root_adapter()
            if old_adapter is None or old_adapter.IsNull():
                old_adapter = self._get_cached_modification_root_adapter()
        else:
            name, type_guid, model_guid = self._get_adapter_debug_values(old_adapter)
            print(
                "[Premarc] Eliminar premarco -> adapter actual valido: "
                f"name={name}, type={type_guid}, model_guid={model_guid or '<sin-guid>'}"
            )

        if old_adapter is None or old_adapter.IsNull():
            print("[Premarc] Eliminacion cancelada: PPG original no validado")
            return False

        delete_list, delete_count = self._build_safe_premarc_delete_list(old_adapter)
        if delete_count <= 0:
            print(
                "[Premarc] Eliminacion cancelada: no se pudo construir "
                "una lista segura de subelementos del PPG"
            )
            return False

        try:
            AllplanBaseElements.DeleteElements(self.document, delete_list)
            print(
                "[Premarc] Subelementos del PPG borrados OK -> "
                f"delete_count={delete_count}"
            )
        except Exception as exc:
            print(f"[Premarc] No se pudo borrar la lista segura del PPG: {exc}")
            return False

        self._clear_runtime_state_after_direct_delete()
        print("[Premarc] Borrado directo finalizado OK")
        return True

    def _replace_modified_premarc_direct(self) -> bool:
        """Reemplaza el PythonPart editado sin usar modification_ele_list.

        Workaround acotado: despues de borrar/recrear un opening reducido,
        Allplan lanza una excepcion C++ al confirmar con la lista de
        modificacion. Borramos el PPG anterior y creamos el nuevo PPG como
        insercion limpia para cerrar la operacion sin reentrar al framework.
        """
        if self.placement_pnt == AllplanGeo.Point3D():
            return False
        if not self.selected_wall:
            return False

        old_adapter = self._get_modification_root_adapter()
        if old_adapter is None or old_adapter.IsNull():
            print(
                "[Premarc] Adapter actual no validado; probando GUID cacheado "
                "del PPG original"
            )
            old_adapter = self._get_cached_modification_adapter_object()
            if old_adapter is None or old_adapter.IsNull():
                old_adapter = self._get_cached_modification_root_adapter()
            if old_adapter is None or old_adapter.IsNull():
                print(
                    "[Premarc] PPG original no validado; creando PPG nuevo "
                    "sin borrar adapter anterior"
                )
                return self._create_current_premarc_direct(delete_existing_adapter=None)

        return self._create_current_premarc_direct(delete_existing_adapter=old_adapter)

    def _create_current_premarc_direct(self, delete_existing_adapter=None) -> bool:
        """Create the current PPG as a clean insertion, optionally deleting an old root."""

        z_unique = z_unique_as_int(self.build_ele.z_unique.value)
        if z_unique <= 0:
            z_unique = int(random.random() * 3600)
        self.build_ele.z_unique.value = z_unique
        self.thickness_premarc = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )

        self._rebuild_placement_mat()

        original_modification_mode = self.is_modification_mode
        try:
            self.is_modification_mode = False
            premarc_elements = self.create_premarcs_group()
        finally:
            self.is_modification_mode = original_modification_mode

        if not premarc_elements:
            print("[Premarc] Reemplazo directo cancelado: sin geometria")
            return False

        trans_mat = AllplanGeo.Matrix3D()
        trans_mat.SetTranslation(AllplanGeo.Vector3D(self.placement_pnt))

        if delete_existing_adapter is not None and not delete_existing_adapter.IsNull():
            try:
                old_list = AllplanEleAdapter.BaseElementAdapterList()
                old_list.append(delete_existing_adapter)
                AllplanBaseElements.DeleteElements(self.document, old_list)
                print(
                    "[Premarc] PythonPart anterior borrado antes del reemplazo directo"
                )
            except Exception as exc:
                print(f"[Premarc] No se pudo borrar el PythonPart anterior: {exc}")
                return False

        try:
            created_elements = AllplanBaseElements.CreateElements(
                self.document,
                trans_mat,
                premarc_elements,
                [],
                None,
            )
        except Exception as exc:
            print(f"[Premarc] Reemplazo directo fallo al crear PPG: {exc}")
            return False

        print(
            "[Premarc] Reemplazo directo OK "
            f"({len(created_elements) if created_elements else 0} elementos)"
        )
        return bool(created_elements)

    def is_cuboid_inside_wall(
        self,
        cuboid: AllplanGeo.Polyhedron3D,
        wall: AllplanEleAdapter.BaseElementAdapter,
    ) -> bool:
        try:
            wall_geometry = wall.GetModelGeometry()

            if not isinstance(wall_geometry, AllplanGeo.Polyhedron3D):
                print(
                    "[Premarc] Geometría del muro no es Polyhedron3D, permitiendo opening"
                )
                return True

            if not wall_geometry.IsValid():
                print("[Premarc] Geometría del muro inválida, permitiendo opening")
                return True

            # Verificar intersección entre el cuboide y el muro
            error_code, intersection = AllplanGeo.MakeIntersection(
                cuboid, wall_geometry
            )

            if error_code != AllplanGeo.eGeometryErrorCode.eOK:
                print(f"[Premarc] Sin intersección con el muro (error: {error_code})")
                return False

            if (
                not isinstance(intersection, AllplanGeo.Polyhedron3D)
                or not intersection.IsValid()
            ):
                print(
                    "[Premarc] Intersección vacía o inválida — cuboide fuera del muro"
                )
                return False

            print("[Premarc] Cuboide intersecta con el muro, OK")
            return True

        except Exception as e:
            print(f"[Premarc] Error validando posición del opening: {e}")
            import traceback

            traceback.print_exc()
            return True  # en caso de error, permitir el opening para no bloquear

    def _create_wall_opening(
        self,
        height: float | None = None,
        width: float | None = None,
        bottom_z: float | None = None,
        modify_existing: bool = False,
    ):
        if not self.selected_wall or self.selected_wall.IsNull():
            return False
        if self.placement_pnt == AllplanGeo.Point3D():
            return False

        import math
        from DocumentManager import DocumentManager
        from PythonPartTransaction import PythonPartTransaction
        from TypeCollections.ModificationElementList import ModificationElementList

        # CLAVE: setear el documento correcto antes de la transacción
        DocumentManager.get_instance().document = (
            self.coord_input.GetInputViewDocument()
        )

        pos = self.placement_pnt
        llarg = width if width is not None else self.build_ele.width.value
        alt = height if height is not None else self.build_ele.heigh.value
        bottom_z_ = bottom_z if bottom_z is not None else (pos.Z - alt)

        axis_ele = AllplanEleAdapter.AxisElementAdapter(self.selected_wall)
        if axis_ele.IsNull():
            print("[Premarc] Sin eje, skip opening")
        #     return
            return False
        gruix = axis_ele.GetThickness() if width is None else float(width)
        wall_axis = axis_ele.GetAxis()  # Line2D: eje central del muro

        # ── 1. Proyectar el click sobre el eje del muro ──────────────────────
        p0 = wall_axis.StartPoint  # Point2D
        p1 = wall_axis.EndPoint  # Point2D
        dx = p1.X - p0.X
        dy = p1.Y - p0.Y
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1e-10:
            print("[Premarc] Muro sin longitud, skip opening")
            return False

        ux, uy = dx / length, dy / length  # dirección unitaria a lo largo del muro
        nx, ny = -uy, ux  # perpendicular (normal izquierda)

        # Pie de perpendicular desde el click al eje del muro
        t = (pos.X - p0.X) * ux + (pos.Y - p0.Y) * uy
        proj_x = p0.X + t * ux
        proj_y = p0.Y + t * uy

        # ── Ajustar proj si el premarco apunta en sentido contrario al eje del muro ──
        # Cuando rotation ≈ wall_angle + 180°, el premarco extiende en (-ux,-uy),
        # así que el opening debe empezar desplazado -llarg en la dirección del muro.
        rot_rad = math.radians(self.rotation)
        premarc_dir_x = math.cos(rot_rad)
        premarc_dir_y = math.sin(rot_rad)
        dot_premarc_wall = premarc_dir_x * ux + premarc_dir_y * uy
        if dot_premarc_wall < 0:
            proj_x -= llarg * ux
            proj_y -= llarg * uy

        print(f"[Premarc] Opening → llarg={llarg}, gruix={gruix}, alt={alt}")
        print(
            f"[Premarc] Click=({pos.X:.1f},{pos.Y:.1f}) → proj=({proj_x:.1f},{proj_y:.1f})"
        )

        # ── 2. Construir cuboid orientado con el eje del muro ────────────────
        # Esquina inicial: punto proyectado, centrado perpendicularmente en el eje

        wall_thickness = axis_ele.GetThickness()  # espesor total real del muro
        dist_n = (pos.X - proj_x) * nx + (pos.Y - proj_y) * ny  # positivo = click por el lado +n

        if width is None:
        # Comportamiento original: centrado en el eje (opening a todo el espesor)
            start_x = proj_x - (gruix / 2.0) * nx
            start_y = proj_y - (gruix / 2.0) * ny
        else:
            # Partial width: arrancar desde la cara más cercana al click (dist_n)
            if dist_n >= 0:
                # Cara front está en proj + (wall_thickness/2)*n
                start_x = proj_x + (wall_thickness / 2.0 - gruix) * nx
                start_y = proj_y + (wall_thickness / 2.0 - gruix) * ny
            else:
                # Cara front está en proj - (wall_thickness/2)*n
                start_x = proj_x - (wall_thickness / 2.0) * nx
                start_y = proj_y - (wall_thickness / 2.0) * ny

        # Matriz de rotación: alinea el eje X del cuboid (1,0,0) con la dirección del muro
        rot_mat = AllplanGeo.Matrix3D()
        rot_mat.SetIdentity()
        wall_dir_3d = AllplanGeo.Vector3D(ux, uy, 0.0)
        if abs(ux - 1.0) > 1e-6 or abs(uy) > 1e-6:
            rot_mat.SetRotation(AllplanGeo.Vector3D(1.0, 0.0, 0.0), wall_dir_3d)

        # Matriz de traslación: lleva la esquina a (start_x, start_y, pos.Z)
        trans_mat = AllplanGeo.Matrix3D()
        # trans_mat.SetTranslation(AllplanGeo.Vector3D(start_x, start_y, pos.Z - alt))
        trans_mat.SetTranslation(AllplanGeo.Vector3D(start_x, start_y, bottom_z_))


        # Combinada: primero rotar, luego trasladar → combined = rot_mat * trans_mat
        combined = AllplanGeo.Matrix3D()
        combined.SetIdentity()
        combined.Multiply(rot_mat)  # combined = rot_mat
        combined.Multiply(trans_mat)  # combined = rot_mat * trans_mat

        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(llarg, gruix, alt)
        cuboid = AllplanGeo.Transform(cuboid, combined)

        # ── 3. Validar intersección con la geometría del muro ────────────────
        if not self.is_cuboid_inside_wall(cuboid, self.selected_wall):
            print("[Premarc] Cuboide fuera del muro, skip opening")
            return False

        # ── 4. Crear el opening con placement_line alineada al eje del muro ─
        wall_geo = self.selected_wall.GetGroundViewArchitectureElementGeometry()
        start_2d = AllplanGeo.Point2D(proj_x, proj_y)
        placement_line = AllplanGeo.Line2D(
            start_2d,
            AllplanGeo.Point2D(
                proj_x + ux * (llarg + 1.0), proj_y + uy * (llarg + 1.0)
            ),
        )

        opening_end_pnt = OpeningPointsUtil.create_opening_end_point_for_axis_element(
            start_2d, llarg, wall_axis, wall_geo, placement_line
        )

        if width is None:
            # Llamada sin argumentos → WindowOpening (premarc standard)
            opening_prop = AllplanArchElements.WindowOpeningProperties()
            opening_prop.Independent2DInteraction = False

            plane_ref = AllplanArchElements.PlaneReferences(
                self.document, AllplanEleAdapter.BaseElementAdapter()
            )
            plane_ref.SetBottomOffset(bottom_z_)
            plane_ref.SetHeight(alt)
            opening_prop.PlaneReferences = plane_ref

        #     geom       = opening_prop.GetGeometryProperties()
        #     geom.Depth = gruix

        #     opening_element = AllplanArchElements.WindowOpeningElement(
        #         opening_prop,
        #         self.selected_wall,
        #         start_2d,
        #         opening_end_pnt,
        #         drawPlacementPreview=False
        #     )
        # else:
        #     # Llamada con argumentos → GeneralOpening eRecess (nicho persiana)
        #     opening_prop = AllplanArchElements.GeneralOpeningProperties(
        #         AllplanArchElements.OpeningType.eRecess
        #     )
        #     opening_prop.VisibleInViewSection3D   = True
        #     opening_prop.Independent2DInteraction = False

        #     plane_ref = AllplanArchElements.PlaneReferences(
        #         self.document, AllplanEleAdapter.BaseElementAdapter()
        #     )
        #     plane_ref.SetBottomOffset(bottom_z_)
        #     plane_ref.SetHeight(alt)
        #     opening_prop.PlaneReferences = plane_ref

        #     geom       = opening_prop.GetGeometryProperties()
        #     geom.Depth = gruix

        #     opening_element = AllplanArchElements.GeneralOpeningElement(
        #             opening_prop,
        #             self.selected_wall,
        #             start_2d,
        #             opening_end_pnt,
        #             drawPlacementPreview=False
        #         )
        geom = opening_prop.GetGeometryProperties()
        geom.Depth = gruix

        opening_element = AllplanArchElements.WindowOpeningElement(
            opening_prop,
            self.selected_wall,
            start_2d,
            opening_end_pnt,
            drawPlacementPreview=False,
        )

        modification_list = ModificationElementList()
        opening_guid_str = str(getattr(self.build_ele.opening_guid, "value", "") or "")
        if modify_existing and opening_guid_str:
            try:
                opening_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                    AllplanEleAdapter.GUID.FromString(opening_guid_str),
                    self.coord_input.GetInputViewDocument(),
                )
                if not opening_adapter.IsNull():
                    modification_list = ModificationElementList([opening_adapter])
                    print(
                        "[Premarc] Actualizando opening existente para regenerar "
                        "marcas de apertura"
                    )
            except Exception as exc:
                print(f"[Premarc] No se pudo preparar modificacion de opening: {exc}")

        transaction = PythonPartTransaction(self.document)
        created_opening = transaction.execute(
            AllplanGeo.Matrix3D(),
            AllplanIFW.ViewWorldProjection(),
            [opening_element],
            modification_list,
        )
        print("[Premarc] Opening creado OK")
        # Guardar el GUID en el parámetro del PythonPart
        # El opening creado es el primer elemento de la lista


        if created_opening:
            opening_adapters = [
                x
                for x in created_opening
                if x.GetElementAdapterType() == AllplanEleAdapter.WindowTier_TypeUUID
            ]
            if not opening_adapters:
                print("[Premarc] Opening creado sin WindowTier reconocible")
                return False

            opening_adapter = opening_adapters[0]
            opening_guid = opening_adapter.GetModelElementUUID()  # objeto GUID
            opening_guid_str = str(opening_guid)  # string persistible
            print(f"[Premarc] Opening GUID: {opening_guid_str}")
            if width is None:
                # window opening premarc
                self.build_ele.opening_guid.value = opening_guid_str
            else:
                # niche opening persiana
                self.build_ele.niche_guid.value = opening_guid_str
            # self.build_ele.opening_guid.value = opening_guid_str
            self._opening_created_width = llarg
            self._opening_created_heigh = alt
            self._opening_baseline_width = float(llarg)
            self._opening_baseline_height = float(alt)
            self._opening_baseline_point = self._copy_point3d(self.placement_pnt)
            return True

        return False

    def _recreate_wall_opening(self):
        if not self.selected_wall:
            return

        if self.build_ele.opening_guid.value:
            self._create_wall_opening(modify_existing=True)
            return

        self._create_wall_opening()

    def _sync_wall_opening_for_modification(self):
        """Sincroniza el hueco con el premarco editado.

        Allplan modifica bien cuando el opening crece, pero puede no reducirlo
        al achicar el ancho/alto. Al mover el premarco tampoco siempre desplaza
        el hueco existente. En ambos casos se recrea el opening.
        """
        self._opening_recreated_during_cancel = False
        self._opening_sync_requires_direct_update = False

        if not self.selected_wall:
            print("[Premarc] Sin muro seleccionado; no se actualiza opening")
            return

        current_w = float(self.build_ele.width.value)
        current_h = float(self.build_ele.heigh.value)
        baseline_w = self._opening_baseline_width
        baseline_h = self._opening_baseline_height
        has_moved = self._did_opening_placement_change()
        opening_guid = self.build_ele.opening_guid.value

        has_shrunk = (
            opening_guid
            and baseline_w is not None
            and baseline_h is not None
            and (current_w < baseline_w - 0.01 or current_h < baseline_h - 0.01)
        )

        if has_shrunk or (opening_guid and has_moved):
            reason = "Opening disminuye" if has_shrunk else "Opening cambia de posicion"
            print(
                f"[Premarc] {reason}: "
                f"{baseline_w}x{baseline_h} -> {current_w}x{current_h}, "
                f"pnt={self.placement_pnt}. "
                "Recreando hueco."
            )
            self._opening_sync_requires_direct_update = True
            self._delete_wall_opening()
            if self._create_wall_opening():
                self._opening_recreated_during_cancel = True
            self._opening_baseline_width = current_w
            self._opening_baseline_height = current_h
            self._opening_baseline_point = self._copy_point3d(self.placement_pnt)
            return

        if opening_guid:
            print(
                "[Premarc] Opening crece/se mantiene: "
                f"{baseline_w}x{baseline_h} -> {current_w}x{current_h}. "
                "Actualizando in-place."
            )
            self._create_wall_opening(modify_existing=True)
            return

        self._create_wall_opening()

    def _delete_wall_opening(
        self,
        opening_guid_str: str | None = None,
        is_window_opening: bool = True,
    ):
        if opening_guid_str is None:
            opening_guid_str = self.build_ele.opening_guid.value
        if not opening_guid_str:
            return False

        from DocumentManager import DocumentManager

        doc = self.coord_input.GetInputViewDocument()
        DocumentManager.get_instance().document = doc

        # guid = AllplanEleAdapter.GUID()
        # guid.FromString(opening_guid_str)
        guid = AllplanEleAdapter.GUID.FromString(opening_guid_str)

        opening_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(guid, doc)
        if opening_adapter.IsNull():
            print(
                "[Premarc] Opening ya no existe en el documento actual, limpiando GUID"
            )
            if is_window_opening:
                self.build_ele.opening_guid.value = ""
            elif hasattr(self.build_ele, "niche_guid"):
                self.build_ele.niche_guid.value = ""
            return False

        ele_list = AllplanEleAdapter.BaseElementAdapterList()
        ele_list.append(opening_adapter)

        AllplanBaseElements.DeleteElements(doc, ele_list)

        if is_window_opening:
            self.build_ele.opening_guid.value = ""
        elif hasattr(self.build_ele, "niche_guid"):
            self.build_ele.niche_guid.value = ""
        self._opening_created_width = 0
        self._opening_created_heigh = 0
        print("[delete_wall_opening] Opening borrado OK")
        return True

    # TODO detectar grosor de muro correctamente
    def _get_wall_thickness(self, wall_adapter) -> float:
        """Lee el grosor del muro desde su geometria 2D en planta.
        Funciona bien para muros rectos de un solo tier.
        Fallback al valor thickness_wall del .pyp.
        """
        # --- Geometria 2D (metodo principal) ---
        try:
            geo_2d = wall_adapter.GetGroundViewArchitectureElementGeometry()
            # geo_2d es Polygon2D o Polyline2D con 4 puntos para muro recto
            pts = list(geo_2d.Points)
            if len(pts) >= 4:
                import NemAll_Python_Geometry as AllplanGeo

                # Distancia entre el primer y el cuarto punto = grosor del muro
                # (los dos primeros forman un lado largo, el 2o y 3o el lado corto)
                d01 = AllplanGeo.Vector2D(
                    pts[1].X - pts[0].X, pts[1].Y - pts[0].Y
                ).GetLength()
                d12 = AllplanGeo.Vector2D(
                    pts[2].X - pts[1].X, pts[2].Y - pts[1].Y
                ).GetLength()
                # El grosor es el lado más corto
                thickness = min(d01, d12)
                if thickness > 0:
                    print(f"[Premarc] Grosor muro detectado: {thickness} mm")
                    return thickness
        except Exception as e:
            print(f"[Premarc] No se pudo leer grosor del muro: {e}")

        # --- Atributo ID=216 (grosor en metros) ---
        try:
            attrs = wall_adapter.GetAttributes(
                AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
            )
            for attr in attrs:
                attr_id = getattr(attr, "Id", None) or (
                    attr[0] if isinstance(attr, (tuple, list)) else None
                )
                attr_value = getattr(attr, "Value", None) or (
                    attr[1] if isinstance(attr, (tuple, list)) else None
                )
                if attr_id == 216 and attr_value:
                    thickness = float(attr_value) * 1000  # metros → mm
                    if thickness > 0:
                        print(f"[Premarc] Grosor muro (attr 216): {thickness} mm")
                        return thickness
        except Exception as e:
            print(f"[Premarc] Fallo attr 216: {e}")

        # --- Fallback al .pyp ---
        fallback = self.build_ele.thickness_wall.value
        print(f"[Premarc] Grosor muro (fallback .pyp): {fallback} mm")
        return fallback

    def _get_wall_rotation_deg(self, wall_adapter) -> float:
        """Extract the wall's axis angle (degrees) from its 2D plan-view polygon.
        Returns the angle of the wall's long edge relative to the X axis.
        Falls back to 0.0 if geometry is unavailable.
        """
        try:
            geo_2d = wall_adapter.GetGroundViewArchitectureElementGeometry()
            pts = list(geo_2d.Points)
            if len(pts) >= 4:
                d01 = AllplanGeo.Vector2D(
                    pts[1].X - pts[0].X, pts[1].Y - pts[0].Y
                ).GetLength()
                d12 = AllplanGeo.Vector2D(
                    pts[2].X - pts[1].X, pts[2].Y - pts[1].Y
                ).GetLength()
                if d01 >= d12:
                    dx, dy = pts[1].X - pts[0].X, pts[1].Y - pts[0].Y
                else:
                    dx, dy = pts[2].X - pts[1].X, pts[2].Y - pts[1].Y
                angle_deg = math.degrees(math.atan2(dy, dx))
                print(f"[Premarc] Wall rotation detected: {angle_deg} deg")
                return angle_deg
        except Exception as e:
            print(f"[Premarc] Could not read wall rotation: {e}")
        return 0.0

    def _debug_wall_attrs(self, wall_adapter):
        """Diagnostico: imprime todos los atributos del muro seleccionado."""
        try:
            attrs = wall_adapter.GetAttributes(
                AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
            )
            print(f"[Premarc DEBUG] {len(attrs)} atributos en el muro:")
            for attr in attrs:
                attr_id = getattr(attr, "Id", None) or (
                    attr[0] if isinstance(attr, (tuple, list)) else None
                )
                attr_value = getattr(attr, "Value", None) or (
                    attr[1] if isinstance(attr, (tuple, list)) else None
                )
                print(f"  ID={attr_id}  Value={attr_value}")
        except Exception as e:
            print(f"Error leyendo atributos: {e}")

    def _premarc_labels(self):
        label = ""
        extra_user = ""
        fondo_label = self._fondo_labels()
        cajon_label, cajon_extras = self._cajon_labels()
        pendiente_label, pendiente_extras = self._pendiente_labels()
        encaje_label, encaje_extras = self._encaje_labels()

        extras = cajon_extras + pendiente_extras + encaje_extras
        first_label = f"{fondo_label}{cajon_label}{pendiente_label}{encaje_label}"

        # if self.build_ele.extraLabelUser.value:
        #     first_label += f".{self.build_ele.extraLabelUser.value}"

        # label = f"TIPUS-$<bold, height(5)>{first_label}$;$<bold>{extras}$"
        label = f"TIPUS-{first_label}{extras}"
        self.build_ele.INPUT_PMP_PREMARC_LABELS.value = label

        return first_label, extras

    def _format_premarc_label(self, plain_label: str) -> str:
        """Convert plain text label to formatted version with bold tags.

        Example:
            'TIPUS-6.13.B CALAIX OCULT' -> 'TIPUS-$<bold, height(5)>6.13.B$;$<bold> CALAIX OCULT$'
        """
        prefix = "TIPUS-"
        if plain_label.startswith(prefix):
            rest = plain_label[len(prefix) :]
            space_idx = rest.find(" ")
            if space_idx != -1:
                first = rest[:space_idx]
                extras = rest[
                    space_idx:
                ]  # preserves leading space, e.g. " CALAIX OCULT"
                return f"TIPUS-$<bold, height(5)>{first}$;$<bold>{extras}$"
            return f"TIPUS-$<bold, height(5)>{rest}$"
        return plain_label

    def _premarc_labels_without_extras(self):
        label = ""

        fondo_label = self._fondo_labels()
        cajon_label, _ = self._cajon_labels()
        pendiente_label, _ = self._pendiente_labels()
        encaje_label, _ = self._encaje_labels()

        first_label = f"TIPUS-{fondo_label}{cajon_label}{pendiente_label}{encaje_label}"

        return first_label

    def _fondo_labels(self):
        label = ""
        optional = ""

        if not self.build_ele.ComboBoxAbiertoCerrado.value == "TANCAT":
            optional = ".7"

        match self.thickness:
            case 160:
                label = "1"
            case 295:
                if self.build_ele.PassamaOptions.value[0] == 1:
                    label = "2"
                else:
                    label = "4"
            case 310:
                label = "3"
            case _:
                pass

        if self.build_ele.enable_manual_thickness.value:
            num_lines = 20

            try:
                with open(self.color_file, "r", encoding="utf-8") as file:
                    for line in file:
                        num_lines += 1
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split(",")
                        if len(parts) != 2:
                            continue
                        thickness, color = parts[0].strip(), parts[1].strip()
                        if thickness == self.thickness:
                            break

            except FileNotFoundError:
                pass

            label = f"{num_lines}"

        # Check optional labels
        if optional:
            label += optional

        # check if enable cajon persiana: return empty string
        if (
            not self.build_ele.ComboBoxPersianas.value == "NO"
            and not self.thickness == 310
        ):
            label = ""

        return label

    def _cajon_labels(self):
        """Return the label for the cajon persiana."""
        label = ""
        extras = ""
        if self.build_ele.ComboBoxPersianas.value in ["LAMISOL VIST", "METALUNIC VIST"]:
            label = ".5"
            if self.build_ele.ComboBoxPersianas.value == "METALUNIC VIST":
                extras = " CALAIX OCULT"

        if self.build_ele.ComboBoxPersianas.value in ["MONOBLOCK OCULT", "FALS CALAIX"]:
            label = ".6"
            if self.build_ele.ComboBoxPersianas.value == "FALS CALAIX":
                label += ".2"

        # fix label for cajon persiana without label fondo
        if not self._fondo_labels():
            label = label[1:]

        return label, extras

    def _pendiente_labels(self):
        """Return the label for the pendiente."""
        label = ""
        extras = ""
        if self.build_ele.ComboBoxPendiente.value == "NO":
            label = ".0"
            extras = " SENSE PENDENT"
        return label, extras

    def _encaje_labels(self):
        """Return the label for the encaje."""
        label = ""
        extras = ""
        match self.build_ele.ComboBoxEncajes.value:
            case "PLEC INFERIOR":
                label = ".2"
                extras = " PLEC INFERIOR"
            case "45*30":
                label = ".10"
            case "35*30":
                label = ".13"
            case "90*30":
                label = ".14"
            case "35*60":
                label = ".15"

        # manage manual encaje
        if self.build_ele.EnableManualEncaje.value:
            base = self.build_ele.EncajeBase.value
            altura = self.build_ele.EncajeAltura.value
            count_line = 16
            try:
                with open(self.encaje_file, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        if line == f"{base}x{altura}":
                            self.disable_save_encaje = True
                            break
                        count_line += 1
                    label = f".{count_line}"
            except FileNotFoundError:
                label = f".{count_line}"
                pass

        return label, extras

    def _saved_checkbox_01(self, value) -> int:
        """JSON con true/false rompe la lectura inicial (eval en framework). Usar 0/1."""
        return 1 if value else 0

    # =========================================================================
    # PMP_XPS_PREMARC_DETAIL helpers
    # =========================================================================
    # Compose the attribute value (Type;Material;A;B;C;D;E;F;G;H;I;J) applied
    # to every XPS piece. The Type is decided by the flowchart in
    # ayuda_detalles.pdf and the slot population mirrors condiciones_xps_prem.xlsx.

    def _get_selected_passama(self) -> set[str]:
        """Return the names of currently selected Passamà options (excluding 'NO')."""
        try:
            names = list(self.build_ele.valueListaPassama.value)
            flags = list(self.build_ele.PassamaOptions.value)
        except Exception:
            return set()
        selected: set[str] = set()
        for name, flag in zip(names, flags):
            if not flag:
                continue
            if not name or name == "NO":
                continue
            selected.add(name)
        return selected

    def _get_refuerzo_kind(self) -> str:
        """Return 'FALCA', 'PASAMANO' or 'NONE' based on PassamaOptions selection."""
        selected = self._get_selected_passama()
        if selected & PASSAMA_FALCA_OPTIONS:
            return "FALCA"
        if selected & PASSAMA_PASAMANO_OPTIONS:
            return "PASAMANO"
        return "NONE"

    def _get_encaje_base_cm(self) -> float | None:
        """Return the encaje base in cm, or None when no encaje applies.

        - Manual encaje (EnableManualEncaje) → EncajeBase / 10
        - Combo encaje with a 'BASExALTURA' pattern (e.g. '35*30', '70*30') → BASE / 10
        - 'NO' or 'PLEC INFERIOR' → None
        """
        try:
            if self.build_ele.EnableManualEncaje.value:
                base_mm = float(self.build_ele.EncajeBase.value or 0)
                return base_mm / 10.0 if base_mm > 0 else None
        except Exception:
            pass

        combo = ""
        try:
            combo = self.build_ele.ComboBoxEncajes.value or ""
        except Exception:
            return None

        if not combo or combo in ("NO", "PLEC INFERIOR", "Encajes"):
            return None

        for sep in ("*", "x", "X"):
            if sep in combo:
                head = combo.split(sep, 1)[0].strip()
                try:
                    return float(head) / 10.0
                except ValueError:
                    return None
        return None

    def _has_plec_inferior(self) -> bool:
        try:
            return self.build_ele.ComboBoxEncajes.value == "PLEC INFERIOR"
        except Exception:
            return False

    def _get_persiana_kind(self) -> str:
        """Return one of 'NO', 'MONOBLOCK', 'LAMISOL_METALUNIC'.

        FALS CALAIX is grouped with MONOBLOCK (both are 'calaix ocult' configurations
        per the flowchart's 'MONOBLOCK OCULT' leaf).
        """
        try:
            value = self.build_ele.ComboBoxPersianas.value
        except Exception:
            return "NO"
        if value in ("MONOBLOCK OCULT", "FALS CALAIX"):
            return "MONOBLOCK"
        if value in ("LAMISOL VIST", "METALUNIC VIST"):
            return "LAMISOL_METALUNIC"
        return "NO"

    def _get_xps_tipus(self) -> str:
        """Decide TIPUS_1..TIPUS_9 from the flowchart in ayuda_detalles.pdf."""
        try:
            fondo = float(self.thickness_premarc or 0)
        except Exception:
            fondo = 0.0
        try:
            pared = float(self.build_ele.thickness_wall.value or 0)
        except Exception:
            pared = 0.0

        if fondo <= pared:
            return "TIPUS_5"

        refuerzo = self._get_refuerzo_kind()
        persiana = self._get_persiana_kind()
        plec = self._has_plec_inferior()

        if persiana == "MONOBLOCK":
            return "TIPUS_1"
        if plec:
            return "TIPUS_6"

        if refuerzo == "NONE":
            return "TIPUS_2"

        if persiana == "LAMISOL_METALUNIC":
            if int(round(fondo)) == 310:
                return "TIPUS_3"
            if refuerzo == "FALCA":
                return "TIPUS_7"
            # PASAMANO branch: TIPUS_8 by default, TIPUS_9 when an encaje is configured
            if self._get_encaje_base_cm() is not None:
                return "TIPUS_9"
            return "TIPUS_8"

        # REFUERZO=SI but no LAMISOL/METALUNIC and no MONOBLOCK/PLEC → default
        return "TIPUS_2"

    @staticmethod
    def _format_slot(value, decimals: int = 3) -> str:
        """Format a numeric slot value: empty string for None, trimmed decimal otherwise."""
        if value is None:
            return ""
        try:
            num = float(value)
        except (TypeError, ValueError):
            return ""
        if decimals <= 0:
            formatted = f"{num:.0f}"
        else:
            formatted = f"{num:.{decimals}f}"
            if "." in formatted:
                formatted = formatted.rstrip("0").rstrip(".")
        return formatted or "0"

    def _xps_thickness_mm(self) -> float:
        """Resolve the effective XPS/PIR thickness in mm used in the detail attribute."""
        try:
            xps_type = self.build_ele.xps_type.value
        except Exception:
            xps_type = "XPS"
        try:
            manual = bool(self.build_ele.XPSthicknessInd.value)
        except Exception:
            manual = False
        try:
            manual_value = float(self.build_ele.XPSthickness.value or 0)
        except Exception:
            manual_value = 0.0
        if manual and manual_value > 0:
            return manual_value
        return 40.0 if xps_type == "XPS" else 120.0

    def _xps_wall_thickness_mm(self) -> float:
        """Return the wall thickness reference used by XPS calculations.

        XPS must be driven by the manual wall thickness from the palette, not by
        auto-detected host wall thickness, because detection is not reliable
        enough for production geometry.
        """
        try:
            return float(self.build_ele.thickness_wall.value or 0.0)
        except Exception:
            return 0.0

    def _build_xps_premarc_detail(self) -> str:
        """Build the PMP_XPS_PREMARC_DETAIL attribute string for the current state."""
        try:
            material = self.build_ele.xps_type.value or "XPS"
        except Exception:
            material = "XPS"

        tipus = self._get_xps_tipus()

        try:
            fondo_mm = float(self.thickness_premarc or 0)
        except Exception:
            fondo_mm = 0.0
        try:
            pared_mm = float(self.build_ele.thickness_wall.value or 0)
        except Exception:
            pared_mm = 0.0

        xps_mm = self._xps_thickness_mm()

        # "Sobresaliente" = how much the premarc sticks out beyond the wall, in metres.
        # Matches the user-supplied example (fondo=295, pared=160 → 0.135).
        sobresaliente_m = (fondo_mm - pared_mm) / 1000.0
        grosor_xps_m = xps_mm / 1000.0
        fondo_m = fondo_mm / 1000.0
        if tipus == "TIPUS_3":
            fondo_m = 0.310

        encaje_cm = self._get_encaje_base_cm()
        passama_present = self._get_refuerzo_kind() != "NONE"
        e_value = float(PASSAMA_SEPARATION_CM) if passama_present else None
        f_value = e_value  # =E in cm (same numeric value), per VAL_PMP_XPS_PREMARC_DETAIL example

        ancho_persiana_mm = float(BOX_SHUTTER_WIDTH)
        alto_persiana_mm = float(BOX_SHUTTER_HEIGHT)
        ancho_caja_persiana_m = BOX_SHUTTER_WIDTH / 1000.0

        slots_a_to_j: list[str] = [""] * 10

        def set_slot(index: int, value, decimals: int = 3):
            slots_a_to_j[index] = self._format_slot(value, decimals)

        if tipus == "TIPUS_1":
            # MONOBLOCK OCULT / FALS CALAIX
            set_slot(0, sobresaliente_m)
            set_slot(1, grosor_xps_m)
            set_slot(2, fondo_m)
            set_slot(3, encaje_cm, decimals=1)
            set_slot(4, e_value, decimals=0)
            set_slot(5, f_value, decimals=0)
            # G, H left empty for TIPUS_1
            set_slot(8, ancho_caja_persiana_m)
            set_slot(9, None)  # ancho_extra_pared currently unknown → NULL
        elif tipus == "TIPUS_2":
            set_slot(0, sobresaliente_m)
            set_slot(1, grosor_xps_m)
            set_slot(2, fondo_m)
            set_slot(3, encaje_cm, decimals=1)
        elif tipus == "TIPUS_3":
            set_slot(0, sobresaliente_m)
            set_slot(1, grosor_xps_m)
            set_slot(2, fondo_m)
            set_slot(3, encaje_cm, decimals=1)
            # E left empty for TIPUS_3
            set_slot(5, f_value, decimals=0)
        elif tipus == "TIPUS_4":
            set_slot(0, sobresaliente_m)
            set_slot(1, grosor_xps_m)
            set_slot(2, fondo_m)
            set_slot(3, encaje_cm, decimals=1)
            set_slot(4, e_value, decimals=0)
        elif tipus == "TIPUS_5":
            # FONDO == PARED → only fondo present
            set_slot(2, fondo_m)
        elif tipus == "TIPUS_6":
            set_slot(0, sobresaliente_m)
            set_slot(1, grosor_xps_m)
            set_slot(2, fondo_m)
            set_slot(3, encaje_cm, decimals=1)
            set_slot(4, e_value, decimals=0)
            set_slot(5, f_value, decimals=0)
        elif tipus in ("TIPUS_7", "TIPUS_8", "TIPUS_9"):
            set_slot(0, sobresaliente_m)
            set_slot(1, grosor_xps_m)
            set_slot(2, fondo_m)
            set_slot(3, encaje_cm, decimals=1)
            set_slot(4, e_value, decimals=0)
            set_slot(5, f_value, decimals=0)
            set_slot(6, ancho_persiana_mm, decimals=0)
            set_slot(7, alto_persiana_mm, decimals=0)

        return ";".join([tipus, material, *slots_a_to_j])

    def create_premarcs_group(self):
        # if self._create_union_frames:
        #         # Lógica específica para on_cancel_function (solo frames unidos)
        #     print("Lógica específica para on_cancel_function (solo frames unidos)")
        #     self.elements = self._create_union_frame_elements()
        # else:
        #     # Lógica normal (con XPS + frames separados)
        #     self.elements = self.create_premarc()
        self.elements = self.create_premarc()

        # manage handles for height and width
        # handle_parameter_data = HandleParameterData("CubeHeight", HandleParameterType.Z_DISTANCE)
        self.handle_list = []

        self._sync_placement_point_parameter()

        handle_placement = HandleProperties(
            "PlacementHandle",
            AllplanGeo.Point3D(),
            AllplanGeo.Point3D(),
            [HandleParameterData("PlacementPnt", HandleParameterType.POINT)],
            HandleDirection.XYZ_DIR,
            info_text="Reposicionar premarco",
        )

        handle_height = HandleProperties(
            "HeighHandle",
            AllplanGeo.Point3D(0, 0, self.build_ele.heigh.value),
            AllplanGeo.Point3D(0, 0, 0),
            [HandleParameterData("heigh", HandleParameterType.Z_DISTANCE)],
            HandleDirection.Z_DIR,
        )

        self.handle_list.append(handle_placement)
        self.handle_list.append(handle_height)

        individual_pythonparts = self.create_individual_pythonparts_from_elements(
            self.elements, self.build_ele
        )

        # pp_util = PythonPartUtil()
        # pp_util.add_pythonpart_view_2d3d(self.elements)
        # pp = pp_util.create_pythonpart(self.build_ele, placement_matrix=self.placement_mat, type_display_name="PythonPart XPS Premarcs")

        if not individual_pythonparts:
            raise Exception("No se pudieron crear PythonParts individuales")

        saved_state_json = json.dumps(
            self._build_premarc_saved_state_dict(self.placement_pnt)
        )
        self.build_ele.SavedState.value = saved_state_json

        global_params = {
            "TotalElements": len(self.elements),
            "SavedState": saved_state_json,
            "z_unique": z_unique_as_int(self.build_ele.z_unique.value),
        }

        if self.is_modification_mode:
            premarc_hash = self._get_existing_group_hash()
            if not premarc_hash:
                premarc_hash = create_element_hash(
                    "premarcos",
                    stable=True,
                    z_unique=global_params["z_unique"],
                )
        else:
            premarc_hash = create_element_hash("premarcos", **global_params)

        # Crear lista de parámetros
        param_list = create_params_list_from_dict(global_params)

        # Obtener el nombre del archivo .pyp
        python_file_name = (
            self.build_ele.pyp_file_name
            if hasattr(self.build_ele, "pyp_file_name")
            else ""
        )

        # Crear el PythonPartGroup con todos los parámetros requeridos
        # Firma: PythonPartGroup(name, parameter_list, hash_value, python_file, pythonpart_list)
        pythonpart_group = PythonPartGroup(
            "Premarcs",  # name
            param_list,  # parameter_list
            premarc_hash,  # hash_value
            python_file_name,  # python_file (nombre del .pyp)
            individual_pythonparts,  # pythonpart_list
        )

        # Crear los elementos del grupo
        model_elem_list = pythonpart_group.create()

        return model_elem_list

    def check_falcas_and_persianas(self):
        listOptions = self.build_ele.valueListaPassama.value
        listValuesOptions = self.build_ele.PassamaOptions.value
        tuple_list = list(zip(listOptions, listValuesOptions))
        result = False

        for name, value in tuple_list:
            if name == "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)" and value == 1:
                if self.build_ele.ComboBoxPersianas.value in [
                    "LAMISOL VIST",
                    "METALUNIC VIST",
                ]:
                    result = False
                else:
                    result = True

        return result

    def on_cancel_function(self):
        """Función de cancelación: se llama cuando el usuario cancela la operación."""
        print("ON_CANCEL_FUNCTION\n\n\n")

        if self._palette_reposition_active and not self._palette_reposition_has_new_point:
            self.script_object_interactor = None
            self.interactor_state = STOPPED
            original_state = dict(self._palette_reposition_original_state or {})
            if self._palette_reposition_original_point is not None:
                self.placement_pnt = self._copy_point3d(
                    self._palette_reposition_original_point
                )
                self._sync_placement_point_parameter()
                self._rebuild_placement_mat()
                self._has_confirmed_placement = True
            if self.is_modification_mode and original_state:
                self._apply_premarc_saved_state(original_state)
                if (
                    self._palette_reposition_deleted_opening
                    and self.selected_wall
                    and self.placement_pnt != AllplanGeo.Point3D()
                ):
                    self._create_wall_opening()
                if self._palette_reposition_deleted_root:
                    self._create_current_premarc_direct()
            self._palette_reposition_active = False
            self._palette_reposition_has_new_point = False
            self._palette_reposition_original_point = None
            self._palette_reposition_original_state = {}
            self._palette_reposition_deleted_root = False
            self._palette_reposition_deleted_opening = False
            print("[Premarc] Reubicacion cancelada; se conserva la posicion previa")
            if self.is_modification_mode:
                return OnCancelFunctionResult.CANCEL_INPUT
            return OnCancelFunctionResult.CONTINUE_INPUT

        if self.is_modification_mode:
            self.script_object_interactor = None
            self.interactor_state = STOPPED
            print(
                "[Premarc] Cierre en modificacion -> "
                f"delete_requested={self._delete_current_premarc_requested}, "
                f"placement_is_zero={self.placement_pnt == AllplanGeo.Point3D()}, "
                f"selected_wall={'si' if bool(self.selected_wall) else 'no'}, "
                f"opening_guid={str(getattr(getattr(self.build_ele, 'opening_guid', None), 'value', '') or '<sin-opening>')}, "
                f"cached_ppg_guid={self._modification_ppg_guid_str or '<sin-guid>'}"
            )

            if self._delete_current_premarc_requested:
                print("[Premarc] Eliminacion solicitada -> borrando PPG en cierre")
                deleted = self._delete_modified_premarc_direct()
                self._delete_current_premarc_requested = False
                self._opening_deleted_on_modification_entry = False
                self._opening_sync_requires_direct_update = False
                self._opening_recreated_during_cancel = False
                self._reset_reposition_state()
                if not deleted:
                    print("[Premarc] Eliminacion del premarco no confirmada")
                return OnCancelFunctionResult.CANCEL_INPUT

            if self.placement_pnt == AllplanGeo.Point3D():
                print(
                    "[Premarc] Modificación sin punto de colocación; "
                    "se conserva el PPG"
                )
                return OnCancelFunctionResult.CANCEL_INPUT

            self.update_params()
            if self.build_ele.enable_manual_thickness.value:
                self.save_color_manual_thickness()
            if self.build_ele.EnableManualEncaje.value and not self.disable_save_encaje:
                self.save_manual_encaje()

            if self.selected_wall:
                self._sync_wall_opening_for_modification()

            if self._palette_reposition_deleted_root:
                print("[Premarc] Reubicacion confirmada con insercion directa")
                created = self._create_current_premarc_direct()
                self._opening_deleted_on_modification_entry = False
                self._reset_reposition_state()
                if not created:
                    print(
                        "[Premarc] No se pudo recrear el premarco tras la reubicacion"
                    )
                return OnCancelFunctionResult.CANCEL_INPUT

            if (
                self._opening_deleted_on_modification_entry
                and self._palette_reposition_active
                and self._palette_reposition_has_new_point
            ):
                print(
                    "[Premarc] Reubicacion con opening recreado -> "
                    "reemplazo directo del PythonPart"
                )
                self._create_union_frames = True
                replaced = self._replace_modified_premarc_direct()
                self._opening_deleted_on_modification_entry = False
                self._reset_reposition_state()
                if not replaced:
                    print(
                        "[Premarc] Reemplazo directo no confirmado tras "
                        "reubicar y recrear opening"
                    )
                return OnCancelFunctionResult.CANCEL_INPUT

            if self._opening_deleted_on_modification_entry:
                print(
                    "[Premarc] Opening eliminado al entrar en modificacion; "
                    "cerrando con reemplazo directo del PythonPart"
                )
                replaced = self._replace_modified_premarc_direct()
                self._opening_deleted_on_modification_entry = False
                self._reset_reposition_state()
                if not replaced:
                    print(
                        "[Premarc] Reemplazo directo no confirmado tras recrear opening"
                    )
                return OnCancelFunctionResult.CANCEL_INPUT

            if self._opening_sync_requires_direct_update:
                print(
                    "[Premarc] Opening reducido; reemplazando PythonPart "
                    "sin modification_ele_list"
                )
                self._create_union_frames = True
                replaced = self._replace_modified_premarc_direct()
                if not replaced:
                    print(
                        "[Premarc] Reemplazo directo no confirmado; se evita "
                        "CREATE_ELEMENTS para no reentrar en excepcion C++"
                    )
                self._opening_sync_requires_direct_update = False
                self._opening_recreated_during_cancel = False
                self._opening_deleted_on_modification_entry = False
                self._reset_reposition_state()
                return OnCancelFunctionResult.CANCEL_INPUT

            print("[Premarc] Modificación confirmada -> CREATE_ELEMENTS")
            self._reset_reposition_state()
            self._opening_deleted_on_modification_entry = False
            return OnCancelFunctionResult.CREATE_ELEMENTS

        if self.interactor_state == SELECTING_WALL:
            self.script_object_interactor = None
            self.interactor_state = STOPPED
            return OnCancelFunctionResult.CANCEL_INPUT

        if self.interactor_state == PLACING_POINT:
            self.script_object_interactor = None
            self.interactor_state = STOPPED

        if self.script_object_interactor is None:
            self._finalize_session_created_premarcs()
            if self._final_creation_cancelled_by_user:
                return OnCancelFunctionResult.CONTINUE_INPUT
            return OnCancelFunctionResult.CANCEL_INPUT

        self.update_params()
        if self.build_ele.enable_manual_thickness.value:
            self.save_color_manual_thickness()
        if self.build_ele.EnableManualEncaje.value and not self.disable_save_encaje:
            self.save_manual_encaje()

        if self.check_falcas_and_persianas():
            resp = PythonUtility.ShowMessageBox(
                f"Selecciono Falcas, pero no hay persianas.\n" "¿Desea continuar?",
                PythonUtility.MB_OKCANCEL,
            )
            if resp == PythonUtility.IDCANCEL:
                return OnCancelFunctionResult.CONTINUE_INPUT

        # Si no hay interactor activo y hay un punto de colocación
        # if self.script_object_interactor is None and self.placement_pnt != AllplanGeo.Point3D():
        #     # Activar el modo de unión de frames
        #     print("Activar el modo de unión de frames")
        #     self._create_union_frames = True
        #     return OnCancelFunctionResult.CREATE_ELEMENTS

        # # Si hay interactor, cancelar la entrada actual
        # if self.script_object_interactor is not None:
        #     self.script_object_interactor = None

        # return OnCancelFunctionResult.CANCEL_INPUT
        # Usuario canceló durante la selección de muro → cancelar todo
        if self.interactor_state == SELECTING_WALL:
            self.script_object_interactor = None
            self.interactor_state = STOPPED
            return OnCancelFunctionResult.CANCEL_INPUT
        # Usuario canceló durante el punto → si ya tiene muro y punto, crear
        if self.interactor_state == PLACING_POINT:
            self.script_object_interactor = None
            self.interactor_state = STOPPED
        # Estado STOPPED con punto ya colocado
        if (
            self.script_object_interactor is None
            and self.placement_pnt != AllplanGeo.Point3D()
        ):
            # if self.selected_wall and not self.is_modification_mode :
            #     self._create_wall_opening()

            # if self.selected_wall and not self.is_modification_mode and not self.build_ele.opening_guid.value:
            # if self.selected_wall and not self.is_modification_mode:
            if self.selected_wall:
                #     # ── PRIMER ESC ──────────────────────────────────────────────────────
                #     # Crear el opening y guardar el GUID en build_ele
                #     self._create_wall_opening()
                #     # Retornar CONTINUE_INPUT:
                #     # → framework llama start_next_input()
                #     # → script_object_interactor es None → execute_script_object() es llamado
                #     # → execute() corre con opening_guid seteado → cache actualizado
                #     self._create_union_frames = True
                #     self._elements_placed = False
                #     return OnCancelFunctionResult.CONTINUE_INPUT

            # ── SEGUNDO ESC (o modo modificación) ───────────────────────────────────
            # opening_guid ya está en build_ele → execute() ya lo incluyó en el cache
                # self._create_wall_opening() # opening premarc
                # print("create wall opening")
                # # Manage niche or windows opening from persianas (box shutter)
                # if self.build_ele.ComboBoxPersianas.value == "MONOBLOCK OCULT":
                #     # Width_persiana: Premaco queda fijo en parte trasera
                #     width_persiana = self.detected_wall_thickness - self.build_ele.thickness.value + self.build_ele.PersianaWidth.value
                #     self._create_wall_opening(
                #             height   = self.build_ele.PersianaHeight.value,
                #             width    = width_persiana,
                #             bottom_z = self.placement_pnt.Z
                #         )
                # elif self.build_ele.ComboBoxPersianas.value == "FALS CALAIX":
                #     # Usar placement_pnt (cara trasera del muro) como start_pnt.
                #     # OpeningCreationUtil usa ese punto directamente como 2D start
                #     # del GeneralOpeningElement, lo que indica a Allplan la cara trasera.
                #     opening_util = OpeningCreationUtil()
                #     solid_opening = SolidOpening(
                #         solid    = None,
                #         placement = self.placement_pnt,
                #         size     = [
                #             self.build_ele.width.value,
                #             self.build_ele.PersianaWidth.value,
                #             self.build_ele.PersianaHeight.value,
                #         ]
                #     )
                #     opening_util.create_openings(self.selected_wall, [solid_opening], [])
                # elif self.build_ele.ComboBoxPersianas.value == "LAMISOL VIST":
                #     # TODO: logic window opening from persianas (lamisol vist)
                #     # height: self.build_ele.PersianaHeight.value
                #     # width: self.detected_wall_thickness
                #     self._create_wall_opening(
                #         height   = self.build_ele.PersianaHeight.value,
                #         width    = self.detected_wall_thickness,
                #         bottom_z = self.placement_pnt.Z
                #     )
                # ── SEGUNDO ESC (o modo modificación) ───────────────────────────────────
                # opening_guid ya está en build_ele → execute() ya lo incluyó en el cache
                if self.is_modification_mode and self.build_ele.opening_guid.value:
                    self._create_wall_opening(modify_existing=True)
                elif (
                    not self.is_modification_mode
                    or not self.build_ele.opening_guid.value
                ):
                    self._create_wall_opening()
                self._create_union_frames = True
                self._execute()
                return OnCancelFunctionResult.CANCEL_INPUT

        return OnCancelFunctionResult.CANCEL_INPUT

    def draw_placement_preview(self):
        preview_model = self._create_accumulated_placement_preview(
            self.point_result.input_point
        )

        AllplanBaseElements.DrawElementPreview(
            self.document, AllplanGeo.Matrix3D(), preview_model, False, None
        )

    def get_data_endpoint(self, at1value: str) -> dict:
        if not _premarc_comandes_ot_enabled():
            return _premarc_empty_data_endpoint()
        try:
            # Thickness manual → endpoint de valores por defecto (formato values)
            # Thickness de paleta → endpoint por at1value (formato options)
            if self.build_ele.enable_manual_thickness.value:
                url = f"{API_URL_DEFAULT}"
            else:
                url = f"{API_URL}?at1value={str(at1value)}"

            response = self.session.get(url, verify=False)

            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                print("Success data endpoint:")
                # print(data)
                return data

        except Exception as e:
            _warn_comandes_ot_once(
                f"[Premarc] ComandesOT no disponible ({e}); listas dinámicas vacías. "
                "La API solo se usa si PREMARC_USE_COMANDES_OT=1 y el servicio responde."
            )
        return _premarc_empty_data_endpoint()

    def get_values_for_config_API(self) -> dict:
        fallback = {"values": _premarc_fallback_config_values()}
        if not _premarc_comandes_ot_enabled():
            return fallback
        try:
            url = f"{API_URL_AT1}"

            response = self.session.get(url, verify=False)

            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                print("Success data endpoint:")
                # print(data)
                vals = data.get("values") if isinstance(data, dict) else None
                if not vals:
                    return fallback
                return data
            return fallback
        except Exception as e:
            _warn_comandes_ot_once(
                f"[Premarc] ComandesOT no disponible ({e}); usando grosores locales."
            )
            return fallback

    # Helper API
    # def get_description_by_position(self, data, position):
    #     """Obtiene las descripciones de una posición específica
    #     data: datos de la API
    #     position: posición segun Excel -> AT2=1, AT3=2, AT4=3, etc
    #     """
    #     print(f"Data: {data}")
    #     print(f"Position: {position}")
    #     option_values = next((option['values'] for option in data['options'] if option['position'] == position), None)
    #     if option_values:
    #         return [value_item['description'] for value_item in option_values]
    #     return None

    # def get_description_by_position(self, data, position):
    #     """
    #     Obtiene las descripciones de una posición específica.
    #     Soporta dos formatos de API:
    #     - options: { options: [{ position, values: [{description, value}] }] }  (res_295)
    #     - values:  { values: { "2", "3", ...: [{key, value}] } }               (res.json manual)
    #     position: AT2=1, AT3=2, AT4=3, AT5=4, AT6=5, AT7=6, AT8=7, AT9=8
    #     """
    #     # print(f"Data: {data}")
    #     # print(f"Position: {position}")

    #     # Validar que data no sea None y tenga la estructura esperada
    #     if not data or not isinstance(data, dict):
    #         print("Warning: data is None or not a dictionary")
    #         return []

    #     # Validar que exista la clave 'options'
    #     if 'options' not in data:
    #         print("Warning: 'options' key not found in data")
    #         return []

    #     options = data.get('options', [])
    #     if not options or not isinstance(options, list):
    #         print("Warning: 'options' is empty or not a list")
    #         return []

    #     # Buscar la opción con la posición especificada
    #     option_values = None
    #     for option in options:
    #         if not isinstance(option, dict):
    #             continue
    #         if option.get('position') == position:
    #             option_values = option.get('values')
    #             break

    #     # Validar y extraer las descripciones
    #     if not option_values or not isinstance(option_values, list):
    #         print(f"Warning: No values found for position {position}")
    #         return []

    #     descriptions = []
    #     for value_item in option_values:
    #         if isinstance(value_item, dict) and 'description' in value_item:
    #             descriptions.append(value_item['description'])

    #     return descriptions

    def get_description_by_position(self, data, position):
        """Obtiene las descripciones de una posición específica.
        Soporta dos formatos de API:
        - options: { options: [{ position, values: [{description, value}] }] }  (res_295)
        - values:  { values: { "2", "3", ...: [{key, value}] } }               (res.json manual)
        position: AT2=1, AT3=2, AT4=3, AT5=4, AT6=5, AT7=6, AT8=7, AT9=8
        """
        if not data or not isinstance(data, dict):
            print("Warning: data is None or not a dictionary")
            return []
        # Formato 1: API por thickness → options
        if "options" in data:
            options = data.get("options", [])
            for option in options:
                if isinstance(option, dict) and option.get("position") == position:
                    option_values = option.get("values", [])
                    return [
                        v["description"]
                        for v in option_values
                        if isinstance(v, dict) and "description" in v
                    ]
            return []
        # Formato 2: API manual/default → values
        # position 1 → key "2", position 2 → key "3", etc.
        if "values" in data:
            key = str(position + 1)
            option_values = data.get("values", {}).get(key, [])
            return [
                v["value"]
                for v in option_values
                if isinstance(v, dict) and "value" in v
            ]
        print("Warning: formato de data no reconocido (ni 'options' ni 'values')")
        return []

    def crearListaAbiertoCerrado(self):
        """Crea una lista de abierto/cerrado"""
        listaActual = self.build_ele.valueListaAbiertoCerrado.value
        data = self.data_endpoint

        listaAbiertoCerrado = self.get_description_by_position(data, 1)

        debe_actualizar = len(listaActual) == 0 or listaActual != listaAbiertoCerrado

        # TODO quitar
        if len(listaAbiertoCerrado) == 0:
            listaAbiertoCerrado = ['TANCAT', 'OBERT FEMELLA DRETA', 'OBERT FEMELLA ESQUERRA', 'OBERT FEMELLA DRETA + REA', 'OBERT FEMELLA ESQUERRA + REA', 'OBERT NO FEMELLA DRETA', 'OBERT NO FEMELLA ESQUERRA', 'OBERT NO FEMELLA DRETA + REA', 'OBERT NO FEMELLA ESQUERRA + REA', 'SUP. FEMELLA / INF NO FEMELLA DRET.', 'SUP. FEMELLA / INF NO FEMELLA ESQ.', 'SUP. FEMELLA / INF NO FEMELLA DRET. + REA', 'SUP. FEMELLA / INF NO FEMELLA ESQ. + REA', 'SUP. NO FEMELLA / INF. FEMELLA DRET.', 'SUP. NO FEMELLA / INF. FEMELLA ESQ.', 'SUP. NO FEMELLA / INF. FEMELLA DRET. + REA', 'SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA', 'OBERT PER DALT', 'OBERT PER DALT + REA', 'OBERT PER DALT + REA VARIANT', 'OBERT PER BAIX', 'OBERT PER BAIX + REA', 'OBERT PER BAIX + REA VARIANT']

        opciones_locales_anadidas = False
        for option in (
            "OBERT PER DALT",
            "OBERT PER DALT + REA",
            "OBERT PER DALT + REA VARIANT",
            "OBERT PER BAIX",
            "OBERT PER BAIX + REA",
            "OBERT PER BAIX + REA VARIANT",
        ):
            if option not in listaAbiertoCerrado:
                listaAbiertoCerrado.append(option)
                opciones_locales_anadidas = True

        if debe_actualizar or opciones_locales_anadidas:
            self.build_ele.valueListaAbiertoCerrado.value = listaAbiertoCerrado

    def crearListaPendiente(self):
        """Crea una lista de pendiente"""
        listaActual = self.build_ele.valueListaPendiente.value
        data = self.data_endpoint
        listaPendiente = self.get_description_by_position(data, 2)

        # TODO quitar
        if len(listaPendiente) == 0:
            listaPendiente = ['NO', 'SI']

        debe_actualizar = len(listaActual) == 0 or listaActual != listaPendiente
        if debe_actualizar:
            self.build_ele.valueListaPendiente.value = listaPendiente

    def crearListaEncajes(self):
        """Crea una lista de encajes"""
        listaActual = self.build_ele.valueListaEncajes.value
        data = self.data_endpoint
        listaEncajes = self.get_description_by_position(data, 4)

        # TODO quitar
        if len(listaEncajes) == 0:
            listaEncajes = ['NO', '35*30', '70*30', 'PLEC INFERIOR']

        debe_actualizar = len(listaActual) == 0 or listaActual != listaEncajes
        if debe_actualizar:
            self.build_ele.valueListaEncajes.value = listaEncajes

    def crearListaEscuadras(self):
        """Crea una lista de escuadras"""
        listaActual = self.build_ele.valueListaEscuadras.value
        data = self.data_endpoint
        listaEscuadras = self.get_description_by_position(data, 7)

        # TODO quitar
        if len(listaEscuadras) == 0:
            listaEscuadras = ['NO', '2', '4']

        debe_actualizar = len(listaActual) == 0 or listaActual != listaEscuadras
        if debe_actualizar:
            self.build_ele.valueListaEscuadras.value = listaEscuadras

    def crearListaTubos(self):
        """Crea una lista de tubos"""
        listaActual = self.build_ele.valueListaTubos.value
        data = self.data_endpoint
        listaTubos = self.get_description_by_position(data, 8)

        # TODO quitar
        if len(listaTubos) == 0:
            listaTubos = ['NO', '1 VERT.', '2 VERT.', '3 VERT.', '4 VERT.', '1 HORIT.', '2 HORITZ.']

        debe_actualizar = len(listaActual) == 0 or listaActual != listaTubos
        if debe_actualizar:
            self.build_ele.valueListaTubos.value = listaTubos

    def crearListaPerianas(self):
        """Crea una lista de perianas"""
        listaActual = self.build_ele.valueListaPersianas.value
        data = self.data_endpoint
        listaPersianas = self.get_description_by_position(data, 6)

        # TODO quitar
        if len(listaPersianas) == 0:
            listaPersianas = ['NO', 'MONOBLOCK OCULT', 'LAMISOL VIST', 'METALUNIC VIST', 'FALS CALAIX']

        debe_actualizar = len(listaActual) == 0 or listaActual != listaPersianas
        if debe_actualizar:
            self.build_ele.valueListaPersianas.value = listaPersianas

    def crearListaConfiguraciones(self):
        """Crea una lista de configuraciones"""
        data = self.values_for_config or {}
        values = data.get("values") or {}
        if not values:
            values = _premarc_fallback_config_values()
        lista_conf = [values[k] for k in sorted(values, key=int)]
        self.build_ele.valueListaGrosor.value = lista_conf

    def update_pallete_values(self):
        """Actualiza los valores de la paleta"""
        self.data_endpoint = self.get_data_endpoint(self.get_thickness_for_api())
        self.crearListaPendiente()
        self.crearListaAbiertoCerrado()
        self.load_passama_checkboxes()
        self.load_rebajes_checkboxes()
        self.default_options_rebajes()
        self.crearListaEncajes()
        self.crearListaEscuadras()
        self.crearListaTubos()
        self.crearListaPerianas()

    # def getValueForDescription(self, data: dict, position: int, description: str):
    #     """Obtiene el valor de una descripción específica"""
    #     option_position = next((opt for opt in data['options'] if opt['position'] == position), None)

    #     if option_position:
    #         value = next((v['value'] for v in option_position['values'] if v['description'] == description), None)
    #         print(f"Valor de {description}: {value}")  # Resultado: 0
    #     else:
    #         print(f"No se encontró un elemento con position = {position}")
    #         value = ''
    #     return value

    def getValueForDescription(self, data: dict, position: int, description: str):
        """Obtiene el valor numérico asociado a una descripción.
        Soporta dos formatos de API:
        - options: values tiene {description, value} → devuelve value
        - values:  arrays tienen {key, value} donde value=descripción → devuelve key
        """
        try:
            if not data or not isinstance(data, dict):
                print("Warning: data is None or not a dictionary")
                return ""

            # Formato 1: API por thickness (res_295) → options
            if "options" in data:
                option_position = next(
                    (
                        opt
                        for opt in data.get("options", [])
                        if opt.get("position") == position
                    ),
                    None,
                )
                if option_position:
                    value = next(
                        (
                            v["value"]
                            for v in option_position.get("values", [])
                            if isinstance(v, dict)
                            and v.get("description") == description
                        ),
                        None,
                    )
                    if value is not None:
                        return value
                print(
                    f"No se encontró elemento con position={position} y description={description}"
                )
                return ""

            # Formato 2: API manual (res.json) → values
            if "values" in data:
                key = str(position + 1)
                option_values = data.get("values", {}).get(key, [])
                for v in option_values:
                    if isinstance(v, dict) and v.get("value") == description:
                        return v.get("key", "")
                print(
                    f"No se encontró elemento en key={key} con description={description}"
                )
                return ""

            print("Warning: formato de data no reconocido")
            return ""

        except Exception as ex:
            print(f"ERROR: {ex}")
            return ""

    def categorizeByRelation(self, base: float, altura: float) -> str:
        """
        Determina la categoría según la relación entre base y altura.
        Cuadrado: r >= 0.75; Largo: r < 0.75 y base > altura; Alto: r < 0.75 y altura > base.
        """
        if base <= 0 or altura <= 0:
            return ""  # o lanzar error, según tu criterio

        menor = min(base, altura)
        mayor = max(base, altura)
        r = menor / mayor

        if r >= 0.75:
            return "cuadrado"
        if base > altura:
            return "largo"
        return "alto"

    def getValuesFromInputDataPallet(self):
        """
        Obtiene los valores de la paleta de entrada
        Position: AT2 = 1, AT3 = 2, AT4 = 3, AT5 = 4, AT6 = 5, AT7 = 6, AT8 = 7, AT9 = 8
        """
        data_endpoint = self.data_endpoint
        FALCAS_MAP = (
            FALCAS_MAP_NO_SLOPE
            if self.build_ele.ComboBoxPendiente.value == "NO"
            else FALCAS_MAP_SLOPE
        )
        ESCUADRAS_MAP = (
            ESCUADRAS_MAP_NO_SLOPE
            if self.build_ele.ComboBoxPendiente.value == "NO"
            else ESCUADRAS_MAP_SLOPE
        )
        ESCUADRAS_MAP_MANUAL = (
            ESCUADRAS_MAP_MANUAL_NO_SLOPE
            if self.build_ele.ComboBoxPendiente.value == "NO"
            else ESCUADRAS_MAP_MANUAL_SLOPE
        )
        at11_value = "0"
        if self.thickness_premarc == self.build_ele.thickness_wall.value:
            at11_value = "1"
        else:
            if self.thickness_premarc > self.build_ele.thickness_wall.value:
                at11_value = "2"
        pallete_values = {
            "at1": self.thickness_premarc,
            "at2": self.getValueForDescription(
                data_endpoint, 1, self.build_ele.ComboBoxAbiertoCerrado.value
            ),
            "at3": self.getValueForDescription(
                data_endpoint, 2, self.build_ele.ComboBoxPendiente.value
            ),
            "at4": self.buildOptionsSelectedFromMap(
                self.build_ele.valueListaPassama.value,
                self.build_ele.PassamaOptions.value,
                FALCAS_MAP,
            ),
            "at5": (
                "" if self.build_ele.ComboBoxEncajes.value not in ESCUADRAS_MAP else
                ESCUADRAS_MAP[self.build_ele.ComboBoxEncajes.value]
                if self.build_ele.EnableManualEncaje.value == 0
                else ESCUADRAS_MAP_MANUAL[
                    self.categorizeByRelation(
                        self.build_ele.EncajeBase.value,
                        self.build_ele.EncajeAltura.value,
                    )
                ]
            ),
            "at6": self.buildOptionsSelected(
                data_endpoint,
                5,
                self.build_ele.valueListaRebajes.value,
                self.build_ele.RebajesOptions.value,
            ),
            "at7": self.getValueForDescription(
                data_endpoint, 6, self.build_ele.ComboBoxPersianas.value
            ),
            "at8": self.getValueForDescription(
                data_endpoint, 7, self.build_ele.ComboBoxEscuadras.value
            ),
            "at9": (
                self.getValueForDescription(
                    data_endpoint, 8, self.build_ele.ComboBoxTubos.value
                )
                if self.build_ele.TypeTubos.value == "FABRICA"
                else ""
            ),
            "at10": (
                self.getValueForDescription(
                    data_endpoint, 8, self.build_ele.ComboBoxTubos.value
                )
                if self.build_ele.TypeTubos.value == "OBRA"
                else ""
            ),
            "at11": at11_value,
        }

        data = f"PREM#{pallete_values['at1']}.{pallete_values['at2']}.{pallete_values['at3']}.{pallete_values['at4']}.{pallete_values['at5']}.{pallete_values['at6']}.{pallete_values['at7']}.{pallete_values['at8']}.{pallete_values['at9']}.{pallete_values['at10']}"

        return data

    def buildOptionsSelected(
        self, data_endpoint: dict, position: int, listOptions, listValuesOptions
    ):
        """
        Construye las opciones seleccionadas
        """
        tuple_list = list(
            zip(
                self.build_ele.valueListaPassama.value,
                self.build_ele.PassamaOptions.value,
            )
        )
        tuple_list = list(zip(listOptions, listValuesOptions))

        values_list = []
        for name, value in tuple_list:
            if value == 1:
                values_list.append(
                    f"{self.getValueForDescription(data_endpoint, position, name)}"
                )

        options_selected = "-".join(values_list)

        if options_selected == "":
            return ""
        print(f"Options selected: {options_selected}")
        return options_selected

    def buildOptionsSelectedFromMap(
        self, listOptions, listValuesOptions, options_map=None
    ):
        print(f"List options: {listOptions}")
        if options_map is None:
            options_map = FALCAS_MAP_NO_SLOPE
        tuple_list = list(zip(listOptions, listValuesOptions))
        values_list = []
        for name, value in tuple_list:
            if value == 1:  # o "if value:" si son booleanos
                # if name == "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)":
                #     if self.build_ele.ComboBoxPersianas.value == "LAMISOL VIST":
                #         values_list.append("5")
                #     elif self.build_ele.ComboBoxPersianas.value == "METALUNIC VIST":
                #         values_list.append("6")
                #     else:
                #         values_list.append(options_map.get(name, ""))
                # else:
                #     values_list.append(options_map.get(name, ""))
                if name == "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)":
                    value = MAP_PERSIANAS.get(
                        self.build_ele.ComboBoxPersianas.value,
                        options_map.get(name, "8"),
                    )
                else:
                    value = options_map.get(name, "")
                values_list.append(value)
        options_selected = "-".join(values_list)
        return options_selected if options_selected else ""

    def get_color_by_thickness(self, thickness: int):
        if thickness in COLOR_THICKNESS_MAP:
            return COLOR_THICKNESS_MAP[thickness]
        else:
            return 19  # gris negruc

    # -- Define color tubos -- #

    def define_color_tubos(
        self, props_tubos_elements: AllplanBaseElements.CommonProperties
    ):
        """Function to get tub type and set color"""

        OBRA_TYPE = "OBRA"
        FABRICA_TYPE = "FABRICA"
        DEFAULT_COLOR = 6
        COLOR_ROJO = 6
        COLOR_VERDE = 4

        type_tubos_value = self.build_ele.TypeTubos.value
        if type_tubos_value == OBRA_TYPE:
            props_tubos_elements.Color = COLOR_ROJO
        elif type_tubos_value == FABRICA_TYPE:
            props_tubos_elements.Color = COLOR_VERDE
        else:
            props_tubos_elements.Color = DEFAULT_COLOR

    def _create_premarc_placement_preview_only(self):
        """Marco premarco + base color 48 + perfil U mientras se coloca el punto (sin XPS, ventana, ampits…)."""
        self.update_params()
        model_ele_list = ModelEleList()
        self.color_premarc = (
            self.build_ele.color_manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else COLOR_THICKNESS_MAP[self.thickness_premarc]
        )
        layer_frame_id = AllplanBaseElements.LayerService.GetIDByShortName(
            FRAME_LAYER, self.document
        )
        props_frame = AllplanBaseElements.CommonProperties()
        props_frame.Color = int(self.color_premarc)
        props_frame.Layer = layer_frame_id
        props_frame_base_no_slope = AllplanBaseElements.CommonProperties()
        props_frame_base_no_slope.Color = 48
        props_frame_base_no_slope.Layer = layer_frame_id
        layer_retall_ganxo = AllplanBaseElements.LayerService.GetIDByShortName(
            RETALL_GANXO_LAYER, self.document
        )
        props_rebajes_debug = AllplanBaseElements.CommonProperties()
        props_rebajes_debug.Color = 25
        props_rebajes_debug.Layer = layer_retall_ganxo
        frame, frame_base_no_slope, substract_rebajes = self.create_premarc_frame()
        self._append_frame_elements_to_model_list(model_ele_list, props_frame, frame)
        if frame_base_no_slope:
            model_ele_list.append_geometry_3d(
                frame_base_no_slope, props_frame_base_no_slope
            )
        for substract_rebaje in substract_rebajes:
            model_ele_list.append_geometry_3d(substract_rebaje, props_rebajes_debug)
        self._pink_sill_poly = frame_base_no_slope
        u_poly = self.create_u_accessory_polyhedron()
        if u_poly is not None:
            try:
                acc_layer_id = AllplanBaseElements.LayerService.GetIDByShortName(
                    ACCESSORIS_PREMARCS_LAYER, self.document
                )
            except Exception:
                acc_layer_id = None
            if acc_layer_id is not None:
                props_u = AllplanBaseElements.CommonProperties()
                props_u.Layer = acc_layer_id
                props_u.Color = U_ACCESSOR_COLOR_INT
                model_ele_list.append_geometry_3d(u_poly, props_u)
        return model_ele_list

    def create_premarc(self):
        if getattr(self, "_in_placement_preview", False):
            return self._create_premarc_placement_preview_only()

        model_ele_list = ModelEleList()

        layer_xps_id = AllplanBaseElements.LayerService.GetIDByShortName(
            XPS_LAYER, self.document
        )
        props_xps = AllplanBaseElements.CommonProperties()
        props_xps.Color = 7
        props_xps.Layer = layer_xps_id

        self.color_premarc = (
            self.build_ele.color_manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else COLOR_THICKNESS_MAP[self.thickness_premarc]
        )
        layer_frame_id = AllplanBaseElements.LayerService.GetIDByShortName(
            FRAME_LAYER, self.document
        )
        props_frame = AllplanBaseElements.CommonProperties()
        props_frame.Color = int(self.color_premarc)
        print(f"Color frame: {props_frame.Color}")
        props_frame.Layer = layer_frame_id

        props_frame_base_no_slope = AllplanBaseElements.CommonProperties()
        props_frame_base_no_slope.Color = 48
        props_frame_base_no_slope.Layer = layer_frame_id

        layer_optionals_elements_id = AllplanBaseElements.LayerService.GetIDByShortName(
            ACCESSORIS_PREMARCS, self.document
        )
        props_optional_elements = AllplanBaseElements.CommonProperties()
        props_optional_elements.Color = 8
        props_optional_elements.Layer = layer_optionals_elements_id

        layer_escaire_id = AllplanBaseElements.LayerService.GetIDByShortName(
            ESCAIRE_LAYER, self.document
        )
        props_squares = AllplanBaseElements.CommonProperties()
        props_squares.Color = 6  # rojo
        props_squares.Layer = layer_escaire_id

        layer_tubs_vertical_horizontal_id = (
            AllplanBaseElements.LayerService.GetIDByShortName(
                TUBS_HORIZONTAL_VERTICAL_LAYER, self.document
            )
        )
        props_vertical_tubs = AllplanBaseElements.CommonProperties()
        # props_vertical_tubs.Color = 4 # verde
        props_vertical_tubs.Layer = layer_tubs_vertical_horizontal_id

        # --- Define color -- #
        # Get and define color tubos vertical
        self.define_color_tubos(props_vertical_tubs)

        props_horizontal_tubs = AllplanBaseElements.CommonProperties()
        # props_horizontal_tubs.Color = 6 # rojo
        props_horizontal_tubs.Layer = layer_tubs_vertical_horizontal_id

        # Get and define color tubos horizontal
        self.define_color_tubos(props_horizontal_tubs)

        # --- End Define color -- #

        layer_tubs_rea_id = AllplanBaseElements.LayerService.GetIDByShortName(
            TUBS_REA_LAYER, self.document
        )
        props_cuboids_rea = AllplanBaseElements.CommonProperties()
        props_cylinders_rea = AllplanBaseElements.CommonProperties()
        props_cuboids_rea.Color = 4  # verde
        props_cuboids_rea.Layer = layer_tubs_rea_id
        props_cylinders_rea.Color = 8  # naranja
        props_cylinders_rea.Layer = layer_tubs_rea_id

        layer_falcas_id = AllplanBaseElements.LayerService.GetIDByShortName(
            FALCAS_LAYER, self.document
        )
        props_falcas = AllplanBaseElements.CommonProperties()
        props_falcas.Color = 5  # fucsia
        props_falcas.Layer = layer_falcas_id

        layer_box_shutter_id = AllplanBaseElements.LayerService.GetIDByShortName(
            BOX_SHUTTER_LAYER, self.document
        )
        props_box_shutter = AllplanBaseElements.CommonProperties()
        props_box_shutter.Color = int(self.color_premarc)
        props_box_shutter.Layer = layer_box_shutter_id

        layer_socket_id = AllplanBaseElements.LayerService.GetIDByShortName(
            ENCAIX_LAYER, self.document
        )
        props_encaix = AllplanBaseElements.CommonProperties()
        props_encaix.Color = int(self.color_premarc)
        props_encaix.Layer = layer_socket_id

        layer_window_id = AllplanBaseElements.LayerService.GetIDByShortName(
            WINDOW_LAYER, self.document
        )
        props_window = AllplanBaseElements.CommonProperties()
        props_window.Color = 16
        props_window.Layer = layer_window_id

        layer_mosquitera_id = AllplanBaseElements.LayerService.GetIDByShortName(
            MOSQUITERA_LAYER, self.document
        )
        props_mosquitera = AllplanBaseElements.CommonProperties()
        props_mosquitera.Color = 8
        props_mosquitera.Layer = layer_mosquitera_id

        layer_ampit_id = AllplanBaseElements.LayerService.GetIDByShortName(
            AMPIT_LAYER, self.document
        )
        props_ampit = AllplanBaseElements.CommonProperties()
        props_ampit.Color = 91
        props_ampit.Layer = layer_ampit_id

        layer_ampit_eix_fg_id = AllplanBaseElements.LayerService.GetIDByShortName(
            LAYER_AMPIT_EIX_FORMIGO, self.document
        )
        props_ampit_eix_fg = AllplanBaseElements.CommonProperties()
        props_ampit_eix_fg.Layer = layer_ampit_eix_fg_id

        layer_ampit_eix_add_id = AllplanBaseElements.LayerService.GetIDByShortName(
            LAYER_AMPIT_EIX_AFEGIT, self.document
        )
        props_ampit_eix_add = AllplanBaseElements.CommonProperties()
        props_ampit_eix_add.Layer = layer_ampit_eix_add_id

        layer_space_real_id = AllplanBaseElements.LayerService.GetIDByShortName(
            SPACE_LAYER_REAL, self.document
        )
        props_space_real = AllplanBaseElements.CommonProperties()
        props_space_real.Color = 6  # red. Change to same color as premarc
        props_space_real.Layer = layer_space_real_id

        layer_space_inner_id = AllplanBaseElements.LayerService.GetIDByShortName(
            SPACE_LAYER_INNER, self.document
        )
        props_space_inner = AllplanBaseElements.CommonProperties()
        props_space_inner.Color = 6  # red. Change to same color as premarc
        props_space_inner.Layer = layer_space_inner_id

        layer_retall_ganxo = AllplanBaseElements.LayerService.GetIDByShortName(
            RETALL_GANXO_LAYER, self.document
        )
        props_retall_ganxo = AllplanBaseElements.CommonProperties()
        props_retall_ganxo.Color = 25
        props_retall_ganxo.Layer = layer_retall_ganxo

        ## Creates 3D elements
        # if self.build_ele.ComboBoxPersianas.value == "NO":
        #     xps = self.create_xps_premarc()
        # else:
        #     xps = self.create_xps_L_test()
        #     props_xps.Color = 8

        xps = self.create_xps_premarc()
        for elem in xps:
            model_ele_list.append_geometry_3d(elem, props_xps)

        xps_detail_value = self._build_xps_premarc_detail()
        xps_material_value = self.build_ele.xps_type.value or "XPS"

        # NUEVO
        # length_medidas_str = 2950
        # width_medidas_str = 600
        # thickness_medidas_str = length_medidas_str - 1600
        # medidas_str = f"{length_medidas_str}x{width_medidas_str}x{thickness_medidas_str}mm"

        xps_attribute_list = BuildingElementAttributeList()
        # xps_attribute_list.add_attribute(self.sizes_attribute_id, medidas_str)
        xps_attribute_list.add_attribute(self.pmp_xps_premarc_detail_text_id, xps_material_value)
        xps_attribute_list.add_attribute(self.pmp_id_premarc_id, self.val_pmp_id_premarc)
        if self.selected_wall:
            xps_attribute_list.add_attribute(self.pmp_pare_id, self.get_wall_material_name(self.selected_wall))
        xps_attribute_list.add_attribute(self.pmp_wall_id_attr_id, self.build_ele.wall_id.value)

        init_i = len(model_ele_list) - len(xps)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, xps_attribute_list.get_attribute_list()
            )

        frame, frame_base_no_slope, substract_rebajes = self.create_premarc_frame()
        for elem in frame:
            model_ele_list.append_geometry_3d(elem, props_frame)

        frame_attribute_list = BuildingElementAttributeList()
        #TODO añadir ComboBoxDEN a Cavidad de ventana
        # frame_attribute_list.add_attribute(self.den_id, self.build_ele.ComboBoxDEN.value)
        frame_attribute_list.add_attribute(self.den_id, self.getValuesFromInputDataPallet())
        frame_attribute_list.add_attribute(self.pmp_tipus_premarc_id, f"FONS {self.thickness_premarc} mm")
        frame_attribute_list.add_attribute(self.pmp_prem_encaje_altura_id, self.prem_encaje_altura)
        frame_attribute_list.add_attribute(self.pmp_prem_encaje_base_id, self.prem_encaje_base)
        frame_attribute_list.add_attribute(self.pmp_id_premarc_id, self.val_pmp_id_premarc)
        frame_attribute_list.add_attribute(self.pmp_prem_muro_id, self.build_ele.thickness_wall.value)
        frame_attribute_list.add_attribute(self.pmp_prem_color_id, self.color_id_to_rgb_or_hex()[0])
        if self.selected_wall:
            frame_attribute_list.add_attribute(self.pmp_pare_id, self.get_wall_material_name(self.selected_wall))
        frame_attribute_list.add_attribute(self.pmp_wall_id_attr_id, self.build_ele.wall_id.value)
        frame_attribute_list.add_attribute(self.pmp_premarc_type_id, self._premarc_labels_without_extras())
        frame_attribute_list.add_attribute(self.pmp_prem_fondo_id, self.thickness)
        frame_attribute_list.add_attribute(self.pmp_xps_premarc_detail_text_id, self.build_ele.xps_type.value)
        frame_attribute_list.add_attribute(self.pmp_xps_premarc_detail_id, xps_detail_value)
        first_label, extras = self._premarc_labels()  # updates INPUT_PMP_PREMARC_LABELS with auto value
        if self._user_label_override:
            plain_label = self._user_label_override
            self.build_ele.INPUT_PMP_PREMARC_LABELS.value = (
                plain_label  # keep field in sync
            )
        else:
            plain_label = self.build_ele.INPUT_PMP_PREMARC_LABELS.value
        label = self._format_premarc_label(plain_label)
        frame_attribute_list.add_attribute(self.pmp_premarc_labels_id, label)

        init_i = len(model_ele_list) - len(frame)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, frame_attribute_list.get_attribute_list()
            )

        if frame_base_no_slope and self.build_ele.ComboBoxPendiente.value == "NO":
            model_ele_list.append_geometry_3d(
                frame_base_no_slope, props_frame_base_no_slope
            )
        self._pink_sill_poly = frame_base_no_slope
        for substract_rebaje in substract_rebajes:
            model_ele_list.append_geometry_3d(substract_rebaje, props_retall_ganxo)

        u_poly = self.create_u_accessory_polyhedron()
        if u_poly is not None:
            acc_layer_id = None
            try:
                acc_layer_id = AllplanBaseElements.LayerService.GetIDByShortName(
                    ACCESSORIS_PREMARCS_LAYER, self.document
                )
            except Exception as ex:
                print(f"[Premarc] Accesorio U: capa {ACCESSORIS_PREMARCS_LAYER}: {ex}")
            if acc_layer_id is not None:
                props_accessor = AllplanBaseElements.CommonProperties()
                props_accessor.Layer = acc_layer_id
                props_accessor.Color = U_ACCESSOR_COLOR_INT
                model_ele_list.append_geometry_3d(u_poly, props_accessor)
                empty_attr = BuildingElementAttributeList()
                model_ele_list.set_element_attributes(
                    len(model_ele_list) - 1, empty_attr.get_attribute_list()
                )
            else:
                print(
                    f"[Premarc] Capa '{ACCESSORIS_PREMARCS_LAYER}' no disponible; accesorio U omitido"
                )

        (
            optionals_elements,
            squares,
            vertical_tubs,
            horizontal_tubs,
            falcas,
            polyhedron_socket,
        ) = self.create_premarc_optionals_elements()

        for elem in squares:
            model_ele_list.append_geometry_3d(elem, props_squares)

        squares_attribute_list = BuildingElementAttributeList()
        squares_attribute_list.add_attribute(
            self.pmp_premarc_element_labels_id, VAL_PMP_PREMARC_ELEMENT_LABELS_ESCAIRE
        )
        self._add_shared_generated_element_attributes(squares_attribute_list)

        init_i = len(model_ele_list) - len(squares)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, squares_attribute_list.get_attribute_list()
            )

        for elem in vertical_tubs:
            model_ele_list.append_geometry_3d(elem, props_vertical_tubs)

        vertical_tubes_attribute_list = BuildingElementAttributeList()
        vertical_tubes_attribute_list.add_attribute(
            self.pmp_premarc_element_labels_id,
            VAL_PMP_PREMARC_ELEMENT_LABELS_TUB_VERTICAL,
        )
        self._add_shared_generated_element_attributes(vertical_tubes_attribute_list)

        init_i = len(model_ele_list) - len(vertical_tubs)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, vertical_tubes_attribute_list.get_attribute_list()
            )

        for elem in horizontal_tubs:
            model_ele_list.append_geometry_3d(elem, props_horizontal_tubs)

        horitzontal_tubes_attribute_list = BuildingElementAttributeList()
        horitzontal_tubes_attribute_list.add_attribute(
            self.pmp_premarc_element_labels_id,
            VAL_PMP_PREMARC_ELEMENT_LABELS_TUB_HORITZONTAL,
        )
        self._add_shared_generated_element_attributes(
            horitzontal_tubes_attribute_list
        )

        init_i = len(model_ele_list) - len(horizontal_tubs)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, horitzontal_tubes_attribute_list.get_attribute_list()
            )

        cuboids_rea, cylinders_rea = self.create_premarc_REA()
        for elem in cuboids_rea:
            model_ele_list.append_geometry_3d(elem, props_cuboids_rea)
        for elem in cylinders_rea:
            model_ele_list.append_geometry_3d(elem, props_cylinders_rea)

        rea_attribute_list = BuildingElementAttributeList()
        rea_attribute_list.add_attribute(
            self.pmp_premarc_element_labels_id, VAL_PMP_PREMARC_ELEMENT_LABELS_REA
        )
        self._add_shared_generated_element_attributes(rea_attribute_list)

        init_i = len(model_ele_list) - len(cuboids_rea) - len(cylinders_rea)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, rea_attribute_list.get_attribute_list()
            )

        for elem in falcas:
            model_ele_list.append_geometry_3d(elem, props_falcas)

        falca_attribute_list = BuildingElementAttributeList()
        falca_attribute_list.add_attribute(
            self.pmp_premarc_element_labels_id, VAL_PMP_PREMARC_ELEMENT_LABELS_FALCA
        )
        self._add_shared_generated_element_attributes(falca_attribute_list)

        init_i = len(model_ele_list) - len(falcas)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, falca_attribute_list.get_attribute_list()
            )

        for elem in optionals_elements:
            model_ele_list.append_geometry_3d(elem, props_optional_elements)

        if polyhedron_socket:
            model_ele_list.append_geometry_3d(polyhedron_socket, props_encaix)
            socket_attribute_list = BuildingElementAttributeList()
            self._add_shared_generated_element_attributes(socket_attribute_list)
            model_ele_list.set_element_attributes(
                len(model_ele_list) - 1, socket_attribute_list.get_attribute_list()
            )

        box_shutter = self.create_box_shutter()
        for elem in box_shutter:
            model_ele_list.append_geometry_3d(
                elem, props_box_shutter
            )  # use same color from premarc

        if box_shutter:
            shutter_attribute_list = BuildingElementAttributeList()
            self._add_shared_generated_element_attributes(shutter_attribute_list)
            init_i = len(model_ele_list) - len(box_shutter)
            for i in range(init_i, len(model_ele_list)):
                model_ele_list.set_element_attributes(
                    i, shutter_attribute_list.get_attribute_list()
                )

        # window_3d, window_2d = self.create_premarc_window()
        # for elem in window_3d:
        #     model_ele_list.append_geometry_3d(elem, props_window)
        window_3d = []
        window_2d = []

        window_attribute_list = self._build_window_attribute_list()

        init_i = len(model_ele_list) - len(window_3d)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, window_attribute_list.get_attribute_list()
            )

        for elem in window_2d:
            model_ele_list.append_geometry_2d(elem, props_window)

        mosquitera = self.create_premarc_mosquitera()
        for elem in mosquitera:
            model_ele_list.append_geometry_3d(elem, props_mosquitera)

        bottom_open = self.is_bottom_open_premarc()

        if self.build_ele.EnableAmpit.value and not bottom_open:
            ampit, ampit_2d, ampit_edge_fg, ampit_edge_add, ampit_edge_add_cuboid, ampit_spec = self.create_premarc_ampit()

            # Per-type layer + FORCED color. A FRESH CommonProperties() instance
            # is built per material so the generic props_ampit defaults cannot
            # leak through. ColorByLayer=False + ForceColor=True is the only
            # combination that actually overrides the layer color in Allplan
            # (otherwise the layer's "Pen color from layer" wins regardless of
            # what we set on .Color). Same pattern as XPS.py preview faces.
            # Palette indices verified against NEOPRENO + PREMARCS' own usages:
            #   CERAMIC = 91 (rosa), CERAMICA_MAYOR = 8 (naranja),
            #   XAPA    = 3  (turquesa), PAVIMENTO     = 19 (gris negruc).
            # (color 7 in Allplan's standard palette is cyan/blue, NOT grey;
            #  this file's own get_color_by_thickness fallback uses 19 for grey)
            ampit_layer_id = AllplanBaseElements.LayerService.GetIDByShortName(ampit_spec["layer"], self.document)
            if ampit_layer_id is None:
                ampit_layer_id = AllplanBaseElements.LayerService.GetIDByShortName(AMPIT_LAYER, self.document)
            props_ampit_typed = AllplanBaseElements.CommonProperties()
            props_ampit_typed.Layer = ampit_layer_id
            props_ampit_typed.Color = ampit_spec["color"]
            props_ampit_typed.ColorByLayer = False
            props_ampit_typed.ForceColor = True

            for elem in ampit:
                model_ele_list.append_geometry_3d(elem, props_ampit_typed)

            # Aplacat is auto-derived from REB. BAIX selection (literal-text directive,
            # no manual checkbox, no pendiente gating). Sobresaliente saved is the
            # EFFECTIVE value: nominal spec + LENGTH_REBAJES_MM when aplacat is on.
            baix_selected = self.bottom_rebaje_enabled()
            aplacat_val = "SI" if baix_selected else "NO"
            sobresaliente_efectivo = ampit_spec["sobresaliente"] + (LENGTH_REBAJES_MM if baix_selected else 0)

            ampit_attribute_list = self._build_ampit_attribute_list()

            init_i = len(model_ele_list) - len(ampit)
            for i in range(init_i, len(model_ele_list)):
                model_ele_list.set_element_attributes(
                    i, ampit_attribute_list.get_attribute_list()
                )

            ampit_edge_fg_attribute_list = self._build_ampit_edge_fg_attribute_list()
            ampit_edge_add_attribute_list = self._build_ampit_edge_add_attribute_list()

            model_ele_list.append_geometry_3d(ampit_edge_fg, props_ampit_eix_fg)
            model_ele_list.set_element_attributes(
                len(model_ele_list) - 1, ampit_edge_fg_attribute_list.get_attribute_list()
            )

            if len(ampit_edge_add) > 0:
                model_ele_list.append_geometry_3d(ampit_edge_add, props_ampit_eix_add)
                model_ele_list.set_element_attributes(
                    len(model_ele_list) - 1,
                    ampit_edge_add_attribute_list.get_attribute_list(),
                )

            eix_fg_attribute_list = BuildingElementAttributeList()
            eix_fg_attribute_list.add_attribute(self.pmp_id_premarc_id, self.val_pmp_id_premarc)
            if self.selected_wall:
                eix_fg_attribute_list.add_attribute(self.pmp_pare_id, self.get_wall_material_name(self.selected_wall))
            eix_fg_attribute_list.add_attribute(self.pmp_wall_id_attr_id, self.build_ele.wall_id.value)

            eix_add_attribute_list = BuildingElementAttributeList()
            eix_add_attribute_list.add_attribute(self.pmp_id_premarc_id, self.val_pmp_id_premarc)
            if self.selected_wall:
                eix_add_attribute_list.add_attribute(self.pmp_pare_id, self.get_wall_material_name(self.selected_wall))
            eix_add_attribute_list.add_attribute(self.pmp_wall_id_attr_id, self.build_ele.wall_id.value)
            eix_add_attribute_list.add_attribute(self.pmp_fg_ampit_parts_id, self.build_ele.ampit_parts.value)
            eix_add_attribute_list.add_attribute(self.pmp_fg_ampit_ref_1_id, self.build_ele.ampit_ref_1.value)
            eix_add_attribute_list.add_attribute(self.pmp_fg_ampit_ref_2_id, self.get_wall_material_name(self.selected_wall))

            if len(ampit_edge_fg) > 0:
                model_ele_list.append_geometry_3d(ampit_edge_fg, props_ampit_eix_fg)
                model_ele_list.set_element_attributes(len(model_ele_list)-1, eix_fg_attribute_list.get_attribute_list())

            if len(ampit_edge_add) > 0:
                model_ele_list.append_geometry_3d(ampit_edge_add, props_ampit_eix_add)
                model_ele_list.set_element_attributes(len(model_ele_list)-1, eix_add_attribute_list.get_attribute_list())

            for cuboid in ampit_edge_add_cuboid:
                model_ele_list.append_geometry_3d(cuboid, props_ampit_eix_add)
                model_ele_list.set_element_attributes(
                    len(model_ele_list) - 1, eix_add_attribute_list.get_attribute_list()
                )

            for elem in ampit_2d:
                model_ele_list.append_geometry_2d(elem, props_ampit_typed)

        if self.build_ele.EnableImpermeabilizacio.value and not bottom_open:
            layer_imperm_id = AllplanBaseElements.LayerService.GetIDByShortName(IMPERM_LAYER, self.document)
            props_imperm = AllplanBaseElements.CommonProperties()
            props_imperm.Layer = layer_imperm_id

            imperm_type_name = self.build_ele.imperm_type.value
            imperm_spec = IMPERM_TYPE_SPECS.get(
                imperm_type_name, IMPERM_TYPE_SPECS["Water-Stop"]
            )
            imperm_type = imperm_spec["code"]
            props_imperm.Color = imperm_spec["color"]

            imperm_model = self._resolve_imperm_model()
            imperm_detail = self._resolve_imperm_detail(imperm_type_name, imperm_model)
            imperm_muntatge = self.build_ele.imperm_muntatge.value

            imperm = self.create_impermeabilitzacio()
            for elem in imperm:
                model_ele_list.append_geometry_3d(elem, props_imperm)

            imperm_attribute_list = BuildingElementAttributeList()
            imperm_attribute_list.add_attribute(
                self.pmp_tipus_impermeabilitzacio_id, imperm_type
            )
            if imperm_detail:
                imperm_attribute_list.add_attribute(self.pmp_fg_fus_tipus_impermeabilitzacio_detail_id, imperm_detail)
            imperm_attribute_list.add_attribute(self.pmp_fg_fusteria_tipus_muntatge_id, imperm_muntatge)
            self._add_shared_generated_element_attributes(imperm_attribute_list)
            init_i = len(model_ele_list) - len(imperm)
            for i in range(init_i, len(model_ele_list)):
                model_ele_list.set_element_attributes(
                    i, imperm_attribute_list.get_attribute_list()
                )

        poly_inside_space, poly_real_space = self.create_real_inside_space()
        if poly_inside_space:
            model_ele_list.append_geometry_3d(poly_inside_space, props_space_inner)
        if poly_real_space:
            model_ele_list.append_geometry_3d(poly_real_space, props_space_real)

        retall_representation = self.create_retall_representation()
        if retall_representation:
            model_ele_list.append_geometry_3d(retall_representation, props_retall_ganxo)

        return model_ele_list

    def create_xps_premarc(self):
        wall_thickness_xps = self._xps_wall_thickness_mm()

        if self.thickness <= wall_thickness_xps:
            return []

        xps_thickness = self.xps_thickness if self.xps_thickness_ind else (40 if self.xps_type == "XPS" else 120)
        sheet_offset = float(THICKNESS_MM)
        xps_depth = self.thickness - wall_thickness_xps - sheet_offset

        if xps_depth <= 0:
            return []

        horizontal_x = -xps_thickness - sheet_offset
        horizontal_width = self.width + ((xps_thickness + sheet_offset) * 2)
        left_x = -xps_thickness - sheet_offset
        right_x = self.width + sheet_offset
        bottom_z = -xps_thickness - sheet_offset
        vertical_z = -sheet_offset
        vertical_height = self.heigh + (sheet_offset * 2)
        xps_y = sheet_offset

        pos_bottom = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(horizontal_x, xps_y, bottom_z))
        pos_top = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(horizontal_x, xps_y, 0 + self.heigh))
        pos_left = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(left_x, xps_y, vertical_z))
        pos_right = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(right_x, xps_y, vertical_z))

        cuboid_bottom = AllplanGeo.Polyhedron3D.CreateCuboid(pos_bottom, horizontal_width, xps_depth, xps_thickness)
        cuboid_bottom = AllplanGeo.Move(cuboid_bottom, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))

        cuboid_top = AllplanGeo.Polyhedron3D.CreateCuboid(pos_top, horizontal_width, xps_depth, xps_thickness)
        cuboid_top = AllplanGeo.Move(cuboid_top, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))

        cuboid_left = AllplanGeo.Polyhedron3D.CreateCuboid(pos_left, xps_thickness,xps_depth, vertical_height)
        cuboid_left = AllplanGeo.Move(cuboid_left, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))

        cuboid_right = AllplanGeo.Polyhedron3D.CreateCuboid(pos_right, xps_thickness, xps_depth, vertical_height)
        cuboid_right = AllplanGeo.Move(cuboid_right, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))

        elems = [cuboid_bottom, cuboid_top, cuboid_left, cuboid_right]

        # Manage Open Premarc
        match self.build_ele.ComboBoxAbiertoCerrado.value:
            case "OBERT FEMELLA DRETA":
                elems.remove(cuboid_right)
            case "OBERT FEMELLA ESQUERRA":
                elems.remove(cuboid_left)
            case "OBERT PER DALT":
                elems.remove(cuboid_top)
            case "OBERT PER DALT + REA":
                elems.remove(cuboid_top)
            case "OBERT PER DALT + REA VARIANT":
                elems.remove(cuboid_top)
            case "OBERT PER BAIX":
                elems.remove(cuboid_bottom)
            case "OBERT PER BAIX + REA":
                elems.remove(cuboid_bottom)
            case "OBERT PER BAIX + REA VARIANT":
                elems.remove(cuboid_bottom)
            case "OBERT FEMELLA DRETA + REA":
                elems.remove(cuboid_right)
            case "OBERT FEMELLA ESQUERRA + REA":
                elems.remove(cuboid_left)
            case "OBERT NO FEMELLA DRETA":
                elems.remove(cuboid_right)
            case "OBERT NO FEMELLA ESQUERRA":
                elems.remove(cuboid_left)
            case "OBERT NO FEMELLA DRETA + REA":
                elems.remove(cuboid_right)
            case "OBERT NO FEMELLA ESQUERRA + REA":
                elems.remove(cuboid_left)
            case "SUP. FEMELLA / INF NO FEMELLA DRET.":
                elems.remove(cuboid_right)
            case "SUP. FEMELLA / INF NO FEMELLA ESQ.":
                elems.remove(cuboid_left)
            case "SUP. FEMELLA / INF NO FEMELLA DRET. + REA":
                elems.remove(cuboid_right)
            case "SUP. FEMELLA / INF NO FEMELLA ESQ. + REA":
                elems.remove(cuboid_left)
            case "SUP. NO FEMELLA / INF. FEMELLA DRET.":
                elems.remove(cuboid_right)
            case "SUP. NO FEMELLA / INF. FEMELLA ESQ.":
                elems.remove(cuboid_left)
            case "SUP. NO FEMELLA / INF. FEMELLA DRET. + REA":
                elems.remove(cuboid_right)
            case "SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA":
                elems.remove(cuboid_left)
            case _:
                print("Selected default")



        # Manage Disable XPS for Persianas
        metalunic_upper_xps_depth = min(
            max(float(self.build_ele.PersianaWidth.value), 0.0),
            max(float(xps_depth), 0.0),
        )
        metalunic_upper_xps_y = (
            self.thickness
            - wall_thickness_xps
            - metalunic_upper_xps_depth
        )
        metalunic_upper_top_cover = (
            float(xps_thickness) if self.xps_type == "PIR" else 40.0
        )
        metalunic_upper_top_xps_depth = min(
            metalunic_upper_xps_depth + metalunic_upper_top_cover,
            max(float(xps_depth), 0.0),
        )
        metalunic_upper_top_xps_y = (
            self.thickness
            - wall_thickness_xps
            - metalunic_upper_top_xps_depth
        )
        metalunic_inner_xps_depth = (
            self.thickness
            - wall_thickness_xps
            - self.build_ele.PersianaWidth.value
            - sheet_offset
        )
        add_xps_bool = metalunic_upper_xps_depth > 0
        add_xps_bool_fals_calaix = self.thickness - wall_thickness_xps - sheet_offset > xps_thickness
        shutter_xps_elems = []
        match self.build_ele.ComboBoxPersianas.value:
            case "METALUNIC VIST":
                print(
                    "[Premarc][XPS][METALUNIC] "
                    f"thickness={float(self.thickness):.1f}, "
                    f"wall_manual={float(wall_thickness_xps):.1f}, "
                    f"persiana_width={float(self.build_ele.PersianaWidth.value):.1f}, "
                    f"persiana_height={float(self.build_ele.PersianaHeight.value):.1f}, "
                    f"xps_thickness={float(xps_thickness):.1f}, "
                    f"metalunic_upper_xps_depth={float(metalunic_upper_xps_depth):.1f}, "
                    f"metalunic_upper_xps_y={float(metalunic_upper_xps_y):.1f}, "
                    f"metalunic_upper_top_xps_depth={float(metalunic_upper_top_xps_depth):.1f}, "
                    f"metalunic_upper_top_xps_y={float(metalunic_upper_top_xps_y):.1f}, "
                    f"metalunic_inner_xps_depth={float(metalunic_inner_xps_depth):.1f}"
                )
                if cuboid_top in elems:
                    elems.remove(cuboid_top)
                    if add_xps_bool:
                        print(
                            "[Premarc][XPS][METALUNIC] "
                            "Creando XPS metalunic + laterales superiores + tapa superior"
                        )
                        metalunic_xps = self.create_xps_metalunic()
                        upper_side_extensions = self.create_upper_xps_side_extensions(
                            metalunic_upper_xps_depth,
                            self.build_ele.PersianaHeight.value,
                            metalunic_upper_xps_y,
                        )
                        upper_top_extensions = self.create_upper_xps_top_extension(
                            metalunic_upper_top_xps_depth,
                            self.build_ele.PersianaHeight.value,
                            metalunic_upper_top_xps_y,
                        )
                        shutter_xps_elems.extend(metalunic_xps)
                        shutter_xps_elems.extend(upper_side_extensions)
                        shutter_xps_elems.extend(upper_top_extensions)
                        elems.extend(metalunic_xps)
                        elems.extend(upper_side_extensions)
                        elems.extend(upper_top_extensions)
                    else:
                        print(
                            "[Premarc][XPS][METALUNIC] "
                            "No se crea XPS superior: metalunic_upper_xps_depth <= 0"
                        )
            case "MONOBLOCK OCULT":
                if cuboid_top in elems:
                    elems.remove(cuboid_top)
                    upper_side_extensions = self.create_upper_xps_side_extensions(
                        xps_depth, self.build_ele.PersianaHeight.value
                    )
                    shutter_xps_elems.extend(upper_side_extensions)
                    elems.extend(upper_side_extensions)
                    upper_top_extensions = self.create_upper_xps_top_extension(
                        xps_depth, self.build_ele.PersianaHeight.value
                    )
                    shutter_xps_elems.extend(upper_top_extensions)
                    elems.extend(upper_top_extensions)
            case "FALS CALAIX":
                if cuboid_top in elems:
                    elems.remove(cuboid_top)
                    if add_xps_bool_fals_calaix:
                        fals_calaix_xps = self.create_xps_fals_calaix()
                        shutter_xps_elems.extend(fals_calaix_xps)
                        elems.extend(fals_calaix_xps)
        # Manage Disable XPS
        if self.build_ele.DisableTopXPS.value:
            if cuboid_top in elems:
                elems.remove(cuboid_top)
            for shutter_xps in shutter_xps_elems:
                if shutter_xps in elems:
                    elems.remove(shutter_xps)
            # Check if XPS enters the space available


        if self.build_ele.DisableBottomXPS.value:
            if cuboid_bottom in elems:
                elems.remove(cuboid_bottom)
        if self.build_ele.DisableLeftXPS.value:
            if cuboid_left in elems:
                elems.remove(cuboid_left)
        if self.build_ele.DisableRightXPS.value:
            if cuboid_right in elems:
                elems.remove(cuboid_right)

        return elems


    def create_xps_metalunic(self):
        wall_thickness_xps = self._xps_wall_thickness_mm()
        xps_thickness = self.xps_thickness if self.xps_thickness_ind else (40 if self.xps_type == "XPS" else 120)
        sheet_offset = float(THICKNESS_MM)
        xps_depth = self.thickness - wall_thickness_xps - self.build_ele.PersianaWidth.value - sheet_offset
        horizontal_x = -xps_thickness - sheet_offset
        horizontal_width = self.width + ((xps_thickness + sheet_offset) * 2)
        shutter_upper_z = sheet_offset

        position_vertical = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(horizontal_x, 0 , shutter_upper_z))
        position_horizontal = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(horizontal_x, 0 , shutter_upper_z))

        if xps_depth > 0:
            cuboid_vertical = AllplanGeo.Polyhedron3D.CreateCuboid(position_vertical, horizontal_width, xps_thickness, self.build_ele.PersianaHeight.value)
            cuboid_vertical = AllplanGeo.Move(cuboid_vertical, AllplanGeo.Vector3D(0,-(wall_thickness_xps + self.build_ele.PersianaWidth.value + xps_thickness),0))

            cuboid_horizontal = AllplanGeo.Polyhedron3D.CreateCuboid(position_horizontal, horizontal_width, xps_depth, xps_thickness)
            cuboid_horizontal = AllplanGeo.Move(cuboid_horizontal, AllplanGeo.Vector3D(0,-(self.thickness - sheet_offset),0))

            polyhedrons = AllplanGeo.Polyhedron3DList()

            polyhedrons += [cuboid_vertical, cuboid_horizontal]

            success, union_final = AllplanGeo.MakeUnion(polyhedrons)
            if success != True:
                print("Error in make union XPS metalunic")
                return []
            return [union_final]
            # return [cuboid_horizontal]

        return []

    def create_xps_fals_calaix(self):
        wall_thickness_xps = self._xps_wall_thickness_mm()
        xps_thickness = self.xps_thickness if self.xps_thickness_ind else (40 if self.xps_type == "XPS" else 120)
        sheet_offset = float(THICKNESS_MM)
        xps_depth = self.thickness - wall_thickness_xps - sheet_offset
        horizontal_x = -xps_thickness - sheet_offset
        horizontal_width = self.width + ((xps_thickness + sheet_offset) * 2)
        shutter_upper_z = sheet_offset

        position_horizontal = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(horizontal_x, 0 , shutter_upper_z))

        if xps_depth > 0:
            cuboid_horizontal = AllplanGeo.Polyhedron3D.CreateCuboid(position_horizontal, horizontal_width, xps_depth, xps_thickness)
            cuboid_horizontal = AllplanGeo.Move(cuboid_horizontal, AllplanGeo.Vector3D(0,-(self.thickness - sheet_offset),0))
            return [cuboid_horizontal]

        return []

    def create_upper_xps_side_extensions(self, depth: float, height: float, y_offset: float = THICKNESS_MM):
        """Create the two XPS side extensions above the opening top.

        Local reference:
        - opening top plane is z=0 after the common move(0, -thickness, -heigh)
        - positive local Z grows upward above the opening
        - y_offset is expressed before the common move; final Y = y_offset - thickness
        - shutter XPS starts 3 mm above the opening top to clear the premarc sheet
        """
        if depth <= 0 or height <= 0:
            return []

        xps_thickness = (
            self.xps_thickness
            if self.xps_thickness_ind
            else (40 if self.xps_type == "XPS" else 120)
        )
        sheet_offset = float(THICKNESS_MM)
        left_x = -xps_thickness - sheet_offset
        right_x = self.width + sheet_offset
        shutter_upper_z = float(THICKNESS_MM)

        pos_left_top = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(left_x, y_offset, self.heigh + shutter_upper_z)
        )
        pos_right_top = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(right_x, y_offset, self.heigh + shutter_upper_z)
        )

        cuboid_left_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_left_top, xps_thickness, depth, height
        )
        cuboid_right_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_right_top, xps_thickness, depth, height
        )

        move_vec = AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        cuboid_left_top = AllplanGeo.Move(cuboid_left_top, move_vec)
        cuboid_right_top = AllplanGeo.Move(cuboid_right_top, move_vec)
        return [cuboid_left_top, cuboid_right_top]

    def create_upper_xps_top_extension(self, depth: float, height: float, y_offset: float = THICKNESS_MM):
        """Create the XPS top piece above the shutter zone."""
        if depth <= 0 or height <= 0:
            return []

        xps_thickness = (
            self.xps_thickness
            if self.xps_thickness_ind
            else (40 if self.xps_type == "XPS" else 120)
        )
        sheet_offset = float(THICKNESS_MM)
        horizontal_x = -xps_thickness - sheet_offset
        horizontal_width = self.width + ((xps_thickness + sheet_offset) * 2)
        shutter_upper_z = sheet_offset

        pos_top_upper = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(horizontal_x, y_offset, self.heigh + height + shutter_upper_z)
        )
        cuboid_top_upper = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top_upper, horizontal_width, depth, xps_thickness
        )
        cuboid_top_upper = AllplanGeo.Move(
            cuboid_top_upper, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        )
        return [cuboid_top_upper]

    # TODO: MODIFICACION PRUEBAS XPS L

    def create_xps_L_test(self):

        # =========================
        # PARÁMETROS
        # =========================

        # variables height width thickness
        height_premarco_value = self.build_ele.heigh.value
        width_premarco_value = self.build_ele.width.value
        thickness_premarco_value = self.build_ele.thickness.value

        # Height premarco: 1410.0
        # Width premarco: 1200.0
        # Thickness premarco: 295

        # Definicion de espesor del XPS, si es XPS
        # xps_thickness = 40
        # xps_thickness = 40 if self.xps_type == "XPS" else 120

        xps_thickness_grosor = self.xps_thickness
        if self.xps_type == "XPS":
            xps_thickness = xps_thickness_grosor
        else:
            xps_thickness = 120

        # xps_thickness = 40

        valor_chapa = 3
        correccion_tamaño = 6 #TODO: Revisar porque la corrección tamaño es necesaria
        valor_hardcode_pared_trasera = 160
        alto_xps_horizontal = 20
        alto_box_shutter = 260
        mitad_box_shutter = BOX_SHUTTER_WIDTH / 2
        correccion_tamaño_harcode = 21 # profundidad del xps bajo

        # l_width  = 40
        l_width  = xps_thickness

        # l_depth  = (130 / 2) + 40                 # Aca es el valor BOX_SHUTTER_WIDTH 130 + espesor del XPS persiana
        l_depth  = mitad_box_shutter + xps_thickness                 # Aca es el valor BOX_SHUTTER_WIDTH 130 + espesor del XPS persiana

        # l_height = 240
        l_height = alto_box_shutter - alto_xps_horizontal

        # v_width  = 40
        v_width  = xps_thickness

        # v_depth  = 135 - 3 # Aca es el valor harcode de 135 del ticket y 3 es la chapa 295 - 160 = 135 lo que hoy es 175 SIEMPRE 160
        v_depth = thickness_premarco_value - valor_hardcode_pared_trasera - valor_chapa

        # v_height = 1436 - 20
        v_height = height_premarco_value + correccion_tamaño + alto_xps_horizontal

        # desplazamiento_opuesto = 1246 # ←  medida
        desplazamiento_opuesto = width_premarco_value + xps_thickness + correccion_tamaño

        inicio_en_origen_z = 3

        elems = []

        # =========================
        # FUNCIÓN INTERNA PARA CREAR UNA L
        # =========================

        def crear_L(offset_x):


            pos_horizontal_x = -xps_thickness - valor_chapa + offset_x
            pos_horizontal_y = -thickness_premarco_value + xps_thickness + 10 + 1 #TODO: correccion 10 y 1
            pos_horizontal_z = inicio_en_origen_z + alto_xps_horizontal

            # ---- HORIZONTAL ----
            pos_horizontal = AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    pos_horizontal_x,
                    pos_horizontal_y,
                    pos_horizontal_z
                )
            )

            cuboid_horizontal = AllplanGeo.Polyhedron3D.CreateCuboid(
                pos_horizontal,
                l_width,
                l_depth,
                l_height
            )

            pos_vertical_x = -xps_thickness - valor_chapa + offset_x
            pos_vertical_y = -thickness_premarco_value + valor_chapa
            pos_vertical_z = -v_height + inicio_en_origen_z + alto_xps_horizontal

            # ---- VERTICAL ----
            pos_vertical = AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    pos_vertical_x,
                    pos_vertical_y,
                    pos_vertical_z
                )
            )


            cuboid_vertical = AllplanGeo.Polyhedron3D.CreateCuboid(
                pos_vertical,
                v_width,
                v_depth,
                v_height
            )

            return [cuboid_horizontal, cuboid_vertical]

        # =========================
        # XPS EXTRA EN ORIGEN
        # =========================

        pos_xps_1_x = -valor_chapa # valor_chapa negativo
        pos_xps_1_y = -thickness_premarco_value + valor_chapa # valor_chapa negativo
        pos_xps_1_z = inicio_en_origen_z


        pos_xps_1 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(pos_xps_1_x, pos_xps_1_y, pos_xps_1_z)
        )

        xps_1 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_xps_1,
            width_premarco_value + correccion_tamaño, # Largo del XPS
            88, # Ancho del XPS en profundidad #TODO: Revisar como calcular este valor en base a lo que tengo
            alto_xps_horizontal # Alto del XPS
        )

        pos_xps_2_x = -valor_chapa # valor_chapa negativo
        pos_xps_2_y = -244 # TODO: Revisar como calcular este valor en base a lo que tengo
        pos_xps_2_z = alto_xps_horizontal + inicio_en_origen_z # suba el valor de alto_xps_horizontal

        pos_xps_2 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(pos_xps_2_x, pos_xps_2_y, pos_xps_2_z)
        )

        xps_2 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_xps_2,
            width_premarco_value + correccion_tamaño, # Largo del XPS
            xps_thickness, # Ancho del XPS
            alto_box_shutter - alto_xps_horizontal # Alto del XPS
        )

        pos_xps_3_x = -valor_chapa # valor_chapa negativo
        pos_xps_3_y = -thickness_premarco_value + valor_chapa # valor_chapa negativo
        pos_xps_3_z = -height_premarco_value - xps_thickness - inicio_en_origen_z


        pos_xps_3 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(pos_xps_3_x, pos_xps_3_y, pos_xps_3_z)
        )

        xps_3 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_xps_3,
            width_premarco_value + correccion_tamaño, # Largo del XPS
            88, # Ancho del XPS en profundidad #TODO: Revisar como calcular este valor en base a lo que tengo
            xps_thickness # Alto del XPS
        )

        # =========================
        # L IZQUIERDA (original)
        # =========================

        # elems.extend(crear_L(0))

        # =========================
        # L DERECHA (opuesta)
        # =========================

        # elems.extend(crear_L(desplazamiento_opuesto))


        # =========================
        # L IZQUIERDA (original)
        # =========================
        left_L = crear_L(0)
        cuboid_left_horizontal = left_L[0]
        cuboid_left_vertical = left_L[1]
        elems.extend(left_L)

        # =========================
        # L DERECHA (opuesta)
        # =========================
        right_L = crear_L(desplazamiento_opuesto)
        cuboid_right_horizontal = right_L[0]
        cuboid_right_vertical = right_L[1]
        elems.extend(right_L)

        # Arriba
        elems.append(xps_1)

        # persiana arriba
        elems.append(xps_2)

        # abajo
        elems.append(xps_3)

        # =========================
        # Manage Open Premarc
        # =========================

        selected = self.build_ele.ComboBoxAbiertoCerrado.value

        remove_right_cases = [
            "OBERT FEMELLA DRETA",
            "OBERT FEMELLA DRETA + REA",
            "OBERT NO FEMELLA DRETA",
            "OBERT NO FEMELLA DRETA + REA",
            "SUP. FEMELLA / INF NO FEMELLA DRET.",
            "SUP. FEMELLA / INF NO FEMELLA DRET. + REA",
            "SUP. NO FEMELLA / INF. FEMELLA DRET.",
            "SUP. NO FEMELLA / INF. FEMELLA DRET. + REA",
        ]

        remove_left_cases = [
            "OBERT FEMELLA ESQUERRA",
            "OBERT FEMELLA ESQUERRA + REA",
            "OBERT NO FEMELLA ESQUERRA",
            "OBERT NO FEMELLA ESQUERRA + REA",
            "SUP. FEMELLA / INF NO FEMELLA ESQ.",
            "SUP. FEMELLA / INF NO FEMELLA ESQ. + REA",
            "SUP. NO FEMELLA / INF. FEMELLA ESQ.",
            "SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA",
        ]

        if selected in remove_right_cases:
            if cuboid_right_vertical in elems:
                elems.remove(cuboid_right_vertical)

        if selected in remove_left_cases:
            if cuboid_left_vertical in elems:
                elems.remove(cuboid_left_vertical)


        # =========================
        # Manage Disable XPS
        # =========================

        if self.build_ele.DisableTopXPS.value:
            if xps_1 in elems:
                elems.remove(xps_1)

        if self.build_ele.DisableBottomXPS.value:
            if xps_3 in elems:
                elems.remove(xps_3)

        if self.build_ele.DisableLeftXPS.value:
            if cuboid_left_vertical in elems:
                elems.remove(cuboid_left_vertical)

        if self.build_ele.DisableRightXPS.value:
            if cuboid_right_vertical in elems:
                elems.remove(cuboid_right_vertical)

        return elems

    def extrude_frame(
        self, frame: AllplanGeo.Polygon3D, direction: str
    ) -> tuple[AllplanGeo.eGeometryErrorCode, AllplanGeo.Polyhedron3D]:
        """
        Extrude a frame to a polyhedron

        Args:
            frame
            direction

        Returns:
            tuple: (error_code, polyhedron)
        """
        area = AllplanGeo.PolygonalArea3D()
        area += frame

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()

        if direction == "frame_top":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, 1 * THICKNESS_MM))
        elif direction == "frame_bottom":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, -1 * THICKNESS_MM))
        elif direction == "frame_left":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(-1 * THICKNESS_MM, 0, 0))
        elif direction == "frame_right":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(1 * THICKNESS_MM, 0, 0))
        elif direction == "frame_finish_top":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 1 * THICKNESS_MM, 0))
        elif direction == "frame_finish_bottom":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 1 * THICKNESS_MM, 0))
        elif direction == "frame_finish_left":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 1 * THICKNESS_MM, 0))
        elif direction == "frame_finish_right":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 1 * THICKNESS_MM, 0))
        elif direction == "frame_square":
            extruded_solid.SetDirection(
                AllplanGeo.Vector3D(0, -1 * SQUARE_THICKNESS, 0)
            )
        elif direction == "frame_tub":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, -1 * self.heigh))
        elif direction == "frame_tub_horizontal":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(self.width, 0, 0))
        elif direction == "socket_frame_front":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 1 * THICKNESS_MM, 0))
        elif direction == "socket_frame_back":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, -1 * THICKNESS_MM, 0))
        elif direction == "socket_frame_top":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, -1 * THICKNESS_MM))
        elif direction == "fold_bottom":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, -1 * THICKNESS_MM))
        elif direction == "fold_top":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, 1 * THICKNESS_MM))
        elif direction == "perpendicular_union":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 1 * THICKNESS_MM, 0))
        elif direction == "frame_falca":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(1 * THICKNESS_MM, 0, 0))
        elif direction == "frame_hexagon_top":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, 1 * THICKNESS_MM * 2))
        elif direction == "frame_hexagon_bottom":
            extruded_solid.SetDirection(
                AllplanGeo.Vector3D(0, 0, -1 * THICKNESS_MM * 2)
            )
        elif direction == "tube_open_premarc":
            extruded_solid.SetDirection(
                AllplanGeo.Vector3D(0, 0, -1 * (self.heigh + 400))
            )
        elif direction == "box_shutter":
            extruded_solid.SetDirection(
                AllplanGeo.Vector3D(1 * (self.width + THICKNESS_MM * 2), 0, 0)
            )
        else:
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, 1))

        extruded_solid.SetRefPoint(AllplanGeo.Point3D(0, 0, 0))
        extruded_solid.SetExtrudedArea(area)

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)

        return error_code, polyhedron

    def get_square_y_offset(self):
        return self.build_ele.thickness_wall.value / 2 - SQUARE_THICKNESS / 2

    # def create_vertical_tub(self)->AllplanGeo.Polyhedron3D:
    #     frame_tub_bottom = AllplanGeo.Polygon3D()
    #     frame_tub_bottom += AllplanGeo.Point3D(0, -(self.thickness/2-TUB_WIDTH_LENGTH/2), 0)
    #     frame_tub_bottom += AllplanGeo.Point3D(0, -(self.thickness/2+TUB_WIDTH_LENGTH/2), 0)
    #     frame_tub_bottom += AllplanGeo.Point3D(TUB_WIDTH_LENGTH, -(self.thickness/2+TUB_WIDTH_LENGTH/2), 0)
    #     frame_tub_bottom += AllplanGeo.Point3D(TUB_WIDTH_LENGTH, -(self.thickness/2-TUB_WIDTH_LENGTH/2), 0)
    #     frame_tub_bottom += AllplanGeo.Point3D(0, -(self.thickness/2-TUB_WIDTH_LENGTH/2), 0)
    #     error_code, polyhedron_tub = self.extrude_frame(frame_tub_bottom, "frame_tub")
    #     return polyhedron_tub

    # def create_horizontal_tub(self)->AllplanGeo.Polyhedron3D:
    #     frame_tub_left = AllplanGeo.Polygon3D()
    #     frame_tub_left += AllplanGeo.Point3D(0, -(self.thickness/2-TUB_WIDTH_LENGTH/2), 0)
    #     frame_tub_left += AllplanGeo.Point3D(0, -(self.thickness/2+TUB_WIDTH_LENGTH/2), 0)
    #     frame_tub_left += AllplanGeo.Point3D(0, -(self.thickness/2+TUB_WIDTH_LENGTH/2), -TUB_WIDTH_LENGTH)
    #     frame_tub_left += AllplanGeo.Point3D(0, -(self.thickness/2-TUB_WIDTH_LENGTH/2), -TUB_WIDTH_LENGTH)
    #     frame_tub_left += AllplanGeo.Point3D(0, -(self.thickness/2-TUB_WIDTH_LENGTH/2), 0)
    #     error_code, polyhedron_tub = self.extrude_frame(frame_tub_left, "frame_tub_horizontal")
    #     return polyhedron_tub

    def create_vertical_tub(self) -> AllplanGeo.Polyhedron3D:
        # wall_center = self.build_ele.thickness_wall.value / 2 if self.build_ele.enable_manual_thickness.value else self._get_wall_thickness(self.selected_wall) / 2
        wall_center = self.build_ele.thickness_wall.value / 2
        frame_tub_bottom = AllplanGeo.Polygon3D()
        frame_tub_bottom += AllplanGeo.Point3D(
            0, -(wall_center - TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            0, -(wall_center + TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            TUB_WIDTH_LENGTH, -(wall_center + TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            TUB_WIDTH_LENGTH, -(wall_center - TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            0, -(wall_center - TUB_WIDTH_LENGTH / 2), 0
        )
        error_code, polyhedron_tub = self.extrude_frame(frame_tub_bottom, "frame_tub")
        return polyhedron_tub

    def create_horizontal_tub(self) -> AllplanGeo.Polyhedron3D:

        # wall_center = self.build_ele.thickness_wall.value / 2 if self.build_ele.enable_manual_thickness.value else self._get_wall_thickness(self.selected_wall) / 2
        wall_center = self.build_ele.thickness_wall.value / 2
        frame_tub_left = AllplanGeo.Polygon3D()
        frame_tub_left += AllplanGeo.Point3D(
            0, -(wall_center - TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_left += AllplanGeo.Point3D(
            0, -(wall_center + TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_left += AllplanGeo.Point3D(
            0, -(wall_center + TUB_WIDTH_LENGTH / 2), -TUB_WIDTH_LENGTH
        )
        frame_tub_left += AllplanGeo.Point3D(
            0, -(wall_center - TUB_WIDTH_LENGTH / 2), -TUB_WIDTH_LENGTH
        )
        frame_tub_left += AllplanGeo.Point3D(
            0, -(wall_center - TUB_WIDTH_LENGTH / 2), 0
        )
        error_code, polyhedron_tub = self.extrude_frame(
            frame_tub_left, "frame_tub_horizontal"
        )
        return polyhedron_tub

    def create_tubs_proportioned(self, tubs_number, orientation) -> list:
        polyhedron_tubs = []

        if orientation == VERTICAL_TUB:
            tub_spacing = self.width / (
                tubs_number + 1
            )  # Espacio entre centros de tubos
            tub_x_offset = (
                tub_spacing - TUB_WIDTH_LENGTH / 2
            )  # Offset desde el borde izquierdo

            for i in range(1, tubs_number + 1):
                # Posición X del centro del tubo
                tub_center_x = tub_spacing * i
                # Vector de traslación (centro del tubo menos la mitad del ancho del tubo)
                translation_vector = AllplanGeo.Vector3D(
                    tub_center_x - TUB_WIDTH_LENGTH / 2, 0, 0
                )
                polyhedron_tub = self.create_vertical_tub()
                polyhedron_tub_moved = AllplanGeo.Move(
                    polyhedron_tub, translation_vector
                )
                polyhedron_tubs.append(polyhedron_tub_moved)
            return polyhedron_tubs
        elif orientation == HORIZONTAL_TUB:
            tub_spacing = self.heigh / (
                tubs_number + 1
            )  # Espacio entre centros de tubos
            tub_x_offset = (
                tub_spacing - TUB_WIDTH_LENGTH / 2
            )  # Offset desde el borde izquierdo

            for i in range(1, tubs_number + 1):
                # Posición X del centro del tubo
                tub_center_z = tub_spacing * i
                # Vector de traslación (centro del tubo menos la mitad del ancho del tubo)
                translation_vector = AllplanGeo.Vector3D(
                    0, 0, -(tub_center_z - TUB_WIDTH_LENGTH / 2)
                )
                polyhedron_tub = self.create_horizontal_tub()
                polyhedron_tub_moved = AllplanGeo.Move(
                    polyhedron_tub, translation_vector
                )
                polyhedron_tubs.append(polyhedron_tub_moved)
            return polyhedron_tubs

    def create_socket(self, socket_width, socket_height):
        polyhedron_sockets = AllplanGeo.Polyhedron3DList()

        socket_frame_front = AllplanGeo.Polygon3D()
        socket_frame_front += AllplanGeo.Point3D(
            0, -self.thickness, -self.heigh
        )  # bottom left point
        socket_frame_front += AllplanGeo.Point3D(
            self.width, -self.thickness, -self.heigh
        )
        socket_frame_front += AllplanGeo.Point3D(
            self.width, -self.thickness, -(self.heigh - socket_height)
        )
        socket_frame_front += AllplanGeo.Point3D(
            0, -self.thickness, -(self.heigh - socket_height)
        )
        socket_frame_front += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)
        error_code, polyhedron_socket_front = self.extrude_frame(
            socket_frame_front, "socket_frame_front"
        )
        polyhedron_sockets.append(polyhedron_socket_front)

        socket_frame_top = AllplanGeo.Polygon3D()
        socket_frame_top += AllplanGeo.Point3D(
            0, -self.thickness, -(self.heigh - socket_height)
        )
        socket_frame_top += AllplanGeo.Point3D(
            0, -(self.thickness - socket_width), -(self.heigh - socket_height)
        )
        socket_frame_top += AllplanGeo.Point3D(
            self.width, -(self.thickness - socket_width), -(self.heigh - socket_height)
        )
        socket_frame_top += AllplanGeo.Point3D(
            self.width, -self.thickness, -(self.heigh - socket_height)
        )
        socket_frame_top += AllplanGeo.Point3D(
            0, -self.thickness, -(self.heigh - socket_height)
        )
        error_code, polyhedron_socket_top = self.extrude_frame(
            socket_frame_top, "socket_frame_top"
        )
        polyhedron_sockets.append(polyhedron_socket_top)

        socket_frame_back = AllplanGeo.Polygon3D()
        socket_frame_back += AllplanGeo.Point3D(
            0, -(self.thickness - socket_width), -self.heigh
        )  # bottom left point
        socket_frame_back += AllplanGeo.Point3D(
            self.width, -(self.thickness - socket_width), -self.heigh
        )
        socket_frame_back += AllplanGeo.Point3D(
            self.width, -(self.thickness - socket_width), -(self.heigh - socket_height)
        )
        socket_frame_back += AllplanGeo.Point3D(
            0, -(self.thickness - socket_width), -(self.heigh - socket_height)
        )
        socket_frame_back += AllplanGeo.Point3D(
            0, -(self.thickness - socket_width), -self.heigh
        )
        error_code, polyhedron_socket_back = self.extrude_frame(
            socket_frame_back, "socket_frame_front"
        )
        polyhedron_sockets.append(polyhedron_socket_back)

        return polyhedron_sockets

    def create_origin_falca_top(self)->AllplanGeo.Polygon3D:
        height_falca = HEIGHT_FALCA
        thickness_falca = THICKNESS_FALCA
        if self.build_ele.ComboBoxPersianas.value == "METALUNIC VIST":
            height_falca = self.build_ele.PersianaHeight.value
            thickness_falca = abs(
                self.thickness
                - self.detected_wall_thickness
                - self.build_ele.PersianaWidth.value
                - THICKNESS_MM
            )
        frame_falca = AllplanGeo.Polygon3D()
        frame_falca += AllplanGeo.Point3D(0, 0, 0)
        frame_falca += AllplanGeo.Point3D(0, 0, height_falca)
        frame_falca += AllplanGeo.Point3D(0, -MINUS_THICKNESS_FALCA, height_falca)
        frame_falca += AllplanGeo.Point3D(0, -thickness_falca, MINUS_HEIGHT_FALCA)
        frame_falca += AllplanGeo.Point3D(0, -thickness_falca, 0)
        # error_code, polyhedron_falca = self.extrude_frame(frame_falca, "frame_falca")
        # return polyhedron_falca
        return frame_falca

    def create_origin_falca_bottom(self) -> AllplanGeo.Polygon3D:

        frame_falca = AllplanGeo.Polygon3D()
        frame_falca += AllplanGeo.Point3D(0, 0, 0)
        frame_falca += AllplanGeo.Point3D(0, 0, -HEIGHT_FALCA)
        frame_falca += AllplanGeo.Point3D(0, -MINUS_THICKNESS_FALCA, -HEIGHT_FALCA)
        frame_falca += AllplanGeo.Point3D(0, -THICKNESS_FALCA, -MINUS_HEIGHT_FALCA)
        frame_falca += AllplanGeo.Point3D(0, -THICKNESS_FALCA, 0)
        frame_falca += AllplanGeo.Point3D(0, 0, 0)
        # error_code, polyhedron_falca = self.extrude_frame(frame_falca, "frame_falca")
        # return polyhedron_falca
        return frame_falca

    def create_hexagon_frame(self) -> AllplanGeo.Polygon3D:
        """
        Propiedades del hexagono https://es.wikipedia.org/wiki/Hex%C3%A1gono

        - a : longitud de un lado
        - Radio i: Radio del circulo inscrito
        - Radio u: Radio del circulo circunscrito


        - Radio u = a
        - Radio i = a / 2 * sqrt(3)
        """
        radius_u = LENGTH_SIDE_HEXAGON
        radius_i = LENGTH_SIDE_HEXAGON / 2 * math.sqrt(3)
        frame_hexagon = AllplanGeo.Polygon3D()
        frame_hexagon += AllplanGeo.Point3D(
            0, -(self.thickness / 2 - radius_u), 0
        )  # P1
        frame_hexagon += AllplanGeo.Point3D(
            radius_i, -(self.thickness / 2 - radius_u / 2), 0
        )  # P2
        frame_hexagon += AllplanGeo.Point3D(
            radius_i, -(self.thickness / 2 + radius_u / 2), 0
        )  # P3
        frame_hexagon += AllplanGeo.Point3D(
            0, -(self.thickness / 2 + radius_u), 0
        )  # P4
        frame_hexagon += AllplanGeo.Point3D(
            -radius_i, -(self.thickness / 2 + radius_u / 2), 0
        )  # P5
        frame_hexagon += AllplanGeo.Point3D(
            -radius_i, -(self.thickness / 2 - radius_u / 2), 0
        )  # P6
        frame_hexagon += AllplanGeo.Point3D(0, -(self.thickness / 2 - radius_u), 0)
        return frame_hexagon

    def create_polygon_open(
        self, position: str, minuend_polyhedron: AllplanGeo.Polyhedron3D
    ) -> AllplanGeo.Polyhedron3D:
        """
        Create a hexagon frame open
        Position: top right, bottom right, top left, bottom left
        """
        frame_hexagon = self.create_hexagon_frame()
        # 107,5 origin position femella after change requirements.
        if position == "top left":
            error_code, polyhedron_hexagon = self.extrude_frame(
                frame_hexagon, "frame_hexagon_top"
            )
            # Fix position hexagon top left
            translation_vector = AllplanGeo.Vector3D(
                -THICKNESS_MM, 107.5 - FIX_FEMELLA_Y, 0
            )
            polyhedron_hexagon_moved = AllplanGeo.Move(
                polyhedron_hexagon, translation_vector
            )

            error, polyhedron_top_open = AllplanGeo.MakeSubtraction(
                minuend_polyhedron, polyhedron_hexagon_moved
            )
            return polyhedron_top_open
        if position == "top right":
            translation_vector = AllplanGeo.Vector3D(
                self.width + THICKNESS_MM, 107.5 - FIX_FEMELLA_Y, 0
            )
            polyhedron_hexagon_moved = AllplanGeo.Move(
                frame_hexagon, translation_vector
            )
            error_code, polyhedron_hexagon = self.extrude_frame(
                polyhedron_hexagon_moved, "frame_hexagon_top"
            )
            if error_code != 0:
                return minuend_polyhedron

            error, polyhedron_open = AllplanGeo.MakeSubtraction(
                minuend_polyhedron, polyhedron_hexagon
            )
            if error != 0:
                return minuend_polyhedron
            return polyhedron_open
        if position == "bottom left":
            translation_vector = AllplanGeo.Vector3D(
                -THICKNESS_MM, 107.5 - FIX_FEMELLA_Y, -self.heigh
            )
            polyhedron_hexagon_moved = AllplanGeo.Move(
                frame_hexagon, translation_vector
            )
            error_code, polyhedron_hexagon = self.extrude_frame(
                polyhedron_hexagon_moved, "frame_hexagon_bottom"
            )
            if error_code != 0:
                return minuend_polyhedron

            error, polyhedron_open = AllplanGeo.MakeSubtraction(
                minuend_polyhedron, polyhedron_hexagon
            )
            if error != 0:
                return minuend_polyhedron
            return polyhedron_open
        if position == "bottom right":
            translation_vector = AllplanGeo.Vector3D(
                self.width + THICKNESS_MM, 107.5 - FIX_FEMELLA_Y, -self.heigh
            )
            polyhedron_hexagon_moved = AllplanGeo.Move(
                frame_hexagon, translation_vector
            )
            error_code, polyhedron_hexagon = self.extrude_frame(
                polyhedron_hexagon_moved, "frame_hexagon_bottom"
            )
            if error_code != 0:
                return minuend_polyhedron

            error, polyhedron_open = AllplanGeo.MakeSubtraction(
                minuend_polyhedron, polyhedron_hexagon
            )
            if error != 0:
                return minuend_polyhedron
            return polyhedron_open
        else:
            return minuend_polyhedron

    # def create_polygon_open(self, position: str, minuend_polyhedron: AllplanGeo.Polyhedron3D) -> AllplanGeo.Polyhedron3D:
    #     """
    #     Create a hexagon frame open
    #     Position: top right, bottom right, top left, bottom left
    #     """
    #     frame_hexagon = self.create_hexagon_frame()

    #     if position == "top left":
    #         error_code, polyhedron_hexagon = self.extrude_frame(frame_hexagon, "frame_hexagon")
    #         if error_code != 0:
    #             return minuend_polyhedron

    #         error, polyhedron_open = AllplanGeo.MakeSubtraction(minuend_polyhedron, polyhedron_hexagon)
    #         if error != 0:
    #             return minuend_polyhedron
    #         return polyhedron_open

    #     elif position == "top right":
    #         translation_vector = AllplanGeo.Vector3D(self.width, 0, 0)
    #         polyhedron_hexagon_moved = AllplanGeo.Move(frame_hexagon, translation_vector)
    #         error_code, polyhedron_hexagon = self.extrude_frame(polyhedron_hexagon_moved, "frame_hexagon")
    #         if error_code != 0:
    #             return minuend_polyhedron

    #         error, polyhedron_open = AllplanGeo.MakeSubtraction(minuend_polyhedron, polyhedron_hexagon)
    #         if error != 0:
    #             return minuend_polyhedron
    #         return polyhedron_open
    #     else:
    #         return minuend_polyhedron  # Retorna el poliedro original si la posición no es válida
    # Create tube for open premarc

    def create_union_premarc(
        self, polyhedron_list: list
    ) -> AllplanGeo.Polyhedron3D | None:
        """
        Create a union of the element and the list
        """
        polyhedron_list_union = AllplanGeo.Polyhedron3DList()
        for poly in polyhedron_list:
            polyhedron_list_union.append(poly)
        if len(polyhedron_list_union) > 1:
            success, union_final = AllplanGeo.MakeUnion(polyhedron_list_union)
            if success != True:
                print("Error in make union premarc")
                return None
            return union_final
        else:
            return None

    def create_tube_open_premarc(self) -> AllplanGeo.Polyhedron3D:
        """
        Create a tube for open premarc
        """
        top_tub = AllplanGeo.Polygon3D()
        top_tub += AllplanGeo.Point3D(0, 0, 0)
        top_tub += AllplanGeo.Point3D(TUB_DELTA_X_OPEN_PREMARC, 0, 0)
        top_tub += AllplanGeo.Point3D(
            TUB_DELTA_X_OPEN_PREMARC, -TUB_DELTA_Y_OPEN_PREMARC, 0
        )
        top_tub += AllplanGeo.Point3D(0, -TUB_DELTA_Y_OPEN_PREMARC, 0)
        top_tub += AllplanGeo.Point3D(0, 0, 0)
        translation_vector = AllplanGeo.Vector3D(170, -60, 200)  # Check values
        top_tub_moved = AllplanGeo.Move(top_tub, translation_vector)
        error_code, polyhedron_tub = self.extrude_frame(
            top_tub_moved, "tube_open_premarc"
        )
        return polyhedron_tub

    def get_active_u_accessory_segments(self) -> set[str]:
        """
        Only the **bottom edge** of the premarco: one U profile (no top or jambs).
        """
        return {"bottom"}

    def _append_frame_elements_to_model_list(
        self, model_ele_list, props_frame, frame
    ) -> None:
        """
        create_premarc_frame returns elems = [polyhedron_premarc_union, polyhedron_other_elements_list].
        ModelEleList.append_geometry_3d expects a polyhedron per call — flatten nested lists.
        """
        if not frame:
            return
        for item in frame:
            if item is None:
                continue
            if isinstance(item, (list, tuple)):
                for sub in item:
                    if sub is not None:
                        model_ele_list.append_geometry_3d(sub, props_frame)
            else:
                model_ele_list.append_geometry_3d(item, props_frame)

    def _u_channel_cuboid(self, p_min: AllplanGeo.Point3D, p_max: AllplanGeo.Point3D):
        return AllplanGeo.Polyhedron3D.CreateCuboid(p_min, p_max)

    def _hollow_u_channel(
        self,
        solid: AllplanGeo.Polyhedron3D,
        void_min: AllplanGeo.Point3D,
        void_max: AllplanGeo.Point3D,
    ) -> AllplanGeo.Polyhedron3D:
        """Vacía el interior del perfil U (grosor de pared ~U_WALL_THICKNESS_MM)."""
        void = self._u_channel_cuboid(void_min, void_max)
        err, out = AllplanGeo.MakeSubtraction(solid, void)
        if err != 0 or out is None:
            return solid
        try:
            if not out.IsValid():
                return solid
        except Exception:
            return solid
        return out

    def _frame_bottom_extrude_z_magnitude_mm(self) -> float:
        """Z extrusion thickness of the bottom sill; must match extrude_frame(..., 'frame_bottom')."""
        return float(THICKNESS_MM)

    def _poly_bbox_max_z(self, poly: AllplanGeo.Polyhedron3D) -> float | None:
        try:
            ret = AllplanGeo.CalcMinMax(poly)
            mm = self._extract_minmax(ret)
            if mm is None:
                return None
            return float(mm.Max.Z)
        except Exception:
            return None

    @staticmethod
    def _extract_minmax(ret):
        """Handle CalcMinMax returning MinMax3D directly or a tuple (err, MinMax3D)."""
        if ret is None:
            return None
        if hasattr(ret, "Max"):
            return ret
        if isinstance(ret, (tuple, list)):
            for item in ret:
                if hasattr(item, "Max"):
                    return item
        return None

    def _z_plausible_bottom_sill_bbox_top(self, zmx: float) -> bool:
        """Reject bbox tops from upper jambs (~z≈0); allow sill + small lifts (e.g. finish bottom +10.2 mm)."""
        sill_z = -float(self.heigh)
        h = float(self.heigh)
        upper_cut = sill_z + h * 0.55
        if zmx > upper_cut:
            return False
        if zmx < sill_z - h * 0.5:
            return False
        return True

    def _refresh_bottom_sill_top_z_cache(
        self, poly: AllplanGeo.Polyhedron3D, *, accept_any_z: bool = False
    ) -> None:
        """
        Cache Z of the top of the bottom sill solid (AllplanGeo.CalcMinMax(poly).Max.Z = highest vertex Z).
        That is the plane you see as the horizontal top of the pink color-48 base solid.

        accept_any_z=True: always use bbox Max.Z.
        accept_any_z=False: reject bbox tops clearly in the upper part of the opening (wrong poly in
        some OBERT modes).
        """
        try:
            ret = AllplanGeo.CalcMinMax(poly)
            mm = self._extract_minmax(ret)
            if mm is None:
                self._cached_bottom_sill_top_z = None
                return
            zmx = float(mm.Max.Z)
            if accept_any_z:
                self._cached_bottom_sill_top_z = zmx
                return
            if not self._z_plausible_bottom_sill_bbox_top(zmx):
                return
            self._cached_bottom_sill_top_z = zmx
        except Exception:
            self._cached_bottom_sill_top_z = None

    def _premarc_bottom_opening_plane_z(self) -> float:
        """Same Z as `frame_bottom` polygon in create_premarc_frame (top of bottom sill / opening datum)."""
        return -float(self.heigh)

    def _premarc_window_bottom_rail_top_z_mm(self) -> float:
        """Upper Z of the simplified window bottom cuboid (same model as create_premarc_window)."""
        return self._premarc_bottom_opening_plane_z() + float(
            WINDOW_BOTTOM_RAIL_Z_EXTENT_MM
        )

    def _u_sill_top_z_mm(self) -> float:
        """
        Z of the sill polygon plane (top of the bottom frame member).
        Uses the MAXIMUM of available Z sources.
        """
        z_open = self._premarc_bottom_opening_plane_z()
        off = U_PROFILE_SILL_TOP_OFFSET_FROM_OPENING_MM
        if off is not None:
            return z_open + float(off)
        candidates = [z_open]
        zt = getattr(self, "_cached_bottom_sill_top_z", None)
        if zt is not None:
            candidates.append(float(zt))
        pink = getattr(self, "_pink_sill_poly", None)
        if pink is not None:
            zp = self._poly_bbox_max_z(pink)
            if zp is not None:
                candidates.append(zp)
        return max(candidates)

    def _u_accessory_bottom_plane_z(self) -> float:
        """
        Z of the lowest face of the U-beam (z0).

        Per Arnau 2026-06-11: the U must sit ABOVE the imp + premarco lip.
        Previously the formula subtracted U_PROFILE_Z_INTO_AMPIT_DIP_MM (=3)
        which sank the U into the dip and let the imp rise leg poke through
        the top. Two corrections:

        1. Drop the `- dip` so the U sits flush with the sill top (+3mm lift
           relative to the previous formula — the "3mm más arriba" Arnau
           asked for, salva the premarco lip).
        2. Add `+ grosor_imp` when impermeabilizacio is active so the imp
           slab fits between the premarco and the U bottom face.
        """
        adj = float(U_PROFILE_BASE_Z_ADJUST_MM)
        z_top = self._u_sill_top_z_mm()
        eps = float(U_SILL_CONTACT_Z_EPSILON_MM)
        return z_top + eps + adj + self._grosor_imp_mm()

    def _u_channel_bottom(self) -> AllplanGeo.Polyhedron3D:
        """
        Sheet-metal U (115×30×3 catalog). Long axis = X. U opens toward +Z.
        One leg hangs U_OVERHANG_Y_MM (24 mm) past the sill outer face (Y direction).
        """
        t = U_WALL_THICKNESS_MM  # 3
        p = U_PROTRUSION_MM  # 115 (Y span)
        legz = float(U_LEG_HEIGHT_MM)  # 30 (Z height from catalog)
        z0 = self._u_accessory_bottom_plane_z()

        overhang = float(U_OVERHANG_Y_MM)
        x_min = float(-THICKNESS_MM)
        x_max = float(self.width) + float(THICKNESS_MM)

        y0 = -float(self.thickness) - overhang
        y0 += float(U_SILL_EDGE_HANG_SHIFT_Y_MM)
        y_in = y0 + t
        y_out = y0 + p - t
        if y_out <= y_in:
            y_out = min(y_in + 1e-3, y0 + p - 1e-3)

        leg_in = self._u_channel_cuboid(
            AllplanGeo.Point3D(x_min, y0, z0),
            AllplanGeo.Point3D(x_max, y_in, z0 + legz),
        )
        leg_out = self._u_channel_cuboid(
            AllplanGeo.Point3D(x_min, y_out, z0),
            AllplanGeo.Point3D(x_max, y0 + p, z0 + legz),
        )
        base = self._u_channel_cuboid(
            AllplanGeo.Point3D(x_min, y_in, z0),
            AllplanGeo.Point3D(x_max, y_out, z0 + t),
        )
        lst = AllplanGeo.Polyhedron3DList()
        lst.append(leg_in)
        lst.append(leg_out)
        lst.append(base)
        ok, uni = AllplanGeo.MakeUnion(lst)
        solid = uni if ok else base

        if legz > 2 * t and y_out > y_in + 0.01:
            solid = self._hollow_u_channel(
                solid,
                AllplanGeo.Point3D(x_min - 0.02, y_in, z0 + t),
                AllplanGeo.Point3D(x_max + 0.02, y_out, z0 + legz - t),
            )
        return solid

    def create_u_accessory_polyhedron(self):
        """
        Single U profile on the **bottom** edge of the premarco. Layer and attributes set in create_premarc.
        """
        show_u = getattr(self.build_ele, "ShowAccessorUPerimeter", None)
        if show_u is None or not show_u.value:
            return None
        if "bottom" not in self.get_active_u_accessory_segments():
            return None
        z0 = self._u_accessory_bottom_plane_z()
        cached = getattr(self, "_cached_bottom_sill_top_z", None)
        pink = getattr(self, "_pink_sill_poly", None)
        zp = self._poly_bbox_max_z(pink) if pink is not None else None
        z_top = self._u_sill_top_z_mm()
        manual_en = getattr(self.build_ele, "enable_manual_thickness", None)
        manual_en_v = manual_en.value if manual_en is not None else "N/A"
        manual_th = getattr(self.build_ele, "manual_thickness", None)
        manual_th_v = manual_th.value if manual_th is not None else "N/A"
        y0_dbg = (
            -float(self.thickness)
            - float(U_OVERHANG_Y_MM)
            + float(U_SILL_EDGE_HANG_SHIFT_Y_MM)
        )
        print(
            f"[Premarc] U z0={z0:.2f}, z_top_used={z_top:.2f}, "
            f"y0={y0_dbg:.1f}, overhang_Y={U_OVERHANG_Y_MM}, "
            f"pink_maxZ={zp}, cache={cached}, "
            f"heigh={float(self.heigh):.1f}, "
            f"thickness={float(self.thickness):.1f}, tp={float(self.thickness_premarc):.1f}, "
            f"pend={self.build_ele.ComboBoxPendiente.value}, "
            f"pink_poly={'YES' if pink is not None else 'NO'}, "
            f"offset={U_PROFILE_SILL_TOP_OFFSET_FROM_OPENING_MM}, "
            f"eps={U_SILL_CONTACT_Z_EPSILON_MM}, dip={U_PROFILE_Z_INTO_AMPIT_DIP_MM}"
        )
        solid = self._u_channel_bottom()
        sx = float(U_PROFILE_SHIFT_X_MM)
        sy = float(U_PROFILE_EXTRA_Y_SHIFT_MM)
        sz = float(U_PROFILE_SHIFT_Z_MM)
        if sx != 0.0 or sy != 0.0 or sz != 0.0:
            solid = AllplanGeo.Move(solid, AllplanGeo.Vector3D(sx, sy, sz))
        return solid

    def create_premarc_frame(self):

        self._cached_bottom_sill_top_z = None
        self._u_sill_finish_poly = None

        # polyhedron_premarc_list = AllplanGeo.Polyhedron3DList() # Premarc elements
        polyhedron_premarc_list = []
        polyhedron_other_elements_list = (
            []
        )  # List to store other elements like REA, falcas, etc.

        frame_x_min = -float(THICKNESS_MM)
        frame_x_max = float(self.width) + float(THICKNESS_MM)
        frame_z_top = float(THICKNESS_MM)
        frame_z_bottom = -float(self.heigh) - float(THICKNESS_MM)

        frame_bottom = AllplanGeo.Polygon3D()
        frame_bottom += AllplanGeo.Point3D(frame_x_min, -self.thickness, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(frame_x_max, -self.thickness, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(frame_x_max, 0, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(frame_x_min, 0, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(frame_x_min, -self.thickness, -self.heigh)

        error_code, polyhedron_bottom = self.extrude_frame(frame_bottom, "frame_bottom")

        # Fix dimensions frame bottom
        # transformation_matrix = AllplanGeo.Matrix3D()
        # scale_factor_x = (self.width + THICKNESS_MM * 2) / self.width
        # transformation_matrix.SetScaling(scale_factor_x,1,1)

        # polyhedron_bottom_translated = AllplanGeo.Transform(polyhedron_bottom, transformation_matrix)
        # translation_vector = AllplanGeo.Vector3D(-THICKNESS_MM,0,0)
        # polyhedron_bottom = AllplanGeo.Move(polyhedron_bottom_translated, translation_vector)
        polyhedron_premarc_list.append(polyhedron_bottom)
        self._refresh_bottom_sill_top_z_cache(polyhedron_bottom)

        frame_top = AllplanGeo.Polygon3D()
        frame_top += AllplanGeo.Point3D(frame_x_min, -self.thickness, 0)
        frame_top += AllplanGeo.Point3D(frame_x_max, -self.thickness, 0)
        frame_top += AllplanGeo.Point3D(frame_x_max, 0, 0)
        frame_top += AllplanGeo.Point3D(frame_x_min, 0, 0)
        frame_top += AllplanGeo.Point3D(frame_x_min, -self.thickness, 0)

        error_code, polyhedron_top = self.extrude_frame(frame_top, "frame_top")



        # Fix dimensions frame top
        # transformation_matrix = AllplanGeo.Matrix3D()
        # scale_factor_x = (self.width + THICKNESS_MM * 2) / self.width
        # transformation_matrix.SetScaling(scale_factor_x,1,1)

        # polyhedron_top_translated = AllplanGeo.Transform(polyhedron_top, transformation_matrix)
        # translation_vector = AllplanGeo.Vector3D(-THICKNESS_MM,0,0)
        # polyhedron_top = AllplanGeo.Move(polyhedron_top_translated, translation_vector)
        # transformation_matrix = AllplanGeo.Matrix3D()
        # scale_factor_x = (self.width + THICKNESS_MM * 2) / self.width
        # transformation_matrix.SetScaling(scale_factor_x,1,1)
        # polyhedron_top_translated = AllplanGeo.Transform(polyhedron_top, transformation_matrix)
        # translation_vector = AllplanGeo.Vector3D(-THICKNESS_MM,0,0)
        # polyhedron_top = AllplanGeo.Move(polyhedron_top_translated, translation_vector)
        polyhedron_premarc_list.append(polyhedron_top)

        frame_left = AllplanGeo.Polygon3D()
        frame_left += AllplanGeo.Point3D(0, -self.thickness, frame_z_bottom)
        frame_left += AllplanGeo.Point3D(0, 0, frame_z_bottom)
        frame_left += AllplanGeo.Point3D(0, 0, frame_z_top)
        frame_left += AllplanGeo.Point3D(0, -self.thickness, frame_z_top)
        frame_left += AllplanGeo.Point3D(0, -self.thickness, frame_z_bottom)

        error_code, polyhedron_left = self.extrude_frame(frame_left, "frame_left")
        polyhedron_premarc_list.append(polyhedron_left)

        frame_right = AllplanGeo.Polygon3D()
        frame_right += AllplanGeo.Point3D(self.width, -self.thickness, frame_z_bottom)
        frame_right += AllplanGeo.Point3D(self.width, 0, frame_z_bottom)
        frame_right += AllplanGeo.Point3D(self.width, 0, frame_z_top)
        frame_right += AllplanGeo.Point3D(self.width, -self.thickness, frame_z_top)
        frame_right += AllplanGeo.Point3D(self.width, -self.thickness, frame_z_bottom)

        error_code, polyhedron_right = self.extrude_frame(frame_right, "frame_right")
        polyhedron_premarc_list.append(polyhedron_right)

        frame_finish_bottom = AllplanGeo.Polygon3D()
        frame_finish_bottom += AllplanGeo.Point3D(-23, -self.thickness, -self.heigh)
        frame_finish_bottom += AllplanGeo.Point3D(
            self.width + 23, -self.thickness, -self.heigh
        )
        frame_finish_bottom += AllplanGeo.Point3D(
            self.width + 23, -self.thickness, -self.heigh - 23
        )
        frame_finish_bottom += AllplanGeo.Point3D(
            -23, -self.thickness, -self.heigh - 23
        )
        frame_finish_bottom += AllplanGeo.Point3D(-23, -self.thickness, -self.heigh)
        error_code, polyhedron_finish_bottom = self.extrude_frame(
            frame_finish_bottom, "frame_finish_bottom"
        )
        polyhedron_premarc_list.append(polyhedron_finish_bottom)

        frame_finish_top = AllplanGeo.Polygon3D()
        frame_finish_top += AllplanGeo.Point3D(-23, -self.thickness, 0)
        frame_finish_top += AllplanGeo.Point3D(self.width + 23, -self.thickness, 0)
        frame_finish_top += AllplanGeo.Point3D(self.width + 23, -self.thickness, 23)
        frame_finish_top += AllplanGeo.Point3D(-23, -self.thickness, 23)
        frame_finish_top += AllplanGeo.Point3D(-23, -self.thickness, 0)
        error_code, polyhedron_finish_top = self.extrude_frame(frame_finish_top, "frame_finish_top")

        # Fix frame finish top for Monoblock persiana selected
        if self.build_ele.ComboBoxPersianas.value == "MONOBLOCK OCULT":
            translation_vector = AllplanGeo.Vector3D(0, 0, self.build_ele.PersianaHeight.value)
            polyhedron_finish_top = AllplanGeo.Move(polyhedron_finish_top, translation_vector)

        polyhedron_premarc_list.append(polyhedron_finish_top)

        #### frame_finish_left
        offset_left_z = self.build_ele.PersianaHeight.value if self.build_ele.ComboBoxPersianas.value == "MONOBLOCK OCULT" else 0

        frame_finish_left = AllplanGeo.Polygon3D()
        frame_finish_left += AllplanGeo.Point3D(0, -self.thickness, -self.heigh) #1
        frame_finish_left += AllplanGeo.Point3D(0, -self.thickness, offset_left_z) #2
        frame_finish_left += AllplanGeo.Point3D(-23, -self.thickness, offset_left_z) #3
        frame_finish_left += AllplanGeo.Point3D(-23, -self.thickness, -self.heigh) #4
        frame_finish_left += AllplanGeo.Point3D(0, -self.thickness, -self.heigh) #5-1
        error_code, polyhedron_finish_left = self.extrude_frame(frame_finish_left, "frame_finish_left")
        polyhedron_premarc_list.append(polyhedron_finish_left)

        #### frame_finish_right
        offset_right_z = self.build_ele.PersianaHeight.value if self.build_ele.ComboBoxPersianas.value == "MONOBLOCK OCULT" else 0

        frame_finish_right = AllplanGeo.Polygon3D()
        frame_finish_right += AllplanGeo.Point3D(self.width, -self.thickness, -self.heigh) #1
        frame_finish_right += AllplanGeo.Point3D(self.width + 23, -self.thickness, -self.heigh) #2
        frame_finish_right += AllplanGeo.Point3D(self.width + 23, -self.thickness, offset_right_z) #3
        frame_finish_right += AllplanGeo.Point3D(self.width, -self.thickness, offset_right_z) #4
        frame_finish_right += AllplanGeo.Point3D(self.width, -self.thickness, -self.heigh) #5-1
        error_code, polyhedron_finish_right = self.extrude_frame(frame_finish_right, "frame_finish_right")
        polyhedron_premarc_list.append(polyhedron_finish_right)

        #### Tubs
        frame_tub_bottom = AllplanGeo.Polygon3D()
        frame_tub_bottom += AllplanGeo.Point3D(
            0, -(self.thickness / 2 - TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            0, -(self.thickness / 2 + TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            TUB_WIDTH_LENGTH, -(self.thickness / 2 + TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            TUB_WIDTH_LENGTH, -(self.thickness / 2 - TUB_WIDTH_LENGTH / 2), 0
        )
        frame_tub_bottom += AllplanGeo.Point3D(
            0, -(self.thickness / 2 - TUB_WIDTH_LENGTH / 2), 0
        )
        error_code, polyhedron_tub_left_top = self.extrude_frame(
            frame_tub_bottom, "frame_tub"
        )

        # logic Tubs
        # Mover el tubo al centro del ancho
        # Mover el tubo al centro del ancho
        tub_x_offset = self.width / 2 - TUB_WIDTH_LENGTH / 2
        # transform_matrix = AllplanGeo.Matrix3D()
        # transform_matrix.SetTranslation(AllplanGeo.Vector3D(tub_x_offset, 0, 0))

        # Transformar el poliedro usando la función de geometría

        # Mover el tubo al centro del ancho
        # tub_x_offset = self.width/2 - TUB_WIDTH_LENGTH/2
        # move_vector = AllplanGeo.Vector3D(tub_x_offset, 0, 0)
        # error_code, polyhedron_tub_moved = AllplanGeo.MovePolyhedron3D(polyhedron_tub_left_top, move_vector)

        # error_code, polyhedron_tub_moved = AllplanGeo.TransformPolyhedron3D(polyhedron_tub_left_top, transform_matrix)

        # polyhedron_tub_left_top_copy = AllplanGeo.Polyhedron3D(polyhedron_tub_left_top)
        # polyhedron_tub_left_top_copy = self.create_tub()

        translation_vector = AllplanGeo.Vector3D(tub_x_offset, 0, 0)

        # polyhedron_tub_moved = AllplanGeo.Move(polyhedron_tub_left_top_copy, translation_vector)

        # Create Tubs
        # tub_x_offset = self.width/(TUBS_NUMBER+1) - TUB_WIDTH_LENGTH/2
        # polyhedron_tubs = []
        # for i in range(1, TUBS_NUMBER+1):
        #     translation_vector = AllplanGeo.Vector3D(tub_x_offset*i, 0, 0)
        #     polyhedron_tub = self.create_tub()
        #     polyhedron_tub_moved = AllplanGeo.Move(polyhedron_tub, translation_vector)
        #     polyhedron_tubs.append(polyhedron_tub_moved)

        # Create Tubs
        # Para distribuir 4 tubos uniformemente, dividimos el ancho en 5 secciones
        # y colocamos cada tubo en el centro de su sección
        tub_spacing = self.width / (TUBS_NUMBER + 1)  # Espacio entre centros de tubos
        tub_x_offset = (
            tub_spacing - TUB_WIDTH_LENGTH / 2
        )  # Offset desde el borde izquierdo

        # polyhedron_tubs = []
        # for i in range(1, TUBS_NUMBER+1):
        #     # Posición X del centro del tubo
        #     tub_center_x = tub_spacing * i
        #     # Vector de traslación (centro del tubo menos la mitad del ancho del tubo)
        #     translation_vector = AllplanGeo.Vector3D(tub_center_x - TUB_WIDTH_LENGTH/2, 0, 0)
        #     polyhedron_tub = self.create_tub()
        #     polyhedron_tub_moved = AllplanGeo.Move(polyhedron_tub, translation_vector)
        #     polyhedron_tubs.append(polyhedron_tub_moved)

        ### Encajes
        self.socket_width = 32  # compensa extrude, la medida es 35 medido de afuera.
        self.socket_height = 27  # compensa extrude, la medida es 30 medido de afuera.

        polyedron_sockets = self.create_socket(self.socket_width, self.socket_height)
        error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(polyedron_sockets)
        error_code_socket = False

        # Pliegue inferior/ Fold bottom

        # Fix initial position of fold bottom and top
        fold_top_fix = AllplanGeo.Polygon3D()
        fold_top_fix += AllplanGeo.Point3D(0, 0, 0)  # P1
        fold_top_fix += AllplanGeo.Point3D(self.width, 0, 0)  # P2
        fold_top_fix += AllplanGeo.Point3D(self.width, -FOLD_WIDTH_MM, 0)  # P3
        fold_top_fix += AllplanGeo.Point3D(0, -FOLD_WIDTH_MM, 0)  # P4
        fold_top_fix += AllplanGeo.Point3D(0, 0, 0)
        error_code, polyhedron_fold_top_fix = self.extrude_frame(
            fold_top_fix, "fold_top"
        )

        fold_bottom_fix = AllplanGeo.Polygon3D()
        fold_bottom_fix += AllplanGeo.Point3D(
            0, 0, -FOLD_SPACING_MM
        )  # P1 bottom left front point
        fold_bottom_fix += AllplanGeo.Point3D(self.width, 0, -FOLD_SPACING_MM)  # P2
        fold_bottom_fix += AllplanGeo.Point3D(
            self.width, -FOLD_WIDTH_MM, -FOLD_SPACING_MM
        )  # P3
        fold_bottom_fix += AllplanGeo.Point3D(0, -FOLD_WIDTH_MM, -FOLD_SPACING_MM)  # P4
        fold_bottom_fix += AllplanGeo.Point3D(0, 0, -FOLD_SPACING_MM)
        error_code, polyhedron_fold_bottom_fix = self.extrude_frame(
            fold_bottom_fix, "fold_bottom"
        )

        # Cylinder for external vertex top

        # Crear cilindro vertical primero (esto funciona)
        cylinder = AllplanGeo.Cylinder3D(4.5, 4.5, AllplanGeo.Point3D(0, 0, self.width))
        error_code, polyhedron_cylinder = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )  # deprecated

        rotation_axis = AllplanGeo.Axis3D(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Vector3D(0, 1, 0),  # Eje Z como eje de rotación
        )

        # Ángulo de 90 grados
        rotation_angle = AllplanGeo.Angle.FromDeg(90)

        # Rotar el cilindro
        cylinder_mayor = AllplanGeo.Rotate(
            polyhedron_cylinder, rotation_axis, rotation_angle
        )

        cylinder = AllplanGeo.Cylinder3D(1.5, 1.5, AllplanGeo.Point3D(0, 0, self.width))
        error_code, polyhedron_cylinder = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )  # deprecated

        rotation_axis = AllplanGeo.Axis3D(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Vector3D(0, 1, 0),  # Eje Z como eje de rotación
        )

        # Ángulo de 90 grados
        rotation_angle = AllplanGeo.Angle.FromDeg(90)

        # Rotar el cilindro
        cylinder_minor = AllplanGeo.Rotate(
            polyhedron_cylinder, rotation_axis, rotation_angle
        )

        # Move cylinders
        translation_vector = AllplanGeo.Vector3D(
            0, -FOLD_WIDTH_MM, -FOLD_SPACING_MM / 2
        )
        cylinder_mayor_moved = AllplanGeo.Move(cylinder_mayor, translation_vector)
        cylinder_minor_moved = AllplanGeo.Move(cylinder_minor, translation_vector)

        fold_cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(self.width, -7, -7)
        )

        # move fold_uboid
        translation_vector = AllplanGeo.Vector3D(
            0, -(FOLD_WIDTH_MM - 7), FOLD_SPACING_MM / 2
        )
        fold_cuboid_moved = AllplanGeo.Move(fold_cuboid, translation_vector)

        # operation betweem solids

        error_code, substracted_cylinder = AllplanGeo.MakeSubtraction(
            cylinder_mayor_moved, cylinder_minor_moved
        )
        error_code, substracted_cuboid_cylinder = AllplanGeo.MakeSubtraction(
            substracted_cylinder, fold_cuboid_moved
        )

        # union each part of fold
        error_code, polyhedron_fold_with_fillet = AllplanGeo.MakeUnion(
            polyhedron_fold_bottom_fix, substracted_cuboid_cylinder
        )
        error_code, polyhedron_fold_with_fillet = AllplanGeo.MakeUnion(
            polyhedron_fold_with_fillet, polyhedron_fold_top_fix
        )

        # move finish fold to bottom
        translation_vector = AllplanGeo.Vector3D(
            0, -(self.thickness - FOLD_WIDTH_MM - 4.5), -(self.heigh + THICKNESS_MM)
        )
        polyhedron_fold_with_fillet_moved = AllplanGeo.Move(
            polyhedron_fold_with_fillet, translation_vector
        )

        ### Falcas -----------------

        TOP_FALCAS = False
        BOTTOM_FALCAS = False

        available_width = self.width - (OFFSET_FALCA * 2)
        max_falcas = int(available_width / DISTANCE_BETWEEN_FALCAS)
        polyhedron_top_falcas = []
        polyhedron_bottom_falcas = []
        if max_falcas > 0:
            total_falcas_width = max_falcas * DISTANCE_BETWEEN_FALCAS
            adjusted_offset = (self.width - total_falcas_width) / 2
            # adjusted_offset = OFFSET_FALCA + remaining_space / 2
        else:
            adjusted_offset = OFFSET_FALCA
            max_falcas = 0

        # Top Falcas
        for i in range(max_falcas + 1):
            falca = self.create_origin_falca_top()
            translation_vector = AllplanGeo.Vector3D(
                adjusted_offset + DISTANCE_BETWEEN_FALCAS * i - THICKNESS_MM / 2,
                -(self.thickness - THICKNESS_MM - THICKNESS_FALCA),
                0,
            )
            falca_moved = AllplanGeo.Move(falca, translation_vector)
            error_code, polyhedron_falca = self.extrude_frame(
                falca_moved, "frame_falca"
            )
            polyhedron_top_falcas.append(polyhedron_falca)

        # TOP_FALCAS = True

        # Bottom Falcas
        for i in range(max_falcas + 1):
            falca = self.create_origin_falca_bottom()
            translation_vector = AllplanGeo.Vector3D(
                adjusted_offset + DISTANCE_BETWEEN_FALCAS * i - THICKNESS_MM / 2,
                -(self.thickness - THICKNESS_MM - THICKNESS_FALCA),
                -(self.heigh + THICKNESS_MM),
            )
            falca_moved = AllplanGeo.Move(falca, translation_vector)
            error_code, polyhedron_falca = self.extrude_frame(
                falca_moved, "frame_falca"
            )
            polyhedron_bottom_falcas.append(polyhedron_falca)

        # BOTTOM_FALCAS = True

        ### Create open premarc

        # polyhedron_top_left_open = self.create_polygon_open("top left", polyhedron_top)
        polyhedron_top_right_open = self.create_polygon_open(
            "top right", polyhedron_top
        )
        polyhedron_bottom_right_open = self.create_polygon_open(
            "bottom right", polyhedron_bottom
        )
        # polyhedron_bottom_left_open = self.create_polygon_open("bottom left", polyhedron_bottom)

        # Define None to deactivate open premarc
        polyhedron_top_right_open = None
        polyhedron_bottom_right_open = None

        # Create REA (tube) for open premarc
        top_tub = AllplanGeo.Polygon3D()
        top_tub += AllplanGeo.Point3D(0, 0, 0)
        top_tub += AllplanGeo.Point3D(TUB_DELTA_X_OPEN_PREMARC, 0, 0)
        top_tub += AllplanGeo.Point3D(
            TUB_DELTA_X_OPEN_PREMARC, -TUB_DELTA_Y_OPEN_PREMARC, 0
        )
        top_tub += AllplanGeo.Point3D(0, -TUB_DELTA_Y_OPEN_PREMARC, 0)
        top_tub += AllplanGeo.Point3D(0, 0, 0)
        translation_vector = AllplanGeo.Vector3D(170, -60, 200)  # Check values
        top_tub_moved = AllplanGeo.Move(top_tub, translation_vector)
        error_code, polyhedron_tub = self.extrude_frame(
            top_tub_moved, "tube_open_premarc"
        )

        # Premarc with pendents in bottom

        # Copy and extrude top frame
        # Need expand because after rotate and move, the frame don't close premarc
        transformation_matrix = AllplanGeo.Matrix3D()
        transformation_matrix.SetScaling(1, 1.001, 1)

        polyhedron_top_expanded = AllplanGeo.Transform(
            polyhedron_top, transformation_matrix
        )

        rotation_axis = AllplanGeo.Axis3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0)
        )
        # Calculate rotation angle based on thickness
        CO = 10
        CA = self.thickness_premarc

        angulo_radianes = math.atan2(CO, CA)
        angulo_grados = math.degrees(angulo_radianes)

        rotation_angle = AllplanGeo.Angle.FromDeg(-angulo_grados)

        rotated_frame_premarc = AllplanGeo.Rotate(
            polyhedron_top_expanded, rotation_axis, rotation_angle
        )
        translation_vector = AllplanGeo.Vector3D(0, -0.1, -(self.heigh + THICKNESS_MM))
        polyhedron_bottom_grade = AllplanGeo.Move(
            rotated_frame_premarc, translation_vector
        )
        # polyhedron_bottom_grade = None

        FIX_BOTTOM_FINISH = 10.2
        translation_vector = AllplanGeo.Vector3D(0, 0, FIX_BOTTOM_FINISH)
        polyhedron_finish_bottom_fix = AllplanGeo.Move(
            polyhedron_finish_bottom, translation_vector
        )

        # fix position socket
        FIX_HEIGHT_SOCKET = 9  # 9 mm
        translation_vector = AllplanGeo.Vector3D(0, 0, FIX_HEIGHT_SOCKET)
        polyhedron_socket_fix = AllplanGeo.Move(polyhedron_socket, translation_vector)

        # Fix angle pliegue inferior
        # polyhedron_fold_with_fillet --> pliegue inferior en coordenadas de origen

        rotation_axis = AllplanGeo.Axis3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0)
        )
        rotation_angle = AllplanGeo.Angle.FromDeg(-2)
        rotated_polyhedron_fold_with_fillet = AllplanGeo.Rotate(
            polyhedron_fold_with_fillet, rotation_axis, rotation_angle
        )

        translation_vector = AllplanGeo.Vector3D(
            0, -(self.thickness - FOLD_WIDTH_MM - 4.5), -(self.heigh - 5.69)
        )
        rotated_polyhedron_fold_with_fillet_moved = AllplanGeo.Move(
            rotated_polyhedron_fold_with_fillet, translation_vector
        )

        # TODO rotate elements related:
        # Frame_finish_bottom/ Encaje

        # Box shutters
        box_shutter = AllplanGeo.Polygon3D()
        box_shutter += AllplanGeo.Point3D(0, 0, 0)
        box_shutter += AllplanGeo.Point3D(0, 0, BOX_SHUTTER_HEIGHT)
        box_shutter += AllplanGeo.Point3D(0, -BOX_SHUTTER_WIDTH, BOX_SHUTTER_HEIGHT)
        box_shutter += AllplanGeo.Point3D(0, -BOX_SHUTTER_WIDTH, 0)
        box_shutter += AllplanGeo.Point3D(0, 0, 0)

        # Move box shutters to offset from front
        translation_vector = AllplanGeo.Vector3D(
            -THICKNESS_MM, -(OFFSET_FRONT_BOX_SHUTTER), 0
        )
        box_shutter_moved = AllplanGeo.Move(box_shutter, translation_vector)
        error_code, polyhedron_box_shutter = self.extrude_frame(
            box_shutter_moved, "box_shutter"
        )
        polyhedron_box_shutter = None

        ### Handle options entered in palette

        # Open/ Closed premarc
        # TODO delete code deprecated
        # TODO redimensionar elementos del premarco.
        # pasarlos como parametros a create_polygon_open
        # refactor create_polygon_open para para actualizar la posicion del poligono

        # shorten top and bottom elements to position them in the correct position

        # polyhedron_top_left_open = self.create_polygon_open("top left", polyhedron_top)
        # polyhedron_top_right_open = self.create_polygon_open("top right", polyhedron_top)
        # polyhedron_bottom_right_open = self.create_polygon_open("bottom right", polyhedron_bottom)
        # polyhedron_bottom_left_open = self.create_polygon_open("bottom left", polyhedron_bottom)
        polyedron_REA = self.create_tube_open_premarc()

        pos_left = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(-10, -self.thickness, -(self.heigh + 20))
        )
        pos_right = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(self.width, -self.thickness, -(self.heigh + 20))
        )
        cuboid_to_substract_left_open = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_left, 10, self.thickness, (self.heigh + 40)
        )
        cuboid_to_substract_right_open = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_right, 10, self.thickness, (self.heigh + 40)
        )

        error_code, poly_top_left_without_open = AllplanGeo.MakeSubtraction(
            polyhedron_top, cuboid_to_substract_left_open
        )
        error_code, poly_top_right_whithout_open = AllplanGeo.MakeSubtraction(
            polyhedron_top, cuboid_to_substract_right_open
        )
        error_code, poly_bottom_left_whithout_open = AllplanGeo.MakeSubtraction(
            polyhedron_bottom, cuboid_to_substract_left_open
        )
        error_code, poly_bottom_right_whithout_open = AllplanGeo.MakeSubtraction(
            polyhedron_bottom, cuboid_to_substract_right_open
        )

        polyhedron_top_right_open = self.create_polygon_open(
            "top right", poly_top_right_whithout_open
        )
        polyhedron_bottom_right_open = self.create_polygon_open(
            "bottom right", poly_bottom_right_whithout_open
        )
        polyhedron_top_left_open = self.create_polygon_open(
            "top left", poly_top_left_without_open
        )
        polyhedron_bottom_left_open = self.create_polygon_open(
            "bottom left", poly_bottom_left_whithout_open
        )

        debug_rebaje_solids = []
        show_rebajes_debug = bool(
            getattr(getattr(self.build_ele, "ShowRebajesDebug", None), "value", False)
        )

        ### Build substract rebajes ###
        # Top rebaje
        position = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, -LENGTH_REBAJES_MM, 0)
        )
        substract_rebajes_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            position,
            self.width,
            LENGTH_REBAJES_MM + 20,
            THICKNESS_MM + 3,  # 3 mm to ensure cuboid is not too small
        )

        # Bottom rebaje
        substract_rebajes_bottom = AllplanGeo.Polyhedron3D(substract_rebajes_top)
        substract_rebajes_bottom = AllplanGeo.Move(
            substract_rebajes_bottom,
            AllplanGeo.Vector3D(0, 0, -(self.heigh + THICKNESS_MM * 2)),
        )

        # left rebaje
        position = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(-THICKNESS_MM, -LENGTH_REBAJES_MM, -self.heigh)
        )
        substract_rebajes_left = AllplanGeo.Polyhedron3D.CreateCuboid(
            position, THICKNESS_MM, LENGTH_REBAJES_MM + 20, self.heigh
        )

        # right rebaje
        substract_rebajes_right = AllplanGeo.Polyhedron3D(substract_rebajes_left)
        substract_rebajes_right = AllplanGeo.Move(
            substract_rebajes_right,
            AllplanGeo.Vector3D(self.width + THICKNESS_MM, 0, 0),
        )


        # bottom grade with rebaje
        transformation_matrix = AllplanGeo.Matrix3D()
        transformation_matrix.SetScaling(1, 1, 1)

        error_code, bottom_rebaje = AllplanGeo.MakeSubtraction(
            polyhedron_bottom, substract_rebajes_bottom
        )

        scale_factor_x = (self.width + THICKNESS_MM * 2) / self.width
        center_x = (self.width * scale_factor_x) / 2 - THICKNESS_MM
        axis_point = AllplanGeo.Point3D(
            center_x, -float(LENGTH_REBAJES_MM), -self.heigh
        )
        rotation_axis = AllplanGeo.Axis3D(axis_point, AllplanGeo.Vector3D(1, 0, 0))
        # With REB. BAIX the effective sloped length is the hypotenuse after
        # removing the rebaje depth, so use asin(opposite / hypotenuse).
        CO = 10.0
        hipotenusa = max(float(self.thickness_premarc) - float(LENGTH_REBAJES_MM), abs(CO))
        angulo_radianes = math.asin(CO / hipotenusa)
        angulo_grados = math.degrees(angulo_radianes)
        if show_rebajes_debug:
            print(
                "[Premarc][REB. BAIX][PENDIENTE] "
                f"CO={CO:.3f}, hipotenusa={hipotenusa:.3f}, "
                f"axis_y={-float(LENGTH_REBAJES_MM):.3f}, "
                f"angulo_grados={angulo_grados:.6f}"
            )
        rotation_angle = AllplanGeo.Angle.FromDeg(-angulo_grados)

        polyhedron_bottom_grade = AllplanGeo.Rotate(
            polyhedron_bottom, rotation_axis, rotation_angle
        )
        error_code, polyhedron_bottom_grade_with_rebaje = AllplanGeo.MakeSubtraction(
            polyhedron_bottom_grade, substract_rebajes_bottom
        )
        if error_code != AllplanGeo.eGeometryErrorCode.eOK:
            print(
                "[Premarc][REB. BAIX][PENDIENTE] "
                f"MakeSubtraction tras rotacion fallo: {error_code}; "
                "se usa fondo rotado sin rebaje"
            )
            polyhedron_bottom_grade_with_rebaje = polyhedron_bottom_grade

        # Solids fix corners

        # Top left corner
        list_solid_fix_corners = []
        position = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(-THICKNESS_MM, -LENGTH_REBAJES_MM, -THICKNESS_MM)
        )
        substract_top_left_corner = AllplanGeo.Polyhedron3D.CreateCuboid(
            position, THICKNESS_MM * 2, LENGTH_REBAJES_MM * 2, THICKNESS_MM * 2
        )
        list_solid_fix_corners.append(substract_top_left_corner)

        # Top right corner
        vector_move = AllplanGeo.Vector3D(self.width + THICKNESS_MM, 0, 0)
        substract_top_right_corner = AllplanGeo.Move(
            substract_top_left_corner, vector_move
        )
        list_solid_fix_corners.append(substract_top_right_corner)

        # Bottom left corner
        vector_move = AllplanGeo.Vector3D(0, 0, -(self.heigh + THICKNESS_MM))
        substract_bottom_left_corner = AllplanGeo.Move(
            substract_top_left_corner, vector_move
        )
        list_solid_fix_corners.append(substract_bottom_left_corner)

        # Bottom right corner
        vector_move = AllplanGeo.Vector3D(0, 0, -(self.heigh + THICKNESS_MM))
        substract_bottom_right_corner = AllplanGeo.Move(
            substract_top_right_corner, vector_move
        )
        list_solid_fix_corners.append(substract_bottom_right_corner)


        ## End rebajes ##

        poly_base_no_slope = None
        # open_closed_premarc = self.build_ele.ComboBoxAbiertoCerrado.value
        match self.build_ele.ComboBoxAbiertoCerrado.value:
            case "TANCAT":
                print("Selected TANCAT")  # Close premarc
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [
                        polyhedron_top,
                        polyhedron_right,
                        polyhedron_bottom,
                        polyhedron_left,
                    ]
                ):
                    print("All elements in polyhedron premarc list")
                else:
                    print("Not all elements in polyhedron premarc list")

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(polyhedron_bottom)
                    if self.bottom_rebaje_enabled():
                        # poly_base_no_slope = AllplanGeo.MakeSubtraction(polyhedron_bottom, substract_rebajes_bottom)
                        poly_base_no_slope = AllplanGeo.Polyhedron3D(bottom_rebaje)
                        # Fix corners bottom rebaje
                        if self.get_enabled_rebajes_options(
                            "REB. BAIX"
                        ) and self.get_enabled_rebajes_options("REB. ESQUERRA"):
                            error_code, poly_base_no_slope = AllplanGeo.MakeSubtraction(
                                poly_base_no_slope, substract_bottom_left_corner
                            )
                        if self.get_enabled_rebajes_options(
                            "REB. BAIX"
                        ) and self.get_enabled_rebajes_options("REB. DRETA"):
                            print("REB. BAIX and REB. DRETA")
                            intersecting, result = AllplanGeo.Intersect(
                                poly_base_no_slope, substract_bottom_right_corner
                            )
                            if intersecting:
                                error_code, poly_base_no_slope = (
                                    AllplanGeo.MakeSubtraction(
                                        poly_base_no_slope, result
                                    )
                                )
                            else:
                                print("Error in intersection")
                                pass

            case (
                "OBERT PER DALT"
                | "OBERT PER DALT + REA"
                | "OBERT PER DALT + REA VARIANT"
            ):
                print(f"Selected {self.build_ele.ComboBoxAbiertoCerrado.value}")
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                if polyhedron_finish_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_finish_top)
                    except ValueError:
                        print("Error in remove polyhedron finish top")

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(polyhedron_bottom)

            case (
                "OBERT PER BAIX"
                | "OBERT PER BAIX + REA"
                | "OBERT PER BAIX + REA VARIANT"
            ):
                print(f"Selected {self.build_ele.ComboBoxAbiertoCerrado.value}")
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                if polyhedron_finish_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_finish_bottom)
                    except ValueError:
                        print("Error in remove polyhedron finish bottom")

            case "OBERT FEMELLA DRETA":
                print("Selected OBERT FEMELLA DRETA")  # Open premarc with right femella
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_right_open)
                polyhedron_premarc_list.append(polyhedron_bottom_right_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [
                        polyhedron_top_right_open,
                        polyhedron_bottom_right_open,
                    ]
                ):
                    print("All elements in polyhedron premarc list open premarc right")
                else:
                    print("Not all elements in polyhedron premarc list")

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        polyhedron_bottom_right_open
                    )
            case "OBERT FEMELLA ESQUERRA":
                print(
                    "Selected OBERT FEMELLA ESQUERRA "
                )  # Abierto a la izquierda con femella a la derecha arriba y abajo.
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_left_open)
                polyhedron_premarc_list.append(polyhedron_bottom_left_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [polyhedron_top_left_open, polyhedron_bottom_left_open]
                ):
                    print("All elements in polyhedron premarc list open premarc right")
                else:
                    print("Not all elements in polyhedron premarc list")

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        polyhedron_bottom_left_open
                    )
            case "OBERT FEMELLA DRETA + REA":
                print(
                    "Selected OBERT FEMELLA DRETA + REA"
                )  # Abierto a la derecha, con femella a la derecha arriba y abajo + REA
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_right_open)
                polyhedron_premarc_list.append(polyhedron_bottom_right_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [
                        polyhedron_top_right_open,
                        polyhedron_bottom_right_open,
                    ]
                ):
                    print(
                        "All elements in polyhedron premarc list open premarc right + REA"
                    )
                else:
                    print("Not all elements in polyhedron premarc list")

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        polyhedron_bottom_right_open
                    )
            case "OBERT FEMELLA ESQUERRA + REA":
                print(
                    "Selected OBERT FEMELLA ESQUERRA + REA"
                )  #  Abierto a la izquierda con femella a la derecha arriba y abajo + REA
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_left_open)
                polyhedron_premarc_list.append(polyhedron_bottom_left_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [polyhedron_top_left_open, polyhedron_bottom_left_open]
                ):
                    print(
                        "All elements in polyhedron premarc list open premarc left + REA"
                    )
                else:
                    print("Not all elements in polyhedron premarc list")

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        polyhedron_bottom_left_open
                    )
            case "OBERT NO FEMELLA DRETA":
                print(
                    "Selected OBERT NO FEMELLA DRETA"
                )  # Abierto a la derecha, sin femella
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_right not in polyhedron_premarc_list:
                    print("Success in remove polyhedron right")
                else:
                    print("Error in remove polyhedron right")
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_top_right_whithout_open)
                polyhedron_premarc_list.append(poly_bottom_right_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_right_whithout_open
                    )
            case "OBERT NO FEMELLA ESQUERRA":
                print(
                    "Selected OBERT NO FEMELLA ESQUERRA"
                )  # Abierto a la izquierda, sin femella
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_left not in polyhedron_premarc_list:
                    print("Success in remove polyhedron left")
                else:
                    print("Error in remove polyhedron left")
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_top_left_without_open)
                polyhedron_premarc_list.append(poly_bottom_left_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_left_whithout_open
                    )
            case "OBERT NO FEMELLA DRETA + REA":
                print(
                    "Selected OBERT NO FEMELLA DRETA + REA"
                )  # Abierto a la derecha, sin femella + REA
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_right not in polyhedron_premarc_list:
                    print("Success in remove polyhedron right")
                else:
                    print("Error in remove polyhedron right")

                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_top_right_whithout_open)
                polyhedron_premarc_list.append(poly_bottom_right_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_right_whithout_open
                    )

            case "OBERT NO FEMELLA ESQUERRA + REA":
                print(
                    "Selected OBERT NO FEMELLA ESQUERRA + REA"
                )  # Abierto a la izquierda, sin femella + REA
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_left not in polyhedron_premarc_list:
                    print("Success in remove polyhedron left")
                else:
                    print("Error in remove polyhedron left")

                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_top_left_without_open)
                polyhedron_premarc_list.append(poly_bottom_left_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_left_whithout_open
                    )

            case "SUP. FEMELLA / INF NO FEMELLA DRET.":
                print(
                    "Selected SUP. FEMELLA / INF NO FEMELLA DRET."
                )  # Abierto a la derecha. Superior con femella, inferior sin femella
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_right_open)
                if polyhedron_top_right_open in polyhedron_premarc_list:
                    print("All elements in polyhedron premarc list open premarc right")
                else:
                    print("Not all elements in polyhedron premarc list")

                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_bottom_right_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_right_whithout_open
                    )

            case "SUP. FEMELLA / INF NO FEMELLA ESQ.":
                print(
                    "Selected SUP. FEMELLA / INF NO FEMELLA ESQ."
                )  # Abierto a la izquierda. Superior con femella, inferior sin femella
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_left_open)
                if polyhedron_top_left_open in polyhedron_premarc_list:
                    print("Success in add polyhedron top left open")
                else:
                    print("Error in add polyhedron top left open")

                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_bottom_left_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_left_whithout_open
                    )

            case "SUP. FEMELLA / INF NO FEMELLA DRET. + REA":
                print(
                    "Selected SUP. FEMELLA / INF NO FEMELLA DRET. + REA"
                )  # Abierto a la derecha. Superior con femella, inferior sin femella + REA
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_right_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [polyhedron_top_right_open]
                ):
                    print("All elements in polyhedron premarc list open premarc right")
                else:
                    print("Not all elements in polyhedron premarc list")

                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_bottom_right_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_right_whithout_open
                    )
            case "SUP. FEMELLA / INF NO FEMELLA ESQ. + REA":
                print(
                    "Selected SUP. FEMELLA / INF NO FEMELLA ESQ. + REA"
                )  # Abierto a la izquierda. Superior con femella, inferior sin femella + REA
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(polyhedron_top_left_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [polyhedron_top_left_open]
                ):
                    print("Success in add polyhedron top left open + REA")
                else:
                    print("Error in add polyhedron top left open + REA")

                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        pass
                polyhedron_premarc_list.append(poly_bottom_left_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_bottom_left_whithout_open
                    )

            case "SUP. NO FEMELLA / INF. FEMELLA DRET.":
                print(
                    "Selected SUP. NO FEMELLA / INF. FEMELLA DRET."
                )  # Abierto a la derecha. Superior sin femella, inferior con femella
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_bottom_right_open)
                if polyhedron_bottom_right_open in polyhedron_premarc_list:
                    print("Success in add polyhedron bottom right open")
                else:
                    print("Error in add polyhedron bottom right open")

                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(poly_top_right_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_top_right_whithout_open
                    )

            case "SUP. NO FEMELLA / INF. FEMELLA ESQ.":
                print(
                    "Selected SUP. NO FEMELLA / INF. FEMELLA ESQ."
                )  # Abierto a la izquierda. Superior sin femella, inferior con femella
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_bottom_left_open)
                if polyhedron_bottom_left_open in polyhedron_premarc_list:
                    print("Success in add polyhedron bottom left open")
                else:
                    print("Error in add polyhedron bottom left open")

                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(poly_top_left_without_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_top_left_without_open
                    )

            case "SUP. NO FEMELLA / INF. FEMELLA DRET. + REA":
                print(
                    "Selected SUP. NO FEMELLA / INF. FEMELLA DRET. + REA"
                )  # Abierto a la derecha. Superior sin femella, inferior con femella + REA
                if polyhedron_right in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_right)
                        polyhedron_premarc_list.remove(polyhedron_finish_right)
                    except ValueError:
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_bottom_right_open)
                if all(
                    elem in polyhedron_premarc_list
                    for elem in [polyhedron_bottom_right_open]
                ):
                    print("Success in add polyhedron bottom right open + REA")
                else:
                    print("Error in add polyhedron bottom right open + REA")

                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(poly_top_right_whithout_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_top_right_whithout_open
                    )

            case "SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA":
                print(
                    "Selected SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA"
                )  # Abierto a la izquierda. Superior sin femella, inferior con femella + REA
                if polyhedron_left in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_left)
                        polyhedron_premarc_list.remove(polyhedron_finish_left)
                    except ValueError:
                        pass
                if polyhedron_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_bottom)
                    except ValueError:
                        print("Error in remove polyhedron bottom")
                        pass
                polyhedron_premarc_list.append(polyhedron_bottom_left_open)

                if all(
                    elem in polyhedron_premarc_list
                    for elem in [polyhedron_bottom_left_open]
                ):
                    print("Success in add polyhedron bottom left open + REA")
                else:
                    print("Error in add polyhedron bottom left open + REA")

                if polyhedron_top in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_top)
                    except ValueError:
                        print("Error in remove polyhedron top")
                        pass
                polyhedron_premarc_list.append(poly_top_left_without_open)

                if self.build_ele.ComboBoxPendiente.value == "NO":
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        poly_top_left_without_open
                    )
            case _:
                print("Selected default")

        if poly_base_no_slope is None and not self.is_bottom_open_premarc():
            if self.build_ele.ComboBoxPendiente.value == "SI":
                if self.bottom_rebaje_enabled():
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        polyhedron_bottom_grade_with_rebaje
                    )
                else:
                    poly_base_no_slope = AllplanGeo.Polyhedron3D(
                        polyhedron_bottom_grade
                    )
            else:
                poly_base_no_slope = AllplanGeo.Polyhedron3D(polyhedron_bottom)
            print(
                f"[Premarc] poly_base_no_slope was None, fallback applied (pend={self.build_ele.ComboBoxPendiente.value})"
            )

        # Passama - Controlar cada selección del CheckBox dinámico
        lista_passama = self.build_ele.valueListaPassama.value
        opciones_seleccionadas = self.build_ele.PassamaOptions.value

        # Iterar sobre cada opción y controlar si está seleccionada
        for nombre_opcion, esta_seleccionada in zip(
            lista_passama, opciones_seleccionadas
        ):
            if esta_seleccionada:  # Si la opción está en True
                print(f"Opción seleccionada: '{nombre_opcion}'")

                # Controlar cada opción según su nombre
                match nombre_opcion:
                    case "NO":
                        print("Ejecutando acción para NO - Sin passamà")
                        # Tu código aquí para NO
                    case "PASSAMÀ LATERALS":
                        print("Ejecutando acción para PASSAMÀ LATERALS")
                        # Tu código aquí para passamà laterals
                    case "PASSAMÀ INF/SUP":
                        print("Ejecutando acción para PASSAMÀ INF/SUP")
                        # Tu código aquí para passamà inferior/superior
                    case "PASSAMÀ 4 COSTATS":
                        print("Ejecutando acción para PASSAMÀ 4 COSTATS")
                        # Tu código aquí para passamà 4 costats
                    case "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)":
                        print("Ejecutando acción para PASSAMÀ FALCA SUP.")
                        # Tu código aquí para falca superior
                    case "PASSAMÀ FALCA INF. (+ de 4 m)":
                        print("Ejecutando acción para PASSAMÀ FALCA INF.")
                        # Tu código aquí para falca inferior > 4m
                    case "PASSAMÀ FALCA SUP./INF. (+ de 6m)":
                        print("Ejecutando acción para PASSAMÀ FALCA SUP./INF.")
                        # Tu código aquí para falca sup/inf > 6m
                    case _:
                        print(f"Opción no reconocida: '{nombre_opcion}'")

        # Passama
        match self.build_ele.PassamaOptions.value:
            case "NO":
                print("Selected NO")
            case "SI":
                print("Selected SI")
            case _:
                print("Selected default")

        ### Encajes, solamente maneja pliegue inferior, que es parte del premarco.
        polyhedron_socket = None
        match self.build_ele.ComboBoxEncajes.value:
            #     case "NO":
            #         print("Falca Selected NO")
            #     case "35*30":
            #         print("Falca Selected 35*30")
            #         socket_width = 35-3 # 32 compensa extrude, la medida es 35 medido de afuera.
            #         socket_height = 30-3 # 27  compensa extrude, la medida es 30 medido de afuera.

            #         polyedron_sockets = self.create_socket(socket_width, socket_height)
            #         error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(polyedron_sockets)
            #         polyhedron_other_elements_list.append(polyhedron_socket)
            #     case "70*30":
            #         print("Falca Selected 70*30")
            #         socket_width = 70-3 # 68 compensa extrude, la medida es 70 medido de afuera.
            #         socket_height = 30-3 # 27  compensa extrude, la medida es 30 medido de afuera.

            #         polyedron_sockets = self.create_socket(socket_width, socket_height)
            #         error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(polyedron_sockets)
            #         polyhedron_other_elements_list.append(polyhedron_socket)
            case "PLEC INFERIOR":
                print("Falca Selected PLEC INFERIOR")
                polyhedron_premarc_list.append(polyhedron_fold_with_fillet_moved)
                # remove bottom
                if polyhedron_finish_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.remove(polyhedron_finish_bottom)
                    except ValueError:
                        print(
                            "Error in remove polyhedron finish bottom with Pliegue inferior"
                        )
                        pass
        #     case _:
        #         print("Falca Selected default")

        # ## Escuadras
        # match self.build_ele.ComboBoxEscuadras.value:
        #     case "NO":
        #         print("Escuadra Selected NO")
        #     case "2":
        #         print("Escuadra Selected 2 de arriba")
        #         polyhedron_other_elements_list.append(polyhedron_square_left_top)
        #         polyhedron_other_elements_list.append(polyhedron_square_right_top)
        #     case "4":
        #         print("Escuadra Selected 4 (2 arriba y 2 abajo)")
        #         polyhedron_other_elements_list.append(polyhedron_square_left_top)
        #         polyhedron_other_elements_list.append(polyhedron_square_right_top)
        #         polyhedron_other_elements_list.append(polyhedron_square_left_bottom)
        #         polyhedron_other_elements_list.append(polyhedron_square_right_bottom)
        #     case _:
        #         print("Escuadra Selected default")

        # ## Tubos
        # match self.build_ele.ComboBoxTubos.value:
        #     case "NO":
        #         print("Tubo Selected NO")
        #     case "1 VERT.":
        #         print("Tubo Selected 1")
        #         polyhedron_tubs = self.create_tubs_proportioned(1, VERTICAL_TUB)
        #         polyhedron_other_elements_list.extend(polyhedron_tubs)
        #     case "2 VERT.":
        #         print("Tubo Selected 2")
        #         polyhedron_tubs = self.create_tubs_proportioned(2, VERTICAL_TUB)
        #         polyhedron_other_elements_list.extend(polyhedron_tubs)
        #     case "3 VERT.":
        #         print("Tubo Selected 3")
        #         polyhedron_tubs = self.create_tubs_proportioned(3, VERTICAL_TUB)
        #         polyhedron_other_elements_list.extend(polyhedron_tubs)
        #     case "4 VERT.":
        #         print("Tubo Selected 4")
        #         polyhedron_tubs = self.create_tubs_proportioned(4, VERTICAL_TUB)
        #         polyhedron_other_elements_list.extend(polyhedron_tubs)
        #     case "1 HORIT.":
        #         print("Tubo Selected 1 horizontal")
        #         polyhedron_tubs = self.create_tubs_proportioned(1, HORIZONTAL_TUB)
        #         polyhedron_other_elements_list.extend(polyhedron_tubs)
        #     case "2 HORITZ.":
        #         print("Tubo Selected 2 horizontal")
        #         polyhedron_tubs = self.create_tubs_proportioned(2, HORIZONTAL_TUB)
        #         polyhedron_other_elements_list.extend(polyhedron_tubs)
        #     case _:
        #         print("Tubo Selected default")

        # Pendent
        pendent_selected = self.build_ele.ComboBoxPendiente.value
        match pendent_selected:
            case "NO":
                print("Pendent Selected NO")
            case "SI":
                print("Pendent Selected SI")
                if self.bottom_rebaje_enabled():
                    if polyhedron_bottom in polyhedron_premarc_list:
                        try:
                            polyhedron_premarc_list.append(
                                polyhedron_bottom_grade_with_rebaje
                            )
                            polyhedron_premarc_list.remove(polyhedron_bottom)
                            self._refresh_bottom_sill_top_z_cache(
                                polyhedron_bottom_grade_with_rebaje, accept_any_z=True
                            )
                        except ValueError:
                            print("Error in remove polyhedron bottom")
                            pass
                else:  # pendiente without rebaje

                    if polyhedron_bottom in polyhedron_premarc_list:
                        try:
                            polyhedron_premarc_list.append(polyhedron_bottom_grade)
                            polyhedron_premarc_list.remove(polyhedron_bottom)
                            self._refresh_bottom_sill_top_z_cache(
                                polyhedron_bottom_grade, accept_any_z=True
                            )
                        except ValueError:
                            print("Error in remove polyhedron bottom")
                            pass
                    # Fix elements related:
                    # Frame_finish_bottom/ Encaje/ Pliegue inferior

                if polyhedron_finish_bottom in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.append(polyhedron_finish_bottom_fix)
                        polyhedron_premarc_list.remove(polyhedron_finish_bottom)
                    except ValueError:
                        print("Error in remove polyhedron finish bottom")
                        pass
                if polyhedron_socket in polyhedron_other_elements_list:
                    # fix position socket
                    count_socket = 0
                    for polyhedron in polyhedron_other_elements_list:
                        if polyhedron == polyhedron_socket:
                            count_socket += 1
                    print(f"Count socket: {count_socket}")
                    FIX_HEIGHT_SOCKET = 9  # 9 mm
                    translation_vector = AllplanGeo.Vector3D(0, 0, FIX_HEIGHT_SOCKET)
                    polyhedron_socket_fix = AllplanGeo.Move(
                        polyhedron_socket, translation_vector
                    )
                    try:
                        polyhedron_other_elements_list.append(polyhedron_socket_fix)
                        polyhedron_other_elements_list.remove(polyhedron_socket)
                    except ValueError:
                        print("Error in remove polyhedron socket")
                        pass
                if polyhedron_fold_with_fillet_moved in polyhedron_premarc_list:
                    try:
                        polyhedron_premarc_list.append(
                            rotated_polyhedron_fold_with_fillet_moved
                        )
                        polyhedron_premarc_list.remove(
                            polyhedron_fold_with_fillet_moved
                        )
                    except ValueError:
                        print("Error in remove polyhedron fold with fillet moved")
                        pass
            case _:
                print("Pendent Selected default")

        # Union premarc
        # TODO refactor to use method create_union_premarc
        polyhedron_premarc_union = self.create_union_premarc(polyhedron_premarc_list)
        if polyhedron_premarc_union is None:
            print("Error in make union premarc")
            # polyhedron_premarc_union = polyhedron_premarc_list

        ### Build substract rebajes ###
        # Manage rebajes
        list_rebajes = list(
            zip(
                self.build_ele.valueListaRebajes.value,
                self.build_ele.RebajesOptions.value,
            )
        )

        for name, option in list_rebajes:
            if option == 1:
                match name:
                    case "NO":
                        print("Rebaje Selected NO. Nothing to do")
                        break  # discard all other rebajes
                    case "REB. DRETA":  # Rebaje derecho
                        print("Rebaje Selected REB. DRETA")
                        if show_rebajes_debug:
                            debug_rebaje_solids.append(substract_rebajes_right)
                        intersecting, _ = AllplanGeo.Intersect(
                            polyhedron_premarc_union, substract_rebajes_right
                        )
                        if intersecting:
                            error_code, polyhedron_premarc_union = (
                                AllplanGeo.MakeSubtraction(
                                    polyhedron_premarc_union, substract_rebajes_right
                                )
                            )
                        else:
                            print("Error in intersect rebaje right")
                            pass
                    case "REB. ESQUERRA":  # Rebaje izquierdo
                        print("Rebaje Selected REB. ESQUERRA")
                        if show_rebajes_debug:
                            debug_rebaje_solids.append(substract_rebajes_left)
                        intersecting, _ = AllplanGeo.Intersect(
                            polyhedron_premarc_union, substract_rebajes_left
                        )
                        if intersecting:
                            error_code, polyhedron_premarc_union = (
                                AllplanGeo.MakeSubtraction(
                                    polyhedron_premarc_union, substract_rebajes_left
                                )
                            )
                        else:
                            print("Error in intersect rebaje left")
                            pass
                    case "REB. BAIX" | "REB. BAIXS":  # Rebaje inferior
                        print("Rebaje Selected REB. BAIX")
                        if show_rebajes_debug:
                            debug_rebaje_solids.append(substract_rebajes_bottom)
                        if self.build_ele.ComboBoxPendiente.value == "SI":
                            # Manage in pendent section
                            continue  # discard rebaje inferior if pendiente is selected
                        intersecting, _ = AllplanGeo.Intersect(
                            polyhedron_premarc_union, substract_rebajes_bottom
                        )
                        if intersecting:
                            error_code, polyhedron_premarc_union = (
                                AllplanGeo.MakeSubtraction(
                                    polyhedron_premarc_union, substract_rebajes_bottom
                                )
                            )
                        else:
                            print("Error in intersect rebaje bottom")
                            pass

                    case "REB. DALT":  # Rebaje superior
                        print("Rebaje Selected REB. DALT")
                        if show_rebajes_debug:
                            debug_rebaje_solids.append(substract_rebajes_top)
                        intersecting, _ = AllplanGeo.Intersect(
                            polyhedron_premarc_union, substract_rebajes_top
                        )
                        if intersecting:
                            error_code, polyhedron_premarc_union = (
                                AllplanGeo.MakeSubtraction(
                                    polyhedron_premarc_union, substract_rebajes_top
                                )
                            )
                        else:
                            print("Error in intersect rebaje top")
                            pass
                    case _:
                        print("Rebaje Selected default")

        # Fix corners
        # top left corner
        if self.get_enabled_rebajes_options(
            "REB. DALT"
        ) and self.get_enabled_rebajes_options("REB. ESQUERRA"):
            if show_rebajes_debug:
                debug_rebaje_solids.append(substract_top_left_corner)
            intersecting, _ = AllplanGeo.Intersect(
                polyhedron_premarc_union, substract_top_left_corner
            )
            if intersecting:
                error_code, polyhedron_premarc_union = AllplanGeo.MakeSubtraction(
                    polyhedron_premarc_union, substract_top_left_corner
                )
            else:
                print("Error in intersect top left corner")
                pass
        # top right corner
        if self.get_enabled_rebajes_options(
            "REB. DALT"
        ) and self.get_enabled_rebajes_options("REB. DRETA"):
            if show_rebajes_debug:
                debug_rebaje_solids.append(substract_top_right_corner)
            intersecting, _ = AllplanGeo.Intersect(
                polyhedron_premarc_union, substract_top_right_corner
            )
            if intersecting:
                error_code, polyhedron_premarc_union = AllplanGeo.MakeSubtraction(
                    polyhedron_premarc_union, substract_top_right_corner
                )
            else:
                print("Error in intersect top right corner")
                pass
        # bottom left corner
        if self.get_enabled_rebajes_options(
            "REB. BAIX"
        ) and self.get_enabled_rebajes_options("REB. ESQUERRA"):
            if show_rebajes_debug:
                debug_rebaje_solids.append(substract_bottom_left_corner)
            intersecting, _ = AllplanGeo.Intersect(
                polyhedron_premarc_union, substract_bottom_left_corner
            )
            if intersecting:
                error_code, polyhedron_premarc_union = AllplanGeo.MakeSubtraction(
                    polyhedron_premarc_union, substract_bottom_left_corner
                )
            else:
                print("Error in intersect bottom left corner")
                pass
        # bottom right corner
        if self.get_enabled_rebajes_options(
            "REB. BAIX"
        ) and self.get_enabled_rebajes_options("REB. DRETA"):
            if show_rebajes_debug:
                debug_rebaje_solids.append(substract_bottom_right_corner)
            intersecting, _ = AllplanGeo.Intersect(
                polyhedron_premarc_union, substract_bottom_right_corner
            )
            if intersecting:
                error_code, polyhedron_premarc_union = AllplanGeo.MakeSubtraction(
                    polyhedron_premarc_union, substract_bottom_right_corner
                )
            else:
                print("Error in intersect bottom right corner")
                pass

        elems = []
        elems.append(polyhedron_premarc_union)
        elems.extend(polyhedron_other_elements_list)

        # elems = [
            # polyhedron_premarc_union,
            # polyhedron_other_elements_list
            # polyhedron_top,
            # polyhedron_top_finish,
            # polyhedron_right,
            # polyhedron_bottom,
            # polyhedron_bottom_finish,
            # polyhedron_left,
            # polyhedron_finish_bottom,
            # polyhedron_finish_top,
            # polyhedron_finish_left,
            # polyhedron_finish_right,
            # frame_square # deprecated
            # polyhedron_square_left_top,
            # polyhedron_square_right_top,
            # polyhedron_square_left_bottom,
            # polyhedron_square_right_bottom,
            # polyhedron_tub_moved, # deprecated
            # polyhedron_tub_left_top # deprecated
            # self.create_horizontal_tub(),
            # polyhedron_fold_bottom,
            # polyhedron_fold_top
            # polyhedron_fold_bottom,
            # polyhedron_fold_top,
            # polyhedron_union,
            # polyhedron_top_falca,
            # polyhedron_bottom_falca,
            # polyhedron_hexagon
            # polyhedron_top_open
            # polyhedron_tub,
            # bottom_falcas,
            # polyhedron_cylinder_moved
            # ]
        # if polyhedron_other_elements_list:
        #     elems.extend(polyhedron_other_elements_list)
        # else:
        #     print("No other elements to add")
        # if polyhedron_socket:
        #     elems.append(polyhedron_socket) # Socket is independent of other elements

        # append squares
        # if polyhedron_square_left_top:
        #     elems.append(polyhedron_square_left_top)
        # if polyhedron_square_right_top:
        #     elems.append(polyhedron_square_right_top)
        # if polyhedron_square_left_bottom:
        #     elems.append(polyhedron_square_left_bottom)
        # if polyhedron_square_right_bottom:
        #     elems.append(polyhedron_square_right_bottom)
        # append fold polyhedron union
        # error != AllplanGeo.eGeometryErrorCode.eOK

        # if success_fold_bottom and error_polyedron_bottom == AllplanGeo.eGeometryErrorCode.eOK:
        # if success_fold_bottom:
        #     elems.append(fold_polyhedron_bottom_moved)
        # elems.remove(polyhedron_finish_bottom)
        # elems.remove(polyhedron_finish_left)
        # elems.remove(polyhedron_finish_right)
        # else:
        #     print(f"Error in make union fold polyhedron bottom: {error_polyedron_bottom}")
        # append falcas
        if TOP_FALCAS:
            elems.extend(polyhedron_top_falcas)
        if BOTTOM_FALCAS:
            elems.extend(polyhedron_bottom_falcas)
        # elems.extend(polyhedron_tubs)
        # if error_code_socket:
        #     elems.append(polyhedron_socket)
        # else:
        #     print(f"Error in make union sockets: {error_code_socket}")
        # if polyhedron_top_left_open:
        #     elems.append(polyhedron_top_left_open)
        #     elems.remove(polyhedron_top)
        #     elems.remove(polyhedron_left)
        #     elems.remove(polyhedron_finish_left)

        # TODO logic to remove once elements for premarc
        # if polyhedron_top_right_open:
        #     elems.append(polyhedron_top_right_open)
        #     elems.remove(polyhedron_top)
        #     elems.remove(polyhedron_right)
        #     elems.remove(polyhedron_finish_right)
        # if polyhedron_bottom_right_open:
        #     elems.append(polyhedron_bottom_right_open)
        #     elems.remove(polyhedron_bottom)
        #     # elems.remove(polyhedron_right)
        #     # elems.remove(polyhedron_finish_right)
        # if polyhedron_bottom_grade:
        #     elems.append(polyhedron_bottom_grade)
        #     elems.remove(polyhedron_bottom)
        if polyhedron_box_shutter:
            elems.append(polyhedron_box_shutter)

        substract_rebaje = debug_rebaje_solids

        if polyhedron_finish_bottom_fix in polyhedron_premarc_list:
            self._u_sill_finish_poly = polyhedron_finish_bottom_fix
        elif polyhedron_finish_bottom in polyhedron_premarc_list:
            self._u_sill_finish_poly = polyhedron_finish_bottom

        cand: list[float] = []
        early_cache = getattr(self, "_cached_bottom_sill_top_z", None)
        if early_cache is not None:
            cand.append(early_cache)
        if poly_base_no_slope is not None:
            zb = self._poly_bbox_max_z(poly_base_no_slope)
            if zb is not None:
                cand.append(zb)
        fin = getattr(self, "_u_sill_finish_poly", None)
        if fin is not None:
            zf = self._poly_bbox_max_z(fin)
            if zf is not None:
                cand.append(zf)
        for poly in (polyhedron_bottom, polyhedron_finish_bottom):
            zz = self._poly_bbox_max_z(poly)
            if zz is not None:
                cand.append(zz)
        if cand:
            self._cached_bottom_sill_top_z = max(cand)
            print(
                f"[Premarc] sill cache={self._cached_bottom_sill_top_z:.2f}, "
                f"early={early_cache}, "
                f"pend={self.build_ele.ComboBoxPendiente.value}, "
                f"thickness={float(self.thickness):.1f}, tp={float(self.thickness_premarc):.1f}"
            )
        elif poly_base_no_slope is not None:
            self._refresh_bottom_sill_top_z_cache(poly_base_no_slope, accept_any_z=True)

        return elems, poly_base_no_slope, substract_rebaje

    def get_enabled_rebajes_options(self, option):
        list_rebajes = list(
            zip(
                self.build_ele.valueListaRebajes.value,
                self.build_ele.RebajesOptions.value,
            )
        )
        d = dict(list_rebajes)
        if option == "REB. BAIX":
            return (d.get("REB. BAIX") == 1 or d.get("REB. BAIXS") == 1) and d.get("NO") == 0
        return d.get(option) == 1 and d.get("NO") == 0

    def bottom_rebaje_enabled(self):
        list_rebajes = list(
            zip(
                self.build_ele.valueListaRebajes.value,
                self.build_ele.RebajesOptions.value,
            )
        )
        d = dict(list_rebajes)
        return (d.get("REB. BAIX") == 1 or d.get("REB. BAIXS") == 1) and d.get("NO") == 0

    def is_bottom_open_premarc(self):
        return self.build_ele.ComboBoxAbiertoCerrado.value in (
            "OBERT PER BAIX",
            "OBERT PER BAIX + REA",
            "OBERT PER BAIX + REA VARIANT",
        )

    def get_direction_open_premarc(self):
        direction_open_premarc = self.build_ele.ComboBoxAbiertoCerrado.value
        values_direction_right = [
            "OBERT FEMELLA DRETA + REA",
            "OBERT NO FEMELLA DRETA + REA",
            "SUP. FEMELLA / INF NO FEMELLA DRET. + REA",
            "SUP. NO FEMELLA / INF. FEMELLA DRET. + REA",
        ]
        values_direction_left = [
            "OBERT FEMELLA ESQUERRA + REA",
            "OBERT NO FEMELLA ESQUERRA + REA",
            "SUP. FEMELLA / INF NO FEMELLA ESQ. + REA",
            "SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA",
        ]
        values_direction_top = [
            "OBERT PER DALT + REA",
        ]
        values_direction_top_variant = [
            "OBERT PER DALT + REA VARIANT",
        ]
        values_direction_bottom = [
            "OBERT PER BAIX + REA",
        ]
        values_direction_bottom_variant = [
            "OBERT PER BAIX + REA VARIANT",
        ]
        if direction_open_premarc in values_direction_right:
            return "RIGHT"
        elif direction_open_premarc in values_direction_left:
            return "LEFT"
        elif direction_open_premarc in values_direction_top:
            return "TOP"
        elif direction_open_premarc in values_direction_top_variant:
            return "TOP_VARIANT"
        elif direction_open_premarc in values_direction_bottom:
            return "BOTTOM"
        elif direction_open_premarc in values_direction_bottom_variant:
            return "BOTTOM_VARIANT"
        else:
            return "NOTHING"

    def get_direction_retall_ganxo(self):
        direction_retall_ganxo = self.build_ele.ComboBoxAbiertoCerrado.value

        values_direction_right = [
            "OBERT FEMELLA DRETA",
            "OBERT FEMELLA DRETA + REA",
            "OBERT NO FEMELLA DRETA",
            "OBERT NO FEMELLA DRETA + REA",
            "SUP. FEMELLA / INF NO FEMELLA DRET.",
            "SUP. FEMELLA / INF NO FEMELLA DRET. + REA",
            "SUP. NO FEMELLA / INF. FEMELLA DRET.",
            "SUP. NO FEMELLA / INF. FEMELLA DRET. + REA",
        ]

        values_direction_left = [
            "OBERT FEMELLA ESQUERRA",
            "OBERT FEMELLA ESQUERRA + REA",
            "OBERT NO FEMELLA ESQUERRA",
            "OBERT NO FEMELLA ESQUERRA + REA",
            "SUP. FEMELLA / INF NO FEMELLA ESQ.",
            "SUP. FEMELLA / INF NO FEMELLA ESQ. + REA",
            "SUP. NO FEMELLA / INF. FEMELLA ESQ.",
            "SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA",
        ]

        if direction_retall_ganxo in values_direction_right:
            return "RIGHT"
        elif direction_retall_ganxo in values_direction_left:
            return "LEFT"
        else:
            return None

    def create_box_shutter(self):  # Cajon de persiana
        # Box shutters
        wall_thickness_xps = self._xps_wall_thickness_mm()
        BOX_SHUTTER_HEIGHT = self.build_ele.PersianaHeight.value
        BOX_SHUTTER_WIDTH = (
            wall_thickness_xps
            if self.build_ele.ComboBoxPersianas.value == "LAMISOL VIST"
            else self.build_ele.PersianaWidth.value
        )
        box_shutter = AllplanGeo.Polygon3D()
        box_shutter_x = 0
        box_shutter += AllplanGeo.Point3D(box_shutter_x, 0, 0)
        box_shutter += AllplanGeo.Point3D(box_shutter_x, 0, BOX_SHUTTER_HEIGHT)
        box_shutter += AllplanGeo.Point3D(box_shutter_x, -BOX_SHUTTER_WIDTH, BOX_SHUTTER_HEIGHT)
        box_shutter += AllplanGeo.Point3D(box_shutter_x, -BOX_SHUTTER_WIDTH, 0)
        box_shutter += AllplanGeo.Point3D(box_shutter_x, 0, 0)

        # Manage config UI
        box_shutter_list = []
        shutter_lateral_offset = float(THICKNESS_MM)
        shutter_z_offset = float(THICKNESS_MM)
        match (self.build_ele.ComboBoxPersianas.value):
            case "NO":
                print("Persiana Selected NO. Nothing to do")
                box_shutter_list = []
            case "MONOBLOCK OCULT":
                print("MONOBLOCK OCULT")
                # Move box shutters to offset from front
                fix_y = self.thickness - self.build_ele.PersianaWidth.value
                translation_vector = AllplanGeo.Vector3D(-shutter_lateral_offset, -(fix_y), shutter_z_offset)
                box_shutter_moved = AllplanGeo.Move(box_shutter, translation_vector)
                error_code, polyhedron_box_shutter = self.extrude_frame(box_shutter_moved, "box_shutter")

                box_shutter_list.append(polyhedron_box_shutter)
            case "LAMISOL VIST":
                print("LAMISOL VIST")
                box_shutter_moved = AllplanGeo.Move(box_shutter, AllplanGeo.Vector3D(-shutter_lateral_offset, 0, shutter_z_offset))
                error_code, polyhedron_box_shutter = self.extrude_frame(box_shutter_moved, "box_shutter")
                box_shutter_list.append(polyhedron_box_shutter)
            case "METALUNIC VIST":
                print("METALUNIC VIST")

                # Move box shutters to wall thickness
                fix_y = wall_thickness_xps
                translation_vector = AllplanGeo.Vector3D(-shutter_lateral_offset, -fix_y, shutter_z_offset)
                box_shutter_moved = AllplanGeo.Move(box_shutter, translation_vector)
                error_code, polyhedron_box_shutter = self.extrude_frame(box_shutter_moved, "box_shutter")

                box_shutter_list.append(polyhedron_box_shutter)
            case "FALS CALAIX":
                print("FALS CALAIX")
                box_shutter_moved = AllplanGeo.Move(box_shutter, AllplanGeo.Vector3D(-shutter_lateral_offset, 0, shutter_z_offset))
                error_code, polyhedron_box_shutter = self.extrude_frame(box_shutter_moved, "box_shutter")
                box_shutter_list.append(polyhedron_box_shutter)
            case _:
                print("Persiana Selected default")
                box_shutter_list = []

        # TODO: Eliminar hardcode
        # box_shutter_list = []
        # box_shutter_list.append(polyhedron_box_shutter)

        return box_shutter_list

    def create_premarc_REA(self):
        elems = []
        cuboids = []
        cylinders = []

        REA_x_y = 40
        REA_extra = 200
        # Firts
        pos_REA = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, REA_extra))
        first_cuboid_REA = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_REA, REA_x_y, -REA_x_y, -(self.heigh + REA_extra * 2)
        )
        # elems.append(first_cuboid_REA)
        cuboids.append(first_cuboid_REA)

        # Second cuboid
        pos_REA = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(REA_x_y, 0, REA_extra))
        second_cuboid_REA = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_REA, REA_x_y, -REA_x_y, -(self.heigh + REA_extra * 2)
        )
        # elems.append(second_cuboid_REA)
        cuboids.append(second_cuboid_REA)

        # Cilinders ####
        # # left top
        # cylinder = AllplanGeo.Cylinder3D(
        #     AllplanGeo.AxisPlacement3D(
        #         AllplanGeo.Point3D(-5, -(REA_x_y/2 - 5), REA_extra),
        #         AllplanGeo.Vector3D(1, 0, 0),
        #         AllplanGeo.Vector3D(0, 0, -1)
        #     ),
        #     5,
        #     5,
        #     AllplanGeo.Point3D(0, 0, self.heigh + REA_extra * 2)
        # )

        # error_code, polyhedron_cylinder_left_top = AllplanGeo.CreatePolyhedron(cylinder, 36)
        # # elems.append(polyhedron_cylinder_left_top)
        # cylinders.append(polyhedron_cylinder_left_top)

        # # left bottom
        # cylinder = AllplanGeo.Cylinder3D(
        #     AllplanGeo.AxisPlacement3D(
        #         AllplanGeo.Point3D(-5, -(REA_x_y/2 + 5), REA_extra),
        #         AllplanGeo.Vector3D(1, 0, 0),
        #         AllplanGeo.Vector3D(0, 0, -1)
        #     ),
        #     5,
        #     5,
        #     AllplanGeo.Point3D(0, 0, self.heigh + REA_extra * 2)
        # )

        # error_code, polyhedron_cylinder_left_bottom = AllplanGeo.CreatePolyhedron(cylinder, 36)
        # # elems.append(polyhedron_cylinder_left_bottom)
        # cylinders.append(polyhedron_cylinder_left_bottom)

        # left back top
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    -5, -(REA_x_y / 2 - 5), REA_Z_ORIGIN
                ),  # Centro base inferior
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            5,
            5,
            AllplanGeo.Point3D(0, 0, REA_Z_FINAL),  # centro base superior
        )

        error_code, polyhedron_cylinder_left_back_top = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )
        # elems.append(polyhedron_cylinder_left_top)
        cylinders.append(polyhedron_cylinder_left_back_top)

        # left forward top
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(-5, -(REA_x_y / 2 + 5), REA_Z_ORIGIN),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            5,
            5,
            AllplanGeo.Point3D(0, 0, REA_Z_FINAL),
        )

        error_code, polyhedron_cylinder_left_forward_top = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )
        # elems.append(polyhedron_cylinder_left_bottom)
        cylinders.append(polyhedron_cylinder_left_forward_top)

        # left back bottom
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    -5, -(REA_x_y / 2 - 5), -(self.heigh + REA_Z_ORIGIN)
                ),  # Centro base inferior
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, -1),
            ),
            5,
            5,
            AllplanGeo.Point3D(
                0, 0, REA_Z_FINAL
            ),  # Cuanto se expande, en direccion setiada de z
        )

        error_code, polyhedron_cylinder_left_back_bottom = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )
        # elems.append(polyhedron_cylinder_left_top)
        cylinders.append(polyhedron_cylinder_left_back_bottom)

        # left forward bottom
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    -5, -(REA_x_y / 2 + 5), -(self.heigh + REA_Z_ORIGIN)
                ),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, -1),
            ),
            5,
            5,
            AllplanGeo.Point3D(0, 0, REA_Z_FINAL),
        )

        error_code, polyhedron_cylinder_left_forward_bottom = (
            AllplanGeo.CreatePolyhedron(cylinder, 36)
        )
        # elems.append(polyhedron_cylinder_left_bottom)
        cylinders.append(polyhedron_cylinder_left_forward_bottom)

        # right back top
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(REA_x_y * 2 + 5, -(REA_x_y / 2 - 5), REA_Z_ORIGIN),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            5,
            5,
            AllplanGeo.Point3D(0, 0, REA_Z_FINAL),
        )

        error_code, polyhedron_cylinder_right_back_top = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )
        # elems.append(polyhedron_cylinder_right_top)
        cylinders.append(polyhedron_cylinder_right_back_top)

        # right forward top
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(REA_x_y * 2 + 5, -(REA_x_y / 2 + 5), REA_Z_ORIGIN),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            5,
            5,
            AllplanGeo.Point3D(0, 0, REA_Z_FINAL),
        )

        error_code, polyhedron_cylinder_right_forward_top = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )
        # elems.append(polyhedron_cylinder_right_bottom)
        cylinders.append(polyhedron_cylinder_right_forward_top)

        # right back bottom
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    REA_x_y * 2 + 5, -(REA_x_y / 2 - 5), -(self.heigh + REA_Z_ORIGIN)
                ),  # Centro base inferior
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, -1),
            ),
            5,
            5,
            AllplanGeo.Point3D(
                0, 0, REA_Z_FINAL
            ),  # Cuanto se expande, en direccion setiada de z
        )

        error_code, polyhedron_cylinder_rigth_back_bottom = AllplanGeo.CreatePolyhedron(
            cylinder, 36
        )
        # elems.append(polyhedron_cylinder_left_top)
        cylinders.append(polyhedron_cylinder_rigth_back_bottom)

        # right forward bottom
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    REA_x_y * 2 + 5, -(REA_x_y / 2 + 5), -(self.heigh + REA_Z_ORIGIN)
                ),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, -1),
            ),
            5,
            5,
            AllplanGeo.Point3D(0, 0, REA_Z_FINAL),
        )

        error_code, polyhedron_cylinder_left_forward_bottom = (
            AllplanGeo.CreatePolyhedron(cylinder, 36)
        )
        # elems.append(polyhedron_cylinder_left_bottom)
        cylinders.append(polyhedron_cylinder_left_forward_bottom)

        ### manage config UI
        offset_rea = 250
        space_y = 60
        translation_vector_rigth = AllplanGeo.Vector3D(
            self.width - offset_rea - REA_x_y * 2, -space_y, 0
        )
        translation_vector_left = AllplanGeo.Vector3D(offset_rea, -space_y, 0)
        elems_moved = []
        cuboids_moved = []
        cylinders_moved = []
        direction_open = self.get_direction_open_premarc()

        def create_horizontal_rea(z_positions, variant=False):
            rea_length = self.width + REA_extra * 2
            rea_x = -REA_extra
            try:
                wall_thickness = float(self.build_ele.thickness_wall.value or 0.0)
            except Exception:
                wall_thickness = 0.0
            if wall_thickness <= 0:
                wall_thickness = float(self.detected_wall_thickness or 0.0)
            wall_center_y = -wall_thickness / 2
            # Cuboids are created with a negative Y depth (-REA_x_y). For a
            # single tube, start Y must be center + half depth. For variant,
            # center the two adjacent tubes as one 2*REA_x_y package.
            y_positions = (
                (wall_center_y + REA_x_y, wall_center_y)
                if variant
                else (wall_center_y + REA_x_y / 2, wall_center_y + REA_x_y / 2)
            )
            result = []
            for z_pos, y_pos in zip(z_positions, y_positions):
                pos_rea = AllplanGeo.AxisPlacement3D(
                    AllplanGeo.Point3D(rea_x, y_pos, z_pos)
                )
                result.append(
                    AllplanGeo.Polyhedron3D.CreateCuboid(
                        pos_rea, rea_length, -REA_x_y, -REA_x_y
                    )
                )
            return result

        if direction_open == "RIGHT":
            # for elem in elems:
            #     elem_moved = AllplanGeo.Move(elem, translation_vector_rigth)
            #     elems_moved.append(elem_moved)
            for elem in cuboids:
                elem_moved = AllplanGeo.Move(elem, translation_vector_rigth)
                cuboids_moved.append(elem_moved)
            for elem in cylinders:
                elem_moved = AllplanGeo.Move(elem, translation_vector_rigth)
                cylinders_moved.append(elem_moved)
        elif self.get_direction_open_premarc() == "LEFT":
            # for elem in elems:
            #     elem_moved = AllplanGeo.Move(elem, translation_vector_left)
            #     elems_moved.append(elem_moved)
            for elem in cuboids:
                elem_moved = AllplanGeo.Move(elem, translation_vector_left)
                cuboids_moved.append(elem_moved)
            for elem in cylinders:
                elem_moved = AllplanGeo.Move(elem, translation_vector_left)
                cylinders_moved.append(elem_moved)
        elif direction_open == "TOP":
            cuboids_moved = create_horizontal_rea(
                (-offset_rea, -(offset_rea + REA_x_y))
            )
            cylinders_moved = []
        elif direction_open == "TOP_VARIANT":
            cuboids_moved = create_horizontal_rea((-offset_rea, -offset_rea), True)
            cylinders_moved = []
        elif direction_open == "BOTTOM":
            cuboids_moved = create_horizontal_rea(
                (
                    -self.heigh + offset_rea + REA_x_y,
                    -self.heigh + offset_rea + REA_x_y * 2,
                )
            )
            cylinders_moved = []
        elif direction_open == "BOTTOM_VARIANT":
            cuboids_moved = create_horizontal_rea(
                (
                    -self.heigh + offset_rea + REA_x_y,
                    -self.heigh + offset_rea + REA_x_y,
                ),
                True,
            )
            cylinders_moved = []
        else:
            cuboids_moved = []
            cylinders_moved = []

        return cuboids_moved, cylinders_moved

    ##### Squares #######

    # TODO sacar
    # def create_premarc_optionals_elements_test(self):

    #     # --- Offset constants (0.0 - 1.0) ---
    #     # Initial
    #     low_measure,  medium_measure_1 = 0.20, 0.32
    #     medium_measure_2, high_measure = 0.68, 0.80

    #     # Test

    #     #low_measure,  medium_measure_1 = 0.0, 0.10
    #     #medium_measure_2, high_measure = 0.10, 0.20

    #     #low_measure,  medium_measure_1 = 0.0, 0.0
    #     #medium_measure_2, high_measure = 0.0, 0.0

    #     #low_measure,  medium_measure_1 = 0.10, 0.32
    #     #medium_measure_2, high_measure = 0.68, 0.20

    #     #low_measure,  medium_measure_1 = 0.50, 0.55
    #     #medium_measure_2, high_measure = 0.60, 0.100

    #     #low_measure,  medium_measure_1 = 0.20, 0.32
    #     #medium_measure_2, high_measure = 0.68, 1

    #     #low_measure,  medium_measure_1 = 0.0, 0.0
    #     medium_measure_2, high_measure = 0.30, 1

    #     y_off = -self.get_square_y_offset()
    #     w, h  = self.width, self.heigh

    #     # --- Build polygon ---
    #     def build_square_polygon(coords):
    #         """Crea un Polygon3D a partir de una lista de puntos (x, y, z)"""
    #         poly = AllplanGeo.Polygon3D()
    #         for x, y, z in coords:
    #             poly += AllplanGeo.Point3D(x, y, z)
    #         return poly

    #     # --- Define 4 polyhedron ---
    #     # Left Top
    #     frame_lt = build_square_polygon([
    #         (0,      y_off, -h * low_measure), (0,      y_off, -h * medium_measure_1),
    #         (w * medium_measure_1, y_off, 0),         (w * low_measure, y_off, 0),
    #         (0,      y_off, -h * low_measure)
    #     ])

    #     # Right Top
    #     frame_rt = build_square_polygon([
    #         (w,      y_off, -h * low_measure), (w,      y_off, -h * medium_measure_1),
    #         (w * medium_measure_2, y_off, 0),         (w * high_measure, y_off, 0),
    #         (w,      y_off, -h * low_measure)
    #     ])

    #     # Left Bottom
    #     frame_lb = build_square_polygon([
    #         (0,      y_off, -h * high_measure), (0,      y_off, -h * medium_measure_2),
    #         (w * medium_measure_1, y_off, -h),        (w * low_measure, y_off, -h),
    #         (0,      y_off, -h * high_measure)
    #     ])

    #     # Right Bottom
    #     frame_rb = build_square_polygon([
    #         (w,      y_off, -h * high_measure), (w,      y_off, -h * medium_measure_2),
    #         (w * medium_measure_2, y_off, -h),        (w * high_measure, y_off, -h),
    #         (w,      y_off, -h * high_measure)
    #     ])

    #     # --- Extrude polyhedrons ---
    #     # Aquí ejecutamos la extrusión para cada uno de manera individual
    #     err_lt, polyhedron_square_left_top = self.extrude_frame(frame_lt, "frame_square")
    #     err_rt, polyhedron_square_right_top = self.extrude_frame(frame_rt, "frame_square")
    #     err_lb, polyhedron_square_left_bottom = self.extrude_frame(frame_lb, "frame_square")
    #     err_rb, polyhedron_square_right_bottom = self.extrude_frame(frame_rb, "frame_square")

    #     return polyhedron_square_left_top, polyhedron_square_right_top, polyhedron_square_left_bottom, polyhedron_square_right_bottom

    # def build_square(self, points_list):
    #    poly = AllplanGeo.Polygon3D()
    #    for pt in points_list:
    #        poly += AllplanGeo.Point3D(pt[0], pt[1], pt[2])
    #    _, polyhedron = self.extrude_frame(poly, "frame_square")
    #    return polyhedron

    ##### End Squares #######

    def create_premarc_optionals_elements(self):

        other_elements = []
        # Squares - Escuadras

        frame_square_left_top = AllplanGeo.Polygon3D()
        frame_square_left_top += AllplanGeo.Point3D(
            0, 0, -(DISTANCE_FROM_ORIGIN - SQUARE_VERTEX_OFFSET)
        )  # 1
        frame_square_left_top += AllplanGeo.Point3D(
            DISTANCE_FROM_ORIGIN - SQUARE_VERTEX_OFFSET, 0, 0
        )  # 2
        frame_square_left_top += AllplanGeo.Point3D(DISTANCE_FROM_ORIGIN, 0, 0)  # 3
        frame_square_left_top += AllplanGeo.Point3D(0, 0, -(DISTANCE_FROM_ORIGIN))  # 4
        frame_square_left_top += AllplanGeo.Point3D(
            0, 0, -(DISTANCE_FROM_ORIGIN - SQUARE_VERTEX_OFFSET)
        )  # 5
        error_code, polyhedron_square_left_top = self.extrude_frame(
            frame_square_left_top, "frame_square"
        )

        # Square right top
        frame_square_right_top = AllplanGeo.Polygon3D()
        frame_square_right_top += AllplanGeo.Point3D(
            self.width - DISTANCE_FROM_ORIGIN, 0, 0
        )  # 1
        frame_square_right_top += AllplanGeo.Point3D(
            self.width - DISTANCE_FROM_ORIGIN + SQUARE_VERTEX_OFFSET, 0, 0
        )  # 2
        frame_square_right_top += AllplanGeo.Point3D(
            self.width, 0, -(DISTANCE_FROM_ORIGIN - SQUARE_VERTEX_OFFSET)
        )  # 3
        frame_square_right_top += AllplanGeo.Point3D(
            self.width, 0, -DISTANCE_FROM_ORIGIN
        )  # 4
        frame_square_right_top += AllplanGeo.Point3D(
            self.width - DISTANCE_FROM_ORIGIN, 0, 0
        )  # 5

        error_code, polyhedron_square_right_top = self.extrude_frame(
            frame_square_right_top, "frame_square"
        )

        # Square left bottom
        frame_square_left_bottom = AllplanGeo.Polygon3D()
        frame_square_left_bottom += AllplanGeo.Point3D(
            0, 0, -(self.heigh - DISTANCE_FROM_ORIGIN + SQUARE_VERTEX_OFFSET)
        )  # 1
        frame_square_left_bottom += AllplanGeo.Point3D(
            0, 0, -(self.heigh - DISTANCE_FROM_ORIGIN)
        )  # 2
        frame_square_left_bottom += AllplanGeo.Point3D(
            DISTANCE_FROM_ORIGIN, 0, -self.heigh
        )  # 3
        frame_square_left_bottom += AllplanGeo.Point3D(
            DISTANCE_FROM_ORIGIN - SQUARE_VERTEX_OFFSET, 0, -self.heigh
        )  # 4
        frame_square_left_bottom += AllplanGeo.Point3D(
            0, 0, -(self.heigh - DISTANCE_FROM_ORIGIN + SQUARE_VERTEX_OFFSET)
        )  # 5
        error_code, polyhedron_square_left_bottom = self.extrude_frame(
            frame_square_left_bottom, "frame_square"
        )

        # Square right bottom
        frame_square_right_bottom = AllplanGeo.Polygon3D()
        frame_square_right_bottom += AllplanGeo.Point3D(
            self.width - DISTANCE_FROM_ORIGIN, 0, -self.heigh
        )  # 1
        frame_square_right_bottom += AllplanGeo.Point3D(
            self.width - DISTANCE_FROM_ORIGIN + SQUARE_VERTEX_OFFSET, 0, -self.heigh
        )  # 2
        frame_square_right_bottom += AllplanGeo.Point3D(
            self.width, 0, -(self.heigh - DISTANCE_FROM_ORIGIN + SQUARE_VERTEX_OFFSET)
        )  # 3
        frame_square_right_bottom += AllplanGeo.Point3D(
            self.width, 0, -(self.heigh - DISTANCE_FROM_ORIGIN)
        )  # 4
        frame_square_right_bottom += AllplanGeo.Point3D(
            self.width - DISTANCE_FROM_ORIGIN, 0, -self.heigh
        )  # 5
        error_code, polyhedron_square_right_bottom = self.extrude_frame(
            frame_square_right_bottom, "frame_square"
        )

        # Test function to changes position
        # TODO sacar
        # polyhedron_square_left_top, polyhedron_square_right_top, polyhedron_square_left_bottom, polyhedron_square_right_bottom = self.create_premarc_optionals_elements_test()

        ## Escuadras
        squares = []
        original_squares = []
        match self.build_ele.ComboBoxEscuadras.value:
            case "NO":
                print("Escuadra Selected NO")
            case "2":
                print("Escuadra Selected 2 de arriba")
                original_squares.append(polyhedron_square_left_top)
                original_squares.append(polyhedron_square_right_top)
            case "4":
                print("Escuadra Selected 4 (2 arriba y 2 abajo)")
                original_squares.append(polyhedron_square_left_top)
                original_squares.append(polyhedron_square_right_top)
                original_squares.append(polyhedron_square_left_bottom)
                original_squares.append(polyhedron_square_right_bottom)
            case _:
                print("Escuadra Selected default")

        # Move squares to the correct position
        # Rules:
        # - Si fondo premarco == grosor pared, en el centro
        # - Si fondo premarco > grosor pared, en el final de la pared

        if self.thickness_premarc == self.build_ele.thickness_wall.value:
            vector_move = AllplanGeo.Vector3D(0, -LENGTH_CENTER_FOR_WALL, 0)
        elif self.thickness_premarc > self.build_ele.thickness_wall.value:
            vector_move = AllplanGeo.Vector3D(
                0, -(self.thickness_premarc - self.build_ele.thickness_wall.value), 0
            )
        else:
            vector_move = AllplanGeo.Vector3D(0, 0, 0)

        squares_moved = []
        for square in original_squares:
            # square.Move(vector_move)
            elem_moved = AllplanGeo.Move(square, vector_move)
            squares_moved.append(elem_moved)

        squares = squares_moved

        # Manage Open Premarc for squares
        # Rule: remove squares related to open sides (right or left)
        print("Manage Open Premarc in optionals elements (squares - Escuadras)")
        match self.build_ele.ComboBoxAbiertoCerrado.value:
            case (
                "OBERT PER DALT"
                | "OBERT PER DALT + REA"
                | "OBERT PER DALT + REA VARIANT"
            ):
                top_squares = (
                    polyhedron_square_left_top,
                    polyhedron_square_right_top,
                )
                for original_square, moved_square in zip(original_squares, squares_moved):
                    if original_square in top_squares:
                        try:
                            squares.remove(moved_square)
                        except ValueError:
                            print(f"Error in remove polyhedron square: {moved_square}")
            case (
                "OBERT PER BAIX"
                | "OBERT PER BAIX + REA"
                | "OBERT PER BAIX + REA VARIANT"
            ):
                bottom_squares = (
                    polyhedron_square_left_bottom,
                    polyhedron_square_right_bottom,
                )
                for original_square, moved_square in zip(original_squares, squares_moved):
                    if original_square in bottom_squares:
                        try:
                            squares.remove(moved_square)
                        except ValueError:
                            print(f"Error in remove polyhedron square: {moved_square}")
            case "OBERT FEMELLA DRETA":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT FEMELLA ESQUERRA":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT FEMELLA DRETA + REA":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT FEMELLA ESQUERRA + REA":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT NO FEMELLA DRETA":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT NO FEMELLA ESQUERRA":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT NO FEMELLA DRETA + REA":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "OBERT NO FEMELLA ESQUERRA + REA":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. FEMELLA / INF NO FEMELLA DRET.":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. FEMELLA / INF NO FEMELLA ESQ.":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. FEMELLA / INF NO FEMELLA DRET. + REA":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. FEMELLA / INF NO FEMELLA ESQ. + REA":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. NO FEMELLA / INF. FEMELLA DRET.":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. NO FEMELLA / INF. FEMELLA ESQ.":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. NO FEMELLA / INF. FEMELLA DRET. + REA":
                for square in (
                    polyhedron_square_right_top,
                    polyhedron_square_right_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case "SUP. NO FEMELLA / INF. FEMELLA ESQ. + REA":
                for square in (
                    polyhedron_square_left_top,
                    polyhedron_square_left_bottom,
                ):
                    try:
                        squares.remove(square)
                    except ValueError:
                        print(f"Error in remove polyhedron square: {square}")
            case _:
                print("Selected default")

        print(f"\n\n")

        ## Tubos
        vertical_tubs = []
        horizontal_tubs = []
        match self.build_ele.ComboBoxTubos.value:
            case "NO":
                print("Tubo Selected NO")
            case "1 VERT.":
                print("Tubo Selected 1")
                polyhedron_tubs = self.create_tubs_proportioned(1, VERTICAL_TUB)
                vertical_tubs.extend(polyhedron_tubs)
                # other_elements.extend(polyhedron_tubs)
            case "2 VERT.":
                print("Tubo Selected 2")
                polyhedron_tubs = self.create_tubs_proportioned(2, VERTICAL_TUB)
                vertical_tubs.extend(polyhedron_tubs)
                # other_elements.extend(polyhedron_tubs)
            case "3 VERT.":
                print("Tubo Selected 3")
                polyhedron_tubs = self.create_tubs_proportioned(3, VERTICAL_TUB)
                vertical_tubs.extend(polyhedron_tubs)
                # other_elements.extend(polyhedron_tubs)
            case "4 VERT.":
                print("Tubo Selected 4")
                polyhedron_tubs = self.create_tubs_proportioned(4, VERTICAL_TUB)
                vertical_tubs.extend(polyhedron_tubs)
                # other_elements.extend(polyhedron_tubs)
            case "1 HORIT.":
                print("Tubo Selected 1 horizontal")
                polyhedron_tubs = self.create_tubs_proportioned(1, HORIZONTAL_TUB)
                horizontal_tubs.extend(polyhedron_tubs)
                # other_elements.extend(polyhedron_tubs)
            case "2 HORITZ.":
                print("Tubo Selected 2 horizontal")
                polyhedron_tubs = self.create_tubs_proportioned(2, HORIZONTAL_TUB)
                horizontal_tubs.extend(polyhedron_tubs)
                # other_elements.extend(polyhedron_tubs)
            case _:
                print("Tubo Selected default")

        # Posicionamiento de tubos en Y
        if self.build_ele.PositionTubos.value == "OFFSET":
            vector_move_tubs = AllplanGeo.Vector3D(
                0, self.build_ele.OffsetTubos.value, 0
            )
            vertical_tubs = [
                AllplanGeo.Move(t, vector_move_tubs) for t in vertical_tubs
            ]
            horizontal_tubs = [
                AllplanGeo.Move(t, vector_move_tubs) for t in horizontal_tubs
            ]

        ## Encajes
        polyhedron_socket = None
        match self.build_ele.ComboBoxEncajes.value:
            case "NO":
                print("Falca Selected NO")
                polyhedron_socket = None
            case "35*30":
                print("Falca Selected 35*30")
                self.socket_width = (
                    35 - 3
                )  # 32 compensa extrude, la medida es 35 medido de afuera.
                self.socket_height = (
                    30 - 3
                )  # 27  compensa extrude, la medida es 30 medido de afuera.

                polyedron_sockets = self.create_socket(
                    self.socket_width, self.socket_height
                )
                error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(
                    polyedron_sockets
                )
                self.prem_encaje = "35 * 30"
                self.prem_encaje_base = 35
                self.prem_encaje_altura = 30
            case "70*30":
                print("Falca Selected 70*30")
                self.socket_width = (
                    70 - 3
                )  # 68 compensa extrude, la medida es 70 medido de afuera.
                self.socket_height = (
                    30 - 3
                )  # 27  compensa extrude, la medida es 30 medido de afuera.

                polyedron_sockets = self.create_socket(
                    self.socket_width, self.socket_height
                )
                error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(
                    polyedron_sockets
                )
                self.prem_encaje = "70 * 30"
                self.prem_encaje_base = 70
                self.prem_encaje_altura = 30
            case "PLEC INFERIOR":
                print("Falca Selected PLEC INFERIOR")
            case _:
                print("Falca Selected default")

        # Manage manual encaje
        if (
            self.build_ele.EnableManualEncaje.value
            and self.build_ele.ComboBoxEncajes.value != "PLEC INFERIOR"
        ):
            print("Manual encaje Selected")
            socket_width = (
                self.build_ele.EncajeBase.value - 3
            )  # compensa extrude, la medida es medida de afuera.
            socket_height = (
                self.build_ele.EncajeAltura.value - 3
            )  # compensa extrude, la medida es medido de afuera.

            polyedron_sockets = self.create_socket(socket_width, socket_height)
            error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(
                polyedron_sockets
            )
            self.prem_encaje = f"{socket_width} * {socket_height}"
            self.prem_encaje_base = self.build_ele.EncajeBase.value
            self.prem_encaje_altura = self.build_ele.EncajeAltura.value
        else:
            print("Manual encaje Selected NO")

        #### Pendiente
        # Manage pendent only in socket (Encaje)

        ### Encajes
        # self.socket_width = 32 # compensa extrude, la medida es 35 medido de afuera.
        # self.socket_height = 27 # compensa extrude, la medida es 30 medido de afuera.

        # polyedron_sockets = self.create_socket(self.socket_width, self.socket_height)
        # error_code_socket, polyhedron_socket = AllplanGeo.MakeUnion(polyedron_sockets)

        pendent_selected = self.build_ele.ComboBoxPendiente.value
        FIX_HEIGHT_SOCKET = 7.5  # Defaul to 295 mm thickness
        if self.thickness_premarc == 160:
            FIX_HEIGHT_SOCKET = 5.60
        match pendent_selected:
            # case "NO":
            #     print("Pendent Selected NO")
            case "SI":
                print("Pendent Selected SI - Manage only in socket")
                if polyhedron_socket:
                    # fix position socket
                    count_socket = 0
                    print(f"Count socket: {count_socket}")

                    translation_vector = AllplanGeo.Vector3D(0, 0, FIX_HEIGHT_SOCKET)
                    polyhedron_socket = AllplanGeo.Move(
                        polyhedron_socket, translation_vector
                    )
                    # try:

                    #     # other_elements.append(polyhedron_socket_fix)
                    #     # other_elements.remove(polyhedron_socket)
                    # except ValueError:
                    #     print("Error in remove polyhedron socket")
                    #     pass
                # if polyhedron_fold_with_fillet_moved in polyhedron_premarc_list:
                #     try:
                #         polyhedron_premarc_list.append(rotated_polyhedron_fold_with_fillet_moved)
                #         polyhedron_premarc_list.remove(polyhedron_fold_with_fillet_moved)
                #     except ValueError:
                #         print("Error in remove polyhedron fold with fillet moved")
                #         pass
            case _:
                print("Pendent Selected default")

        # Falcas
        TOP_FALCAS = False
        BOTTOM_FALCAS = False

        available_width = self.width - (OFFSET_FALCA * 2)
        max_falcas = int(available_width / DISTANCE_BETWEEN_FALCAS)
        polyhedron_top_falcas = []
        polyhedron_bottom_falcas = []
        if max_falcas > 0:
            total_falcas_width = max_falcas * DISTANCE_BETWEEN_FALCAS
            adjusted_offset = (self.width - total_falcas_width) / 2
            # adjusted_offset = OFFSET_FALCA + remaining_space / 2
        else:
            adjusted_offset = OFFSET_FALCA
            max_falcas = 0

        # Top Falcas
        y_position_top_falcas = -(self.thickness - THICKNESS_MM - THICKNESS_FALCA)
        if self.build_ele.ComboBoxPersianas.value == "METALUNIC VIST":
            y_position_top_falcas = -(self.detected_wall_thickness + self.build_ele.PersianaWidth.value)
        for i in range(max_falcas+1):
            falca = self.create_origin_falca_top()
            translation_vector = AllplanGeo.Vector3D(
                adjusted_offset + DISTANCE_BETWEEN_FALCAS * i - THICKNESS_MM / 2,
                y_position_top_falcas,
                0
            )
            falca_moved = AllplanGeo.Move(falca, translation_vector)
            error_code, polyhedron_falca = self.extrude_frame(
                falca_moved, "frame_falca"
            )
            polyhedron_top_falcas.append(polyhedron_falca)

        # Bottom Falcas
        for i in range(max_falcas + 1):
            falca = self.create_origin_falca_bottom()
            translation_vector = AllplanGeo.Vector3D(
                adjusted_offset + DISTANCE_BETWEEN_FALCAS * i - THICKNESS_MM / 2,
                -(self.thickness - THICKNESS_MM - THICKNESS_FALCA),
                -(self.heigh + THICKNESS_MM),
            )
            falca_moved = AllplanGeo.Move(falca, translation_vector)
            error_code, polyhedron_falca = self.extrude_frame(
                falca_moved, "frame_falca"
            )
            polyhedron_bottom_falcas.append(polyhedron_falca)

        # Manage CheckBox Falcas
        falcas_selected = self.read_checkbox_falcas()
        falcas = []
        if "PASSAMÀ FALCA SUP.(LAMISOL/METAL.)" in falcas_selected:
            TOP_FALCAS = True
            # other_elements.extend(polyhedron_top_falcas)
            falcas.extend(polyhedron_top_falcas)
        if "PASSAMÀ FALCA INF. (+ de 4 m)" in falcas_selected:
            BOTTOM_FALCAS = True
            # other_elements.extend(polyhedron_bottom_falcas)
            falcas.extend(polyhedron_bottom_falcas)
        if "PASSAMÀ FALCA SUP./INF. (+ de 6m)" in falcas_selected:
            if TOP_FALCAS and BOTTOM_FALCAS:
                print("nothing to add")
            if TOP_FALCAS and not BOTTOM_FALCAS:
                # other_elements.extend(polyhedron_bottom_falcas)
                falcas.extend(polyhedron_bottom_falcas)
            if not TOP_FALCAS and BOTTOM_FALCAS:
                # other_elements.extend(polyhedron_top_falcas)
                falcas.extend(polyhedron_top_falcas)
            if not TOP_FALCAS and not BOTTOM_FALCAS:
                # other_elements.extend(polyhedron_top_falcas)
                falcas.extend(polyhedron_top_falcas)
                # other_elements.extend(polyhedron_bottom_falcas)
                falcas.extend(polyhedron_bottom_falcas)

        return (
            other_elements,
            squares,
            vertical_tubs,
            horizontal_tubs,
            falcas,
            polyhedron_socket,
        )

    def read_checkbox_falcas(self):
        lista_passama = self.build_ele.valueListaPassama.value
        opciones_seleccionadas = self.build_ele.PassamaOptions.value
        list_checkbox_falcas = []
        # PASSAMÀ FALCA INF. (+ de 4 m)
        # PASSAMÀ FALCA SUP./INF. (+ de 6m)

        try:
            indice = lista_passama.index("PASSAMÀ FALCA SUP.(LAMISOL/METAL.)")
            esta_seleccionado = opciones_seleccionadas[indice]

            if esta_seleccionado:
                print("PASSAMÀ FALCA SUP.(LAMISOL/METAL.) está seleccionado")
                list_checkbox_falcas.append("PASSAMÀ FALCA SUP.(LAMISOL/METAL.)")

        except ValueError:
            print("PASSAMÀ FALCA SUP.(LAMISOL/METAL.) no se encontró en la lista")
        except IndexError:
            print("PASSAMÀ FALCA SUP.(LAMISOL/METAL.) no se encontró en la lista")

        try:
            indice = lista_passama.index("PASSAMÀ FALCA INF. (+ de 4 m)")
            esta_seleccionado = opciones_seleccionadas[indice]

            if esta_seleccionado:
                print("PASSAMÀ FALCA INF. (+ de 4 m)")
                list_checkbox_falcas.append("PASSAMÀ FALCA INF. (+ de 4 m)")

        except ValueError:
            print("PASSAMÀ FALCA INF. (+ de 4 m) no se encontró en la lista")
        except IndexError:
            print("PASSAMÀ FALCA INF. (+ de 4 m) no se encontró en la lista")

        try:
            indice = lista_passama.index("PASSAMÀ FALCA SUP./INF. (+ de 6m)")
            esta_seleccionado = opciones_seleccionadas[indice]

            if esta_seleccionado:
                print("PASSAMÀ FALCA SUP./INF. (+ de 6m)")
                list_checkbox_falcas.append("PASSAMÀ FALCA SUP./INF. (+ de 6m)")

        except ValueError:
            print("PASSAMÀ FALCA SUP./INF. (+ de 6m) no se encontró en la lista")
        except IndexError:
            print("PASSAMÀ FALCA SUP./INF. (+ de 6m) no se encontró en la lista")

        return list_checkbox_falcas

    def create_perpendicular_union(self, polyhedron_fold_bottom, polyhedron_fold_top):
        try:
            # Definir el radio del fillet (ajusta según necesites)
            fillet_radius = 5.0  # mm - puedes hacerlo configurable

            # Crear un sólido de unión perpendicular
            # Este será un pequeño cilindro o prisma que conecte ambos sólidos
            union_height = FOLD_SPACING_MM  # La distancia entre los pliegues
            union_width = FOLD_WIDTH_MM  # El ancho del pliegue

            # Crear el polígono de la unión perpendicular
            union_polygon = AllplanGeo.Polygon3D()
            union_polygon += AllplanGeo.Point3D(
                0, -(self.thickness - FOLD_WIDTH_MM), -(self.heigh + THICKNESS_MM)
            )  # Punto de conexión inferior
            union_polygon += AllplanGeo.Point3D(
                0,
                -(self.thickness - FOLD_WIDTH_MM),
                -(self.heigh - FOLD_SPACING_MM - THICKNESS_MM),
            )  # Punto de conexión superior
            union_polygon += AllplanGeo.Point3D(
                self.width,
                -(self.thickness - FOLD_WIDTH_MM),
                -(self.heigh - FOLD_SPACING_MM - THICKNESS_MM),
            )  # Punto superior derecho
            union_polygon += AllplanGeo.Point3D(
                self.width,
                -(self.thickness - FOLD_WIDTH_MM),
                -(self.heigh + THICKNESS_MM),
            )  # Punto inferior derecho
            union_polygon += AllplanGeo.Point3D(
                0, -(self.thickness - FOLD_WIDTH_MM), -(self.heigh + THICKNESS_MM)
            )  # Cerrar polígono

            # Extruir la unión perpendicular
            error_code, polyhedron_union = self.extrude_frame(
                union_polygon, "perpendicular_union"
            )

            # return True, polyhedron_union
            polyhedron_list = [
                polyhedron_fold_bottom,
                polyhedron_union,
                polyhedron_fold_top,
            ]
            polyhedron_list = AllplanGeo.Polyhedron3DList()
            polyhedron_list.append(polyhedron_fold_bottom)
            polyhedron_list.append(polyhedron_union)
            polyhedron_list.append(polyhedron_fold_top)

            success, polyhedron_list_union = AllplanGeo.MakeUnion(polyhedron_list)

            return True, polyhedron_list_union
            external_edges = AllplanUtil.VecSizeTList([1, 23])

            # Apply external edges fillet
            error1, first_filleted = AllplanGeo.FilletCalculus3D.Calculate(
                polyhedron_list_union, external_edges, radius=2, propagation=False
            )

            # Apply internal edges fillet
            internal_edges = AllplanUtil.VecSizeTList([10, 11])
            error2, second_filleted = AllplanGeo.FilletCalculus3D.Calculate(
                first_filleted, internal_edges, radius=0.5, propagation=False
            )

            if (
                error1 == AllplanGeo.eFilletErrorCode.eNO_ERROR
                and error2 == AllplanGeo.eFilletErrorCode.eNO_ERROR
            ):
                print("Unión perpendicular con fillet creada exitosamente")
                return True, second_filleted
            else:
                print(f"Error aplicando fillet a la unión: {error1} {error2}")
                return True, polyhedron_list_union  # Retornar sin fillet si hay error

        except Exception as e:
            print(f"Error en create_perpendicular_union: {e}")
            return False, None

    def create_premarc_window(self):
        pos_bottom_frame = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        pos_top_frame = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, 0, self.heigh - 63)
        )
        pos_left_frame = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        pos_right_frame = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(self.width - 63, 0, 0)
        )

        cuboid_bottom_frame = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_bottom_frame, self.width, 63, 63
        )
        cuboid_top_frame = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top_frame, self.width, 63, 63
        )
        cuboid_left_frame = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_left_frame, 63, 63, self.heigh
        )
        cuboid_right_frame = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_right_frame, 63, 63, self.heigh
        )

        pos_bottom1 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(63, 0, self.heigh / 2)
        )
        pos_top1 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(63, 0, self.heigh - (63 * 2))
        )
        pos_left1 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(63, 0, self.heigh / 2)
        )
        pos_right1 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D((self.width / 2) - 63, 0, self.heigh / 2)
        )

        cuboid_bottom1 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_bottom1, (self.width / 2) - 63, 63, 63
        )
        cuboid_top1 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top1, (self.width / 2) - 63, 63, 63
        )
        cuboid_left1 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_left1, 63, 63, self.heigh / 2
        )
        cuboid_right1 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_right1, 63, 63, self.heigh / 2
        )

        pos_bottom2 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(self.width / 2, 0, self.heigh / 2)
        )
        pos_top2 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(self.width / 2, 0, self.heigh - (63 * 2))
        )
        pos_left2 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(self.width / 2, 0, self.heigh / 2)
        )
        pos_right2 = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(self.width - (63 * 2), 0, self.heigh / 2)
        )

        cuboid_bottom2 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_bottom2, (self.width / 2) - 63, 63, 63
        )
        cuboid_top2 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top2, (self.width / 2) - 63, 63, 63
        )
        cuboid_left2 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_left2, 63, 63, self.heigh / 2
        )
        cuboid_right2 = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_right2, 63, 63, self.heigh / 2
        )

        cuboid2d = AllplanGeo.Polygon2D.CreateRectangle(
            AllplanGeo.Point2D(0, -63), AllplanGeo.Point2D(self.width, 0)
        )
        cuboid2d = AllplanGeo.Move(
            cuboid2d, AllplanGeo.Vector2D(0, -self.thickness + 63)
        )

        line1 = AllplanGeo.Line2D(
            AllplanGeo.Point2D(63, -63),
            AllplanGeo.Point2D(63, -((self.width / 2) + 63)),
        )
        line1 = AllplanGeo.Move(line1, AllplanGeo.Vector2D(0, -self.thickness + 63))

        line2 = AllplanGeo.Line2D(
            AllplanGeo.Point2D(self.width - 63, -63),
            AllplanGeo.Point2D(self.width - 63, -((self.width / 2) + 63)),
        )
        line2 = AllplanGeo.Move(line2, AllplanGeo.Vector2D(0, -self.thickness + 63))

        arc1 = AllplanGeo.Arc2D(
            AllplanGeo.Point2D(63, -63),
            (self.width / 2) - 63,
            (self.width / 2) - 63,
            0,
            180,
            270,
            True,
        )
        arc1 = AllplanGeo.Move(arc1, AllplanGeo.Vector2D(0, -self.thickness + 63))

        arc2 = AllplanGeo.Arc2D(
            AllplanGeo.Point2D(self.width - 63, -63),
            (self.width / 2) - 63,
            (self.width / 2) - 63,
            0,
            90,
            180,
            True,
        )
        arc2 = AllplanGeo.Move(arc2, AllplanGeo.Vector2D(0, -self.thickness + 63))

        elems = [
            cuboid_bottom_frame,
            cuboid_top_frame,
            cuboid_left_frame,
            cuboid_right_frame,
            cuboid_bottom1,
            cuboid_top1,
            cuboid_left1,
            cuboid_right1,
            cuboid_bottom2,
            cuboid_top2,
            cuboid_left2,
            cuboid_right2,
        ]

        final_result = []
        union = True
        prev = elems[0]
        for i in range(1, len(elems)):
            ok, union = AllplanGeo.MakeUnion(prev, elems[i])
            if ok is not AllplanGeo.eGeometryErrorCode.eOK:
                final_result = elems
                union = False
                break
            else:
                prev = union

        if union:
            prev = AllplanGeo.Move(
                prev, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
            )
            final_result.append(prev)

        elems_2d = [cuboid2d, line1, line2, arc1, arc2]

        # elems_2d = []

        return final_result, elems_2d

    def create_premarc_mosquitera(self):
        pos_bottom_frame = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, 63, self.socket_height)
        )
        cuboid_mosq = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_bottom_frame, self.width, 3, self.heigh - self.socket_height
        )
        cuboid_mosq = AllplanGeo.Move(
            cuboid_mosq, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        )
        return [cuboid_mosq]

    def _effective_socket_width_mm(self) -> float:
        # Mirror the encaje match block (~5771-5810). Manual encaje takes
        # priority unless PLEC INFERIOR is selected. The -3 compensates for
        # the extrude that fattens the polygon, so the OUTER measurement
        # matches the palette value.
        combo = self.build_ele.ComboBoxEncajes.value
        if self.build_ele.EnableManualEncaje.value and combo != "PLEC INFERIOR":
            return max(0.0, float(self.build_ele.EncajeBase.value or 0) - 3.0)
        if combo == "35*30":
            return 32.0
        if combo == "70*30":
            return 67.0
        return 0.0

    def _effective_socket_height_mm(self) -> float:
        # Mirrors _effective_socket_width_mm for the Z axis. Needed because
        # the manual-encaje branch at ~L6139 reads EncajeAltura into LOCAL
        # vars and never writes self.socket_height — so callers that need
        # the real escalon height must use this helper instead.
        combo = self.build_ele.ComboBoxEncajes.value
        if self.build_ele.EnableManualEncaje.value and combo != "PLEC INFERIOR":
            return max(0.0, float(self.build_ele.EncajeAltura.value or 0) - 3.0)
        if combo in ("35*30", "70*30"):
            return 27.0
        return 0.0

    def _ampit_y_inner_local_mm(self) -> float:
        # Local Y position of the ampit slab INNER face (toward encaje).
        #
        # The encaje back wall polygon sits at y_local = socket_width but its
        # extrude direction in create_socket() is "socket_frame_front" which
        # extrudes +THICKNESS_MM=+3 mm in Y. So the encaje back wall's OUTER
        # face (the one we must clear) is at y_local = socket_width + 3 mm.
        # We then add 2 mm of architect-spec margin past that face. The 3 mm
        # baseline (= depth of marco interior cercano al back) extends the
        # ampit hasta la cara frontal del premarco cuando no hay encaje.
        #
        # When the imp is active, the imp rise sits in this gap at
        # y = sw + 3 with width = grosor_imp. The ampit inner face must stay
        # at least 0.5 mm past the rise's +Y face to remain visually distinct
        # in section views — so the margin expands when grosor_imp > 1.5 mm
        # (i.e., for Tela Asfàltica). Water-Stop and PVC keep the 2 mm margin.
        sw = self._effective_socket_width_mm()
        encaje_back_outer = sw + float(THICKNESS_MM) if sw > 0 else 0.0
        margin = max(2.0, self._grosor_imp_mm() + 0.5)
        return max(3.0, encaje_back_outer) + margin

    def _ampit_slab_outer_local_mm(self, spec: dict) -> float:
        # Local-Y position of the slab + lip OUTER face (= where the front
        # of the ampit ends, including any slab extension needed to keep
        # the 90° lip OUTSIDE the wall interior face).
        #
        # Rule:
        #   - No lip                     → slab_outer = thickness + baseline
        #   - grosor_tope > baseline+sobresaliente
        #     (lip would land INSIDE the wall — CERAMIC's case):
        #     → extend the slab so the lip back sits exactly `sobresaliente`
        #       mm PAST the wall face (the architect's "gap"):
        #       slab_outer = thickness + sobresaliente + grosor_tope
        #   - Otherwise (CERAMICA_MAYOR / XAPA): use the natural value:
        #     slab_outer = thickness + baseline + sobresaliente
        grosor_tope   = float(spec["grosor_tope"])
        sobresaliente = float(spec["sobresaliente"])
        baseline      = float(spec["baseline_protrusion"])
        tope          = float(spec["tope"])
        if tope <= 0 or grosor_tope <= 0 or sobresaliente <= 0:
            return float(self.thickness) + baseline
        if grosor_tope > baseline + sobresaliente:
            return float(self.thickness) + sobresaliente + grosor_tope
        return float(self.thickness) + baseline + sobresaliente

    def _ampit_fondo_3d_total_mm(self, spec: dict) -> float:
        # Total Y depth of the ampit material in 3D, from the slab inner
        # face to the slab + lip OUTER face. Excludes the 2 mm panel /
        # afegit joint gaps per screenshot 7's
        # "EL MARGEN DE 2MM ... NO SE TIENE EN CUENTA".
        slab_outer_local = self._ampit_slab_outer_local_mm(spec)
        fondo = slab_outer_local - self._ampit_y_inner_local_mm()
        if fondo < 0:
            fondo = 0.0
        return fondo

    def create_premarc_ampit(self):
        material = self.build_ele.ampit_material.value or "CERAMIC"
        spec = AMPIT_TYPE_SPECS.get(material, AMPIT_TYPE_SPECS["CERAMIC"])

        # Pavimento has explicit "no sobresale" rule, which conflicts with the
        # universal aplacat rule ("ampit must keep being built as if the base
        # were of standard length"). Per architects' literal-text directive,
        # skip drawing the ampit altogether in this combo.
        if material == "PAVIMENTO" and self.bottom_rebaje_enabled():
            print("[Premarc] PAVIMENTO ampit no compatible con REB. BAIX (no sobresale): ampit omitido.")
            return [], [], [], [], [], spec

        # Z base of the ampit slab. The bottom sheet thickness now extends
        # outward below the opening, so the clear opening bottom remains z=0
        # in premarc-local coordinates. Lift by grosor_imp only when
        # impermeabilizacion is active.
        z_base_ampit = self._grosor_imp_mm()

        # Encaje-aware slab inner Y (2 mm margin from the encaje back face,
        # or from the 63 mm front assembly when sin encaje / narrow encaje).
        y_inner_local = self._ampit_y_inner_local_mm()

        # Real 3D ampit depth = slab fondo + sobresaliente. The 2 mm lateral
        # and afegit-joint gaps are NOT counted here (screenshot 7 directive).
        fondo_3d = self._ampit_fondo_3d_total_mm(spec)

        diff = self.fondo_ampits - fondo_3d
        # retall when palette supplies MORE than the 3D needs (cut the excess);
        # afegit when palette supplies LESS than the 3D needs (add a panel).
        self.retall_ampits = max(diff, 0.0)
        self.afegit_ampits = max(-diff, 0.0)

        if not self.afegit_ampits_manual:
            self.build_ele.afegit_ampits.value = self.afegit_ampits
            # self.build_ele.INPUT_PMP_FG_AMPIT_AFEGIT.value = self.afegit_ampits

        if not self.retall_ampits_manual:
            self.build_ele.retall_ampits.value = self.retall_ampits
            # self.build_ele.INPUT_PMP_FG_AMPIT_RETALL.value = self.retall_ampits

        final_result_3d = []
        final_result_2d = []
        edge_fg = None
        edge_add = None

        # 2 mm clearances:
        #   - Outermost ends: 2 mm gap to the frame uprights (left and right).
        #   - Between panels: 2 mm gap (1 mm trimmed off each adjacent panel).
        # Panels stay equal length for any width: choose the smallest N such that
        #   N panels each <= llarg_ampits fit inside (width - 4) with (N-1) gaps of 2 mm,
        #   i.e. N >= (width - 2) / (llarg_ampits + 2).
        side_gap = 2.0
        inter_gap = 2.0
        # The 3 mm side sheet thickness extends OUTWARD into the concrete, so
        # the real opening remains bounded by x=0 and x=width. The ampit only
        # applies the architectural 2 mm side clearance from that opening.
        frame_inner_inset_x = 0.0
        usable = self.width - 2 * side_gap - 2 * frame_inner_inset_x
        n_panels = 0
        panel_length = 0.0
        if usable > 0 and self.llarg_ampits > 0:
            n_panels = max(1, int(math.ceil((self.width - 2 * frame_inner_inset_x - side_gap) / (self.llarg_ampits + inter_gap))))
            panel_length = (usable - inter_gap * (n_panels - 1)) / n_panels
            if panel_length <= 0:
                n_panels = 0
                panel_length = 0.0

        # Floor-plan footprint Y bounds (same for every panel):
        #   inner = y_inner_local (encaje-aware, 2 mm margin)
        #   outer = slab + lip OUTER face (same helper as 3D so the plan
        #           outline always matches what create_ampit actually builds,
        #           including the CERAMIC slab extension that keeps the
        #           90° lip past the wall face)
        outer_y_2d = self._ampit_slab_outer_local_mm(spec)

        for i in range(n_panels):
            x_start = frame_inner_inset_x + side_gap + i * (panel_length + inter_gap)
            x_end = x_start + panel_length
            if i == n_panels - 1:
                x_end = self.width - frame_inner_inset_x - side_gap
            current_length = x_end - x_start
            if (ampit := self.create_ampit(x_start, current_length, y_inner_local, spec)) is not None:
                ampit = AllplanGeo.Move(ampit, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))
                final_result_3d.append(ampit)
                cuboid2d = AllplanGeo.Polygon2D.CreateRectangle(
                    AllplanGeo.Point2D(x_start, y_inner_local),
                    AllplanGeo.Point2D(x_end, outer_y_2d),
                )
                cuboid2d = AllplanGeo.Move(cuboid2d, AllplanGeo.Vector2D(0,-self.thickness))
                final_result_2d.append(cuboid2d)

        edge_fg_list = []
        edge_add_list = []
        edge_add_cuboid_list = []
        if n_panels > 0:
            x_left_edge = frame_inner_inset_x + side_gap
            x_right_edge = self.width - frame_inner_inset_x - side_gap
            edge_fg = AllplanGeo.Line3D(
                AllplanGeo.Point3D(x_left_edge, self.thickness, z_base_ampit + float(spec["grosor"])),
                AllplanGeo.Point3D(x_right_edge, self.thickness, z_base_ampit + float(spec["grosor"])),
            )
            edge_fg = AllplanGeo.Move(edge_fg, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))
            edge_fg_list = [edge_fg]

            if self.afegit_ampits > 0:
                # Joint plane sits `afegit` mm past the slab inner face,
                # which itself is encaje-aware (y_inner_local).
                edge_add_y = self.afegit_ampits + y_inner_local
                edge_add = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(x_left_edge, edge_add_y, z_base_ampit + float(spec["grosor"])),
                    AllplanGeo.Point3D(x_right_edge, edge_add_y, z_base_ampit + float(spec["grosor"])),
                )
                edge_add = AllplanGeo.Move(edge_add, AllplanGeo.Vector3D(0,-self.thickness,-self.heigh))
                edge_add_list = [edge_add]

                # 2 mm physical joint cuboid co-located with edge_add: same X span,
                # Y centered on the joint plane, Z = ampit slab thickness (spec["grosor"]).
                # Height must match the ampit slab per material (XAPA=2, others=11) so the
                # cuboid never overshoots the ampit top — reported by Arnau on PR review.
                # Layer/color/attributes match edge_add (LAYER_AMPIT_EIX_AFEGIT) at the call site.
                # NOTE: this 2 mm gap is visualization only — it is NOT added or
                # subtracted in the retall/afegit math (screenshot 7 directive).
                joint_y_thickness = 2.0
                joint_pos = AllplanGeo.AxisPlacement3D(
                    AllplanGeo.Point3D(
                        x_left_edge,
                        edge_add_y - joint_y_thickness / 2,
                        z_base_ampit,
                    )
                )
                edge_add_cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
                    joint_pos,
                    x_right_edge - x_left_edge,
                    joint_y_thickness,
                    float(spec["grosor"]),
                )
                edge_add_cuboid = AllplanGeo.Move(
                    edge_add_cuboid, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
                )
                edge_add_cuboid_list = [edge_add_cuboid]

        self.retall_ampits_manual = False
        self.afegit_ampits_manual = False

        return final_result_3d, final_result_2d, edge_fg_list, edge_add_list, edge_add_cuboid_list, spec

    def create_ampit(self, init_x, llarg_ampit, y_inner_local, spec):
        # Geometry in local Y (pre-move). After the parent's move by
        # `-thickness`, local Y = `thickness` maps to the wall INTERIOR face
        # (final y = 0).
        #
        # Architect's spec interpretation:
        #   - grosor       : slab Z thickness
        #   - grosor_tope  : lip Y depth (chunky cross-section width)
        #   - tope         : lip TOTAL Z height (top of lip = slab top)
        #   - sobresaliente: the GAP between the wall interior face and the
        #                    lip BACK face (so the 90° lip stays past the
        #                    wall by `sobresaliente` mm)
        #   - baseline_protrusion: how far the slab natural outer sits past
        #                          the interior wall face when no slab
        #                          extension is needed
        #
        # The LIP geometry is kept as-is — chunky cuboid hanging from the
        # slab's front edge, grosor_tope wide in Y, lip OUTER face aligned
        # with the slab OUTER face. The protrusion is realized purely by
        # EXTENDING THE SLAB (in `_ampit_slab_outer_local_mm`) — only the
        # CERAMIC case actually needs the extension, the other materials
        # already have grosor_tope <= baseline + sobresaliente.
        #
        # Resulting geometry (final coords past the wall face):
        #   - CERAMIC:        slab y=[y_in, +35] z=[3,14]; lip y=[+5, +35] z=[-16,3]   (5 mm gap)
        #   - CERAMICA_MAYOR: slab y=[y_in, +24] z=[3,14]; lip y=[+10,+24] z=[-20,3]   (10 mm gap)
        #   - XAPA:           slab y=[y_in, +12] z=[3, 5]; lip y=[+10,+12] z=[-35,3]   (+6mm remate inward)
        #   - PAVIMENTO:      slab y=[y_in,  0] z=[3,14]; no lip
        grosor        = spec["grosor"]
        grosor_tope   = spec["grosor_tope"]
        tope          = spec["tope"]
        remate        = spec["remate"]

        # Z base lifted by grosor_imp when impermeabilizacion is enabled
        # (the ampit slab sits on top of the imp). With the bottom sheet
        # thickness outside the opening, the base is z=0 when imp is off.
        z_base_ampit = self._grosor_imp_mm()

        y_slab_in  = float(y_inner_local)
        # Slab outer comes from the single source-of-truth helper so the
        # 3D, 2D footprint, and retall/afegit math all agree.
        y_slab_out = self._ampit_slab_outer_local_mm(spec)

        slab_fondo = y_slab_out - y_slab_in
        if slab_fondo <= 0:
            return None  # encaje too deep for this premarco

        pos_top = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(init_x, y_slab_in, z_base_ampit))
        cuboid_top = AllplanGeo.Polyhedron3D.CreateCuboid(pos_top, llarg_ampit, slab_fondo, grosor)

        drop_height = float(tope) - float(grosor)
        if tope <= 0 or grosor_tope <= 0 or drop_height <= 0:
            return cuboid_top  # Pavimento (no lip)

        # Lip = chunky cuboid hanging from the slab front edge.
        #   Y: [y_slab_out - grosor_tope, y_slab_out]  (lip outer = slab outer)
        #   Z: [z_base_ampit - drop_height, z_base_ampit + overlap]
        #                                            (just below the slab;
        #                                             the above-slab portion
        #                                             is already part of slab)
        y_lip_inner = y_slab_out - float(grosor_tope)
        z_drop_top  = z_base_ampit            # slab bottom
        z_drop_bot  = z_drop_top - drop_height
        # Small +Z overlap (0.1 mm) into the slab so MakeUnion does not
        # drop the cuboid on exact face-to-face contact.
        union_overlap = 0.1
        pos_front = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(init_x, y_lip_inner, z_drop_bot)
        )
        cuboid_front = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_front, llarg_ampit, float(grosor_tope), drop_height + union_overlap
        )

        ok, union = AllplanGeo.MakeUnion(cuboid_top, cuboid_front)
        if ok is not AllplanGeo.eGeometryErrorCode.eOK:
            return None

        if remate > 0:
            # XAPA-only horizontal return at the BOTTOM of the lip going
            # INWARD (back toward the wall). Z thickness = grosor_tope
            # (sheet-metal thickness for XAPA = 2 mm).
            remate_overlap = 0.1
            pos_remate = AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(init_x, y_lip_inner - remate, z_drop_bot)
            )
            cuboid_remate = AllplanGeo.Polyhedron3D.CreateCuboid(
                pos_remate, llarg_ampit, remate + remate_overlap, float(grosor_tope)
            )
            ok_r, union_r = AllplanGeo.MakeUnion(union, cuboid_remate)
            if ok_r is AllplanGeo.eGeometryErrorCode.eOK:
                union = union_r

        return union

    def _grosor_imp_mm(self):
        """Z thickness of the active impermeabilizacio in mm (0 if disabled).

        Used by the ampit code to lift Z by `grosor_imp` so the ampit sits on
        top of the imp instead of clashing with it.
        """
        if not self.build_ele.EnableImpermeabilizacio.value:
            return 0.0
        spec = IMPERM_TYPE_SPECS.get(
            self.build_ele.imperm_type.value, IMPERM_TYPE_SPECS["Water-Stop"]
        )
        return float(spec["grosor"])

    def _resolve_imperm_model(self):
        """Pick the imp 3D model. Priority: bandeja_U > sobre_encaje > pliegue_90 > plano_recto.

        Encaje detection ORs EnableManualEncaje with the combo value so the
        combo's default literal 'Encajes' (API-offline fallback) does not
        block the sobre_encaje model when the user has a manual encaje set.
        """
        if self.build_ele.ShowAccessorUPerimeter.value:
            return "con_bandeja_U"
        has_encaje = (
            self.build_ele.EnableManualEncaje.value
            or self.build_ele.ComboBoxEncajes.value not in ("Encajes", "")
        )
        if has_encaje:
            return "sobre_encaje"
        if self.build_ele.EnableImpermPliegue90.value:
            return "pliegue_90"
        return "plano_recto"

    def _resolve_imperm_detail(self, imperm_type, model):
        """Detail code per Arnau's spec table (ASF-1/2, WS-1/2, PVC-1/2/3).

        Tela Asfaltica:   ASF-1 (encaje)        | ASF-2 (pliegue 90)
        Water-Stop:       WS-1 (encaje, fondo_premarco > grosor_pared)
                          WS-2 (encaje, fondo_premarco == grosor_pared)
        PVC:              PVC-1 (pliegue 90)    | PVC-2 (encaje)
                          PVC-3 (base plana)

        Returns "" when the combination is outside the spec (caller can
        decide whether to skip writing the attribute or warn).
        """
        if imperm_type == "Tela Asfàltica":
            if model == "sobre_encaje":
                return "ASF-1"
            if model == "pliegue_90":
                return "ASF-2"
            return ""

        if imperm_type == "Water-Stop":
            if model == "sobre_encaje":
                grosor_premarc = float(self.thickness_premarc or 0)
                grosor_pared = float(self.detected_wall_thickness or 0)
                if grosor_premarc > grosor_pared:
                    return "WS-1"
                if grosor_premarc == grosor_pared:
                    return "WS-2"
                # fondo_premarco < grosor_pared: not in Arnau's table — fall
                # back to WS-2 (closest geometric case) until clarified.
                return "WS-2"
            return ""

        if imperm_type == "PVC":
            if model == "pliegue_90":
                return "PVC-1"
            if model == "sobre_encaje":
                return "PVC-2"
            if model == "plano_recto":
                return "PVC-3"
            return ""

        return ""

    def create_impermeabilitzacio(self):
        spec = IMPERM_TYPE_SPECS.get(
            self.build_ele.imperm_type.value, IMPERM_TYPE_SPECS["Water-Stop"]
        )
        grosor = float(spec["grosor"])
        model = self._resolve_imperm_model()

        if model == "con_bandeja_U":
            return self._imperm_con_bandeja_U(grosor)
        if model == "sobre_encaje":
            return self._imperm_sobre_encaje(grosor)
        if model == "pliegue_90":
            return self._imperm_pliegue_90(grosor)
        return self._imperm_plano_recto(grosor)

    def _imperm_plano_recto(self, grosor):
        """Horizontal slab covering the wall top — no folds."""
        pos = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        imperm = AllplanGeo.Polyhedron3D.CreateCuboid(pos, self.width, self.thickness, grosor)
        imperm = AllplanGeo.Move(imperm, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
        return [imperm]

    def _imperm_pliegue_90(self, grosor):
        """Horizontal slab + an UPWARD 90° flap at the encaje-side end.

        Per Arnau feedback 2026-06-10: the 90° fold goes UP from the top of
        the slab, on the INNER end of the premarco (Y=0), which is the zone
        where the encaje step lands when the encaje is activated. The first
        attempt placed the flap on the exterior (Y=thickness) — wrong side.
        """
        PLIEGUE_LARGO_MM = 50.0
        pos_top = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        pos_pliegue = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, 0, grosor)
        )
        imperm_top = AllplanGeo.Polyhedron3D.CreateCuboid(pos_top, self.width, self.thickness, grosor)
        imperm_pliegue = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_pliegue, self.width, grosor, PLIEGUE_LARGO_MM
        )
        err, union = AllplanGeo.MakeUnion(imperm_top, imperm_pliegue)
        if err == AllplanGeo.eGeometryErrorCode.eOK:
            imperm = AllplanGeo.Move(union, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
            return [imperm]
        imperm_top = AllplanGeo.Move(imperm_top, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
        imperm_pliegue = AllplanGeo.Move(imperm_pliegue, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
        return [imperm_top, imperm_pliegue]

    def _imperm_sobre_encaje(self, grosor):
        """Z-step with the rise sitting in the 2 mm air gap between the encaje
        back wall extrusion and the ampit slab inner face — the rise touches
        the encaje back wall outer face, leaving (2 - grosor) mm between the
        rise's +Y face and the ampit inner face so the two are visually
        distinct in section views.

        Uses _effective_socket_*_mm helpers (not self.socket_*) because the
        manual-encaje branch never updates self.socket_* — those would stay
        at the 30/30 defaults and produce a phantom step in the wrong place.
        """
        sock_w = self._effective_socket_width_mm()
        sock_h = self._effective_socket_height_mm()
        if sock_w <= 0 or sock_h <= 0:
            # No real encaje geometry → fall back to a plain slab.
            return self._imperm_plano_recto(grosor)

        y_rise = sock_w + float(THICKNESS_MM)  # encaje back wall outer face

        pos_bottom = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, y_rise, 0))
        # Rise spans the full Z height from wall top to top-slab body top so
        # volumes overlap with both slabs — MakeUnion needs volume overlap,
        # not just face contact, to fuse the pieces into one polyhedron.
        pos_rise = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, y_rise, 0))
        # Encaje TOP face is at local Z = sock_h. The top slab BOTTOM face
        # sits at the encaje top, body extending `grosor` upward.
        # Top slab Y starts at Y=0 (flush with encaje exterior face); the
        # previous -grosor overhang was a "drip lip" Arnau rejected on
        # 2026-06-17 — must stay al ras with the encaje right edge.
        pos_top = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, 0, sock_h)
        )

        imperm_bottom = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_bottom, self.width, self.thickness - y_rise, grosor
        )
        imperm_rise = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_rise, self.width, grosor, sock_h + grosor
        )
        imperm_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top, self.width, y_rise + grosor, grosor
        )

        err, union = AllplanGeo.MakeUnion(imperm_bottom, imperm_rise)
        if err == AllplanGeo.eGeometryErrorCode.eOK:
            err, union = AllplanGeo.MakeUnion(union, imperm_top)
            if err == AllplanGeo.eGeometryErrorCode.eOK:
                imperm = AllplanGeo.Move(union, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
                return [imperm]

        imperm_bottom = AllplanGeo.Move(imperm_bottom, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
        imperm_rise = AllplanGeo.Move(imperm_rise, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
        imperm_top = AllplanGeo.Move(imperm_top, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
        return [imperm_bottom, imperm_rise, imperm_top]

    def _imperm_con_bandeja_U(self, grosor):
        """Extended slab + vertical rise on the outer face of the U.

        Per Arnau feedback 2026-06-10 (final iteration): same rule as for
        pliegue_90 — "los 90º se hacen arriba". The vertical leg on the
        outer face of the U rises UP from the slab top (not down).

        U profile geometry (constants from the top of the file):
          - U_OVERHANG_Y_MM = 24 (how far the U hangs past the wall exterior)
          - U_LEG_HEIGHT_MM = 30 (Z height of the U — used as rise length)
        """
        U_DEPTH = float(U_OVERHANG_Y_MM)        # 24
        U_RISE_HEIGHT = float(U_LEG_HEIGHT_MM)  # 30 — rise matches U height

        # 1. Slab extending from the U outer face (Y_pre = -U_DEPTH) all the
        # way to the interior wall face (Y_pre = thickness).
        slab_y_start = -U_DEPTH
        slab_y_span = U_DEPTH + self.thickness
        pos_top = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, slab_y_start, 0)
        )
        imperm_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top, self.width, slab_y_span, grosor
        )

        # 2. Vertical RISE on the OUTER face of the U (Y_pre = -U_DEPTH).
        # Starts at the top of the slab and rises upward.
        pos_rise = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, -U_DEPTH, grosor)
        )
        imperm_rise = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_rise, self.width, grosor, U_RISE_HEIGHT
        )

        pieces = [imperm_top, imperm_rise]
        union = pieces[0]
        union_ok = True
        for p in pieces[1:]:
            err, union = AllplanGeo.MakeUnion(union, p)
            if err != AllplanGeo.eGeometryErrorCode.eOK:
                union_ok = False
                break

        if union_ok:
            return [AllplanGeo.Move(
                union, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
            )]

        return [
            AllplanGeo.Move(p, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh))
            for p in pieces
        ]

    def create_real_inside_space(self):
        position = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, -1, -self.heigh))
        poly_inside_space = AllplanGeo.Polyhedron3D.CreateCuboid(
            position, self.width, 1, self.heigh
        )

        options = ["MONOBLOCK OCULT", "LAMISOL VIST", "METALUNIC VIST", "FALS CALAIX"]

        box_shutter = (
            True if self.build_ele.ComboBoxPersianas.value in options else False
        )

        has_pendiente = self.build_ele.ComboBoxPendiente.value == "SI"

        pendiente_offset = 0 if has_pendiente else 0  # Check codig of pendent
        shutter_offset = 263 if box_shutter else 0

        z_position = self.heigh + pendiente_offset
        z_offset = self.heigh + pendiente_offset + shutter_offset

        if not has_pendiente and not box_shutter:
            print("nothing to do")

        position = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, -1, -z_position))
        poly_real_space = AllplanGeo.Polyhedron3D.CreateCuboid(
            position, self.width, 1, z_offset
        )

        if not self.build_ele.CheckBoxRealSpace.value:
            poly_real_space = None

        if not self.build_ele.CheckBoxInnerSpace.value:
            poly_inside_space = None

        return poly_inside_space, poly_real_space

    def create_retall_representation(self):
        Z_position = (
            0
            if self.build_ele.Z_RetallGanxo.value < self.heigh
            else (self.heigh / 2) - 50
        )
        pos_left = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(-THICKNESS_MM, 40, Z_position)
        )

        cuboid_retall = AllplanGeo.Polyhedron3D.CreateCuboid(pos_left, 3, 80, 100)
        Z_move = (
            self.build_ele.Z_RetallGanxo.value + 100.0
            if self.build_ele.Z_RetallGanxo.value < self.heigh
            else self.heigh
        )
        cuboid_retall_origin = AllplanGeo.Move(
            cuboid_retall, AllplanGeo.Vector3D(0, -160, -Z_move)
        )
        # cuboid_retall_origin = AllplanGeo.Move(cuboid_retall, AllplanGeo.Vector3D(0, -160, -self.heigh))
        vector_move_right = AllplanGeo.Vector3D(self.width + THICKNESS_MM, 0, 0)
        if self.build_ele.EnableRetallGanxo.value and self.get_direction_retall_ganxo():
            if self.get_direction_retall_ganxo() == "RIGHT":
                cuboid_retall = AllplanGeo.Move(cuboid_retall_origin, vector_move_right)
            elif self.get_direction_retall_ganxo() == "LEFT":
                cuboid_retall = cuboid_retall_origin
            return cuboid_retall
        else:
            return None

    def update_params(self):
        self.heigh = self.build_ele.heigh.value
        self.width = self.build_ele.width.value
        self.thickness = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )
        self.xps_type = self.build_ele.xps_type.value
        self.rotation = self.build_ele.rotation.value
        self.xps_thickness = self.build_ele.XPSthickness.value
        self.xps_thickness_ind = self.build_ele.XPSthicknessInd.value

        self.llarg_ampits = self.build_ele.llarg_ampits.value
        self.fondo_ampits = self.build_ele.fondo_ampits.value
        self.afegit_ampits = self.build_ele.afegit_ampits.value
        self.retall_ampits = self.build_ele.retall_ampits.value
        self.ampit_material = self.build_ele.ampit_material.value

        self.val_pmp_fg_wall_name = self._get_current_pmp_pare_value()
        self.val_pmp_id_premarc = self._get_current_premarc_id_value()
        # self.val_pmp_xps_premarc_detail = self.build_ele.INPUT_PMP_XPS_PREMARC_DETAIL.value
        # self.val_pmp_fg_fus_codi_panell = self.build_ele.INPUT_PMP_FG_FUS_CODI_PANELL.value
        # self.val_pmp_fg_fus_codi = self.build_ele.INPUT_PMP_FG_FUS_CODI.value
        # self.val_pmp_fg_fus_unitats = self.build_ele.INPUT_PMP_FG_FUS_UNITATS.value
        # self.val_pmp_fg_fus_material = self.build_ele.INPUT_PMP_FG_FUS_MATERIAL.value
        # self.val_pmp_fg_fus_color = self.build_ele.INPUT_PMP_FG_FUS_COLOR.value
        # self.val_pmp_fg_fus_mides = self.build_ele.INPUT_PMP_FG_FUS_MIDES.value
        # self.val_pmp_fg_fus_model_perfil = self.build_ele.INPUT_PMP_FG_FUS_MODEL_PERFIL.value
        # self.val_pmp_fg_fus_fulles = self.build_ele.INPUT_PMP_FG_FUS_FULLES.value
        # self.val_pmp_fg_fus_tipus_fulles = self.build_ele.INPUT_PMP_FG_FUS_TIPUS_FULLES.value
        # self.val_pmp_fg_fus_posicio_manera = self.build_ele.INPUT_PMP_FG_FUS_POSICIO_MANERA.value
        # self.val_pmp_fg_fus_vidriera = self.build_ele.INPUT_PMP_FG_FUS_VIDRIERA.value
        # self.val_pmp_fg_fus_comp_vidriera = self.build_ele.INPUT_PMP_FG_FUS_COMP_VIDRIERA.value
        # self.val_pmp_fg_fus_persiana = self.build_ele.INPUT_PMP_FG_FUS_PERSIANA.value
        # self.val_pmp_fg_fus_ampit = self.build_ele.INPUT_PMP_FG_FUS_AMPIT.value
        # self.val_pmp_fg_fus_aplacat_fa = self.build_ele.INPUT_PMP_FG_FUS_APLACAT_FA.value
        # self.val_pmp_fg_fus_comp_fust = self.build_ele.INPUT_PMP_FG_FUS_COMP_FUST.value
        # self.val_pmp_fg_fus_volada_fust = self.build_ele.INPUT_PMP_FG_FUS_VOLADA_FUST.value
        # self.val_pmp_fg_fus_pintura_obra = self.build_ele.INPUT_PMP_FG_FUS_PINTURA_OBRA.value
        # self.val_pmp_fg_fus_barana = self.build_ele.INPUT_PMP_FG_FUS_BARANA.value
        # self.val_pmp_fg_fus_mosquitera = self.build_ele.INPUT_PMP_FG_FUS_MOSQUITERA.value

        # self.val_pmp_xps_premarc_detail_text    = self.build_ele.INPUT_PMP_XPS_PREMARC_DETAIL_TEXT.value
        # self.val_pmp_fg_fus_marge               = self.build_ele.INPUT_PMP_FG_FUS_MARGE.value
        # self.val_pmp_fg_fus_detail              = self.build_ele.INPUT_PMP_FG_FUS_DETAIL.value
        # self.val_pmp_fg_fus_tapajunts           = self.build_ele.INPUT_PMP_FG_FUS_TAPAJUNTS.value
        # self.val_pmp_fg_ampit_detail            = self.build_ele.INPUT_PMP_FG_AMPIT_DETAIL.value
        # self.val_pmp_fg_ampit_esq  	            = self.build_ele.INPUT_PMP_FG_AMPIT_ESQ.value
        # self.val_pmp_fg_ampit_dre	            = self.build_ele.INPUT_PMP_FG_AMPIT_DRE.value
        # self.val_pmp_fg_ampit_sup	            = self.build_ele.INPUT_PMP_FG_AMPIT_SUP.value
        # self.val_pmp_fg_ampit_inf	            = self.build_ele.INPUT_PMP_FG_AMPIT_INF.value
        # self.val_pmp_fg_ampit_ref_1	            = self.build_ele.INPUT_PMP_FG_AMPIT_REF_1.value
        # self.val_pmp_fg_ampit_ref_2 	        = self.build_ele.INPUT_PMP_FG_AMPIT_REF_2.value
        # self.val_pmp_fg_ampit_parts	            = self.build_ele.INPUT_PMP_FG_AMPIT_PARTS.value
        # self.val_pmp_fg_ampit_muntatge          = self.build_ele.INPUT_PMP_FG_AMPIT_MUNTATGE.value
        # self.val_pmp_fg_fusteria_tipus_muntatge = self.build_ele.INPUT_PMP_FG_FUSTERIA_TIPUS_MUNTATGE.value
        # self.val_pmp_fg_muntatge                = self.build_ele.INPUT_PMP_FG_MUNTATGE.value
        # self.val_pmp_fg_ampit_afegit            = self.build_ele.INPUT_PMP_FG_AMPIT_AFEGIT.value
        # self.val_pmp_fg_ampit_retall            = self.build_ele.INPUT_PMP_FG_AMPIT_RETALL.value

    def create_individual_pythonparts_from_elements(
        self, elements_list: List, build_ele
    ) -> List[PythonPart]:
        """
        Convierte una lista de ModelElement3D en PythonParts individuales.
        Cada elemento 3D se envuelve en su propia PythonPart para que GSI pueda leerlos individualmente.

        1. ModelElement3D ya tiene common_props y attributes
        2. Crear View2D3D con el ModelElement3D
        3. Extraer/crear parameter_list y hash
        4. Crear PythonPart(name, parameter_list, hash, python_file, views, common_props, attribute_list)

        Args:
            elements_list: Lista de ModelElement3D creados
            build_ele: BuildingElement con parámetros

        Returns:
            Lista de PythonParts individuales
        """
        pythonparts_list = []

        # Obtener el nombre del archivo .pyp desde build_ele
        python_file_name = (
            build_ele.pyp_file_name if hasattr(build_ele, "pyp_file_name") else ""
        )

        for idx, element in enumerate(elements_list):
            try:
                # 1. EXTRAER CommonProperties del elemento
                common_props = (
                    AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                )
                try:
                    # El ModelElement3D ya tiene CommonProperties asignados
                    if hasattr(element, "CommonProperties"):
                        common_props = element.GetCommonProperties()
                except:
                    pass

                # 2. EXTRAER atributos del elemento (ya fueron asignados previamente)
                attribute_list = []
                try:
                    if hasattr(element, "GetAttributes"):
                        attrs = element.GetAttributes()
                        if attrs and hasattr(attrs, "GetAttributeSets"):
                            attr_sets = attrs.GetAttributeSets()
                            if attr_sets and len(attr_sets) > 0:
                                # Extraer AttributeString individuales del primer set
                                for attr_set in attr_sets:
                                    if hasattr(attr_set, "GetAttributes"):
                                        attribute_list = list(attr_set.GetAttributes())
                                        break
                except Exception as e:
                    print(
                        f"[SO] Advertencia: No se pudieron extraer atributos del elemento {idx}: {e}"
                    )

                # 3. CREAR VIEWS con el ModelElement3D
                # Patrón del ejemplo: views = [View2D3D([ModelElement3D(...)])]
                views = [View2D3D([element])]

                # 4. CREAR parámetros únicos para este elemento
                # CommonProperties usa atributos directos, no métodos Get*()
                params = {
                    "ElementIndex": idx,
                    "ElementType": type(element).__name__,
                    "Layer": common_props.Layer,
                    "Color": common_props.Color,
                    "Pen": common_props.Pen,
                    "Stroke": common_props.Stroke,
                    "z_unique": z_unique_as_int(self.build_ele.z_unique.value),
                }

                if self.is_modification_mode:
                    hash_value = create_element_hash(
                        "premarc_element",
                        stable=True,
                        ElementIndex=idx,
                        z_unique=params["z_unique"],
                    )
                else:
                    hash_value = create_element_hash("element", **params)

                # 6. CREAR lista de parámetros (formato: "key = value\n")
                param_list = create_params_list_from_dict(params)

                # 7. OBTENER nombre descriptivo basado en atributos (ID 1083 = Atributo Personalizado 01)
                element_name = f"PremarcElement_{idx}"
                try:
                    for attr in attribute_list:
                        if hasattr(attr, "attribute_id") and attr.attribute_id == 1083:
                            if hasattr(attr, "value") and attr.value:
                                element_name = str(attr.value).replace(" ", "_")[
                                    :50
                                ]  # Limitar longitud
                                break
                except:
                    pass

                # 8. CREAR PythonPart individual con la firma completa
                # placement_matrix solo con la rotación (sin traslación): la traslación
                # la aplica el framework vía insert_matrix desde placement_point.
                rot_mat = None
                if abs(float(self.rotation)) > 0.01:
                    rot_mat = AllplanGeo.Matrix3D()
                    rot_mat.SetRotation(
                        AllplanGeo.Line3D(
                            AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 0, 100)
                        ),
                        AllplanGeo.Angle.FromDeg(self.rotation),
                    )

                pythonpart = PythonPart(
                    element_name,  # name
                    parameter_list=param_list,  # parameter_list
                    hash_value=hash_value,  # hash_value
                    python_file=python_file_name,  # python_file (nombre del .pyp)
                    views=views,  # views (View2D3D con ModelElement3D)
                    placement_matrix=rot_mat,  # rotación (None si rotation==0)
                    common_props=common_props,  # common_props
                    attribute_list=(
                        attribute_list if attribute_list else None
                    ),  # attribute_list
                )

                pythonparts_list.append(pythonpart)

            except Exception as e:
                print(
                    f"[SO] Error creando PythonPart individual para elemento {idx}: {e}"
                )
                import traceback

                traceback.print_exc()
                # En caso de error, continuar con los demás elementos
                continue

        print(
            f"[SO] Creadas {len(pythonparts_list)} PythonParts individuales de {len(elements_list)} elementos"
        )
        return pythonparts_list
