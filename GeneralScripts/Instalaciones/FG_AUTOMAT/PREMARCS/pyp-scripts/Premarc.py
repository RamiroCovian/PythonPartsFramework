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
from .opening_creation_util import OpeningCreationUtil, WindowOpeningCreationUtil

import requests


def _site_packages_path(
    base_path,
):  # TODO: Eliminar este metodo antes de entregar a Arnau
    return os.path.join(os.path.normpath(base_path), "PythonParts-site-packages")


def install_packages(package):
    prg_path = AllplanSettings.AllplanPaths.GetPrgPath() + "\\"

    target_dir = _site_packages_path(
        AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()
    )  # TODO: Eliminar esta linea antes de entregar a Arnau y descomentar la siguiente
    # target_dir = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
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

    target_dir = _site_packages_path(AllplanSettings.AllplanPaths.GetUsrPath())
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

_site_etc = _site_packages_path(
    AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()
)  # TODO: Eliminar esta linea antes de entregar a Arnau y descomentar la siguiente
_site_usr = _site_packages_path(
    AllplanSettings.AllplanPaths.GetUsrPath()
)  # TODO: Eliminar esta linea antes de entregar a Arnau y descomentar la siguiente
# _site_etc = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
# _site_usr = f"{AllplanSettings.AllplanPaths.GetUsrPath()}Local\\PythonParts-site-packages"
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
# U_PROFILE_SILL_Y_ANCHOR (full 115 mm step):
#   "pit_span_from_outer_lip" — DEFAULT: y0 ≈ -thickness (back edge of pink sill / finestra); runs toward y=0.
#   "pit_into_opening"        — y0 ≈ 0 (front / inner lip y=0), profile in y>0 only.
#   "pit_inward" / "pit_outer_face" / "half_embed" — alternates (see code).
# Prefer palette ComboBoxUChannelYAnchor when Show U is on (no code edit to flip sides).
U_PROFILE_SILL_Y_ANCHOR = "pit_span_from_outer_lip"
U_PROFILE_Y_ANCHOR_OFFSET_MM = 0.0
# Fallback only if U_PROFILE_SILL_Y_ANCHOR is empty or not recognized:
U_PROFILE_FLUSH_TO_INNER_OPENING_Y = True
U_HALF_EMBED_AT_INNER_FACE = True
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
OFFSET_FRONT_BOX_SHUTTER = 74
OFFSET_FALCA = 25
DISTANCE_BETWEEN_FALCAS = 250
FIX_FEMELLA_Y = 40  # = 160/2- (80/2). 80 mm es el ancho de la femella.
VERTICAL_TUB = 1
HORIZONTAL_TUB = 2
REA_Z_ORIGIN = 50
REA_Z_FINAL = 700
LENGTH_REBAJES_MM = 19

API_URL = "https://localhost:5050/ComandesOT/GetAllDenConfigsByAT1Value"
# API_URL ="http://localhost:5000/ComandesOT/GetAllDenConfigsByAT1Value"
# API_URL ="https://192.168.30.227:8301/ComandesOT/GetAllDenConfigsByAT1Value"

API_URL_AT1 = (
    "https://localhost:5050/ComandesOT/GetAllValuesForConfig?den=PREM&config=1"
)
# API_URL_AT1 ="http://localhost:5000/ComandesOT/GetAllValuesForConfig?den=PREM&config=1"
# API_URL_AT1 ="https://192.168.30.227:8301/ComandesOT/GetAllValuesForConfig?den=PREM&config=1"

API_URL_DEFAULT = "https://localhost:5050/ComandesOT/GetAllValuesForAllConfigs?den=PREM"
# API_URL_DEFAULT = "http://localhost:5000/ComandesOT/GetAllValuesForAllConfigs?den=PREM"
# API_URL_DEFAULT = "https://192.168.30.227:8301/ComandesOT/GetAllValuesForAllConfigs?den=PREM"

LOGIN_URL_DEFAULT = "https://localhost:5050/Usuari/Login"
# LOGIN_URL_DEFAULT = "http://localhost:5000/Usuari/Login"
# LOGIN_URL_DEFAULT = "https://192.168.30.227:8301/Usuari/Login"

COLOR_THICKNESS_MAP = {
    160: 2,  # amarillo
    310: 6,  # rojo
    295: 15,  # morado
}

# TODO: Eliminar los mock antes de enviar a Arnau
MOCK_VALUES_FOR_CONFIG = {
    "values": {
        "1": 160,
        "2": 295,
        "3": 310,
    }
}

MOCK_DATA_ENDPOINT = {
    "options": [
        {
            "position": 1,
            "values": [
                {"description": "Cerrado", "value": "0"},
                {"description": "Abierto", "value": "1"},
            ],
        },
        {
            "position": 2,
            "values": [
                {"description": "NO", "value": "0"},
                {"description": "SI", "value": "1"},
            ],
        },
        {
            "position": 3,
            "values": [
                {"description": "NO", "value": "0"},
                {"description": "PASSAMA LATERALS", "value": "1-2"},
                {"description": "PASSAMA INF/SUP", "value": "3-4"},
                {"description": "PASSAMA 4 COSTATS", "value": "1-2-3-4"},
                {"description": "PASSAMA FALCA SUP.(LAMISOL/METAL.)", "value": "8"},
                {"description": "PASSAMA FALCA INF. (+ de 4 m)", "value": "7"},
                {"description": "PASSAMA FALCA SUP./INF. (+ de 6m)", "value": "8-9"},
            ],
        },
        {
            "position": 4,
            "values": [
                {"description": "NO", "value": "0"},
                {"description": "35*30", "value": "1"},
                {"description": "40*30", "value": "1"},
                {"description": "70*30", "value": "3"},
                {"description": "PLEC INFERIOR", "value": "4"},
                {"description": "30*80", "value": "2"},
            ],
        },
        {
            "position": 5,
            "values": [
                {"description": "NO", "value": "0"},
                {"description": "REB. DRETA", "value": "1"},
                {"description": "REB. ESQUERRA", "value": "2"},
                {"description": "REB. BAIXS", "value": "3"},
                {"description": "REB. DALT", "value": "4"},
            ],
        },
        {
            "position": 6,
            "values": [
                {"description": "NO", "value": "0"},
                {"description": "SI", "value": "1"},
            ],
        },
        {
            "position": 7,
            "values": [
                {"description": "NO", "value": "0"},
                {"description": "35*30", "value": "1"},
                {"description": "40*30", "value": "1"},
                {"description": "70*30", "value": "3"},
                {"description": "PLEC INFERIOR", "value": "4"},
                {"description": "30*80", "value": "2"},
            ],
        },
        {
            "position": 8,
            "values": [
                {"description": "NO", "value": "0"},
            ],
        },
    ]
}

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
PMP_FG_AMPIT_MUNTANTGE = "PMP_FG_AMPIT_MUNTANTGE"
PMP_FG_AMPIT_AFEGIT = "PMP_FG_AMPIT_AFEGIT"
PMP_FG_AMPIT_RETALL = "PMP_FG_AMPIT_RETALL"
PMP_WALL_NAME = "PMP_WALL_NAME"
PMP_ID_PREMARC = "PMP_ID_PREMARC"
PMP_FG_FUS_ACCESORI = "PMP_FG_FUS_ACCESORI"
PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO = "PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO"
PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL = "PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO"
PMP_FG_AMPIT_DETAIL_GENERAL = "PMP_FG_AMPIT_DETAIL_GENERAL"
PMP_FG_AMPIT_DETAIL_MATERIAL = "PMP_FG_AMPIT_DETAIL_MATERIAL"
PMP_PREM_ENCAJE_ALTURA = "PMP_PREM_ENCAJE_ALTURA"
PMP_PREM_ENCAJE_BASE = "PMP_PREM_ENCAJE_BASE"
PMP_PREM_MURO = "PMP_PREM_MURO"
PMP_PREM_COLOR = "PMP_PREM_COLOR"
PMP_PREM_XPS_TYPE = "PMP_PREM_XPS_TYPE"
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
VAL_PMP_PREMARC_LABELS = "TIPUS-$<bold, height(5)>6.13$;$<bold>CALAIX OCULT$"
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
VAL_PMP_FG_AMPIT_MUNTANTGE = "FABRICA"
VAL_PMP_FG_AMPIT_AFEGIT = 0.0
VAL_PMP_FG_AMPIT_RETALL = 0.0
VAL_PMP_FG_AMPIT_DETAIL_GENERAL = "TIPUS_AMPIT_1"
VAL_PMP_FG_AMPIT_DETAIL_MATERIAL = "MATERIAL_1"

