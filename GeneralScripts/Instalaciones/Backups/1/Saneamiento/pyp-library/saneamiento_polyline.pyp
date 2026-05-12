<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Saneamiento\pyp-scripts\saneamiento_polyline.py</Name>
        <Title>Polyline MVP</Title>
        <Version>1.0.0</Version>
        <Interactor>False</Interactor>
    </Script>
    <Page>
        <Name>CrearPolilinea</Name>
        <Text>Definir polilínea para una instalación y generar elementos.</Text>
        <!-- INSTALACIÓN: combo con varias opciones -->
        <Parameter>
            <Name>InstallationName</Name>
            <Text>Instalacion</Text>
            <Value></Value>
            <ValueType>Text</ValueType>
            <FontSize>16</FontSize>
            <FontStyle>2</FontStyle>
        </Parameter>
        <Parameter>
            <Name>InstallationTypeTitle</Name>
            <Text>Tipos de instalacion</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>SupportedAngles</Name>
                <Text>Angulos Soportados</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
            <Parameter>
                <Name>InstallationType</Name>
                <Text>Elegir instalacion</Text>
                <Value></Value>
                <ValueList></ValueList>
                <EventId>1002</EventId>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>DiameterType</Name>
                <Text>Diámetro a aplicar</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>IntegerComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>DiameterTypeStr</Name>
                <Text>Diámetro a aplicar</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowDiameterModify</Name>
                <Text>Modificar</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>DiameterModify</Name>
                    <Text>Modificar diámetro</Text>
                    <EventId>1007</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>FunctionalName</Name>
                <Text>Nombre PythonPartGroup</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
            <Parameter>
                <Name>DistributionType</Name>
                <Text>Tipo de Distribucion</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>WaterType</Name>
                <Text>Tipo de Agua</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>FaceEN</Name>
                <Text>Cara (EN)</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>PointModeTitle</Name>
            <Text>Modos de dibujo</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>PointModeInfoRow</Name>
                <Text>Información</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>InfoPicture</Name>
                    <Text>
    Modos de dibujo (Ayuda):

    • EDICION
        Permite estirar la polilinea desde sus vértices
        y agregar puntos o cortes en los segmentos.
        El CheckBox “Insertar punto” solo se habilita en este modo.

    • CONFIGURACION
        Permite seleccionar tubos, codos, uniones, bifurcaciones, etc,
        para aplicar layers y atributos personalizados.
        También permite eliminar uno o más segmentos mediante selección múltiple.

    • CREACION - EXTENDER
        Permite dibujar y extender la polilinea.
                    </Text>
                    <Value>AllplanSettings.PictResPalette.eHotinfo</Value>
                    <!-- ID del recurso de imagen de Allplan -->
                    <ValueType>Picture</ValueType>
                    <EventId>0</EventId>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>PointMode</Name>
                <Text>Elegir modo</Text>
                <Value>2</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>ExtendPolyline</Name>
                    <Text>Modo Edicion</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>EditPolyline</Name>
                    <Text>Modo Configuracion</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>CreatePolyline</Name>
                    <Text>Modo Creacion - Ext</Text>
                    <Value>2</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowLimitAngles</Name>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CheckBoxLimitarAngulos</Name>
                <Text>Limitar ángulos</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowInsertPoint</Name>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CheckBoxInsertPoint</Name>
                <Text>Insertar punto</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowAddCut</Name>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CheckBoxAddCut</Name>
                <Text>Añadir cortes</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowBorrar</Name>
            <Text>Borrar</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>borrarSeccion</Name>
                <Text>Borrar Seccion o Corte</Text>
                <EventId>1004</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>ElementSeleted</Name>
            <Text>Elemento seleccionado</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>ElementDescription</Name>
                <Text>Info</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>ViewInfo</Name>
                <Text>Ver Info</Text>
                <EventId>1010</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- ORIENTACIÓN 3D (para tubos verticales en paredes / paredes inclinadas) -->
        <Parameter>
            <Name>Orientacion3DExpander</Name>
            <Text>Orientación 3D (segmento unico)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>RotationAngle</Name>
                <Text>Angulo rotacion</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>DefineOrientation</Name>
                <Text>Definir orientación</Text>
                <EventId>1012</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>LayersCustom</Name>
            <Text>Layers</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>LayerTypes</Name>
                <Text>Tipos de layer</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>aplicarLayers</Name>
                <Text>Aplicar layer</Text>
                <EventId>1009</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowAttribute</Name>
            <Text>Atributos</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>AttributeValue</Name>
                <Text>Valor atributo</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>AttributeApply</Name>
                <Text>Aplicar atributo</Text>
                <EventId>1011</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>General</Name>
            <Text>General options</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>CommonProp</Name>
                <Text></Text>
                <Value></Value>
                <Visible>False</Visible>
                <Enable>False</Enable>
                <ValueType>CommonProperties</ValueType>
            </Parameter>
            <!-- Opción para crear PythonPartGroup -->
            <Parameter>
                <Name>RowPythonPart</Name>
                <Text>PythonPartGroup</Text>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CreatePythonPart</Name>
                    <Text>Crear como PythonPartGroup</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                    <!-- <Enable>False</Enable> -->
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowPolilyne</Name>
                <Text>Agregar Polilinea</Text>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>AddPolilyne</Name>
                    <Text>Polilinea</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
                <Parameter>
                    <Name>AddCube</Name>
                    <Text>Polilinea</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
        </Parameter>
        <!-- FINALIZAR -->
        <Parameter>
            <Name>RowFinalizar</Name>
            <Text>Finalizar</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>finalizarCreacion</Name>
                <Text>Finalizar - Crear</Text>
                <EventId>1003</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
        </Parameter>
        <!-- Parámetro oculto para guardar el estado de las polilíneas (para poder restaurar al editar) -->
        <Parameter>
            <Name>SavedState</Name>
            <Text>SavedState</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
        <Parameter>
            <Name>CopiedElementsUUIDs</Name>
            <Text>CopiedElementsUUIDs</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
        <Parameter>
            <Name>CopiedElementsFiles</Name>
            <Text>CopiedElementsFiles</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>PuntosLibresYMacros</Name>
        <Text>Puntos Libres y Macros</Text>
        <!-- MACRO: marcar punto inicial/final/libre y seleccionar SmartSymbol/Fixture -->
        <Parameter>
            <Name>MacroExpander</Name>
            <Text>Macro</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>MarkerPointMode</Name>
                <Text>Elegir punto</Text>
                <Value>2</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Visible>False</Visible>
                <Parameter>
                    <Name>MarkerStart</Name>
                    <Text>Punto inicial</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>MarkerEnd</Name>
                    <Text>Punto final</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>MarkerFree</Name>
                    <Text>Libre</Text>
                    <Value>2</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <ValueType>Row</ValueType>
                <Visible>True</Visible>
                <Parameter>
                    <Name>BtnSelectMacroPoint</Name>
                    <Text>Seleccionar punto</Text>
                    <EventId>1013</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsMacroCaptureMode == False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnAcceptMacro</Name>
                    <Text>Aceptar (Terminar selección)</Text>
                    <EventId>1020</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsMacroCaptureMode == True</Visible>
                </Parameter>
                <Parameter>
                    <Name>IsMacroCaptureMode</Name>
                    <Text>IsMacroCaptureMode</Text>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>
            <!-- Parámetro oculto: Z base del local seleccionado (-999999 = no seleccionado) -->
            <Parameter>
                <Name>MacroSelectedLocalZ</Name>
                <Text>Z local seleccionado</Text>
                <Value>-999999</Value>
                <ValueType>Double</ValueType>
                <Visible>False</Visible>
            </Parameter>
            <!-- Row: Seleccionar Local | Quitar local -->
            <Parameter>
                <ValueType>Row</ValueType>
                <Visible>True</Visible>
                <Parameter>
                    <Name>BtnSelectLocal</Name>
                    <Text>Seleccionar Local</Text>
                    <EventId>1026</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
                <Parameter>
                    <Name>BtnQuitarLocal</Name>
                    <Text>Quitar local</Text>
                    <EventId>1027</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>MacroSelectedLocalZ > -100000</Visible>
                </Parameter>
            </Parameter>
            <!-- Modo MANUAL: Cota Z absoluta (visible cuando no hay local seleccionado) -->
            <Parameter>
                <Name>MacroZAbs</Name>
                <Text>Cota Z (mm)</Text>
                <Value>0</Value>
                <MinValue>-100000</MinValue>
                <MaxValue>100000</MaxValue>
                <ValueType>Integer</ValueType>
                <Visible>MacroSelectedLocalZ &lt;= -100000</Visible>
            </Parameter>
            <!-- Modo con local: Altura relativa al piso (visible cuando hay local seleccionado) -->
            <Parameter>
                <Name>MacroZRelative</Name>
                <Text>Altura sobre el piso (mm)</Text>
                <Value>1000</Value>
                <MinValue>0</MinValue>
                <MaxValue>100000</MaxValue>
                <ValueType>Integer</ValueType>
                <Visible>MacroSelectedLocalZ > -100000</Visible>
            </Parameter>
            <Parameter>
                <Name>MacroLibraryElementType</Name>
                <Text>Tipo de macro</Text>
                <Value>SmartSymbol</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Visible>False</Visible>
                <Parameter>
                    <Name>MacroSmartSymbolRadioButton</Name>
                    <Text>Macro (SmartSymbol .nmk)</Text>
                    <Value>SmartSymbol</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>MacroFixtureRadioButton</Name>
                    <Text>Fixture (.lfx/.pxf)</Text>
                    <Value>Fixture</Value>
                    <ValueType>RadioButton</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>MacroSmartSymbolPath</Name>
                <Text>Seleccionar macro (SmartSymbol)</Text>
                <Value></Value>
                <ValueType>String</ValueType>
                <ValueDialog>SmartSymbolDialog</ValueDialog>
                <Visible>MacroLibraryElementType == "SmartSymbol"</Visible>
            </Parameter>
            <Parameter>
                <Name>MacroFixturePath</Name>
                <Text>Seleccionar fixture</Text>
                <Value></Value>
                <ValueType>String</ValueType>
                <ValueDialog>FixtureDialog</ValueDialog>
                <Visible>False</Visible>
            </Parameter>
        </Parameter>
        <!-- ELEMENTOS DEFINIDOS: UI para colocar elementos predefinidos -->
        <Parameter>
            <Name>ElementExpander</Name>
            <Text>Elemento</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>DefinedElementType</Name>
                <Text>Elemento</Text>
                <Value>Caixa Connexions 200</Value>
                <ValueList>Caixa Connexions 200</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>ElementPointMode</Name>
                <Text>Tipo de punto</Text>
                <Value>2</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Visible>False</Visible>
                <Parameter>
                    <Name>ElementStart</Name>
                    <Text>Punto inicial</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ElementEnd</Name>
                    <Text>Punto final</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ElementFree</Name>
                    <Text>Intermedio o libre</Text>
                    <Value>2</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>BtnSelectElementPoint</Name>
                    <Text>Seleccionar punto</Text>
                    <EventId>1015</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsElementCaptureMode == False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnAcceptElement</Name>
                    <Text>Aceptar (Terminar selección)</Text>
                    <EventId>1021</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsElementCaptureMode == True</Visible>
                </Parameter>
                <Parameter>
                    <Name>IsElementCaptureMode</Name>
                    <Text>IsElementCaptureMode</Text>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>ElementRotX</Name>
                <Text>Rot X (grados)</Text>
                <Value>0</Value>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>ElementRotY</Name>
                <Text>Rot Y (grados)</Text>
                <Value>0</Value>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>ElementRotZ</Name>
                <Text>Rot Z (grados)</Text>
                <Value>0</Value>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>ElementActionRow</Name>
                <Text>Acción</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>BtnAddElementPoint</Name>
                    <Text>Añadir punto</Text>
                    <EventId>1016</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnFinalizarElementos</Name>
                    <Text>Finalizar</Text>
                    <EventId>1003</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
    </Page>
    <Page>
        <Name>PageSoportes</Name>
        <Text>Soportes</Text>
        <!-- ══════════════════════════════════════════
         BLOQUE 1 · Tipo de soporte
         ══════════════════════════════════════════ -->
        <!-- Familia: Zeta / Omega -->
        <Parameter>
            <Name>TypeSupport</Name>
            <Text>Tipo de soporte</Text>
            <Value>Zeta</Value>
            <ValueType>StringComboBox</ValueType>
            <ValueList></ValueList>
            <EventId>1030</EventId>
        </Parameter>
        <!-- Subtipo semántico → campo "subtipo" del mock JSON -->
        <Parameter>
            <Name>SubtipoSoporte</Name>
            <Text>Subtipo instalación</Text>
            <Value></Value>
            <ValueType>Text</ValueType>
            <FontSize>16</FontSize>
            <FontStyle>2</FontStyle>
            <!-- <Value></Value>
            <ValueType>StringComboBox</ValueType>
            <ValueList>Ventilación|Clima|Electricidad|Agua|Saneamiento</ValueList> -->
        </Parameter>
        <!-- Superficie → campo "superficie" del mock JSON -->
        <Parameter>
            <Name>Superficie</Name>
            <Text>Superficie</Text>
            <Value>Liso</Value>
            <ValueType>StringComboBox</ValueType>
            <ValueList>Liso|Perforado</ValueList>
        </Parameter>
        <Parameter>
            <Name>SepDimensiones</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 2 · Dimensiones
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>CotaA</Name>
            <Text>Cota A (mm)</Text>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <MinValue>0.0</MinValue>
        </Parameter>
        <Parameter>
            <Name>CotaB</Name>
            <Text>Cota B (mm)</Text>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <MinValue>0.0</MinValue>
        </Parameter>
        <Parameter>
            <Name>AnguloInclinacion</Name>
            <Text>Ángulo inclinación (°)</Text>
            <Value>0.0</Value>
            <ValueType>Angle</ValueType>
        </Parameter>
        <Parameter>
            <Name>SepAcciones</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 5 · Acciones de inserción
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>RowInsertar</Name>
            <Text>Insertar</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>InsertarSoporte</Name>
                <Text>Insertar soporte</Text>
                <EventId>1033</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowCrear</Name>
            <Text>Crear</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>CrearSoporte</Name>
                <Text>Crear Soporte</Text>
                <EventId>1034</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- Contador de soportes acumulados -->
        <Parameter>
            <Name>RowSoporteCount</Name>
            <Text>Soportes</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>SoporteCount</Name>
                <Text>Estado</Text>
                <Value>Acumulados: 0</Value>
                <ValueType>Text</ValueType>
                <FontSize>14</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>SepGestion</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 6 · Gestión de soportes acumulados
         ══════════════════════════════════════════ -->
        <!-- RadioButtonGroup modo edición: 0=Desactivado, 1=Edición, 2=Edición Mover -->
        <Parameter>
            <Name>SoporteEditMode</Name>
            <Text>Modo edición</Text>
            <Value>0</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <EventId>1038</EventId>
            <Parameter>
                <Name>EditModeDisabled</Name>
                <Text>Desactivado</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>EditModeEdit</Name>
                <Text>Edición</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>EditModeMove</Name>
                <Text>Edición Mover</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
         <Parameter>
            <Name>SepAtributos</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- Botones gestión: borrar + insertar en plano -->
        <Parameter>
            <Name>RowBorrarSoportes</Name>
            <Text>Borrar Soporte</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>BorrarSoportes</Name>
                <Text>Borrar sel.</Text>
                <EventId>1036</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>SepAtributos</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 7 · Atributos de soporte
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>RowSoporteAttr</Name>
            <Text>Atributo de soporte</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>SoporteAttributeValue</Name>
                <Text>Valor atributo</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowAplicarAttr</Name>
            <Text>Aplicar atributo soporte</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>AplicarAtributoSoporte</Name>
                <Text>Aplicar atributo</Text>
                <EventId>1037</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 8 · Estado interno (oculto)
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>SoportesSavedState</Name>
            <Text>SoportesSavedState</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
    </Page>
</Element>