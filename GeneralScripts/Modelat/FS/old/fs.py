import hashlib
import random
import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import GeometryValidate as GeometryValidate
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart
from BuildingElementAttributeList import BuildingElementAttributeList

print('Load fs.py')

def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """
    del build_ele
    del version
    return True

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

def get_xps_color(ancho, largo, espesor):
    """
    Determina el color del XPS basado en sus dimensiones

    Args:
        ancho: ancho de la placa XPS (ya con reducción de 4mm)
        largo: largo de la placa XPS (ya con reducción de 4mm)
        espesor: espesor del XPS

    Returns:
        Código de color para Allplan
    """
    # Valores redondeados para comparación
    ancho_round = round(ancho)
    largo_round = round(largo)

    # Verificar dimensiones y devolver el color correspondiente
    if ancho_round == 2996:
        if largo_round == 11996:
            if espesor == 120:
                return 206
            elif espesor == 100:
                return 134
            elif espesor == 70:
                return 13
            elif espesor == 50:
                return 12
            elif espesor == 40:
                return 235
        elif largo_round == 596:
            if espesor == 120:
                return 14
            elif espesor == 100:
                return 198
            elif espesor == 70:
                return 11
            elif espesor == 50:
                return 8
            elif espesor == 40:
                return 220

    # Si no hay coincidencia exacta, usar el color por defecto
    print(f"No se encontró coincidencia exacta para XPS de {ancho_round}x{largo_round}x{espesor}. Usando color por defecto.")
    return 2

def get_pld_color_by_type_and_dimensions(pld_type, ancho, largo):
    """
    Determine PLD color based on type and dimensions

    Args:
        pld_type: Type of PLD (OMNIA, HUMITAT, R_FOC)
        ancho: Width of PLD plate
        largo: Length of PLD plate

    Returns:
        Color code for Allplan
    """
    # Round dimensions for comparison
    ancho_round = round(ancho)
    largo_round = round(largo)

    # Set default colors
    if pld_type == "OMNIA":
        if largo_round == 3000:
            return 120  # Blue for 3000x1200
        else:
            return 124  # Blue for 2500x1200
    elif pld_type == "HUMITAT":
        if largo_round == 3000:
            return 1  # Black/Gray for 3000x1200
        else:
            return 65  # Black/Gray for 2500x1200
    elif pld_type == "R_FOC":
        if largo_round == 3000:
            return 6  # Red for 3000x1200
        else:
            return 107  # Red for 2500x1200
    else:
        # Default color if type doesn't match
        return 7  # Default color

def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    element = FS()

    # Set properties from build_ele
    element.zUnique = build_ele.zUnique.value if hasattr(build_ele, 'zUnique') else random.random() * 3600
    element.PlanchaAncho = build_ele.PlanchaAncho.value if hasattr(build_ele, 'PlanchaAncho') else 1200
    element.PlanchaLargo = build_ele.PlanchaLargo.value if hasattr(build_ele, 'PlanchaLargo') else 3000
    element.EspesorPLD = build_ele.EspesorPLD.value if hasattr(build_ele, 'EspesorPLD') else 15

    # Manejo específico para el ComboBox de EspesorXPS
    if hasattr(build_ele, 'EspesorXPS'):
        # Convertir a entero para asegurar compatibilidad
        try:
            element.EspesorXPS = int(float(build_ele.EspesorXPS.value))
        except (ValueError, TypeError):
            # Si hay error de conversión, usar el valor predeterminado
            element.EspesorXPS = 40
    else:
        element.EspesorXPS = 40

    # Get PLD type selection
    if hasattr(build_ele, 'PLDType'):
        element.PLDType = build_ele.PLDType.value
    else:
        element.PLDType = "OMNIA"  # Default type

    element.AnchoBorde = build_ele.AnchoBorde.value if hasattr(build_ele, 'AnchoBorde') else 255

    # Determine color based on PLD type and dimensions
    element.ColorPLD = get_pld_color_by_type_and_dimensions(
        element.PLDType, element.PlanchaAncho, element.PlanchaLargo)
    print(f"Asignando color {element.ColorPLD} al PLD de tipo {element.PLDType} y dimensiones {element.PlanchaAncho}x{element.PlanchaLargo}")

    element.LayerPLD = build_ele.LayerPLD.value if hasattr(build_ele, 'LayerPLD') else "PLD_Layer"
    element.LayerXPS = build_ele.LayerXPS.value if hasattr(build_ele, 'LayerXPS') else "XPS_Layer"

    # Manejo de la rotación - ahora con prioridad para el input exacto
    if hasattr(build_ele, 'ZRotationInput'):
        element.ZRotation = build_ele.ZRotationInput.value
    elif hasattr(build_ele, 'ZRotation'):
        element.ZRotation = build_ele.ZRotation.value
    else:
        element.ZRotation = 0

    element.CambiarBorde = build_ele.CambiarBorde.value if hasattr(build_ele, 'CambiarBorde') else False

    # Apply size constraints
    element.PlanchaAncho = max(900, min(1200, element.PlanchaAncho))  # Limit PLD width between 900-1200mm
    element.PlanchaLargo = max(900, min(3000, element.PlanchaLargo))  # Limit length between 900-3000mm
    element.EspesorPLD = 15  # Fix PLD thickness at 15mm

    # Ensure XPS thickness is one of the allowed values (40, 50, 70, 80, 100, 120)
    allowed_xps_thicknesses = [40, 50, 70, 80, 100, 120]
    if element.EspesorXPS not in allowed_xps_thicknesses:
        closest = min(allowed_xps_thicknesses, key=lambda x: abs(x - element.EspesorXPS))
        print(f"Invalid XPS thickness: {element.EspesorXPS}. Setting to closest valid value: {closest}")
        element.EspesorXPS = closest

    # Ensure rotation is within valid range (-360 to 360)
    element.ZRotation = max(-360, min(360, element.ZRotation))

    # Determine if we're in large plate mode
    is_large_plate = element.PlanchaAncho >= 1200

    # Set border properties based on plate size
    if is_large_plate:
        # For large plates, show both borders
        element.ShowBordeIzquierdo = True
        element.ShowBordeDerecho = True
        element.ShowAmbosBordes = True
        print("Modo placa grande: mostrando ambos bordes")
    else:
        # For smaller plates, only show one border based on CambiarBorde toggle
        element.ShowBordeIzquierdo = element.CambiarBorde  # Show left border if CambiarBorde is True
        element.ShowBordeDerecho = not element.CambiarBorde  # Show right border if CambiarBorde is False
        element.ShowAmbosBordes = False
        print(f"Modo placa pequeña: Izquierdo={element.ShowBordeIzquierdo}, Derecho={element.ShowBordeDerecho}, Toggle={element.CambiarBorde}")

    # Calcular dimensiones de XPS (4mm menos que PLD en ancho y largo)
    xps_width = element.PlanchaAncho - 4
    xps_length = element.PlanchaLargo - 4

    # Determinar color de XPS basado en dimensiones
    element.ColorXPS = get_xps_color(xps_width, xps_length, element.EspesorXPS)
    print(f"Asignando color {element.ColorXPS} al XPS de dimensiones {xps_width}x{xps_length}x{element.EspesorXPS}")

    if not element.is_valid():
        return ([], [])

    handle_list = element.create_handles()
    elements = element.create()
    views = [View2D3D(elements)]

    # Updated type info in attributes based on selected PLD type
    pld_type_description = {
        "OMNIA": "GUIX LAMINAT OMNIA",
        "HUMITAT": "GUIX LAMINAT HUMITAT",
        "R_FOC": "GUIX LAMINAT R FOC"
    }.get(element.PLDType, "GUIX LAMINAT")

    attr_list = [
        AllplanBaseElements.AttributeString(2431, element.get_codi_mesures()),
        AllplanBaseElements.AttributeString(2445, element.get_seccio()),
        AllplanBaseElements.AttributeString(220, element.get_dimensiones()),
        AllplanBaseElements.AttributeString(2103, "PLD-XPS"),
        AllplanBaseElements.AttributeString(508, f"{pld_type_description}")
    ]

    pythonpart = PythonPart("FS",
                         parameter_list=build_ele.get_params_list(),
                         hash_value=build_ele.get_hash(),
                         python_file=build_ele.pyp_file_name,
                         views=views,
                         matrix=AllplanGeo.Matrix3D(),
                         attribute_list=attr_list)

    model_elem_list = pythonpart.create()
    return (model_elem_list, handle_list)

class FS:
    """
    Definition of class FS
    """
    def __init__(self):
        """Initialize with default values"""
        self.zUnique = random.random() * 3600
        self.PlanchaAncho = 1200  # Default width changed to 1200mm
        self.PlanchaLargo = 3000  # Default length changed to 3000mm
        self.EspesorPLD = 15      # Fixed at 15mm as per requirements
        self.EspesorXPS = 40      # Default XPS thickness 40mm
        self.AnchoBorde = 255
        self.PLDType = "OMNIA"    # Default PLD type
        self.ColorPLD = 120       # Default color based on OMNIA 3000x1200
        self.ColorXPS = 2
        self.LayerPLD = "PLD_Layer"
        self.LayerXPS = "XPS_Layer"
        self.ZRotation = 0        # Parameter for Z-axis rotation (in degrees)
        self.CambiarBorde = False # New single checkbox to toggle border position
        # Internal properties for border display
        self.ShowBordeIzquierdo = True
        self.ShowBordeDerecho = True
        self.ShowAmbosBordes = True


    def get_params_list(self):
        """
        Append all parameters as parameter list
        Returns: param list
        """
        return [
            f"zUnique = {self.zUnique}\n",
            f"PlanchaAncho = {self.PlanchaAncho}\n",
            f"PlanchaLargo = {self.PlanchaLargo}\n",
            f"EspesorPLD = {self.EspesorPLD}\n",
            f"EspesorXPS = {self.EspesorXPS}\n",
            f"AnchoBorde = {self.AnchoBorde}\n",
            f"PLDType = {self.PLDType}\n",
            f"ColorPLD = {self.ColorPLD}\n",
            f"ColorXPS = {self.ColorXPS}\n",
            f"LayerPLD = {self.LayerPLD}\n",
            f"LayerXPS = {self.LayerXPS}\n",
            f"ZRotation = {self.ZRotation}\n",
            f"CambiarBorde = {self.CambiarBorde}\n",
        ]

    def __repr__(self):
        return f'Plancha_PLD_XPS(zUnique={self.zUnique}, PlanchaAncho={self.PlanchaAncho}, ' \
               f'PlanchaLargo={self.PlanchaLargo}, EspesorPLD={self.EspesorPLD}, ' \
               f'EspesorXPS={self.EspesorXPS}, AnchoBorde={self.AnchoBorde}, ' \
               f'PLDType={self.PLDType}, ColorPLD={self.ColorPLD}, ColorXPS={self.ColorXPS}, ' \
               f'LayerPLD={self.LayerPLD}, LayerXPS={self.LayerXPS}, ' \
               f'ZRotation={self.ZRotation}, CambiarBorde={self.CambiarBorde})\n'

    def hash(self):
        """Calculate hash value for script"""
        return hashlib.sha224(self.__repr__().encode('utf-8')).hexdigest()

    def filename(self):
        """Python script filename"""
        return "fs.py"

    def is_valid(self):
        """Check for valid values"""
        # Validate with size constraints
        allowed_xps_thicknesses = [40, 50, 70, 80, 100, 120]
        return all([
            self.PlanchaAncho >= 900 and self.PlanchaAncho <= 1200,  # PLD width between 900-1200mm
            self.PlanchaLargo >= 900 and self.PlanchaLargo <= 3000,  # Length between 900-3000mm
            self.EspesorPLD == 15,  # PLD thickness must be exactly 15mm
            self.EspesorXPS in allowed_xps_thicknesses,  # XPS thickness must be one of allowed values
            self.AnchoBorde > 0,
            self.ZRotation >= -360 and self.ZRotation <= 360  # Validate rotation range
        ])

    def get_codi_mesures(self):
        return f"#X:@{self.PlanchaAncho}Y:@{self.PlanchaLargo}@|Z1:@{self.EspesorPLD}@|Z2:@{self.EspesorXPS}@#"

    def get_seccio(self):
        return f"{self.PlanchaAncho}x {self.PlanchaLargo}x {self.EspesorPLD + self.EspesorXPS}"

    def get_dimensiones(self):
        return f"{self.PlanchaAncho}x{self.PlanchaLargo}"

    def create_handles(self):
        """Create handles - modified to only allow width and length adjustment within limits"""
        return [
            HandleProperties("PlanchaAncho",
                           AllplanGeo.Point3D(self.PlanchaAncho, 0, 0),
                           AllplanGeo.Point3D(0, 0, 0),
                           [("PlanchaAncho", HandleDirection.x_dir)],
                           HandleDirection.x_dir),
            HandleProperties("PlanchaLargo",
                           AllplanGeo.Point3D(0, self.PlanchaLargo, 0),
                           AllplanGeo.Point3D(0, 0, 0),
                           [("PlanchaLargo", HandleDirection.y_dir)],
                           HandleDirection.y_dir)
        ]

    def create(self):
        """Creates the overlapping plates (PLD below, XPS above) with Z-axis rotation"""
        elements = []

        # Ensure layers are numeric
        try:
            layer_pld = int(self.LayerPLD) if self.LayerPLD is not None else 1
            layer_xps = int(self.LayerXPS) if self.LayerXPS is not None else 2
        except (ValueError, TypeError):
            layer_pld = 1
            layer_xps = 2

        # Create center point for rotation
        center_x = self.PlanchaAncho / 2
        center_y = self.PlanchaLargo / 2
        center_z = (self.EspesorPLD + self.EspesorXPS) / 2
        center_point = AllplanGeo.Point3D(center_x, center_y, center_z)

        # PLD - Main plate (lower plate)
        plancha_pld = AllplanGeo.Polyhedron3D.CreateCuboid(self.PlanchaAncho, self.PlanchaLargo, self.EspesorPLD)

        # Create borders based on which are shown
        borde_izquierdo = None
        diagonal_izquierdo = None
        if self.ShowBordeIzquierdo:
            borde_izquierdo = AllplanGeo.Polyhedron3D.CreateCuboid(self.AnchoBorde, self.PlanchaLargo, self.EspesorPLD / 2)

            # Create diagonal cuboid for left border
            diagonal_izquierdo = AllplanGeo.Polyhedron3D.CreateCuboid(
                self.AnchoBorde,  # Width same as border
                1,                # 1mm height
                self.EspesorPLD / 2  # Same depth as border
            )
            # Position diagonal cuboid along the diagonal of the border
            diagonal_izquierdo = AllplanGeo.Move(
                diagonal_izquierdo,
                AllplanGeo.Vector3D(0, self.PlanchaLargo - 1, 0)  # Move to bottom right of border
            )

        # Right border
        borde_derecho = None
        diagonal_derecho = None
        if self.ShowBordeDerecho:
            borde_derecho = AllplanGeo.Polyhedron3D.CreateCuboid(self.AnchoBorde, self.PlanchaLargo, self.EspesorPLD / 2)
            # Move to right edge
            borde_derecho = AllplanGeo.Move(borde_derecho, AllplanGeo.Vector3D(self.PlanchaAncho - self.AnchoBorde, 0, 0))

            # Create diagonal cuboid for right border
            diagonal_derecho = AllplanGeo.Polyhedron3D.CreateCuboid(
                self.AnchoBorde,  # Width same as border
                1,                # 1mm height
                self.EspesorPLD / 2  # Same depth as border
            )
            # Position diagonal cuboid along the diagonal of the border
            diagonal_derecho = AllplanGeo.Move(
                diagonal_derecho,
                AllplanGeo.Vector3D(self.PlanchaAncho - self.AnchoBorde, self.PlanchaLargo - 1, 0)  # Move to bottom right of border
            )

        # XPS - Top plate
        # Make XPS 4mm narrower than PLD (2mm on each side)
        xps_width = self.PlanchaAncho - 4
        xps_length = self.PlanchaLargo - 4

        # Create the XPS plate with adjusted dimensions
        plancha_xps = AllplanGeo.Polyhedron3D.CreateCuboid(xps_width, xps_length, self.EspesorXPS)

        # Position XPS plate above PLD with 2mm offset from each edge
        plancha_xps = AllplanGeo.Move(plancha_xps, AllplanGeo.Vector3D(2, 2, self.EspesorPLD))

        # Apply rotation if needed
        if self.ZRotation != 0:
            # Convert degrees to radians
            angle_rad = math.radians(self.ZRotation)

            # Create rotation matrix around Z axis
            rotation = AllplanGeo.Matrix3D()
            # Create an Angle object from the radians value
            angle = AllplanGeo.Angle(angle_rad)
            rotation.Rotation(AllplanGeo.Line3D(center_point, AllplanGeo.Vector3D(0, 0, 1)), angle)

            # Apply rotation to all elements
            plancha_pld = AllplanGeo.Transform(plancha_pld, rotation)
            plancha_xps = AllplanGeo.Transform(plancha_xps, rotation)

            if borde_izquierdo:
                borde_izquierdo = AllplanGeo.Transform(borde_izquierdo, rotation)
                diagonal_izquierdo = AllplanGeo.Transform(diagonal_izquierdo, rotation)
            if borde_derecho:
                borde_derecho = AllplanGeo.Transform(borde_derecho, rotation)
                diagonal_derecho = AllplanGeo.Transform(diagonal_derecho, rotation)

        # Create properties
        common_prop_pld = AllplanBaseElements.CommonProperties()
        common_prop_pld.Color = self.ColorPLD
        common_prop_pld.Layer = layer_pld  # Use converted numeric layer

        common_prop_xps = AllplanBaseElements.CommonProperties()
        common_prop_xps.Color = self.ColorXPS
        common_prop_xps.Layer = layer_xps  # Use converted numeric layer

        # Add main elements to list
        elements.append(AllplanBasisElements.ModelElement3D(common_prop_pld, plancha_pld))
        elements.append(AllplanBasisElements.ModelElement3D(common_prop_xps, plancha_xps))

        # Add border elements if they exist
        if borde_izquierdo:
            elements.append(AllplanBasisElements.ModelElement3D(common_prop_pld, borde_izquierdo))
            elements.append(AllplanBasisElements.ModelElement3D(common_prop_pld, diagonal_izquierdo))

        if borde_derecho:
            elements.append(AllplanBasisElements.ModelElement3D(common_prop_pld, borde_derecho))
            elements.append(AllplanBasisElements.ModelElement3D(common_prop_pld, diagonal_derecho))

        return elements