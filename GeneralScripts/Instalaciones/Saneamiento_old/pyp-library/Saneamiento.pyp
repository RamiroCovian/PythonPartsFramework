<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Saneamiento\pyp-scripts\Saneamiento.py</Name>
        <Title>SANEAMIENTO</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <!-- 0. Elegir el diametro de los objetos -->
        <Name>Dimensiones</Name>
        <Text>Parámetros del tubo</Text>
        <TextId>1001</TextId>


        <!-- Ventana principal (Expander) -->
        <Parameter>
            <Name>ExpanderVentanaPrincipal</Name>
            <Text>Ventana principal</Text>
            <TextId>1002</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>RowCrear</Name>
                <Text>Crear Polilíneas</Text>
                <TextId>1003</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CrearPolylinea</Name>
                    <Text>Crear polilínea</Text>
                    <TextId>1004</TextId>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowInsertarPunto</Name>
                <Text>Insertar Punto</Text>
                <TextId>1005</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CheckBoxInsertarPunto</Name>
                    <Text>Mode Insertar punto</Text>
                    <TextId>1006</TextId>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowLimitarAngulos</Name>
                <Text>Limitar ángulos</Text>
                <TextId>1007</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CheckBoxLimitarAngulos</Name>
                    <Text>Limitar ángulos</Text>
                    <TextId>1008</TextId>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowComprobacionAngulosPopup</Name>
                <Text>Comprobación de ángulos</Text>
                <TextId>1009</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CheckBoxComprobacionAngulosPopup</Name>
                    <Text>Comprobación de Angulos permitidos (popup)</Text>
                    <TextId>1010</TextId>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>LongitudMinimaSegmento</Name>
                <Text>Longitud mínima de segmento (mm)</Text>
                <TextId>1011</TextId>
                <Value>600</Value>
                <ValueType>Length</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>5000</MaxValue>
            </Parameter>
            <Parameter>
                <Name>LongitudMinimaInsertar</Name>
                <Text>Longitud mínima para insertar punto/dividir segmento (mm)</Text>
                <TextId>1012</TextId>
                <Value>600</Value>
                <ValueType>Length</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>5000</MaxValue>
            </Parameter>

            <Parameter>
                <Name>RowPlanoTrabajo</Name>
                <Text>Plano de trabajo</Text>
                <TextId>1058</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>PlanoTrabajo</Name>
                    <Text>Restringir trazado a plano</Text>
                    <TextId>1059</TextId>
                    <Value>Libre</Value>
                    <ValueType>StringComboBox</ValueType>
                    <ValueList>Libre|XY|XZ|YZ</ValueList>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowBorrar</Name>
                <Text>Borrar</Text>
                <TextId>1013</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>borrarSeccion</Name>
                    <Text>Borrar sección</Text>
                    <TextId>1014</TextId>
                    <EventId>1004</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowOrientacion3D</Name>
                <Text>Orientación 3D</Text>
                <TextId>1015</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>definirOrientacion</Name>
                    <Text>Definir orientación</Text>
                    <TextId>1016</TextId>
                    <EventId>1012</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>Orientacion3DRow</Name>
                <Text>Orientación Actual</Text>
                <TextId>1017</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>Orientacion3DInfo</Name>
                    <Text></Text>
                    <TextId>1018</TextId>
                    <Value>No definida</Value>
                    <ValueType>Text</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowInvertir</Name>
                <Text>Invertir</Text>
                <TextId>1019</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>invertirFlechas</Name>
                    <Text>Invertir flechas</Text>
                    <TextId>1020</TextId>
                    <EventId>1010</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowGenerar</Name>
                <Text>Guardar</Text>
                <TextId>1021</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>generarpolilinea</Name>
                    <Text>Guardar polilínea</Text>
                    <TextId>1022</TextId>
                    <EventId>1002</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>PreviewModeButtonText</Name>
                <Text>PreviewModeButtonText</Text>
                <TextId>1023</TextId>
                <Value>0</Value>
                <Visible>False</Visible>
                <Enable>False</Enable>
                <ValueType>Integer</ValueType>
                <Persistent>Session</Persistent>
            </Parameter>
            <Parameter>
                <Name>RowFinalizar</Name>
                <Text>Finalizar</Text>
                <TextId>1024</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>finalizarCreacion</Name>
                    <TextDyn>return "Finalizar y crear" if PreviewModeButtonText == 1 else "Pasar a Edición de Layers"</TextDyn>
                    <EventId>1003</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>

        <!-- Cota Z por defecto: debajo de Plano de trabajo (fuera del expander) -->
        <Parameter>
            <Name>CotaTrabajoDefecto</Name>
            <Text>Cota Z por defecto (mm)</Text>
            <TextId>1060</TextId>
            <Value>0.0</Value>
            <ValueType>Length</ValueType>
        </Parameter>

        <!-- Consola: parámetro a nivel raíz para que build_ele.Consola exista y se actualice desde el script -->
        <Parameter>
            <Name>ExpanderConsola</Name>
            <Text>Consola</Text>
            <TextId>1025</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>NameRow</Name>
                <Text>Estado</Text>
                <TextId>1026</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>Consola</Name>
                    <Text></Text>
                    <TextId>1027</TextId>
                    <Value></Value>
                    <ValueType>Text</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <!-- Gestión de Secciones (Expander) -->
        <Parameter>
            <Name>ExpanderSecciones</Name>
            <Text>Gestión de Secciones</Text>
            <TextId>1028</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Saneamiento</Name>
                <Text>Tipo de saneamiento</Text>
                <TextId>1029</TextId>
                <Value>0</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>Pluvial</Name>
                    <Text>Pluvial</Text>
                    <TextId>1030</TextId>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>Fecal</Name>
                    <Text>Fecal</Text>
                    <TextId>1031</TextId>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>SeccionesHeader</Name>
                <Text>Diámetro a aplicar</Text>
                <TextId>1032</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>DiametroAplicarPluvial</Name>
                    <Text>Diámetro a aplicar</Text>
                    <TextId>1033</TextId>
                    <Value>110</Value>
                    <ValueType>IntegerComboBox</ValueType>
                    <ValueList>110</ValueList>
                    <Visible>Saneamiento == 0</Visible>
                </Parameter>
                <Parameter>
                    <Name>DiametroAplicarFecal</Name>
                    <Text>Diámetro a aplicar</Text>
                    <TextId>1034</TextId>
                    <Value>40</Value>
                    <ValueType>IntegerComboBox</ValueType>
                    <ValueList>25|40|110</ValueList>
                    <Visible>Saneamiento == 1</Visible>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowAplicarSeccion</Name>
                <Text>Cambio de sección</Text>
                <TextId>1035</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>aplicarSeccion</Name>
                    <Text>Aplicar diámetro</Text>
                    <TextId>1036</TextId>
                    <EventId>1007</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>

        <!-- Gestión de Layers (Expander) -->
        <Parameter>
            <Name>ExpanderLayers</Name>
            <Text>Gestión de Layers</Text>
            <TextId>1037</TextId>
            <ValueType>Expander</ValueType>
            <!-- Tipo de instalación: Horizontal o Vertical (excluyentes) -->
            <Parameter>
                <Name>TipoOrientacion</Name>
                <Text>Orientación de instalación</Text>
                <TextId>1038</TextId>
                <Value>0</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>OrientacionHorizontal</Name>
                    <Text>Horizontal (Techo)</Text>
                    <TextId>1039</TextId>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>OrientacionVertical</Name>
                    <Text>Vertical (Pared)</Text>
                    <TextId>1040</TextId>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>TipoInstalacionHorizontal</Name>
                <Text>Tipo instalación horizontal</Text>
                <TextId>1041</TextId>
                <Value>FABRICA</Value>
                <ValueType>StringComboBox</ValueType>
                <ValueList>FABRICA|OBRA</ValueList>
                <Visible>TipoOrientacion == 0</Visible>
            </Parameter>
            <Parameter>
                <Name>TipoInstalacionVertical</Name>
                <Text>Tipo instalación vertical</Text>
                <TextId>1042</TextId>
                <Value>TD</Value>
                <ValueType>StringComboBox</ValueType>
                <ValueList>TD|EN|IS</ValueList>
                <Visible>TipoOrientacion == 1</Visible>
            </Parameter>
            <Parameter>
                <Name>CaraEN</Name>
                <Text>Cara (solo EN)</Text>
                <TextId>1043</TextId>
                <Value>X</Value>
                <ValueType>StringComboBox</ValueType>
                <ValueList>X|Y</ValueList>
                <Visible>TipoOrientacion == 1 and TipoInstalacionVertical == "EN"</Visible>
            </Parameter>
            <Parameter>
                <Name>RowSecciones</Name>
                <Text>Acciones de Sección</Text>
                <TextId>1044</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>aplicarLayers</Name>
                    <Text>Aplicar layers</Text>
                    <TextId>1045</TextId>
                    <EventId>1009</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>

        <!-- Gestión de Atributos (dentro de Expander; el Row es necesario para que el botón se muestre) -->
        <Parameter>
            <Name>ExpanderAtributos</Name>
            <Text>Atributos Padre</Text>
            <TextId>1046</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>RowAtributos</Name>
                <Text></Text>
                <TextId>1047</TextId>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>ValorAtributos</Name>
                    <Text>Valor atributo</Text>
                    <TextId>1048</TextId>
                    <Value></Value>
                    <ValueType>String</ValueType>
                </Parameter>
                <Parameter>
                    <Name>aplicarAtributos</Name>
                    <Text>Aplicar atributos</Text>
                    <TextId>1049</TextId>
                    <EventId>1011</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <!-- Parámetro oculto para forzar unicidad de PythonParts -->
        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <TextId>1050</TextId>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        
        <!-- Parámetro oculto para guardar el estado de las polilíneas (para poder restaurar al editar) -->
        <Parameter>
            <Name>SavedState</Name>
            <Text>SavedState</Text>
            <TextId>1051</TextId>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Parámetros ocultos para borrado de copias 3D en otros archivos (igual que Instalaciones MVP) -->
        <Parameter>
            <Name>CopiedElementsUUIDs</Name>
            <Text>CopiedElementsUUIDs</Text>
            <TextId>1052</TextId>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>CopiedElementsFiles</Name>
            <Text>CopiedElementsFiles</Text>
            <TextId>1053</TextId>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
    </Page>
</Element>
