import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements

from ScriptObjectInteractors.LineInteractor import LineInteractor, LineInteractorResult
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart

from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
from TypeCollections.ModelEleList import ModelEleList

print('Load Solido 3D Neopreno PythonPart')


def check_allplan_version(build_ele, version):

    del build_ele, version
    return True


def create_element(build_ele, doc):

    # Validar que tengamos los puntos y dimensiones
    if not hasattr(build_ele, 'PuntoInicial') or not hasattr(build_ele, 'PuntoFinal'):
        return ([], [])

    if not hasattr(build_ele, 'GrosorSeleccionado'):
        return ([], [])

    punto_inicial = build_ele.PuntoInicial.value
    punto_final = build_ele.PuntoFinal.value
    ancho = 50.0  # Ancho fijo e inmutable

    # Obtener el grosor seleccionado de los radio buttons
    grosor = get_selected_thickness(build_ele)

    # Actualizar el color segun el grosor seleccionado
    update_color_for_thickness(build_ele)

    # Validar que los valores no sean None
    if punto_inicial is None or punto_final is None or ancho is None or grosor is None:
        return ([], [])

    # Crear la linea 3D de referencia
    line = AllplanGeo.Line3D(punto_inicial, punto_final)

    # Calcular longitud y verificar que la linea tenga longitud valida
    if (longitud := AllplanGeo.CalcLength(line)) < 0.1:
        return ([], [])

    # Actualizar informacion en la paleta (solo si existe el parametro)
    if hasattr(build_ele, 'InfoLongitud'):
        build_ele.InfoLongitud.value = f"{longitud:.2f}"

    # Actualizar longitud calculada en la paleta principal
    if hasattr(build_ele, 'Longitud'):
        build_ele.Longitud.value = longitud

    # Crear el solido prismatico (paralelepipedo rectangular)
    solid = create_neopreno_solid(line, ancho, grosor)


    # Crear propiedades comunes
    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()

    # Usar el color actualizado segun el grosor (ya se actualizo en update_color_for_thickness)
    if hasattr(build_ele, 'Color'):
        common_props.Color = build_ele.Color.value
    else:
        # Color por defecto si no existe el parametro (fuxia para 5mm)
        common_props.Color = 15

    # Valores por defecto para parametros comentados en la paleta
    if hasattr(build_ele, 'Pen'):
        common_props.Pen = build_ele.Pen.value
    else:
        common_props.Pen = 1  # Valor por defecto

    if hasattr(build_ele, 'Stroke'):
        common_props.Stroke = build_ele.Stroke.value
    else:
        common_props.Stroke = 1  # Valor por defecto

    if hasattr(build_ele, 'Layer'):
        common_props.Layer = build_ele.Layer.value
    else:
        common_props.Layer = -1  # Valor por defecto

    # Crear el elemento 3D del modelo
    model_ele_list = ModelEleList()

    if solid:
        # Si tenemos un solido valido, usarlo
        model_ele_list.append(AllplanBasisElements.ModelElement3D(common_props, solid))
    else:
        # Si no se puede crear el solido, usar la linea como alternativa
        model_ele_list.append(AllplanBasisElements.ModelElement3D(common_props, line))

    # Crear handles para editar los puntos
    handle_list = create_handles(punto_inicial, punto_final)

    # Crear vistas para el PythonPart
    views = [View2D3D(model_ele_list)]

    # Crear atributos
    attr_list = [
        AllplanBaseElements.AttributeDouble(220, longitud),  # Longitud
        AllplanBaseElements.AttributeDouble(221, ancho),     # Ancho
        AllplanBaseElements.AttributeDouble(222, grosor),    # Grosor
        AllplanBaseElements.AttributeString(2103, "SOLIDO 3D NEOPRENO PYTHONPART"),  # Tipo
        AllplanBaseElements.AttributeString(508, "Neopreno"),  # Clasificación
    ]

    # Crear el PythonPart
    pythonpart = PythonPart(
        "Solido3DNeoprenoPP",
        parameter_list=build_ele.get_params_list(),
        hash_value=build_ele.get_hash(),
        python_file=build_ele.pyp_file_name,
        views=views,
        attribute_list=attr_list
    )

    # Crear elementos del modelo
    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


