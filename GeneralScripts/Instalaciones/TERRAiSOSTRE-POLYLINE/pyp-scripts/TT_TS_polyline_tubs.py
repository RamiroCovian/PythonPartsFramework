"""
Script for Line3DInteractor
"""
import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_Input as AllplanIFW
import GeometryValidate as GeometryValidate
import VisualScriptService as VisualScriptService
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Utility as AllplanUtil

import winreg
import subprocess
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import collections
import random
import ctypes

def install_packages():
    prg_path = AllplanSettings.AllplanPaths.GetPrgPath() + "\\"
    package = "numpy"



    target_dir  = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
    print("target_dir ETC: ")
    print(target_dir)
    subprocess.check_call([prg_path + "Python\\Python.exe", "-m", "pip", "install", "--target", target_dir,"--upgrade", package])

    target_dir  = f"{AllplanSettings.AllplanPaths.GetUsrPath()}Local\\PythonParts-site-packages"
    print("target_dir USR: ")
    print(target_dir)
    # subprocess.check_call([prg_path + "Python\\Python.exe", "-m", "pip", "install", "--target", target_dir,"--upgrade", package])

try:
    import numpy as np
except ImportError:
    install_packages()
    print("instalando paquetes: numpy")
    import numpy as np
#import numpy as np

from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup

#from .TD_Horitzontal_PP import PP_TD_Horitzontal
#from .TD_Vertical_PP import PP_TD_Vertical
#from .TD_Vertical_PP_Points import PP_TD_Vertical
#from .TD_TUB_L import PP_IS_TUB_L
#from .TD_TUB_L_Points import PP_IS_TUB_L

from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
from CreateElementResult import CreateElementResult


print('Load Polyline3DInteractor.py')


def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    del build_ele
    del version


    #subprocess.check_call([prg_path + "Python\\Python.exe", "-m", "pip", "cache", "purge"])
    #subprocess.check_call([prg_path + "Python\\Python.exe", "-m", "pip", "cache", "--target", target_dir,"purge"])
    #subprocess.check_call([prg_path + "Python\\Python.exe", "-m", "pip", "install", "--target", target_dir,"--upgrade", package, "--force-reinstall"])
    #pip install -r requirements.txt --force-reinstall


    #AllplanUtil.ShowMessageBox("The installation log is shown in the Trace window", AllplanUtil.MB_OK)
    #try:
    #    fp, pathname, description = imp.find_module(package, [target_dir])
    #    imp.load_module(package, fp, pathname, description)
    #except Exception as e:
    #    print("There was a problem loading startup file: ", target_dir)
    #    print(repr(e))



    return True

    # Support all versions
    return True

def create_element(build_ele, doc):
    """
    Creation of element (only necessary for the library preview)

    Args:
        build_ele: the building element.
        doc:       input document
    """

    #del build_ele
    del doc

    com_prop = AllplanBaseElements.CommonProperties()

    com_prop.GetGlobalProperties()

    poly = AllplanGeo.Polyline3D()
    poly += AllplanGeo.Point3D(0,0,0)
    poly += AllplanGeo.Point3D(0,0,1000)
    poly += AllplanGeo.Point3D(500,0,1000)
    poly += AllplanGeo.Point3D(500,500,2000)

    '''
    horitzontalPP = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruix.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value, #ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParINF.value, desplXSeparat, desplYSeparat) #EncaixosPar)


    pythonpartgroup = PythonPartGroup (build_ele.NomTD.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)


    model_elem_list = pythonpartgroup.create()

    '''
    model_ele_list = [AllplanBasisElements.ModelElement3D(com_prop, poly)]

    return (model_ele_list, None, None)
    group_elems = self.model_Python

    #PythonPart ("PP_TD_Reforc_reforc", parameter_list = reforcRef.get_params_list(),
    #                                    hash_value = reforcRef.hash(), python_file = reforcRef.filename(),
    #                                    views = table_viewsAuxR, matrix = matrix_AuxR, common_props = common_propsR, attribute_list = table_attr_listAux)

    pythonpartgroup = PythonPartGroup ("build_ele.NomTD.value", build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)


    model_elem_list = pythonpartgroup.create()

    return CreateElementResult(elements=            model_elem_list,
                                handles=            [],
                                preview_elements=   model_elem_list)



def create_interactor(coord_input, pyp_path, str_table_service):
    """
    Create the interactor

    Args:
        coord_input:        coordinate input
        pyp_path:           path of the pyp file
        str_table_service:  string table service
    """

    return Line3DInteractor(coord_input, pyp_path, str_table_service)


