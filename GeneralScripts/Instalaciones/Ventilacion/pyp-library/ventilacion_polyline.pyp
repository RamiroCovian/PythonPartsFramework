<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Ventilacion\pyp-scripts\ventilacion_polyline.py</Name>
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
</Element>