ID_PMP_WALL_ID = 683


def create_element_hash(element_type: str, **params) -> str:
    # Generar un número random largo para asegurar unicidad
    # Usar un rango muy grande (10^15 a 10^16-1) para minimizar colisiones
    random_number = random.randint(10**15, 10**16 - 1)
    # Crear string de parámetros ordenados alfabéticamente para consistencia
    param_items = sorted(params.items())
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
        param_list.append(f"{key} = {value}\n")
    return param_list


def check_allplan_version(build_ele, version):
    return True


def create_element(build_ele, doc):
    return ([], [])


def create_script_object(
    build_ele: BuildingElement, script_object_data: BaseScriptObjectData
) -> BaseScriptObject:
    """Creation of the script object (Allplan 2025 ScriptObject)"""
    return PremarcScriptObject(build_ele, script_object_data)


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


class PremarcScriptObject(BaseScriptObject):
    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        # 1) inicializa la base y guarda el building element (acceso a parámetros)
        super().__init__(script_object_data)

        self.build_ele = build_ele

        self.build_ele.z_unique.value = random.random() * 3600  # try solve cache

        self.placement_mat = AllplanGeo.Matrix3D()

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

        if self.is_modification_mode:
            raw_state = self.build_ele.SavedState.value
            if raw_state:
                # SavedState puede venir como JSON string o ya como dict
                if isinstance(raw_state, str):
                    state = json.loads(raw_state)
                elif isinstance(raw_state, dict):
                    state = raw_state
                else:
                    state = {}

                saved_pnt = AllplanGeo.Point3D(state["X"], state["Y"], state["Z"])
                self.placement_pnt = saved_pnt
                self.rotation = state["rotation"]
                self.build_ele.rotation.value = self.rotation
                # self.placement_mat.SetRotation(
                #     AllplanGeo.Line3D(
                #         AllplanGeo.Point3D(saved_pnt.X, saved_pnt.Y, saved_pnt.Z),
                #         AllplanGeo.Point3D(saved_pnt.X, saved_pnt.Y, saved_pnt.Z + 100)
                #     ),
                #     AllplanGeo.Angle.FromDeg(self.rotation)
                # )
                # self.placement_mat.SetTranslation(AllplanGeo.Vector3D(saved_pnt))
                self.heigh = state["height"]
                self.width = state["width"]
                self.build_ele.heigh.value = state["height"]
                self.build_ele.width.value = state["width"]
                self.thickness = state["depth"]  # thickness premarc
                self.thickness_wall = state["thickness_wall"]
                self.build_ele.ComboBoxEncajes.value = state["encaje"]
                self.build_ele.EnableManualEncaje.value = state["encaje_manual"]
                self.build_ele.EncajeBase.value = state["encaje_base"]
                self.build_ele.EncajeAltura.value = state["encaje_altura"]
                self.build_ele.DisableTopXPS.value = state["disable_top_xps"]
                self.build_ele.DisableBottomXPS.value = state["disable_bottom_xps"]
                self.build_ele.DisableLeftXPS.value = state["disable_left_xps"]
                self.build_ele.DisableRightXPS.value = state["disable_right_xps"]
                self.build_ele.XPSthicknessInd.value = state["xps_thickness_index"]
                self.build_ele.XPSthickness.value = state["xps_thickness"]
                self.build_ele.ComboBoxAbiertoCerrado.value = state[
                    "ComboBoxAbiertoCerrado"
                ]
                self.build_ele.EnableRetallGanxo.value = state["EnableRetallGanxo"]
                self.build_ele.Z_RetallGanxo.value = state["Z_RetallGanxo"]
                self.build_ele.ComboBoxPendiente.value = state["ComboBoxPendiente"]
                self.build_ele.ShowAccessorUPerimeter.value = state[
                    "ShowAccessorUPerimeter"
                ]

                self.build_ele.PassamaOptions.value = [
                    int(x) for x in state.get("PassamaOptions", [])
                ]

                self.build_ele.ComboBoxEncajes.value = state["ComboBoxEncajes"]
                self.build_ele.EnableManualEncaje.value = state["EnableManualEncaje"]
                self.build_ele.EncajeBase.value = state["EncajeBase"]
                self.build_ele.EncajeAltura.value = state["EncajeAltura"]

                self.build_ele.RebajesOptions.value = [
                    int(x) for x in state.get("RebajesOptions", [])
                ]

                self.build_ele.ComboBoxPersianas.value = state["ComboBoxPersianas"]
                self.build_ele.ComboBoxEscuadras.value = state["ComboBoxEscuadras"]
                self.build_ele.ComboBoxTubos.value = state["ComboBoxTubos"]
                self.build_ele.TypeTubos.value = state["TypeTubos"]
                self.build_ele.CheckBoxRealSpace.value = state["CheckBoxRealSpace"]
                self.build_ele.CheckBoxInnerSpace.value = state["CheckBoxInnerSpace"]
                self.build_ele.thickness.value = state["thickness_manual"]
                self.build_ele.enable_manual_thickness.value = state[
                    "enable_manual_thickness"
                ]
                self.build_ele.manual_thickness.value = state["manual_thickness"]
                self.build_ele.color_manual_thickness.value = state[
                    "color_manual_thickness"
                ]
                # self.build_ele.valueListaGrosor.value = state["valueListaGrosor"]
                self.build_ele.xps_type.value = state["xps_type"]
                # Ampits
                self.build_ele.fondo_ampits.value = state["fondo_ampits"]
                self.build_ele.llarg_ampits.value = state["llarg_ampits"]
                self.build_ele.afegit_ampits.value = state["afegit_ampits"]
                self.build_ele.retall_ampits.value = state["retall_ampits"]
                self.build_ele.wall_id.value = state["wall_id"]
                self.build_ele.opening_guid.value = state.get("opening_guid", "")
                self.wall_guid_str = state.get("wall_guid", "")

            self.wall_select_result = WallSelectResult()
            if self.wall_guid_str:
                guid = AllplanEleAdapter.GUID.FromString(self.wall_guid_str)
                adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                    guid, self.document
                )
                if not adapter.IsNull():
                    self.wall_select_result.element = adapter
                    self.wall_select_result.element_guid = self.wall_guid_str
                    self.wall_select_result.is_selected = True
                    self.selected_wall = adapter
                    self.detected_wall_thickness = self._get_wall_thickness(
                        self.selected_wall
                    )
                else:
                    self.selected_wall = None  # muro eliminado, modo seguro
            else:
                self.selected_wall = None

            # If opening exists, delete it
            # guid_exists = bool(self.build_ele.opening_guid.value)

            # if guid_exists:
            #     self._delete_wall_opening()

            # opening_guid_str = self.build_ele.opening_guid.value

            # if opening_guid_str:
            #     # Reconstruir el GUID object desde string
            #     guid = AllplanEleAdapter.GUID()
            #     guid.FromString(opening_guid_str)   # o según la API: GUID(opening_guid_str)
            #     # Obtener el BaseElementAdapter desde el GUID
            #     opening_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(guid, self.document)
            #     if not opening_adapter.IsNull():
            #         print("[Premarc] Opening recuperado OK")
            #         # Aquí puedes borrarlo o modificarlo

            # self.detected_wall_thickness = self.build_ele.SavedWallThickness.value

        self.session = requests.Session()
        # self.login_to_api() #TODO: Descomentar esta linea antes de entregar a Arnau

        self.build_ele.SelectionWall.value = "No seleccionado"
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
        # self.build_ele.INPUT_PMP_FG_AMPIT_MUNTANTGE.value           = VAL_PMP_FG_AMPIT_MUNTANTGE
        # self.build_ele.INPUT_PMP_FG_FUSTERIA_TIPUS_MUNTATGE.value   = VAL_PMP_FG_FUSTERIA_TIPUS_MUNTATGE
        # self.build_ele.INPUT_PMP_FG_MUNTATGE.value                  = VAL_PMP_FG_MUNTATGE
        # self.build_ele.INPUT_PMP_FG_AMPIT_AFEGIT.value              = VAL_PMP_FG_AMPIT_AFEGIT
        # self.build_ele.INPUT_PMP_FG_AMPIT_RETALL.value              = VAL_PMP_FG_AMPIT_RETALL
        # self.build_ele.INPUT_PMP_FG_WALL_NAME.value                 = VAL_PMP_FG_WALL_NAME
        # self.build_ele.INPUT_PMP_FG_FUS_ACCESORI.value              = VAL_PMP_FG_FUS_ACCESORI
        # self.build_ele.INPUT_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO.value = VAL_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO
        # self.build_ele.INPUT_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL.value = VAL_PMP_FG_FUS_TIPUS_IMPERMEABILITZACIO_DETAIL
        # self.build_ele.INPUT_PMP_FG_AMPIT_DETAIL_GENERAL.value = VAL_PMP_FG_AMPIT_DETAIL_GENERAL
        # self.build_ele.INPUT_PMP_FG_AMPIT_DETAIL_MATERIAL.value = VAL_PMP_FG_AMPIT_DETAIL_MATERIAL

        self.update_params()

        self.afegit_ampits_manual = False
        self.retall_ampits_manual = False

        if not self.is_modification_mode:
            self.placement_pnt = AllplanGeo.Point3D()
            self.point_result = PointInteractorResult()
            self.wall_select_result = WallSelectResult()
            self.selected_wall = None  # guardará el BaseElementAdapter
            self.detected_wall_thickness = 0

        self.interactor_state = STOPPED
        self.handle_list = []
        self._create_union_frames = False  # Flag para controlar el comportamiento
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
        self.pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(
            self.document, PMP_PARE
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
        self.pmp_fg_ampit_muntantge_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_MUNTANTGE
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
        self.pmp_fg_ampit_detail_material_id = (
            AllplanBaseElements.AttributeService.GetAttributeID(
                self.document, PMP_FG_AMPIT_DETAIL_MATERIAL
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

        # Actualizar la lista de valores
        self.build_ele.valueListaPassama.value = lista_passama

        # Inicializar los CheckBox si no están inicializados
        if (
            len(self.build_ele.PassamaOptions.value) != len(lista_passama)
            and not self.is_modification_mode
        ):
            self.build_ele.PassamaOptions.value = [False] * len(lista_passama)

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
                self.selected_wall = self.wall_select_result.element
                print(
                    f"[Premarc] Muro seleccionado: {self.wall_select_result.element_guid}"
                )
                self.detected_wall_thickness = self._get_wall_thickness(
                    self.selected_wall
                )
                self.build_ele.SelectionWall.value = "Seleccionado"

                wall_angle = self._get_wall_rotation_deg(self.selected_wall)
                self.rotation = wall_angle
                self.build_ele.rotation.value = wall_angle
                print(f"[Premarc] Rotation set to wall angle: {wall_angle} deg")

                # PythonUtility.ShowMessageBox(f"Grosor muro detectado: {self.detected_wall_thickness} mm", PythonUtility.MB_OK)
                self._debug_wall_attrs(self.selected_wall)

                if self.selected_wall:
                    try:
                        mat_raw = self.get_wall_material_name(self.selected_wall)
                        self.wall_name = mat_raw

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
                self._rebuild_placement_mat()

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

            self.script_object_interactor = None
            self.interactor_state = STOPPED

    def _start_placement_point_input(self):
        """Inicia el input de punto conservando el muro seleccionado."""
        self.point_result = PointInteractorResult()
        self.interactor_state = PLACING_POINT
        self.script_object_interactor = PointInteractor(
            interactor_result=self.point_result,
            is_first_input=True,
            request_text="Posicionar Premarco",
            preview_function=self.draw_placement_preview,
        )

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
        if hasattr(self.build_ele, "opening_guid"):
            self.build_ele.opening_guid.value = ""

        print("[Premarc] Premarco confirmado; habilitando nueva posicion")
        return True

    def on_control_event(self, event_id: int):
        # Reiniciar vector_length para recalcular con los nuevos puntos
        if event_id == 1000:
            self.build_ele.SelectionWall.value = "No seleccionado"
            self.wall_select_result = WallSelectResult()
            self.selected_wall = None
            self.interactor_state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result, "Seleccione el muro donde colocar el premarco"
            )
            self.script_object_interactor.start_input(self.coord_input)
            return True
        elif event_id == 1001:
            if self.is_modification_mode:
                return False

            if not self._commit_current_premarc_before_next_placement():
                return True

            if not self.selected_wall:
                self.start_input()
            else:
                self._start_placement_point_input()

            if self.script_object_interactor:
                self.script_object_interactor.start_input(self.coord_input)
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

        HandlePropertiesService.update_property_value(
            self.build_ele, handle_prop, input_pnt
        )

        return self.execute()

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
        print("execute")
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
        self.build_ele.z_unique.value = random.random() * 3600
        self.thickness_premarc = (
            self.build_ele.manual_thickness.value
            if self.build_ele.enable_manual_thickness.value
            else self.build_ele.thickness.value
        )

        if self.placement_pnt == AllplanGeo.Point3D():
            return CreateElementResult([])
        if not self.selected_wall and not self.is_modification_mode:
            return CreateElementResult([])

        self._rebuild_placement_mat()

        premarc_elements = self.create_premarcs_group()

        # En modification mode: borrar el opening.
        if self.is_modification_mode:
            opening_guid_str = self.build_ele.opening_guid.value
            if opening_guid_str:
                self._delete_wall_opening()

        return CreateElementResult(
            elements=premarc_elements,
            handles=self.handle_list,
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
        self.build_ele.z_unique.value = random.random() * 3600
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

        # Traslación solo — la rotación la maneja placement_matrix dentro de cada PythonPart
        trans_mat = AllplanGeo.Matrix3D()
        trans_mat.SetTranslation(AllplanGeo.Vector3D(self.placement_pnt))

        AllplanBaseElements.CreateElements(
            self.document,
            trans_mat,
            premarc_elements,
            [],
            None,
        )

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

    def _create_wall_opening(self):
        if not self.selected_wall or self.selected_wall.IsNull():
            return
        if self.placement_pnt == AllplanGeo.Point3D():
            return

        import math
        from DocumentManager import DocumentManager
        from PythonPartTransaction import PythonPartTransaction
        from TypeCollections.ModificationElementList import ModificationElementList

        # CLAVE: setear el documento correcto antes de la transacción
        DocumentManager.get_instance().document = (
            self.coord_input.GetInputViewDocument()
        )

        pos = self.placement_pnt
        llarg = self.build_ele.width.value
        alt = self.build_ele.heigh.value

        axis_ele = AllplanEleAdapter.AxisElementAdapter(self.selected_wall)
        if axis_ele.IsNull():
            print("[Premarc] Sin eje, skip opening")
            return
        gruix = axis_ele.GetThickness()
        wall_axis = axis_ele.GetAxis()  # Line2D: eje central del muro

        # ── 1. Proyectar el click sobre el eje del muro ──────────────────────
        p0 = wall_axis.StartPoint  # Point2D
        p1 = wall_axis.EndPoint  # Point2D
        dx = p1.X - p0.X
        dy = p1.Y - p0.Y
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1e-10:
            print("[Premarc] Muro sin longitud, skip opening")
            return

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
        start_x = proj_x - (gruix / 2.0) * nx
        start_y = proj_y - (gruix / 2.0) * ny

        # Matriz de rotación: alinea el eje X del cuboid (1,0,0) con la dirección del muro
        rot_mat = AllplanGeo.Matrix3D()
        rot_mat.SetIdentity()
        wall_dir_3d = AllplanGeo.Vector3D(ux, uy, 0.0)
        if abs(ux - 1.0) > 1e-6 or abs(uy) > 1e-6:
            rot_mat.SetRotation(AllplanGeo.Vector3D(1.0, 0.0, 0.0), wall_dir_3d)

        # Matriz de traslación: lleva la esquina a (start_x, start_y, pos.Z)
        trans_mat = AllplanGeo.Matrix3D()
        trans_mat.SetTranslation(AllplanGeo.Vector3D(start_x, start_y, pos.Z - alt))

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
            return

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

        opening_prop = AllplanArchElements.WindowOpeningProperties()
        opening_prop.Independent2DInteraction = False

        plane_ref = AllplanArchElements.PlaneReferences(
            self.document, AllplanEleAdapter.BaseElementAdapter()
        )
        plane_ref.SetBottomOffset(pos.Z - alt)
        plane_ref.SetHeight(alt)
        opening_prop.PlaneReferences = plane_ref

        geom = opening_prop.GetGeometryProperties()
        geom.Depth = gruix

        opening_element = AllplanArchElements.WindowOpeningElement(
            opening_prop,
            self.selected_wall,
            start_2d,
            opening_end_pnt,
            drawPlacementPreview=False,
        )

        transaction = PythonPartTransaction(self.document)
        created_opening = transaction.execute(
            AllplanGeo.Matrix3D(),
            AllplanIFW.ViewWorldProjection(),
            [opening_element],
            ModificationElementList(),
        )
        print("[Premarc] Opening creado OK")
        # Guardar el GUID en el parámetro del PythonPart
        # El opening creado es el primer elemento de la lista

        if created_opening:
            opening_adapter = [
                x
                for x in created_opening
                if x.GetElementAdapterType() == AllplanEleAdapter.WindowTier_TypeUUID
            ][0]
            opening_guid = opening_adapter.GetModelElementUUID()  # objeto GUID
            opening_guid_str = str(opening_guid)  # string persistible
            print(f"[Premarc] Opening GUID: {opening_guid_str}")
            self.build_ele.opening_guid.value = opening_guid_str
            self._opening_created_width = llarg
            self._opening_created_heigh = alt

    def _delete_wall_opening(self):
        opening_guid_str = self.build_ele.opening_guid.value
        if not opening_guid_str:
            return

        from DocumentManager import DocumentManager
        from PythonPartTransaction import PythonPartTransaction

        DocumentManager.get_instance().document = (
            self.coord_input.GetInputViewDocument()
        )

        # guid = AllplanEleAdapter.GUID()
        # guid.FromString(opening_guid_str)
        guid = AllplanEleAdapter.GUID.FromString(opening_guid_str)
        docDrawingFile = AllplanBaseElements.DrawingFileService()
        docAdapter = AllplanEleAdapter.DocumentAdapter()
        listDocumnets = (
            AllplanEleAdapter.DocumentNameService.GetLoadedDocumentsNameData()
        )

        for docValue in range(0, len(listDocumnets)):
            docDrawingFile.LoadFile(
                docAdapter,
                listDocumnets[docValue][1],
                AllplanBaseElements.DrawingFileLoadState.ActiveForeground,
            )
            doc = DocumentManager.get_instance().document  # doc consistente
            opening_adapter = AllplanEleAdapter.BaseElementAdapter.FromGUID(guid, doc)

            if opening_adapter.IsNull():
                # Ya no existe (undo externo, borrado manual, etc.)
                print("[Premarc] Opening ya no existe, limpiando GUID")
                self.build_ele.opening_guid.value = ""
                continue

            ele_list = AllplanEleAdapter.BaseElementAdapterList()
            ele_list.append(opening_adapter)

            AllplanBaseElements.DeleteElements(doc, ele_list)

            self.build_ele.opening_guid.value = ""
            self._opening_created_width = 0
            self._opening_created_heigh = 0
            print("[delete_wall_opening] Opening borrado OK")

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

        handle_height = HandleProperties(
            "HeighHandle",
            AllplanGeo.Point3D(0, 0, self.build_ele.heigh.value),
            AllplanGeo.Point3D(0, 0, 0),
            [HandleParameterData("heigh", HandleParameterType.Z_DISTANCE)],
            HandleDirection.Z_DIR,
        )

        self.handle_list.append(handle_height)

        individual_pythonparts = self.create_individual_pythonparts_from_elements(
            self.elements, self.build_ele
        )

        # pp_util = PythonPartUtil()
        # pp_util.add_pythonpart_view_2d3d(self.elements)
        # pp = pp_util.create_pythonpart(self.build_ele, placement_matrix=self.placement_mat, type_display_name="PythonPart XPS Premarcs")

        if not individual_pythonparts:
            raise Exception("No se pudieron crear PythonParts individuales")

        passama_vals = self.build_ele.PassamaOptions.value
        rebajes_vals = self.build_ele.RebajesOptions.value
        passama_01 = (
            [self._saved_checkbox_01(x) for x in passama_vals] if passama_vals else []
        )
        rebajes_01 = (
            [self._saved_checkbox_01(x) for x in rebajes_vals] if rebajes_vals else []
        )

        global_params = {
            "TotalElements": len(self.elements),
            "SavedState": json.dumps(
                {
                    "X": self.placement_pnt.X,
                    "Y": self.placement_pnt.Y,
                    "Z": self.placement_pnt.Z,
                    "thickness": self.detected_wall_thickness,
                    "height": self.heigh,
                    "width": self.width,
                    "depth": self.thickness_premarc,
                    "thickness_wall": self.build_ele.thickness_wall.value,
                    "rotation": self.rotation,
                    "encaje": self.build_ele.ComboBoxEncajes.value,
                    "encaje_manual": self.build_ele.EncajeBase.value,
                    "encaje_altura": self.build_ele.EncajeAltura.value,
                    "encaje_base": self.build_ele.EncajeBase.value,
                    ###
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
                    # "valueListaGrosor": self.build_ele.valueListaGrosor.value,
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
                    "PassamaOptions": passama_01,  ##
                    "ComboBoxEncajes": self.build_ele.ComboBoxEncajes.value,
                    "EnableManualEncaje": self.build_ele.EnableManualEncaje.value,
                    "EncajeBase": self.build_ele.EncajeBase.value,
                    "EncajeAltura": self.build_ele.EncajeAltura.value,
                    "RebajesOptions": rebajes_01,
                    "ComboBoxPersianas": self.build_ele.ComboBoxPersianas.value,
                    "ComboBoxEscuadras": self.build_ele.ComboBoxEscuadras.value,
                    "ComboBoxTubos": self.build_ele.ComboBoxTubos.value,
                    "TypeTubos": self.build_ele.TypeTubos.value,
                    "CheckBoxRealSpace": self.build_ele.CheckBoxRealSpace.value,
                    "CheckBoxInnerSpace": self.build_ele.CheckBoxInnerSpace.value,
                    "opening_guid": self.build_ele.opening_guid.value,
                    "wall_guid": self.wall_select_result.element_guid or "",
                    "pmp_pare": (
                        self.get_wall_material_name(self.selected_wall)
                        if self.selected_wall
                        else ""
                    ),
                    "ShowAccessorUPerimeter": self.build_ele.ShowAccessorUPerimeter.value,
                    # Attributes
                }
            ),
        }

        # Generar hash único para la instalación completa
        premarc_hash = create_element_hash(
            f"premarcos_{random.random() * 3600}", **global_params
        )

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
                self._create_wall_opening()
                self._create_union_frames = True
                self._execute()
                return OnCancelFunctionResult.CANCEL_INPUT

        return OnCancelFunctionResult.CANCEL_INPUT

    def draw_placement_preview(self):
        self.placement_pnt = self.point_result.input_point
        self._rebuild_placement_mat()
        self._in_placement_preview = True

        try:
            preview_model = self.create_premarc()
        finally:
            self._in_placement_preview = False

        AllplanBaseElements.DrawElementPreview(
            self.document, self.placement_mat, preview_model, False, None
        )

    def get_data_endpoint(self, at1value: str) -> dict:
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
            print(f"Unexpected error: {e}")
            print(
                "[Premarc] API no disponible. Usando datos mock para configuraciones."
            )  # TODO: Eliminar esta linea antes de entregar a Arnau
            return MOCK_DATA_ENDPOINT  # TODO: Eliminar esta linea antes de entregar a Arnau

    def get_values_for_config_API(self) -> dict:
        try:
            url = f"{API_URL_AT1}"
            DEFAULT_CONFIG = MOCK_VALUES_FOR_CONFIG  # TODO: Eliminar esta linea antes de entregar a Arnau y descomentar la siguiente
            # DEFAULT_CONFIG = {"values": {}}

            response = self.session.get(url, verify=False)

            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                print("Success data endpoint:")
                # print(data)
                return data

            return DEFAULT_CONFIG
        except Exception as e:
            print(f"Unexpected error: {e}")
            print(
                "[Premarc] API no disponible. Usando grosores mock."
            )  # TODO: Eliminar esta linea antes de entregar a Arnau
            return DEFAULT_CONFIG

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
        if debe_actualizar:
            self.build_ele.valueListaAbiertoCerrado.value = listaAbiertoCerrado

    def crearListaPendiente(self):
        """Crea una lista de pendiente"""
        listaActual = self.build_ele.valueListaPendiente.value
        data = self.data_endpoint
        listaPendiente = self.get_description_by_position(data, 2)
        debe_actualizar = len(listaActual) == 0 or listaActual != listaPendiente
        if debe_actualizar:
            self.build_ele.valueListaPendiente.value = listaPendiente

    def crearListaEncajes(self):
        """Crea una lista de encajes"""
        listaActual = self.build_ele.valueListaEncajes.value
        data = self.data_endpoint
        listaEncajes = self.get_description_by_position(data, 4)
        debe_actualizar = len(listaActual) == 0 or listaActual != listaEncajes
        if debe_actualizar:
            self.build_ele.valueListaEncajes.value = listaEncajes

    def crearListaEscuadras(self):
        """Crea una lista de escuadras"""
        listaActual = self.build_ele.valueListaEscuadras.value
        data = self.data_endpoint
        listaEscuadras = self.get_description_by_position(data, 7)
        debe_actualizar = len(listaActual) == 0 or listaActual != listaEscuadras
        if debe_actualizar:
            self.build_ele.valueListaEscuadras.value = listaEscuadras

    def crearListaTubos(self):
        """Crea una lista de tubos"""
        listaActual = self.build_ele.valueListaTubos.value
        data = self.data_endpoint
        listaTubos = self.get_description_by_position(data, 8)
        debe_actualizar = len(listaActual) == 0 or listaActual != listaTubos
        if debe_actualizar:
            self.build_ele.valueListaTubos.value = listaTubos

    def crearListaPerianas(self):
        """Crea una lista de perianas"""
        listaActual = self.build_ele.valueListaPersianas.value
        data = self.data_endpoint
        listaPersianas = self.get_description_by_position(data, 6)
        debe_actualizar = len(listaActual) == 0 or listaActual != listaPersianas
        if debe_actualizar:
            self.build_ele.valueListaPersianas.value = listaPersianas

    def crearListaConfiguraciones(self):
        """Crea una lista de configuraciones"""
        data = self.values_for_config
        if data["values"]:
            lista_conf = [data["values"][k] for k in sorted(data["values"], key=int)]
            self.build_ele.valueListaGrosor.value = lista_conf
        else:
            print("Error in create list of configurations")
            self.build_ele.valueListaGrosor.value = []

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
        frame, frame_base_no_slope, _substract_rebajes = self.create_premarc_frame()
        self._append_frame_elements_to_model_list(model_ele_list, props_frame, frame)
        if frame_base_no_slope:
            model_ele_list.append_geometry_3d(
                frame_base_no_slope, props_frame_base_no_slope
            )
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
        xps = self.create_xps_premarc()
        for elem in xps:
            model_ele_list.append_geometry_3d(elem, props_xps)

        xps_attribute_list = BuildingElementAttributeList()
        # xps_attribute_list.add_attribute(self.sizes_attribute_id, "2950x600x120mm")
        xps_attribute_list.add_attribute(
            self.pmp_xps_premarc_detail_id, VAL_PMP_XPS_PREMARC_DETAIL
        )
        xps_attribute_list.add_attribute(
            self.pmp_xps_premarc_detail_text_id, VAL_PMP_XPS_PREMARC_DETAIL_TEXT
        )
        xps_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            xps_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        xps_attribute_list.add_attribute(ID_PMP_WALL_ID, self.build_ele.wall_id.value)

        init_i = len(model_ele_list) - len(xps)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, xps_attribute_list.get_attribute_list()
            )

        frame, frame_base_no_slope, substract_rebajes = self.create_premarc_frame()
        for elem in frame:
            model_ele_list.append_geometry_3d(elem, props_frame)

        frame_attribute_list = BuildingElementAttributeList()
        frame_attribute_list.add_attribute(
            self.den_id, self.build_ele.ComboBoxDEN.value
        )
        frame_attribute_list.add_attribute(
            self.pmp_xps_premarc_detail_text_id, self.build_ele.xps_type.value
        )
        frame_attribute_list.add_attribute(
            self.pmp_tipus_premarc_id, f"FONS {self.thickness_premarc} mm"
        )
        frame_attribute_list.add_attribute(
            self.pmp_prem_encaje_altura_id, self.prem_encaje_altura
        )
        frame_attribute_list.add_attribute(
            self.pmp_prem_encaje_base_id, self.prem_encaje_base
        )
        frame_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        frame_attribute_list.add_attribute(
            self.pmp_prem_muro_id, self.build_ele.thickness_wall.value
        )
        frame_attribute_list.add_attribute(
            self.pmp_prem_color_id, self.color_id_to_rgb_or_hex()[0]
        )
        if self.selected_wall:
            frame_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        frame_attribute_list.add_attribute(ID_PMP_WALL_ID, self.build_ele.wall_id.value)
        frame_attribute_list.add_attribute(
            self.pmp_premarc_type_id, self._premarc_labels_without_extras()
        )
        frame_attribute_list.add_attribute(self.pmp_prem_fondo_id, self.thickness)
        first_label, extras = (
            self._premarc_labels()
        )  # updates INPUT_PMP_PREMARC_LABELS with auto value
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
        # for substract_rebaje in substract_rebajes: # TODO: Test rebaje
        #     model_ele_list.append_geometry_3d(substract_rebaje, props_retall_ganxo)

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
        squares_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            squares_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        squares_attribute_list.add_attribute(
            ID_PMP_WALL_ID, self.build_ele.wall_id.value
        )

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
        vertical_tubes_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            vertical_tubes_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        vertical_tubes_attribute_list.add_attribute(
            ID_PMP_WALL_ID, self.build_ele.wall_id.value
        )

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
        horitzontal_tubes_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            horitzontal_tubes_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        horitzontal_tubes_attribute_list.add_attribute(
            ID_PMP_WALL_ID, self.build_ele.wall_id.value
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
        rea_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            rea_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        rea_attribute_list.add_attribute(ID_PMP_WALL_ID, self.build_ele.wall_id.value)

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
        falca_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            falca_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        falca_attribute_list.add_attribute(ID_PMP_WALL_ID, self.build_ele.wall_id.value)

        init_i = len(model_ele_list) - len(falcas)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, falca_attribute_list.get_attribute_list()
            )

        for elem in optionals_elements:
            model_ele_list.append_geometry_3d(elem, props_optional_elements)

        if polyhedron_socket:
            model_ele_list.append_geometry_3d(polyhedron_socket, props_encaix)

        box_shutter = self.create_box_shutter()
        for elem in box_shutter:
            model_ele_list.append_geometry_3d(
                elem, props_box_shutter
            )  # use same color from premarc

        window_3d, window_2d = self.create_premarc_window()
        for elem in window_3d:
            model_ele_list.append_geometry_3d(elem, props_window)

        window_attribute_list = BuildingElementAttributeList()
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_codipanell_id, VAL_PMP_FG_FUS_CODI_PANELL
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_codi_id, VAL_PMP_FG_FUS_CODI
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_unitats_id, VAL_PMP_FG_FUS_UNITATS
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_material_id, VAL_PMP_FG_FUS_MATERIAL
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_color_id, VAL_PMP_FG_FUS_COLOR
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_mides_id, VAL_PMP_FG_FUS_MIDES
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_model_perfil_id, VAL_PMP_FG_FUS_MODEL_PERFIL
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_fulles_id, VAL_PMP_FG_FUS_FULLES
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_tipus_fulles_id, VAL_PMP_FG_FUS_TIPUS_FULLES
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_posicio_maneta_id, VAL_PMP_FG_FUS_POSICIO_MANETA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_vidriera_id, VAL_PMP_FG_FUS_VIDRIERA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_comp_vidriera_id, VAL_PMP_FG_FUS_COMP_VIDRIERA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_persiana_id, VAL_PMP_FG_FUS_PERSIANA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_ampit_id, VAL_PMP_FG_FUS_AMPIT
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_aplacat_fa_id, VAL_PMP_FG_FUS_APLACAT_FA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_comp_fust_id, VAL_PMP_FG_FUS_COMP_FUST
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_volada_fust_id, VAL_PMP_FG_FUS_VOLADA_FUST
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_pintura_obra_id, VAL_PMP_FG_FUS_PINTURA_OBRA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_barana_id, VAL_PMP_FG_FUS_BARANA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_mosquitera_id, VAL_PMP_FG_FUS_MOSQUITERA
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_marge_id, VAL_PMP_FG_FUS_MARGE
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_detail_id, VAL_PMP_FG_FUS_DETAIL
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fus_tapajunts_id, VAL_PMP_FG_FUS_TAPAJUNTS
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_fusteria_tipus_muntatge_id, VAL_PMP_FG_FUSTERIA_TIPUS_MUNTATGE
        )
        window_attribute_list.add_attribute(
            self.pmp_fg_muntatge_id, VAL_PMP_FG_MUNTATGE
        )
        window_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            window_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        window_attribute_list.add_attribute(
            ID_PMP_WALL_ID, self.build_ele.wall_id.value
        )

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

        ampit, ampit_2d, ampit_edge_fg, ampit_edge_add = self.create_premarc_ampit()
        for elem in ampit:
            model_ele_list.append_geometry_3d(elem, props_ampit)

        ampit_attribute_list = BuildingElementAttributeList()
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_detail_id, VAL_PMP_FG_AMPIT_DETAIL
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_esq_id, VAL_PMP_FG_AMPIT_ESQ
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_dre_id, VAL_PMP_FG_AMPIT_DRE
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_sup_id, VAL_PMP_FG_AMPIT_SUP
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_inf_id, VAL_PMP_FG_AMPIT_INF
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_1_id, VAL_PMP_FG_AMPIT_REF_1
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_2_id, VAL_PMP_FG_AMPIT_REF_2
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_parts_id, VAL_PMP_FG_AMPIT_PARTS
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_muntantge_id, VAL_PMP_FG_AMPIT_MUNTANTGE
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_afegit_id, VAL_PMP_FG_AMPIT_AFEGIT
        )
        ampit_attribute_list.add_attribute(
            self.pmp_fg_ampit_retall_id, VAL_PMP_FG_AMPIT_RETALL
        )
        ampit_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            ampit_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        ampit_attribute_list.add_attribute(ID_PMP_WALL_ID, self.build_ele.wall_id.value)

        init_i = len(model_ele_list) - len(ampit)
        for i in range(init_i, len(model_ele_list)):
            model_ele_list.set_element_attributes(
                i, ampit_attribute_list.get_attribute_list()
            )

        ampit_edge_attribute_list = BuildingElementAttributeList()
        ampit_edge_attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_1_id, VAL_PMP_FG_AMPIT_REF_1
        )
        ampit_edge_attribute_list.add_attribute(
            self.pmp_fg_ampit_ref_2_id, VAL_PMP_FG_AMPIT_REF_2
        )
        ampit_edge_attribute_list.add_attribute(
            self.pmp_fg_ampit_parts_id, VAL_PMP_FG_AMPIT_PARTS
        )
        ampit_edge_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            ampit_edge_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        ampit_edge_attribute_list.add_attribute(
            ID_PMP_WALL_ID, self.build_ele.wall_id.value
        )

        model_ele_list.append_geometry_3d(ampit_edge_fg, props_ampit_eix_fg)
        model_ele_list.set_element_attributes(
            len(model_ele_list) - 1, ampit_edge_attribute_list.get_attribute_list()
        )

        if len(ampit_edge_add) > 0:
            model_ele_list.append_geometry_3d(ampit_edge_add, props_ampit_eix_add)
            model_ele_list.set_element_attributes(
                len(model_ele_list) - 1, ampit_edge_attribute_list.get_attribute_list()
            )

        model_ele_list.append_geometry_2d(ampit_2d, props_ampit)

        layer_imperm_id = AllplanBaseElements.LayerService.GetIDByShortName(
            IMPERM_LAYER, self.document
        )
        props_imperm = AllplanBaseElements.CommonProperties()
        props_imperm.Layer = layer_imperm_id

        if self.build_ele.imperm_type.value == "Tela Asfàltica":
            imperm_type = "A"
            props_imperm.Color = 122
        elif self.build_ele.imperm_type.value == "PVC":
            imperm_type = "B"
            props_imperm.Color = 74
        else:
            imperm_type = "C"
            props_imperm.Color = 106

        imperm = self.create_impermeabilitzacio()
        for elem in imperm:
            model_ele_list.append_geometry_3d(elem, props_imperm)

        imperm_attribute_list = BuildingElementAttributeList()
        imperm_attribute_list.add_attribute(
            self.pmp_tipus_impermeabilitzacio_id, imperm_type
        )
        imperm_attribute_list.add_attribute(
            self.pmp_id_premarc_id, self.val_pmp_id_premarc
        )
        if self.selected_wall:
            imperm_attribute_list.add_attribute(
                self.pmp_pare_id, self.get_wall_material_name(self.selected_wall)
            )
        imperm_attribute_list.add_attribute(
            ID_PMP_WALL_ID, self.build_ele.wall_id.value
        )
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
        xps_thickness = 40 if self.xps_type == "XPS" else 120
        xps_thickness_ind_size = xps_thickness - 160
        if self.xps_thickness_ind:
            xps_thickness_ind_size = self.xps_thickness

        pos_bottom = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0 - xps_thickness, 0, 0 - xps_thickness)
        )
        pos_top = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0 - xps_thickness, 0, 0 + self.heigh)
        )
        pos_left = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0 - xps_thickness, 0, 0)
        )
        pos_right = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.width, 0, 0))

        cuboid_bottom = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_bottom,
            self.width + (xps_thickness * 2),
            xps_thickness_ind_size,
            xps_thickness,
        )
        cuboid_bottom = AllplanGeo.Move(
            cuboid_bottom,
            AllplanGeo.Vector3D(
                0, -self.thickness - xps_thickness_ind_size, -self.heigh
            ),
        )

        cuboid_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top,
            self.width + (xps_thickness * 2),
            xps_thickness_ind_size,
            xps_thickness,
        )
        cuboid_top = AllplanGeo.Move(
            cuboid_top,
            AllplanGeo.Vector3D(
                0, -self.thickness - xps_thickness_ind_size, -self.heigh
            ),
        )

        cuboid_left = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_left, xps_thickness, xps_thickness_ind_size, self.heigh
        )
        cuboid_left = AllplanGeo.Move(
            cuboid_left,
            AllplanGeo.Vector3D(
                0, -self.thickness - xps_thickness_ind_size, -self.heigh
            ),
        )

        cuboid_right = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_right, xps_thickness, xps_thickness_ind_size, self.heigh
        )
        cuboid_right = AllplanGeo.Move(
            cuboid_right,
            AllplanGeo.Vector3D(
                0, -self.thickness - xps_thickness_ind_size, -self.heigh
            ),
        )

        elems = [cuboid_bottom, cuboid_top, cuboid_left, cuboid_right]

        # Manage Open Premarc
        match self.build_ele.ComboBoxAbiertoCerrado.value:
            case "OBERT FEMELLA DRETA":
                elems.remove(cuboid_right)
            case "OBERT FEMELLA ESQUERRA":
                elems.remove(cuboid_left)
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

        # Manage Disable XPS
        if self.build_ele.DisableTopXPS.value:
            if cuboid_top in elems:
                elems.remove(cuboid_top)
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
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, -1 * THICKNESS_MM))
        elif direction == "frame_bottom":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, 1 * THICKNESS_MM))
        elif direction == "frame_left":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(1 * THICKNESS_MM, 0, 0))
        elif direction == "frame_right":
            extruded_solid.SetDirection(AllplanGeo.Vector3D(-1 * THICKNESS_MM, 0, 0))
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
        wall_center = (
            self.build_ele.thickness_wall.value / 2
            if self.build_ele.enable_manual_thickness.value
            else self._get_wall_thickness(self.selected_wall) / 2
        )
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

        wall_center = (
            self.build_ele.thickness_wall.value / 2
            if self.build_ele.enable_manual_thickness.value
            else self._get_wall_thickness(self.selected_wall) / 2
        )
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

    def create_origin_falca_top(self) -> AllplanGeo.Polygon3D:

        frame_falca = AllplanGeo.Polygon3D()
        frame_falca += AllplanGeo.Point3D(0, 0, 0)  # P1
        frame_falca += AllplanGeo.Point3D(0, 0, HEIGHT_FALCA)  # P2
        frame_falca += AllplanGeo.Point3D(0, -MINUS_THICKNESS_FALCA, HEIGHT_FALCA)  # P3
        frame_falca += AllplanGeo.Point3D(0, -THICKNESS_FALCA, MINUS_HEIGHT_FALCA)  # P4
        frame_falca += AllplanGeo.Point3D(0, -THICKNESS_FALCA, 0)  # P5
        frame_falca += AllplanGeo.Point3D(0, 0, 0)
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
        Z of the lowest face of the U-beam (z0): opening plane minus U_PROFILE_Z_INTO_AMPIT_DIP_MM
        so the profile sits one step into the premarc dip (same magnitude as frame_bottom extrusion).
        """
        adj = float(U_PROFILE_BASE_Z_ADJUST_MM)
        z_top = self._u_sill_top_z_mm()
        eps = float(U_SILL_CONTACT_Z_EPSILON_MM)
        dip = float(U_PROFILE_Z_INTO_AMPIT_DIP_MM)
        return z_top + eps + adj - dip

    def _resolve_u_profile_y_anchor(self) -> str:
        """Palette ComboBoxUChannelYAnchor overrides module U_PROFILE_SILL_Y_ANCHOR when set."""
        combo = getattr(self.build_ele, "ComboBoxUChannelYAnchor", None)
        if combo is not None:
            v = getattr(combo, "value", None)
            if isinstance(v, str) and v.strip():
                return v.strip().lower().replace("-", "_")
        return (
            (U_PROFILE_SILL_Y_ANCHOR or "pit_span_from_outer_lip")
            .strip()
            .lower()
            .replace("-", "_")
        )

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

        frame_bottom = AllplanGeo.Polygon3D()
        frame_bottom += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(self.width, -self.thickness, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(self.width, 0, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(0, 0, -self.heigh)
        frame_bottom += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)

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
        frame_top += AllplanGeo.Point3D(0, -self.thickness, 0)
        frame_top += AllplanGeo.Point3D(self.width, -self.thickness, 0)
        frame_top += AllplanGeo.Point3D(self.width, 0, 0)
        frame_top += AllplanGeo.Point3D(0, 0, 0)
        frame_top += AllplanGeo.Point3D(0, -self.thickness, 0)

        error_code, polyhedron_top = self.extrude_frame(frame_top, "frame_top")

        # Fix dimensions frame top
        # transformation_matrix = AllplanGeo.Matrix3D()
        # scale_factor_x = (self.width + THICKNESS_MM * 2) / self.width
        # transformation_matrix.SetScaling(scale_factor_x,1,1)

        # polyhedron_top_translated = AllplanGeo.Transform(polyhedron_top, transformation_matrix)
        # translation_vector = AllplanGeo.Vector3D(-THICKNESS_MM,0,0)
        # polyhedron_top = AllplanGeo.Move(polyhedron_top_translated, translation_vector)
        polyhedron_premarc_list.append(polyhedron_top)

        frame_left = AllplanGeo.Polygon3D()
        frame_left += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)
        frame_left += AllplanGeo.Point3D(0, 0, -self.heigh)
        frame_left += AllplanGeo.Point3D(0, 0, 0)
        frame_left += AllplanGeo.Point3D(0, -self.thickness, 0)
        frame_left += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)

        error_code, polyhedron_left = self.extrude_frame(frame_left, "frame_left")
        polyhedron_premarc_list.append(polyhedron_left)

        frame_right = AllplanGeo.Polygon3D()
        frame_right += AllplanGeo.Point3D(self.width, -self.thickness, -self.heigh)
        frame_right += AllplanGeo.Point3D(self.width, 0, -self.heigh)
        frame_right += AllplanGeo.Point3D(self.width, 0, 0)
        frame_right += AllplanGeo.Point3D(self.width, -self.thickness, 0)
        frame_right += AllplanGeo.Point3D(self.width, -self.thickness, -self.heigh)

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
        error_code, polyhedron_finish_top = self.extrude_frame(
            frame_finish_top, "frame_finish_top"
        )
        polyhedron_premarc_list.append(polyhedron_finish_top)

        frame_finish_left = AllplanGeo.Polygon3D()
        frame_finish_left += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)
        frame_finish_left += AllplanGeo.Point3D(0, -self.thickness, 0)
        frame_finish_left += AllplanGeo.Point3D(-23, -self.thickness, 0)
        frame_finish_left += AllplanGeo.Point3D(-23, -self.thickness, -self.heigh)
        frame_finish_left += AllplanGeo.Point3D(0, -self.thickness, -self.heigh)
        error_code, polyhedron_finish_left = self.extrude_frame(
            frame_finish_left, "frame_finish_left"
        )
        polyhedron_premarc_list.append(polyhedron_finish_left)

        frame_finish_right = AllplanGeo.Polygon3D()
        frame_finish_right += AllplanGeo.Point3D(
            self.width, -self.thickness, -self.heigh
        )
        frame_finish_right += AllplanGeo.Point3D(
            self.width + 23, -self.thickness, -self.heigh
        )
        frame_finish_right += AllplanGeo.Point3D(self.width + 23, -self.thickness, 0)
        frame_finish_right += AllplanGeo.Point3D(self.width, -self.thickness, 0)
        frame_finish_right += AllplanGeo.Point3D(
            self.width, -self.thickness, -self.heigh
        )
        error_code, polyhedron_finish_right = self.extrude_frame(
            frame_finish_right, "frame_finish_right"
        )
        polyhedron_premarc_list.append(polyhedron_finish_right)

        ### Tubs
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
        translation_vector = AllplanGeo.Vector3D(0, -0.1, -(self.heigh))
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
        axis_point = AllplanGeo.Point3D(center_x, 0, -self.heigh)
        rotation_axis = AllplanGeo.Axis3D(axis_point, AllplanGeo.Vector3D(1, 0, 0))
        # Calculate rotation angle based on thickness
        CO = 10
        CA = self.thickness_premarc - LENGTH_REBAJES_MM

        angulo_radianes = math.atan2(CO, CA)
        angulo_grados = math.degrees(angulo_radianes)

        rotation_angle = AllplanGeo.Angle.FromDeg(-angulo_grados)

        polyhedron_bottom_grade_with_rebaje = AllplanGeo.Rotate(
            bottom_rebaje, rotation_axis, rotation_angle
        )

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

        if poly_base_no_slope is None:
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
                    case "REB. BAIX":  # Rebaje inferior
                        print("Rebaje Selected REB. BAIX")
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

        elems = [
            polyhedron_premarc_union,
            polyhedron_other_elements_list,
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
        ]
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

        substract_rebaje = []

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
        return d.get(option) == 1 and d.get("NO") == 0

    def bottom_rebaje_enabled(self):
        list_rebajes = list(
            zip(
                self.build_ele.valueListaRebajes.value,
                self.build_ele.RebajesOptions.value,
            )
        )
        d = dict(list_rebajes)
        return d.get("REB. BAIX") == 1 and d.get("NO") == 0

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
        if direction_open_premarc in values_direction_right:
            return "RIGHT"
        elif direction_open_premarc in values_direction_left:
            return "LEFT"
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

        # Manage config UI
        box_shutter_list = []
        match (self.build_ele.ComboBoxPersianas.value):
            case "NO":
                print("Persiana Selected NO. Nothing to do")
                box_shutter_list = []
            case "MONOBLOCK OCULT":
                print("MONOBLOCK OCULT")
                box_shutter_list.append(polyhedron_box_shutter)
            case "LAMISOL VIST":
                print("LAMISOL VIST")
                box_shutter_list.append(polyhedron_box_shutter)
            case "METALUNIC VIST":
                print("METALUNIC VIST")
                box_shutter_list.append(polyhedron_box_shutter)
            case "FALS CALAIX":
                print("FALS CALAIX")
                box_shutter_list.append(polyhedron_box_shutter)
            case _:
                print("Persiana Selected default")
                box_shutter_list = []

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
        if self.get_direction_open_premarc() == "RIGHT":
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

    def create_premarc_ampit(self):
        fondo_ampits_top = self.thickness - 63 - 2 + 3 + 11

        diff = self.fondo_ampits - fondo_ampits_top
        self.retall_ampits = 0
        self.afegit_ampits = 0
        if diff > 0:
            self.retall_ampits = diff
        else:
            self.afegit_ampits = math.fabs(diff)

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

        total_ampits = self.width // self.llarg_ampits
        length_done = 0

        for i in range(0, int(total_ampits)):
            if (
                ampit := self.create_ampit(
                    length_done, self.llarg_ampits, fondo_ampits_top
                )
            ) is not None:
                ampit = AllplanGeo.Move(
                    ampit, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
                )
                final_result_3d.append(ampit)
                cuboid2d = AllplanGeo.Polygon2D.CreateRectangle(
                    AllplanGeo.Point2D(length_done, 63 + 2),
                    AllplanGeo.Point2D(
                        length_done + self.llarg_ampits, fondo_ampits_top + 63 + 2
                    ),
                )
                cuboid2d = AllplanGeo.Move(
                    cuboid2d, AllplanGeo.Vector2D(0, -self.thickness)
                )
                final_result_2d.append(cuboid2d)

            length_done += self.llarg_ampits

        last_ampit = self.width - length_done
        if (
            last_ampit > 0
            and (ampit := self.create_ampit(length_done, last_ampit, fondo_ampits_top))
            is not None
        ):
            ampit = AllplanGeo.Move(
                ampit, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
            )
            final_result_3d.append(ampit)
            cuboid2d = AllplanGeo.Polygon2D.CreateRectangle(
                AllplanGeo.Point2D(length_done, 63 + 2),
                AllplanGeo.Point2D(length_done + last_ampit, fondo_ampits_top + 63 + 2),
            )
            cuboid2d = AllplanGeo.Move(
                cuboid2d, AllplanGeo.Vector2D(0, -self.thickness)
            )
            final_result_2d.append(cuboid2d)

        edge_fg = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, self.thickness, 3 + 11),
            AllplanGeo.Point3D(self.width, self.thickness, 3 + 11),
        )
        edge_fg = AllplanGeo.Move(
            edge_fg, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        )

        edge_add_list = []
        if self.afegit_ampits > 0:
            edge_add = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, self.afegit_ampits + 63 + 2, 3 + 11),
                AllplanGeo.Point3D(self.width, self.afegit_ampits + 63 + 2, 3 + 11),
            )
            edge_add = AllplanGeo.Move(
                edge_add, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
            )
            edge_add_list = [edge_add]

        self.retall_ampits_manual = False
        self.afegit_ampits_manual = False

        return final_result_3d, final_result_2d, [edge_fg], edge_add_list

    def create_ampit(self, init_x, llarg_ampit, fondo_ampit):
        pos_top = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(init_x, 63 + 2, 3))
        pos_front = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(init_x, fondo_ampit + 63 + 2 - 11, 3 + 11 - 34)
        )

        cuboid_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top, llarg_ampit, fondo_ampit, 11
        )
        cuboid_front = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_front, llarg_ampit, 11, 34
        )

        ok, union = AllplanGeo.MakeUnion(cuboid_top, cuboid_front)
        if ok is AllplanGeo.eGeometryErrorCode.eOK:
            return union

        return None

    def create_impermeabilitzacio(self):
        pos_top = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, self.socket_width, 3)
        )
        pos_front_socket = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, self.socket_width, 3)
        )
        pos_top_socket = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(0, -3, self.socket_height)
        )

        imperm_top = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top, self.width, self.thickness - self.socket_width, 3
        )
        imperm_front_socket = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_front_socket, self.width, 3, self.socket_height
        )
        imperm_top_socket = AllplanGeo.Polyhedron3D.CreateCuboid(
            pos_top_socket, self.width, self.socket_width + 3, 3
        )

        err, union = AllplanGeo.MakeUnion(imperm_top, imperm_front_socket)
        if err == AllplanGeo.eGeometryErrorCode.eOK:
            err, union = AllplanGeo.MakeUnion(union, imperm_top_socket)
            if err == AllplanGeo.eGeometryErrorCode.eOK:
                imperm = AllplanGeo.Move(
                    union, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
                )
                return [imperm]

        imperm_top = AllplanGeo.Move(
            imperm_top, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        )
        imperm_front_socket = AllplanGeo.Move(
            imperm_front_socket, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        )
        imperm_top_socket = AllplanGeo.Move(
            imperm_top_socket, AllplanGeo.Vector3D(0, -self.thickness, -self.heigh)
        )

        return [imperm_top, imperm_front_socket, imperm_top_socket]

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
        pos_left = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 40, Z_position))

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
        vector_move_right = AllplanGeo.Vector3D(self.width - 3, 0, 0)
        # vector_move_left = AllplanGeo.Vector3D(0,self.width, 0)
        if self.build_ele.EnableRetallGanxo.value and self.get_direction_retall_ganxo():
            if self.get_direction_retall_ganxo() == "RIGHT":
                cuboid_retall = cuboid_retall_origin
            elif self.get_direction_retall_ganxo() == "LEFT":
                cuboid_retall = AllplanGeo.Move(cuboid_retall_origin, vector_move_right)
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

        self.val_pmp_fg_wall_name = self.build_ele.wall_id.value
        self.val_pmp_id_premarc = self.build_ele.id_premarc.value
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
        # self.val_pmp_fg_ampit_muntantge         = self.build_ele.INPUT_PMP_FG_AMPIT_MUNTANTGE.value
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
                }

                # 5. GENERAR hash único (SHA224)
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