def on_control_event(build_ele, event_id: int):
    print("exterior button: " + str(event_id))
    if event_id == 1006:
        pos = build_ele.posIniAutoL.value
        nForats = build_ele.nForatsAutoL.value
        orientacio = build_ele.orientacioAutoL.value
        pos = build_ele.posIniAutoL.value
        posF = build_ele.posFinAutoL.value
        posY = build_ele.posYAutoL.value#build_ele.BarraAltura.value/2
        llargada = build_ele.llargadaAutoL.value
        amplada = build_ele.ampladaAutoL.value
        for nForat in range(0, nForats):
            if len(build_ele.ForatsParAut.value) <= nForat:
                TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio PosicioY Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
                bob = TDCollection( Forat = True,
                                    orientacio = orientacio,
                                    Posicio = pos,
                                    PosicioY = posY,
                                    Llargada = llargada,
                                    Amplada = amplada,
                                    Complet = False,
                                    LlargadaB = 20,
                                    AmpladaB = 10,
                                    MostrarBox = False,
                                    Separator = '')
                build_ele.ForatsParAut.value.append(bob)
            else:
                build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Forat = True)
                build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(orientacio = orientacio)
                build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Posicio = pos)
                build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(PosicioY = posY)
                build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Llargada = llargada)
                build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Amplada = amplada)
            pos += build_ele.distanciaAutoL
            if nForat == build_ele.nForatsAutoL.value - 2:
                llargadaL = 0
                if build_ele.mantenirLlargadaSup.value:
                    llargadaL = build_ele.BarraLlargada.value
                else:
                    llargadaL = build_ele.BarraLlargadaSupInd.value
                pos = llargadaL - posF
    elif event_id == 1007:
        build_ele.ForatsParAut.value = []