def get_selected_thickness(build_ele):

    # Obtener el grosor del parametro unico
    if hasattr(build_ele, 'GrosorSeleccionado') and build_ele.GrosorSeleccionado.value is not None:
        return float(build_ele.GrosorSeleccionado.value)

    # Por defecto, usar 5mm
    return 5.0


def get_color_for_thickness(thickness):

    color_map = {
        5.0: 15,   # 5mm -> fuxia (color 15)
        10.0: 4,   # 10mm -> verde (color 4)
        20.0: 5,   # 20mm -> rosa (color 5)
        30.0: 8,   # 30mm -> naranja (color 8)
        40.0: 3    # 40mm -> turquesa (color 3)
    }

    return color_map.get(thickness, 4)  # Verde por defecto


def update_color_for_thickness(build_ele):

    if not build_ele or not hasattr(build_ele, 'GrosorSeleccionado'):
        return

    # Obtener el grosor seleccionado
    thickness = get_selected_thickness(build_ele)

    # Obtener el color correspondiente
    color_number = get_color_for_thickness(thickness)

    # Actualizar el color en el elemento (si el parametro existe)
    if hasattr(build_ele, 'Color'):
        build_ele.Color.value = color_number


def create_neopreno_solid(line, ancho, grosor):

    try:
        # Obtener los puntos de la linea
        punto_inicial = line.StartPoint
        punto_final = line.EndPoint

        # Calcular el vector de direccion de la linea
        vector_direccion = AllplanGeo.Vector3D(
            punto_final.X - punto_inicial.X,
            punto_final.Y - punto_inicial.Y,
            punto_final.Z - punto_inicial.Z
        )

        # Normalizar el vector de direccion
        if (longitud_vector := AllplanGeo.CalcLength(vector_direccion)) < 0.1:
            return None

        vector_direccion = AllplanGeo.Vector3D(
            vector_direccion.X / longitud_vector,
            vector_direccion.Y / longitud_vector,
            vector_direccion.Z / longitud_vector
        )

        # Calcular el vector perpendicular al plano XY (para el ancho)
        # Usar el vector Z como referencia para crear un vector perpendicular
        vector_z = AllplanGeo.Vector3D(0, 0, 1)

        # Calcular el vector perpendicular usando producto cruz
        vector_perpendicular = AllplanGeo.Vector3D(
            vector_direccion.Y * vector_z.Z - vector_direccion.Z * vector_z.Y,
            vector_direccion.Z * vector_z.X - vector_direccion.X * vector_z.Z,
            vector_direccion.X * vector_z.Y - vector_direccion.Y * vector_z.X
        )

        # Normalizar el vector perpendicular
        if (longitud_perp := AllplanGeo.CalcLength(vector_perpendicular)) < 0.1:
            # Si el vector de dirección es paralelo a Z, usar vector Y
            vector_perpendicular = AllplanGeo.Vector3D(0, 1, 0)
        else:
            vector_perpendicular = AllplanGeo.Vector3D(
                vector_perpendicular.X / longitud_perp,
                vector_perpendicular.Y / longitud_perp,
                vector_perpendicular.Z / longitud_perp
            )

        # Calcular el vector para la altura (tercera dimension)
        vector_altura = AllplanGeo.Vector3D(
            vector_direccion.Y * vector_perpendicular.Z - vector_direccion.Z * vector_perpendicular.Y,
            vector_direccion.Z * vector_perpendicular.X - vector_direccion.X * vector_perpendicular.Z,
            vector_direccion.X * vector_perpendicular.Y - vector_direccion.Y * vector_perpendicular.X
        )

        # Normalizar el vector de altura
        if (longitud_altura := AllplanGeo.CalcLength(vector_altura)) > 0.1:
            vector_altura = AllplanGeo.Vector3D(
                vector_altura.X / longitud_altura,
                vector_altura.Y / longitud_altura,
                vector_altura.Z / longitud_altura
            )
        else:
            vector_altura = AllplanGeo.Vector3D(0, 0, 1)

        # Desplazar el punto inicial para centrar la línea en el ancho
        # La línea está en el centro del ancho, a la mitad del grosor
        punto_inicio = AllplanGeo.Point3D(
            punto_inicial.X,  # X original de la linea
            punto_inicial.Y,  # Y original de la linea
            punto_inicial.Z   # Z original de la linea (base inferior)
        )

        # Desplazar el punto para centrar en el ancho (mitad del ancho)
        punto_inicio = AllplanGeo.Point3D(
            punto_inicio.X + vector_perpendicular.X * (ancho / 2.0),
            punto_inicio.Y + vector_perpendicular.Y * (ancho / 2.0),
            punto_inicio.Z + vector_perpendicular.Z * (ancho / 2.0)
        )

        # Crear el AxisPlacement3D para el cuboide
        # X axis: vector de direccion (longitud)
        # Z axis: vector de altura INVERTIDO para que el prisma este por encima de la linea
        vector_altura_invertido = AllplanGeo.Vector3D(
            -1.0 * vector_altura.X,
            -1.0 * vector_altura.Y,
            -1.0 * vector_altura.Z
        )

        axis_placement = AllplanGeo.AxisPlacement3D(
            punto_inicio,  # Origen en el punto inicial de la linea (base del prisma)
            vector_direccion,  # Eje X (longitud del prisma)
            vector_altura_invertido  # Eje Z (altura hacia arriba desde la linea)
        )

        # Crear el cuboide usando BRep3D.CreateCuboid
        cuboid = AllplanGeo.BRep3D.CreateCuboid(
            axis_placement,
            longitud_vector,  # Longitud (variable, paralela a la linea)
            ancho,           # Ancho (fijo)
            grosor           # Grosor/Altura (fijo)
        )

        return cuboid

    except Exception:
        return None


