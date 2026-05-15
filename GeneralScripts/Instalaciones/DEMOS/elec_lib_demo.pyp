<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\DEMOS\elec_lib_demo.py</Name>
        <Title>Editor Polilíneas Instalaciones (Library Demo)</Title>
        <Version>1.0.0</Version>
        <Interactor>False</Interactor>
    </Script>
    <Page>
        <Name>CrearPolilinea</Name>
        <Text>Definir polilínea para una instalación y generar elementos.</Text>
        <TextId>1000</TextId>
        <Parameter>
            <Name>InstallationName</Name>
            <Text>Instalacion</Text>
            <TextId>1001</TextId>
            <Value></Value>
            <ValueType>Text</ValueType>
            <FontSize>16</FontSize>
            <FontStyle>2</FontStyle>
        </Parameter>
        <Parameter>
            <Name>SupportedAngles</Name>
            <Text>Angulos Soportados</Text>
            <TextId>1002</TextId>
            <Value></Value>
            <ValueType>Text</ValueType>
            <FontSize>16</FontSize>
            <FontStyle>2</FontStyle>
        </Parameter>
         <Parameter>
            <Name>InstallationTypeTitle</Name>
            <Text>Tipos de instalacion</Text>
            <TextId>1003</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>InstallationType</Name>
                <Text>Elegir instalacion</Text>
                <TextId>1004</TextId>
                <Value></Value>
                <ValueList></ValueList>
                <EventId>1002</EventId>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>FunctionalName</Name>
                <Text>Nombre funcional del cable</Text>
                <TextId>1005</TextId>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
            <Parameter>
                <Name>DistributionType</Name>
                <Text>Tipo de Distribucion</Text>
                <TextId>1006</TextId>
                <Value>IS</Value>
                <ValueList>IS|TD|EN</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>FaceEN</Name>
                <Text>Cara (EN)</Text>
                <TextId>1007</TextId>
                <Value>Cara X</Value>
                <ValueList>Cara X|Cara Y</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>DistributionType == "EN"</Visible>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RejibandWidthMode</Name>
            <Text>Rejiband Ancho (interno)</Text>
            <TextId>1008</TextId>
            <Value>100</Value>
            <ValueList>100|200</ValueList>
            <Visible>False</Visible>
            <ValueType>StringComboBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>PointModeTitle</Name>
            <Text>Modos de dibujo</Text>
            <TextId>1009</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>AddCut</Name>
                <Text>Añadir cortes</Text>
                <TextId>1010</TextId>
                <Value>0</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
                <Enable>False</Enable>
            </Parameter>
            <Parameter>
                <Name>PointMode</Name>
                <Text>Elegir modo</Text>
                <TextId>1011</TextId>
                <Value>0</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>SelectPolyline</Name>
                    <Text>Modo Edicion</Text>
                    <TextId>1012</TextId>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>SmartPolyline</Name>
                    <Text>Modo Creacion</Text>
                    <TextId>1013</TextId>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>OverlapTitle</Name>
            <Text>Solapamiento</Text>
            <TextId>1014</TextId>
            <ValueType>Expander</ValueType>
            <Visible>False</Visible>
            <Parameter>
                <Name>OverlapMillimeter</Name>
                <Text>Solapar mm</Text>
                <TextId>1015</TextId>
                <Value>0</Value>
                <Visible>False</Visible>
                <MinValue>0</MinValue>
                <MaxValue>10000</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>heightZ</Name>
                <Text>Altura en Z</Text>
                <TextId>1016</TextId>
                <Value>0</Value>
                <MinValue>-9999</MinValue>
                <MaxValue>9999</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>rotation</Name>
            <Text>Rotacion en ejes (grados)</Text>
            <TextId>1017</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>axisX</Name>
                <Text>Eje X</Text>
                <TextId>1018</TextId>
                <Value>0</Value>
                <Visible>False</Visible>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>axisY</Name>
                <Text>Eje Y</Text>
                <TextId>1019</TextId>
                <Value>0</Value>
                <Visible>False</Visible>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>axisZ</Name>
                <Text>Eje Z</Text>
                <TextId>1020</TextId>
                <Value>0</Value>
                <Visible>False</Visible>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>LayersTitle</Name>
            <Text>Layers</Text>
            <TextId>1021</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>LayerTipo</Name>
                <Text>Tipo de instalación (layers)</Text>
                <TextId>1022</TextId>
                <Value>Corrugats electricitat</Value>
                <ValueList>Telecos|Corrugats electricitat|Rejibands|KN_ELECTRICITAT|KN_X_ELECTRICITAT|KN_Y_ELECTRICITAT</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>LayerSubtipo</Name>
                <Text>Subtipo (layers)</Text>
                <TextId>1023</TextId>
                <Value>SOBRE REJIBAND</Value>
                <ValueList>SOBRE REJIBAND|D'ENTRADA|DE SORTIDA</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>LayerTipo != "Rejibands"</Visible>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>aplicarLayers</Name>
                <Text>Aplicar layers</Text>
                <TextId>1024</TextId>
                <EventId>1009</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowAttribute</Name>
            <Text>Atributos</Text>
            <TextId>1025</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>AttributeValue</Name>
                <Text>Valor atributo</Text>
                <TextId>1026</TextId>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>AttributeApply</Name>
                <Text>Aplicar atributo</Text>
                <TextId>1027</TextId>
                <EventId>1011</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>MacroExpander</Name>
            <Text>Macro</Text>
            <TextId>1028</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>MarkerPointMode</Name>
                <Text>Elegir punto</Text>
                <TextId>1029</TextId>
                <Value>2</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Visible>False</Visible>
                <Parameter>
                    <Name>MarkerStart</Name>
                    <Text>Punto inicial</Text>
                    <TextId>1030</TextId>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>MarkerEnd</Name>
                    <Text>Punto final</Text>
                    <TextId>1031</TextId>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>MarkerFree</Name>
                    <Text>Libre</Text>
                    <TextId>1032</TextId>
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
                    <TextId>1033</TextId>
                    <EventId>1013</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsMacroCaptureMode == False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnAddMacroMarker</Name>
                    <Text>Colocar macro</Text>
                    <TextId>1073</TextId>
                    <EventId>1014</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsMacroCaptureMode == False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnAcceptMacro</Name>
                    <Text>Aceptar (Terminar selección)</Text>
                    <TextId>1034</TextId>
                    <EventId>1020</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsMacroCaptureMode == True</Visible>
                </Parameter>
                <Parameter>
                    <Name>IsMacroCaptureMode</Name>
                    <Text>IsMacroCaptureMode</Text>
                    <TextId>1035</TextId>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>MacroZAbs</Name>
                <Text>Cota Z (mm)</Text>
                <TextId>1036</TextId>
                <Value>0</Value>
                <MinValue>-100000</MinValue>
                <MaxValue>100000</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>

            <Parameter>
                <Name>MacroLibraryElementType</Name>
                <Text>Tipo de macro</Text>
                <TextId>1037</TextId>
                <Value>SmartSymbol</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Visible>False</Visible>
                <Parameter>
                    <Name>MacroSmartSymbolRadioButton</Name>
                    <Text>Macro (SmartSymbol .nmk)</Text>
                    <TextId>1038</TextId>
                    <Value>SmartSymbol</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>MacroFixtureRadioButton</Name>
                    <Text>Fixture (.lfx/.pxf)</Text>
                    <TextId>1039</TextId>
                    <Value>Fixture</Value>
                    <ValueType>RadioButton</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>

            <Parameter>
                <Name>MacroSmartSymbolPath</Name>
                <Text>Seleccionar macro (SmartSymbol)</Text>
                <TextId>1040</TextId>
                <Value></Value>
                <ValueType>String</ValueType>
                <ValueDialog>SmartSymbolDialog</ValueDialog>
                <Visible>MacroLibraryElementType == "SmartSymbol"</Visible>
            </Parameter>

            <Parameter>
                <Name>MacroFixturePath</Name>
                <Text>Seleccionar fixture</Text>
                <TextId>1041</TextId>
                <Value></Value>
                <ValueType>String</ValueType>
                <ValueDialog>FixtureDialog</ValueDialog>
                <Visible>False</Visible>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>ElementExpander</Name>
            <Text>Elemento</Text>
            <TextId>1042</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>DefinedElementType</Name>
                <Text>Elemento</Text>
                <TextId>1043</TextId>
                <Value>Circulo</Value>
                <ValueList>Circulo|Cuadrado|Triangulo</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>ElementZAbs</Name>
                <Text>Cota Z (mm)</Text>
                <TextId>1044</TextId>
                <Value>0</Value>
                <MinValue>-100000</MinValue>
                <MaxValue>100000</MaxValue>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>ElementPointMode</Name>
                <Text>Posicion</Text>
                <TextId>1045</TextId>
                <Value>2</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Visible>False</Visible>
                <Parameter>
                    <Name>ElementStart</Name>
                    <Text>Punto inicial</Text>
                    <TextId>1046</TextId>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                    <Visible>False</Visible>
                </Parameter>
                <Parameter>
                    <Name>ElementEnd</Name>
                    <Text>Punto final</Text>
                    <TextId>1047</TextId>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                    <Visible>False</Visible>
                </Parameter>
                <Parameter>
                    <Name>ElementFree</Name>
                    <Text>Libre</Text>
                    <TextId>1048</TextId>
                    <Value>2</Value>
                    <ValueType>RadioButton</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>
            <Parameter>
                <ValueType>Row</ValueType>
                <Visible>True</Visible>
                <Parameter>
                    <Name>BtnSelectElementPoint</Name>
                    <Text>Seleccionar punto</Text>
                    <TextId>1049</TextId>
                    <EventId>1015</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsElementCaptureMode == False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnAddDefinedElement</Name>
                    <Text>Colocar elemento</Text>
                    <TextId>1074</TextId>
                    <EventId>1016</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsElementCaptureMode == False</Visible>
                </Parameter>
                <Parameter>
                    <Name>BtnAcceptElement</Name>
                    <Text>Aceptar (Terminar selección)</Text>
                    <TextId>1050</TextId>
                    <EventId>1021</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                    <Visible>IsElementCaptureMode == True</Visible>
                </Parameter>
                <Parameter>
                    <Name>IsElementCaptureMode</Name>
                    <Text>IsElementCaptureMode</Text>
                    <TextId>1051</TextId>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                    <Visible>False</Visible>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>General</Name>
            <Text>General options</Text>
            <TextId>1052</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>CommonProp</Name>
                <Text></Text>
                <Value></Value>
                <Visible>False</Visible>
                <Enable>False</Enable>
                <ValueType>CommonProperties</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowPythonPart</Name>
                <Text>PythonPartGroup</Text>
                <TextId>1053</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CreatePythonPart</Name>
                    <Text>Crear como PythonPartGroup</Text>
                    <TextId>1054</TextId>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                    <Enable>False</Enable>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>Orientacion3DExpander</Name>
            <Text>Orientación 3D</Text>
            <TextId>1055</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>RowOrientacion3D</Name>
                <Text>Definir orientación</Text>
                <TextId>1056</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>definirOrientacion</Name>
                    <Text>Definir orientación</Text>
                    <TextId>1057</TextId>
                    <EventId>1012</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>Orientacion3DRow</Name>
                <Text>Orientación Actual</Text>
                <TextId>1058</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>Orientacion3DInfo</Name>
                    <Text></Text>
                    <Value>No definida</Value>
                    <ValueType>Text</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowContinuar</Name>
            <Text>Continuar</Text>
            <TextId>1059</TextId>
            <ValueType>Row</ValueType>
            <Visible>PointMode == 0</Visible>
            <Parameter>
                <Name>continuarPolilinea</Name>
                <Text>Continuar Polilinea</Text>
                <TextId>1060</TextId>
                <EventId>1025</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowBorrar</Name>
            <Text>Borrar</Text>
            <TextId>1061</TextId>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>borrarSeccion</Name>
                <Text>Borrar Seleccion</Text>
                <TextId>1062</TextId>
                <EventId>1004</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowJSON</Name>
            <Text>JSON</Text>
            <TextId>1075</TextId>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>exportJSON</Name>
                <Text>Exportar JSON</Text>
                <TextId>1076</TextId>
                <EventId>1030</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
            <Parameter>
                <Name>importJSON</Name>
                <Text>Importar JSON</Text>
                <TextId>1077</TextId>
                <EventId>1031</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
            <Parameter>
                <Name>generateOptimal</Name>
                <Text>Generar Camino Optimo</Text>
                <TextId>1078</TextId>
                <EventId>1032</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowFinalizar</Name>
            <Text>Finalizar</Text>
            <TextId>1063</TextId>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>finalizarCreacion</Name>
                <Text>Finalizar - Crear</Text>
                <TextId>1064</TextId>
                <EventId>1003</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <TextId>1065</TextId>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
        </Parameter>
        <Parameter>
            <Name>PointRole</Name>
            <Text>PointRole</Text>
            <TextId>1066</TextId>
            <Value>Paso</Value>
            <Visible>True</Visible>
            <Enable>True</Enable>
            <ValueType>StringComboBox</ValueType>
            <ValueList>Inicial|Paso|Bifurcacion|Final</ValueList>
        </Parameter>
        <Parameter>
            <Name>PathId</Name>
            <Text>PathId</Text>
            <TextId>1067</TextId>
            <Value>1</Value>
            <Visible>True</Visible>
            <Enable>True</Enable>
            <ValueType>Integer</ValueType>
            <MinValue>1</MinValue>
        </Parameter>
        <Parameter>
            <Name>SegmentId</Name>
            <Text>SegmentId</Text>
            <TextId>1068</TextId>
            <Value>1</Value>
            <Visible>True</Visible>
            <Enable>True</Enable>
            <ValueType>Integer</ValueType>
            <MinValue>1</MinValue>
        </Parameter>
        <Parameter>
            <Name>CreatePythonPartGroup</Name>
            <Text>CreatePythonPartGroup</Text>
            <TextId>1069</TextId>
            <Value>True</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>PendingMacroCapture</Name>
            <Text>PendingMacroCapture</Text>
            <TextId>1070</TextId>
            <Value>False</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>PendingElementCapture</Name>
            <Text>PendingElementCapture</Text>
            <TextId>1071</TextId>
            <Value>False</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>PolylineState</Name>
            <Text>PolylineState</Text>
            <TextId>1072</TextId>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
    </Page>
</Element>