class Line3DInteractor():
    """
    Definition of class Line3DInteractor
    """

    def __init__(self, coord_input, pyp_path, str_table_service):
        """
        Initialization of class Line3DInteractor

        Args:
            coord_input:        coordinate input
            pyp_path:           path of the pyp file
            str_table_service:  string table service
        """

        self.coord_input            = coord_input
        self.pyp_path               = pyp_path
        self.str_table_service      = str_table_service
        self.first_point_input      = True
        self.first_point            = AllplanGeo.Point3D()
        self.model_ele_list         = []
        self.model_Python           = []
        self.model_Python_preview   = []
        self.pythonElem             = []
        self.build_ele_service = BuildingElementService()

        ####
        self.current_point           = AllplanGeo.Point3D()
        self.valid_input             = False
        self.b_use_input_pnt         = True
        self.polyline_lenght         = 0.0
        self.frist_run_transf        = True
        self.cont_polyline           = AllplanGeo.Polyline3D()

        self.click                   = False


        #----------------- read the data and show the palette

        result, self.build_ele_script, self.build_ele_list, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(pyp_path + "\\TERRA_Tub.pal", self.str_table_service.str_table, False,
                                                      self.str_table_service.material_str_table)

        if not result:
            return

        self.palette_service = BuildingElementPaletteService(self.build_ele_list, self.build_ele_composite,
                                                             self.build_ele_script,
                                                             self.control_props_list, self.file_name)

        self.palette_service.show_palette(part_name)

        self.points         = []
        self.direccions     = []


        #----------------- get the properties and start the input

        self.com_prop = AllplanBaseElements.CommonProperties()

        self.set_common_properties()

        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert("Punt Inici"))


    def set_common_properties(self):
        """
        Set the common properties
        """

        self.build_ele = self.build_ele_list[0]

        self.com_prop.Color         = self.build_ele.Color.value
        self.com_prop.Pen           = self.build_ele.Pen.value
        self.com_prop.Stroke        = self.build_ele.Stroke.value
        self.com_prop.ColorByLayer  = self.build_ele.ColorByLayer.value
        self.com_prop.PenByLayer    = self.build_ele.PenByLayer.value
        self.com_prop.StrokeByLayer = self.build_ele.StrokeByLayer.value
        self.com_prop.Layer         = self.build_ele.Layer.value

        self.layer                  = self.build_ele.Layer.value
        if self.build_ele.SelectorLayersTDEN.value == "TD":
            if self.build_ele.SelectorTerraSostre.value == "TERRA":
                if self.build_ele.SelectorTipusTub.value == "Tub":
                    self.layer                  = 40191 #TD_TUBS_TERRA
                else:
                    self.layer                  = 40192 #L_L_TERRA
            else: # SOSTRE
                if self.build_ele.SelectorTipusTub.value == "Tub":
                    self.layer                  = 40189 #TD_TUBS_SOSTRE
                else:
                    self.layer                  = 40190 #TD_L_SOSTRE
        else: #EN
            if self.build_ele.SelectorTerraSostre.value == "TERRA":
                if self.build_ele.SelectorTipusTub.value == "Tub":
                    self.layer                  = 40195 #EN_TUBS_TERRA
                else:
                    self.layer                  = 40196 #EN_L_TERRA
            else: # SOSTRE
                if self.build_ele.SelectorTipusTub.value == "Tub":
                    self.layer                  = 40193 #EN_TUBS_SOSTRE
                else:
                    self.layer                  = 40194 #EN_L_SOSTRE

        self.group_elems = []

        self.DistanciaEntreTD       = self.build_ele.DistanciaEntreTD.value
        self.BarraAmple             = self.build_ele.BarraAmple.value
        self.BarraAltura            = self.build_ele.BarraAltura.value
        self.BarraLlargada          = self.build_ele.BarraLlargada.value
        self.BarraGruix             = self.build_ele.BarraGruix.value
        self.BarraAmpleL             = self.build_ele.BarraAmpleL.value
        self.BarraAlturaL            = self.build_ele.BarraAlturaL.value
        self.BarraGruixL             = self.build_ele.BarraGruixL.value


        self.ColisPar               = self.build_ele.ColisPar.value
        self.PotaPar                = self.build_ele.PotaPar.value
        self.ForatsPar              = self.build_ele.ForatsPar.value

        self.Ample_forat_femella    = self.build_ele.Ample_forat_femella.value
        self.Altura_forat_femella   = self.build_ele.Altura_forat_femella.value
        self.Separacio_forat_femella= self.build_ele.Separacio_forat_femella.value
        self.Femelles               = self.build_ele.Femelles.value

        self.posicio_centre_masses  = self.build_ele.posicio_centre_masses.value
        self.IsFirstCancam          = self.build_ele.IsFirstCancam.value
        self.Dis1cancam             = self.build_ele.Dis1cancam.value
        self.IsSecondCancam         = self.build_ele.IsSecondCancam.value
        self.Dis2cancam             = self.build_ele.Dis2cancam.value

        self.PestanyaSuperior       = self.build_ele.PestanyaSuperior.value
        self.PestanyaInferior       = self.build_ele.PestanyaInferior.value
        self.EncaixosPar            = self.build_ele.EncaixosPar.value

        self.SelectorTerraSostre    = self.build_ele.SelectorTerraSostre.value
        self.SelectorTipusTerra     = self.build_ele.SelectorTipusTerra.value

        self.SelectorTipusTub       = self.build_ele.SelectorTipusTub.value
        self.InvertirLEsqDre         = self.build_ele.InvertirLEsqDre.value
        self.InvertirLSupInf         = self.build_ele.InvertirLSupInf.value

        self.distanciaMaxTub        = self.build_ele.DistanciaMaxTub.value

        self.SeparacioEntreTubs     = self.build_ele.SeparacioEntreTubs.value

        self.distanciaAutoL         = self.build_ele.distanciaAutoL.value
        self.posIniAutoL            = self.build_ele.posIniAutoL.value
        self.posFinAutoL            = self.build_ele.posFinAutoL.value
        self.orientacioAutoL        = self.build_ele.orientacioAutoL.value
        self.llargadaAutoL          = self.build_ele.llargadaAutoL.value
        self.ampladaAutoL           = self.build_ele.ampladaAutoL.value
        self.ForatComplet           = self.build_ele.ForatComplet.value
        self.llargadaAutoLB         = self.build_ele.llargadaAutoLB.value
        self.ampladaAutoLB          = self.build_ele.ampladaAutoLB.value



    def modify_element_property(self, page, name, value):
        """
        Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """


        if ((name == "SelectorTipusTub" and value == "L" ) and self.build_ele_list[0].SelectorTerraSostre.value == "SOSTRE") or \
            ((name == "SelectorTerraSostre" and value == "SOSTRE") and self.build_ele_list[0].SelectorTipusTub.value == "L") :
            self.build_ele_list[0].orientacioAutoL.value = "Sup"
            if self.build_ele_list[0].InvertirLEsqDre.value :
                self.build_ele_list[0].orientacioAutoL.value = "Inf"
            else:
                self.build_ele_list[0].orientacioAutoL.value = "Sup"
        if (name == "SelectorTerraSostre" and value == "TERRA")  :
            self.build_ele_list[0].orientacioAutoL.value = "Sup"
        if (name == "SelectorTipusTerra" and value == "Rajola" ):
            self.build_ele_list[0].ForatsParAut.value = []

        if self.build_ele_list[0].SelectorTipusTub.value == "L" and self.build_ele_list[0].SelectorTerraSostre.value == "SOSTRE":
            if name == "InvertirLEsqDre":
                if value == True:
                    self.build_ele_list[0].orientacioAutoL.value = "Inf"
                else:
                    self.build_ele_list[0].orientacioAutoL.value = "Sup"
        #else:
        #    if name == "InvertirLEsqDre":
        #        if value == True:
        #            self.build_ele_list[0].orientacioAutoL.value = "Dre"
        #        else:
        #            self.build_ele_list[0].orientacioAutoL.value = "Esq"


        update_palette = self.palette_service.modify_element_property(page, name, value)

        if update_palette:
            self.palette_service.update_palette(-1, False)

        self.set_common_properties()


    def on_cancel_function(self):
        """
        Check for input function cancel in case of ESC

        Returns:
            True/False for success.
        """
        if self.valid_input:
            self.create_element()
            self.palette_service.close_palette()
            return True

        self.palette_service.close_palette()
        return True


    def on_preview_draw(self):
        """
        Handles the preview draw event
        """
        print("on_preview_draw")
        if self.first_point_input:
            return

        input_pnt = self.coord_input.GetCurrentPoint(self.first_point).GetPoint()
        self.draw_preview(input_pnt, False)

    def on_mouse_leave(self):
        """
        Handles the mouse leave event
        """
        self.on_preview_draw()


    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        """
        Process the mouse message event

        Args:
            mouse_msg:  the mouse message.
            pnt:        the input point in view coordinates
            msg_info:   additional message info.

        Returns:
            True/False for success.
        """

        input_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point,
                                                   not self.first_point_input).GetPoint()

        #print("input_pnt: " + str(input_pnt))
        self.draw_preview(input_pnt, True)

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        #----------------- New point for polygon
        print("Click new pos")
        if len(self.points) % 2 != 0:
            self.click              = True
        self.current_point = input_pnt
        self.points.append(input_pnt)
        self.direccions.append("Sup")
        if len(self.points) > 1:
            self.valid_input = True

        #----------------- Change to "Next point" input
        if self.first_point_input:
            self.first_point_input = False

        self.coord_input.InitNextPointInput(AllplanIFW.InputStringConvert("Punt Final"))
        if len(self.points) % 2 == 0:
            self.coord_input.InitNextPointInput(AllplanIFW.InputStringConvert("Punt Inici"))
        return True


    def on_control_event(self, event_id: int):
        print("pressed button:_ "+ str(event_id))
        build_ele = self.build_ele_list[0]
        if event_id == 1006:
            self.crear_forats_auto(build_ele.nForatsAutoL.value, build_ele.BarraLlargada.value)
        elif event_id == 1007:
            build_ele.ForatsParAut.value = []

        #elif event_id == 1008:
        #    build_ele.InvertirPos.value = False
        #    #self.InvertirPos.value = False
        #elif event_id == 1009:
        #    build_ele.InvertirPos.value = True


        if event_id == 1008 or event_id == 1009:
            print("InvertirPos: " + str(build_ele.InvertirPos.value))
            build_ele.InvertirPos.value = not build_ele.InvertirPos.value
            self.build_ele.InvertirPos.value = not self.build_ele.InvertirPos.value
            self.build_ele_list[0].InvertirPos.value = not self.build_ele_list[0].InvertirPos.value


        if event_id == 1008 or event_id == 1009 or event_id == 1010:
            if len(self.points) >= 2:
                #borrar self.model_Python
                self.model_Python = []
                self.pythonElem = []
                self.model_Python_preview = []

                posPoint = 0
                for point in self.points:
                    self.click = True
                    #tornar a cridar self.__create_model_element__(input_pnt) amb els punts
                    if posPoint % 2 != 0:
                        self.__create_model_element__(point, posPoint = posPoint)
                    #i el checkbox invertit
                    posPoint += 1


        print("end pressed button:_ "+ str(event_id))



    def create_element(self):
        """
        Create the element

        Args:
            point_list:  Point list
        """
        print("Create_element")
        dmmy_pnt = AllplanGeo.Point3D()
        self.b_use_input_pnt = False
        #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
        #                                   AllplanGeo.Matrix3D(),
        #                                   self.model_Python, [], None)

        #return
        self.polyline_lenght = 0.0 #reset value


        group_elems = self.model_Python

        #for point in self.points:
        return


        pythonpartgroup = PythonPartGroup ("Tub Horitzontal", self.build_ele_list[0].get_params_list(), self.build_ele_list[0].get_hash(),
                                        "DAVIDPolyline3DInteractor.pyp", group_elems)


        model_elem_list = pythonpartgroup.create()

        AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
                                           AllplanGeo.Matrix3D(),
                                           model_elem_list, [], None)

        #return CreateElementResult(elements=            model_elem_list,
        #                            handles=            [],
        #                            preview_elements=   model_elem_list)



    def draw_preview(self, input_pnt, b_use_input_pnt):
        """
        Draw the preview

        Args:
            input_pnt:  Input point
        """
        if len(self.points) < 1:
            return

        if b_use_input_pnt == True:
            self.b_use_input_pnt = True
        else:
            self.b_use_input_pnt = False

        if len(self.points) % 2 == 0:
            self.__create_model_element__(input_pnt)
        else:
            self.__create_model_element__(input_pnt, guardarTubo=True)


        #if not self.model_ele_list:
        #    return
        if not self.model_Python_preview:
            return

        #print("draw_preview")

        AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
                                               AllplanGeo.Matrix3D(),
                                               #self.model_ele_list , False, None)
                                               self.model_ele_list + self.model_Python_preview, False, None)


    def is_negative(self, valor):
        valorString = str(valor)
        if valorString[0] == '-':
            return True
        return False

    def __create_model_element__(self, input_pnt, posPoint = -1, posPreEndPoint = -1, pointPreEnd = AllplanGeo.Point3D(), guardarTubo = True):
        """
        Creates the element
        Args:
            input_pnt:   input point

        Returns:
            Elementlist
        """
        TipusTub = self.SelectorTipusTub
        invertirEsqDre = self.InvertirLEsqDre
        invertirInfSup = self.InvertirLSupInf
        common_props = self.com_prop
        common_props.Layer = self.layer


        if len(self.points) < 1:
            return

        if self.b_use_input_pnt ==False:
            #calc only without mouse movement, this means for create
            self.polyline_lenght = 0.0
            for index in range(1, len(self.points)):
                line_tmp = AllplanGeo.Line3D(self.points[index-1],self.points[index])
                self.polyline_lenght += AllplanGeo.CalcLength(line_tmp)
                self.model_Python_preview.append( AllplanBasisElements.ModelElement3D(common_props, line_tmp))


        if len(self.points) == 1 or guardarTubo == False: #tub en preview

            line = AllplanGeo.Line3D(self.points[len(self.points)-1],input_pnt)
            self.model_ele_list = [AllplanBasisElements.ModelElement3D(self.com_prop, line)]
            self.model_Python_preview = [AllplanBasisElements.ModelElement3D(self.com_prop, line)]



            if len(self.model_Python_preview) > 0:
                    self.model_Python_preview[len(self.model_Python_preview)-1] = AllplanBasisElements.ModelElement3D(common_props, line)
            else:
                self.model_Python_preview.append( AllplanBasisElements.ModelElement3D(common_props, line))

            return

        if len(self.points) >= 2 : # polyline could be created

            #if self.click :
                #print("self.points: " + str(self.points))
                #self.model_ele_list = []
            for index in range(1, len(self.points)):
                line_tmp = AllplanGeo.Line3D(self.points[index-1],self.points[index])
                self.polyline_lenght += AllplanGeo.CalcLength(line_tmp)
                #self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, line_tmp))
                self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, line_tmp))

            #---------------------------------------------

            if self.click:
                print("###### len(self.points)" +str(len(self.points)))
                line_tmp = AllplanGeo.Line3D(self.points[len(self.points)-1],input_pnt)
                self.pythonElem.append(AllplanBasisElements.ModelElement3D(common_props, line_tmp))
                self.model_Python.append(line_tmp)
                self.model_ele_list.append(AllplanBasisElements.ModelElement3D(common_props, line_tmp))


                self.model_Python_preview = []
                #print("-----------------: " + str(len(self.pythonElem)))
                for tub in self.pythonElem: #self.model_Python:
                    self.model_Python_preview.append(tub)

                self.click = False


        if not self.cont_polyline.IsValid():
            return


        #print("HoritzontalPP_Brep creat --------")
        return


    def __transform_base_polygon__(self, path, polyline3D_contur):
        """
        Transforms the base polygon3D

        Args:
            path:               only the first segment is needed
            polyline3D_contur:  will be transformed to placed perpendicular on the first segment of the path

        Returns:
            transformed polyline3D_contur

        """
        pnt1 = path.GetPoint(0)
        pnt2 = path.GetPoint(1)

        diff_x = pnt2.X - pnt1.X
        diff_y = pnt2.Y - pnt1.Y
        diff_z = pnt2.Z - pnt1.Z

        tmp_plane = AllplanGeo.Plane3D(AllplanGeo.Point3D(0,0,0),AllplanGeo.Vector3D(diff_x, diff_y, diff_z))

        matrix = AllplanGeo.Matrix3D()
        matrix = tmp_plane.GetTransformationMatrix()
        result = AllplanGeo.Transform(polyline3D_contur, matrix)
        matrix2 = AllplanGeo.Matrix3D()
        matrix2.SetTranslation(AllplanGeo.Vector3D(pnt1.X, pnt1.Y, pnt1.Z))
        result = AllplanGeo.Transform(result, matrix2)
        return result

    def create_attribute_list(self, value):
        """
        Create an attribute set

        Args:
            value:  double value for attribute 1832 Allfa Zahl03

        Returns:
            AllplanBaseElements.Attributes object filled with attributes
        """
        #------------------ Define attributes for elements
        attr_list = []
        attr_list.append(AllplanBaseElements.AttributeDouble(1832, value))#Allfa Zahl03

        attr_set_list = []
        attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))

        attributes = AllplanBaseElements.Attributes(attr_set_list)
        return attributes

    def crear_forats_auto(self, nForats, llargadaTub):
        build_ele = self.build_ele_list[0]
        pos = self.posIniAutoL
        #nForats = build_ele.nForatsAutoL.value
        orientacio = self.orientacioAutoL
        posF = self.posFinAutoL
        posY = build_ele.posYAutoL.value#build_ele.BarraAltura.value/2
        llargada = self.llargadaAutoL
        amplada  = self.ampladaAutoL
        ForatComplet    = self.ForatComplet
        llargadaAutoLB  = self.llargadaAutoLB
        ampladaAutoLB   = self.ampladaAutoLB
        if self.SelectorTipusTub == "L" and self.SelectorTerraSostre == "SOSTRE":
            posY = self.BarraAmpleL/2 #- amplada
        else:
            posY = self.BarraAltura/2 #- amplada

        if llargadaTub > build_ele.LlargadaMinimaForats.value:
            for nForat in range(0, nForats):
                if orientacio == "Inf" or orientacio == "Sup":
                    if self.SelectorTipusTub == "L"and self.SelectorTerraSostre == "SOSTRE":
                        posY = self.BarraAlturaL/2 #- amplada
                    else:
                        posY = self.BarraAmple/2 #- amplada

                if len(build_ele.ForatsParAut.value) <= nForat:
                    TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio PosicioY Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
                    bob = TDCollection( Forat = True,
                                        orientacio = orientacio,
                                        Posicio = pos,
                                        PosicioY = posY,
                                        Llargada = llargada,
                                        Amplada = amplada,
                                        Complet = ForatComplet,
                                        LlargadaB = llargadaAutoLB,
                                        AmpladaB = ampladaAutoLB,
                                        MostrarBox = False,
                                        Separator = '')
                    build_ele.ForatsParAut.value.append(bob)
                else:
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Forat = True)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(orientacio = orientacio)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Posicio = pos)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(PosicioY = posY)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Llargada = llargada)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Amplada = amplada)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Complet = ForatComplet)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(LlargadaB = llargadaAutoLB)
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(AmpladaB = ampladaAutoLB)
                if pos >= llargadaTub - posF - amplada and nForat != nForats-1:
                    build_ele.ForatsParAut.value[nForat] = build_ele.ForatsParAut.value[nForat]._replace(Forat = False)
                pos += self.distanciaAutoL
                if nForat == nForats - 2:
                    llargadaL = 0
                    #if build_ele.mantenirLlargadaSup.value:
                    #    llargadaL = build_ele.BarraLlargada.value
                    #else:
                    #    llargadaL = build_ele.BarraLlargadaSupInd.value
                    pos = llargadaTub - posF
            for nForat in range(nForats, len(build_ele.ForatsParAut.value) ):
                build_ele.ForatsParAut.value.pop()
        else:
            pos = llargadaTub/2
            if len(build_ele.ForatsParAut.value) == 0:
                TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio PosicioY Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
                bob = TDCollection( Forat = True,
                                    orientacio = orientacio,
                                    Posicio = pos,
                                    PosicioY = posY,
                                    Llargada = llargada,
                                    Amplada = amplada,
                                    Complet = ForatComplet,
                                    LlargadaB = llargadaAutoLB,
                                    AmpladaB = ampladaAutoLB,
                                    MostrarBox = False,
                                    Separator = '')
                build_ele.ForatsParAut.value.append(bob)
            else:
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(Forat = True)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(orientacio = orientacio)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(Posicio = pos)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(PosicioY = posY)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(Llargada = llargada)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(Amplada = amplada)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(Complet = ForatComplet)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(LlargadaB = llargadaAutoLB)
                build_ele.ForatsParAut.value[0] = build_ele.ForatsParAut.value[0]._replace(AmpladaB = ampladaAutoLB)
                pos += self.distanciaAutoL

    def get_posicio_i_llargada_interior(self, angleAjustat, vectorH1POS, correccioX, pntPreEnd):
        """Calcula la posicion y la largada segun la anterior barra y la direcion de la nueva"""

        BarraAmple = self.build_ele_list[0].BarraAmple.value

        if angleAjustat == 0:#Dre
            correccioX = - BarraAmple
            vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
            if self.direccions[len(self.direccions)-2] == "Sup":
                correccioX = + BarraAmple
                vectorH1POS.SetValue(12, pntPreEnd.X - BarraAmple)
                #vectorH1POS.SetValue(14, pntPreEnd.Z - BarraAmple )
            elif self.direccions[len(self.direccions)-2] == "Dre":
                correccioX = 0
                vectorH1POS.SetValue(12, pntPreEnd.X )
            #elif self.direccions[len(self.direccions)-2] == "Inf":
            #    correccioX = + BarraAmple
            #    vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)

        elif angleAjustat == 90:#Sup
            correccioX = - BarraAmple
            if self.direccions[len(self.direccions)-2] == "Esq":
                correccioX = + BarraAmple
                vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)
            elif self.direccions[len(self.direccions)-2] == "Sup":
                correccioX = 0
            elif self.direccions[len(self.direccions)-2] != "Sup":
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)

        elif angleAjustat == 180:#Esq
            correccioX = - BarraAmple
            vectorH1POS.SetValue(12, pntPreEnd.X - BarraAmple)
            if self.direccions[len(self.direccions)-2] == "Inf":
                vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
                correccioX = + BarraAmple
            elif self.direccions[len(self.direccions)-2] == "Sup":
                vectorH1POS.SetValue(12, pntPreEnd.X - BarraAmple)
                correccioX = - BarraAmple
            else:
                correccioX = 0
                vectorH1POS.SetValue(12, pntPreEnd.X )

        elif angleAjustat == 270:#Inf
            correccioX = - BarraAmple
            vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)
            if self.direccions[len(self.direccions)-2] == "Dre":
                correccioX = + BarraAmple
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)
            elif self.direccions[len(self.direccions)-2] == "Esq":
                correccioX = - BarraAmple
                vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)
            else:
                vectorH1POS.SetValue(13, pntPreEnd.Y )
                correccioX = 0

        elif angleAjustat == 360:#Exception
            correccioX = - BarraAmple
            vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)

        return vectorH1POS, correccioX

    def get_posicio_i_llargada_exterior(self, angleAjustat, vectorH1POS, correccioX, pntPreEnd):
        """Calcula la posicion y la largada segun la anterior barra y la direcion de la nueva"""

        BarraAmple = self.BarraAmple

        if angleAjustat == 0:#Dre
            correccioX = - BarraAmple
            vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
            if self.direccions[len(self.direccions)-2] == "Sup":
                vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
            elif self.direccions[len(self.direccions)-2] == "Dre":
                correccioX = 0
                vectorH1POS.SetValue(12, pntPreEnd.X )
            elif self.direccions[len(self.direccions)-2] == "Inf":
                correccioX = + BarraAmple
                vectorH1POS.SetValue(12, pntPreEnd.X - BarraAmple)
                vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)


        elif angleAjustat == 90:#Sup
            vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
            correccioX = - BarraAmple
            if self.direccions[len(self.direccions)-2] == "Esq":
                correccioX = - BarraAmple
                vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)
            elif self.direccions[len(self.direccions)-2] == "Sup":
                correccioX = 0
            elif self.direccions[len(self.direccions)-2] == "Dre":
                correccioX = + BarraAmple
                vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)
            elif self.direccions[len(self.direccions)-2] != "Sup":
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)

        elif angleAjustat == 180:#Esq
            correccioX = + BarraAmple
            vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
            if self.direccions[len(self.direccions)-2] == "Inf":
                vectorH1POS.SetValue(12, pntPreEnd.X - BarraAmple)
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)
                correccioX = -  BarraAmple
            elif self.direccions[len(self.direccions)-2] == "Sup":
                vectorH1POS.SetValue(12, pntPreEnd.X + BarraAmple)
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)
                correccioX = + BarraAmple
            else:
                correccioX = 0
                vectorH1POS.SetValue(12, pntPreEnd.X )

        elif angleAjustat == 270:#Inf
            correccioX = - BarraAmple
            vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)
            if self.direccions[len(self.direccions)-2] == "Dre":
                correccioX = - BarraAmple
                vectorH1POS.SetValue(13, pntPreEnd.Y - BarraAmple)
            elif self.direccions[len(self.direccions)-2] == "Esq":
                correccioX = + BarraAmple
                vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)
                vectorH1POS.SetValue(12, pntPreEnd.X - BarraAmple)
            else:
                vectorH1POS.SetValue(13, pntPreEnd.Y )
                correccioX = 0

        elif angleAjustat == 360:#exception
            correccioX = - BarraAmple
            vectorH1POS.SetValue(13, pntPreEnd.Y + BarraAmple)

        return vectorH1POS, correccioX

    def calcula_regio(self, eje_rotacion, eje_rotacionZ, eje_rotacionY):
        '''
           Planta                         |#|  Alzado                                |#|     Perfil
                  \    |                  |#|                    |    /Y             |#|                     |    /X
            regio = 3  |  regio = 1       |#|   regioAlzado = 3  |  regioAlzado = 1  |#|    regioPerfil = 3  |  regioPerfil = 1
                    \  |                  |#|                    |  /                |#|                     |  /
                    Z\ Y                  |#|                    Z /                 |#|                     Z /
                      \|                  |#|                    |/                  |#|                     |/
           ---------------X-----------    |#|  ---------------X--------------------- |#|   ---------------Y---------------------
                       |                  |#|                    |                   |#|                     |
            regio = 4  |  regio = 2       |#|   regioAlzado = 4  |  regioAlzado = 2  |#|    regioPerfil = 4  |  regioPerfil = 2
                       |                  |#|                    |                   |#|                     |
                       |                  |#|                    |                   |#|                     |
        '''

        regio = None
        regioAlzado = None
        regioPerfil = None

        if self.click:
            #Planta
            print("PLanta:")
            if not self.is_negative(eje_rotacion[1]): #eje_rotacion[1] > 0 :
                print("→")
                if not self.is_negative(eje_rotacion[2]): #eje_rotacion[2] > 0:
                    print("↑")
                    regio = 1
                else:
                    print("↓")
                    regio = 2
            else:# eje_rotacion[1] < 0
                print("←")
                if not self.is_negative(eje_rotacion[2]): #eje_rotacion[2] > 0:
                    print("↑")
                    regio = 3
                else:
                    print("↓")
                    regio = 4

            #Alzado
            print("Alzado:")
            if not self.is_negative(eje_rotacionZ[1]): #eje_rotacion[1] > 0 :
                print("→")
                if not self.is_negative(eje_rotacionZ[0]): #eje_rotacion[2] > 0:
                    print("↑")
                    regioAlzado = 1
                else:
                    print("↓")
                    regioAlzado = 2
            else:# eje_rotacion[1] < 0
                print("←")
                if not self.is_negative(eje_rotacionZ[0]): #eje_rotacion[2] > 0:
                    print("↑")
                    regioAlzado = 3
                else:
                    print("↓")
                    regioAlzado = 4

            #Perfil
            print("Perfil:")
            if not self.is_negative(eje_rotacionY[2]): #eje_rotacion[1] > 0 :
                print("→")
                if not self.is_negative(eje_rotacionY[0]): #eje_rotacion[2] > 0:
                    print("↑")
                    regioPerfil = 1
                else:
                    print("↓")
                    regioPerfil = 2
            else:# eje_rotacion[1] < 0
                print("←")
                if not self.is_negative(eje_rotacionY[0]): #eje_rotacion[2] > 0:
                    print("↑")
                    regioPerfil = 3
                else:
                    print("↓")
                    regioPerfil = 4

    def get_forats_rotats(self):

        femelles = self.build_ele_list[0].ForatsParAut.value
        for nfemella in range(0, len(self.build_ele_list[0].ForatsParAut.value)):
            if self.build_ele_list[0].ForatsParAut.value[nfemella].orientacio == "Sup":
                femelles[nfemella] = femelles[nfemella]._replace(orientacio = "Dre")
            elif self.build_ele_list[0].ForatsParAut.value[nfemella].orientacio == "Inf":
                femelles[nfemella] = femelles[nfemella]._replace(orientacio = "Esq")
            elif self.build_ele_list[0].ForatsParAut.value[nfemella].orientacio == "Esq":
                femelles[nfemella] = femelles[nfemella]._replace(orientacio = "Sup")
            else:
                femelles[nfemella] = femelles[nfemella]._replace(orientacio = "Inf")
            #print(str(nfemella)+" - "+str(femelles[nfemella]))

        return femelles



def normalize(v):
    """Normaliza un vector"""
    norm = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return [v[i] / norm for i in range(3)]

def dot_product(v1, v2):
    """Calcula el producto punto entre dos vectores"""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def cross_product(v1, v2):
    """Calcula el producto cruzado entre dos vectores"""
    return [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]



def dividirAtribut(atributSencer):
    cara_ = atributSencer
    cara_1 = "#"
    cara_2 = "#"
    if len(cara_) > 200:
        cara_1 = cara_[200:]
        if len(cara_1) > 200:
            cara_2 = cara_1[200:]
            if len(cara_2) > 200:
                #ctypes.windll.user32.MessageBoxW(0, "Hi ha un atribut mes llarg de 600 caracters", 0)
                print("Hi ha un atribut mes llarg de 600 caracters")
            cara_1 = cara_1[0:200]
        cara_ = cara_[0:200]
    return cara_, cara_1, cara_2