def create_handles(punto_inicial, punto_final):

    handle_list = []

    # Handle para mover el punto inicial
    handle_list.append(
        HandleProperties(
            "PuntoInicialHandle",
            punto_inicial,
            AllplanGeo.Point3D(0, 0, 0),
            [("PuntoInicial", HandleDirection.xyz_dir)],
            HandleDirection.xyz_dir
        )
    )

    # Handle para mover el punto final
    handle_list.append(
        HandleProperties(
            "PuntoFinalHandle",
            punto_final,
            punto_inicial,
            [("PuntoFinal", HandleDirection.xyz_dir)],
            HandleDirection.xyz_dir
        )
    )

    return handle_list


def move_handle(build_ele, handle_prop, input_pnt, doc):

    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)


def create_interactor(coord_input, pyp_path, str_table_service, build_ele_list=None, build_ele_composite=None, control_props_list=None, modify_uuid_list=None):

    return Solido3DNeoprenoPPInteractor(coord_input, pyp_path, str_table_service, build_ele_list, build_ele_composite, control_props_list, modify_uuid_list)


class Solido3DNeoprenoPPInteractor:

    def __init__(self, coord_input, pyp_path, str_table_service, build_ele_list=None, build_ele_composite=None, control_props_list=None, modify_uuid_list=None):
        self.coord_input = coord_input
        self.pyp_path = pyp_path
        self.str_table_service = str_table_service
        self.build_ele_service = BuildingElementService()
        self.model_ele_list = []
        self.line_created = False
        self.is_editing_existing = False

        # Verificar si estamos editando un PythonPart existente
        # Si recibimos build_ele_list Y modify_uuid_list con elementos, estamos editando
        # Si recibimos build_ele_list pero modify_uuid_list esta vacio o None, estamos creando nuevo
        if modify_uuid_list and len(modify_uuid_list) > 0 and build_ele_list and len(build_ele_list) > 0:
            # Verificar si los puntos ya estan definidos (editando)
            check_build_ele = build_ele_list[0]
            if (hasattr(check_build_ele, 'PuntoInicial') and
                hasattr(check_build_ele, 'PuntoFinal') and
                check_build_ele.PuntoInicial.value != AllplanGeo.Point3D(0,0,0)):
                self.is_editing_existing = True
                self.build_ele_list = build_ele_list
                self.build_ele_composite = build_ele_composite
                self.control_props_list = control_props_list
                self.build_ele_script = None
                self.file_name = "Solido3DNeoprenoPP.pyp"
                part_name = "Solido 3D Neopreno PythonPart"

                # Regenerar el elemento inmediatamente para evitar que se borre
                try:
                    doc = coord_input.GetInputViewDocument()
                    model_elem_list, handle_list = create_element(check_build_ele, doc)
                    if model_elem_list:
                        # Insertar el elemento regenerado en el documento
                        AllplanBaseElements.CreateElements(
                            doc,
                            AllplanGeo.Matrix3D(),
                            model_elem_list,
                            [],
                            None
                        )
                except Exception:
                    pass
            else:
                self.is_editing_existing = False

        if not self.is_editing_existing:
            # Leer los datos de la paleta (usar .pyp no .pal)
            pyp_file = f"{pyp_path}\\Solido3DNeoprenoPP.pyp"
            result, self.build_ele_script, self.build_ele_list, self.control_props_list, \
                self.build_ele_composite, part_name, self.file_name = \
                self.build_ele_service.read_data_from_pyp(
                    pyp_file,
                    self.str_table_service.str_table,
                    False,
                    self.str_table_service.material_str_table
                )

            if not result:
                return

        # Crear y mostrar la paleta
        self.palette_service = BuildingElementPaletteService(
            self.build_ele_list,
            self.build_ele_composite,
            self.build_ele_script,
            self.control_props_list,
            self.file_name
        )
        self.palette_service.show_palette(part_name)

        # Obtener propiedades comunes
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.set_common_properties()

        # Si estamos editando un PythonPart existente, no iniciar el interactor
        if not self.is_editing_existing:
            # Resultado del interactor de linea
            self.line_result = LineInteractorResult()

            # Crear el LineInteractor
            self.line_interactor = LineInteractor(
                self.line_result,
                True,  # is_first_input
                "Punto inicial de linea de referencia para NEOPRENO",
                allow_pick_up=True,
                preview_function=self.preview_line
            )

            # Iniciar el input de la linea
            self.line_interactor.start_input(self.coord_input)

        else:
            # Si estamos editando, no necesitamos el interactor
            self.line_result = None
            self.line_interactor = None

    def set_common_properties(self):
        if self.build_ele_list and len(self.build_ele_list) > 0:
            build_ele = self.build_ele_list[0]
            if hasattr(build_ele, 'Color'):
                self.com_prop.Color = build_ele.Color.value
            if hasattr(build_ele, 'Pen'):
                self.com_prop.Pen = build_ele.Pen.value
            if hasattr(build_ele, 'Stroke'):
                self.com_prop.Stroke = build_ele.Stroke.value
            if hasattr(build_ele, 'Layer'):
                self.com_prop.Layer = build_ele.Layer.value
        else:
            self.com_prop.GetGlobalProperties()

    def preview_line(self, line):
        if not line:
            return []

        # Verificar que la linea tenga longitud valida
        try:
            if AllplanGeo.CalcLength(line) < 0.1:
                return []
        except Exception:
            return []

        # Obtener valores de la paleta para el preview
        ancho_preview = 50.0  # Ancho fijo e inmutable
        grosor_preview = 5.0  # Valor por defecto

        # Intentar obtener el grosor seleccionado si esta disponible
        if self.build_ele_list and len(self.build_ele_list) > 0:
            build_ele = self.build_ele_list[0]
            # Obtener el grosor seleccionado
            grosor_preview = get_selected_thickness(build_ele)

        # Crear el solido 3D de preview
        solid = create_neopreno_solid(line, ancho_preview, grosor_preview)

        # Crear propiedades comunes para el preview
        preview_props = AllplanBaseElements.CommonProperties()
        preview_props.GetGlobalProperties()
        preview_props.Color = 6  # Rojo para el preview

        # Crear elementos para preview
        model_ele_list = ModelEleList()
        if solid:
            model_ele_list.append(AllplanBasisElements.ModelElement3D(preview_props, solid))
        else:
            # Si no se puede crear el solido, mostrar solo la linea
            model_ele_list.append(AllplanBasisElements.ModelElement3D(preview_props, line))

        return model_ele_list

    def on_preview_draw(self):
        """Maneja el evento de dibujo de preview."""
        if self.line_interactor:
            self.line_interactor.on_preview_draw()

    def on_mouse_leave(self):
        """Maneja el evento de salida del raton del viewport."""
        if self.line_interactor:
            self.line_interactor.on_mouse_leave()

    def on_cancel_function(self):
        """Maneja el evento de cancelacion (tecla ESC)."""
        # Si estamos editando un PythonPart existente, solo cerrar la paleta
        if self.is_editing_existing:
            self.palette_service.close_palette()
            return True

        # Si ya creamos una linea, cerrar la paleta y terminar
        if self.line_created:
            self.palette_service.close_palette()
            return True

        # Si tenemos una linea valida, crearla
        if self.line_result and self.line_result.input_line:
            try:
                if AllplanGeo.CalcLength(self.line_result.input_line) > 0.1:
                    self.create_pythonpart_element()
                    self.palette_service.close_palette()
                    return True
            except Exception:
                pass

        # Si no, usar el resultado del line_interactor
        if self.line_interactor:
            result = self.line_interactor.on_cancel_function()

            # Si el interactor dice que debemos crear elementos, hacerlo
            if hasattr(result, 'value') and result.value == 1:  # CREATE_ELEMENTS
                if self.line_result and self.line_result.input_line:
                    try:
                        if AllplanGeo.CalcLength(self.line_result.input_line) > 0.1:
                            self.create_pythonpart_element()
                    except Exception:
                        pass

        self.palette_service.close_palette()
        return True

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):

        # Si estamos editando un PythonPart existente, no procesar mensajes del raton
        if self.is_editing_existing:
            return True

        # Si ya creamos una linea, no procesar mas
        if self.line_created:
            return True

        # Procesar el mensaje a traves del LineInteractor
        if self.line_interactor:
            result = self.line_interactor.process_mouse_msg(mouse_msg, pnt, msg_info)

            # Si la linea esta completa, crear el elemento UNA SOLA VEZ
            if not self.line_created and self.line_result and self.line_result.input_line:
                try:
                    # Verificar que tengamos ambos puntos definidos
                    line = self.line_result.input_line
                    distance = AllplanGeo.CalcLength(line)

                    if distance > 0.1:  # Linea valida con longitud minima
                        self.create_pythonpart_element()
                        self.line_created = True
                        self.palette_service.close_palette()
                        return True
                except Exception:
                    pass

            return result

        return True

    def modify_element_property(self, page, name, value):
        # Si se modifica el grosor, validar que este en el rango permitido
        if name == 'GrosorSeleccionado':
            self.validate_thickness_value(value)

        if self.palette_service.modify_element_property(page, name, value):
            self.palette_service.update_palette(-1, False)

        self.set_common_properties()
        return True

    def validate_thickness_value(self, new_value):
        # Validar que el grosor este en los valores permitidos
        allowed_values = [5, 10, 20, 30, 40]
        if new_value not in allowed_values:
            # Si no esta en los valores permitidos, usar el mas cercano
            closest_value = min(allowed_values, key=lambda x: abs(x - new_value))
            if self.build_ele_list and len(self.build_ele_list) > 0:
                build_ele = self.build_ele_list[0]
                if hasattr(build_ele, 'GrosorSeleccionado'):
                    build_ele.GrosorSeleccionado.value = closest_value

    def create_pythonpart_element(self):

        # Evitar crear multiples veces
        if self.line_created:
            return

        if not self.line_result or not self.line_result.input_line:
            return

        # Obtener el documento desde coord_input
        doc = self.coord_input.GetInputViewDocument()

        line = self.line_result.input_line

        # Obtener valores de la paleta
        ancho = 50.0  # Ancho fijo e inmutable

        # Obtener el grosor seleccionado
        grosor = get_selected_thickness(self.build_ele_list[0] if self.build_ele_list else None)

        # Actualizar los parametros del build_ele con los valores de la linea
        if self.build_ele_list and len(self.build_ele_list) > 0:
            build_ele = self.build_ele_list[0]

            # Guardar los puntos de la linea
            build_ele.PuntoInicial.value = line.StartPoint
            build_ele.PuntoFinal.value = line.EndPoint

            # El ancho es fijo (50mm) y no se modifica

            # Actualizar el color segun el grosor seleccionado
            update_color_for_thickness(build_ele)

            # Crear el PythonPart usando la funcion create_element global
            model_elem_list, handle_list = create_element(build_ele, doc)

            # Insertar el PythonPart en el documento
            if model_elem_list:
                AllplanBaseElements.CreateElements(
                    doc,
                    AllplanGeo.Matrix3D(),
                    model_elem_list,
                    [],
                    None
                )

                self.model_ele_list = model_elem_list
                self.line_created = True
            else:
                pass
        else:
            pass
