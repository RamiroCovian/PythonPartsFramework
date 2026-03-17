<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\Estructura\FS\PY\FS.py</Name>
        <Title>Plancha PLD-XPS</Title>
        <Version>1.0</Version>
        <ReadLastInput>False</ReadLastInput>
    </Script>
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector Fill</Text>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>FlagEntrada</Name>
            <Text>FlagEntrada</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>inputPoint</Name>
            <Text>Point POsicio</Text>
            <Value>Point3D(0,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Enable>False</Enable>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>llargadaPared</Name>
            <Text>llargadaPared</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>ampladaPared</Name>
            <Text>ampladaPared</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>alcadaPared</Name>
            <Text>alcadaPared</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>listUUIDElements</Name>
            <Text></Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- #include TD_COnjunt_8_Parent_copy.pyp;-->

        <Parameter>
            <Name>SelectorPPPare</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>5</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>
            <Enable>False</Enable>


            <Parameter>
                <Name>Pare</Name>
                <Text>Pare</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>TD</Name>
                <Text>TD</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>
            <Parameter>
                <Name>EN</Name>
                <Text>EN</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>
            <Parameter>
                <Name>IS</Name>
                <Text>IS</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>
            <Parameter>
                <Name>FS</Name>
                <Text>FS</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1</Visible>
        </Parameter>


        <Parameter>
            <Name>listofPythonChilds</Name>
            <Text>selector de Python Fills</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1</Visible>
        </Parameter>

        <Parameter>
            <Name>SelectorPPPFill</Name>
            <Text>Selector Python Fill</Text>
            <Value>0</Value>
            <ValueList>[str(value) for value in listofPythonChilds]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>FlagEntrada != 1</Visible>
            <BackgroundColor>(0, 175, 255)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ButtonRowAdd</Name>
            <Text>Button</Text>
            <ValueType>Row</ValueType>
            <Visible>FlagEntrada != 1 and SelectorPPPare == 4</Visible>

            <Parameter>
                <Name>ButtonAddIS</Name>
                <Text>afegirIS</Text>
                <EventId>3000</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
            <Parameter>
                <Name>ButtonAddIS</Name>
                <Text>eliminarIS</Text>
                <EventId>3001</EventId>
                <ValueType>Button</ValueType>
                <Visible>False</Visible>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RecalculIS</Name>
            <Text>recalculIS</Text>
            <EventId>1000</EventId>
            <ValueType>Button</ValueType>
            <Visible> False</Visible>
        </Parameter>

        <Parameter>
            <Name>NameFilesChildren</Name>
            <Text>NameFilesChildren</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1</Visible>
        </Parameter>


        <Parameter>
            <Name>PositionChilds</Name>
            <Text>PositionChilds</Text>
            <ValueType>ListGroup</ValueType>
            <ValueType>Column</ValueType>
            <Parameter>
                <Name>listofPositionsChilds</Name>
                <Text>Position $list_row </Text>
                <Value>[]</Value>
                <ValueType>Point3D</ValueType>
                <Visible>FlagEntrada != 1 and $list_row == int(SelectorPPPFill)</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>listofMesuresChilds</Name>
                <Text>Mesura $list_row</Text>
                <Value>[_]</Value>
                <ValueType>Point3D</ValueType>
                <Visible>FlagEntrada != 1 and $list_row == int(SelectorPPPFill)</Visible>
                <!-- <Enable>False</Enable> -->
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>listofVisibleChilds</Name>
                <Text>Mostrar $list_row</Text>
                <Value>[_]</Value>
                <ValueType>Checkbox</ValueType>
                <Visible>FlagEntrada != 1 and $list_row == int(SelectorPPPFill)</Visible>
                <!-- <Enable>False</Enable> -->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1 and SelectorPPPare == 4</Visible>
        </Parameter>
        <Parameter>
            <Name>direccioISInv</Name>
            <Text>Direccio IS Invertida Total</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>direccioISInvActual</Name>
            <Text>Direccio IS Invertida IS Actual</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>FlagEntrada != 1 and SelectorPPPare == 4</Visible>
        </Parameter>



        <!--
        <Parameter>
            <Name>MiHijoPythonPart</Name>
            <Value>{8E5F3B8A-3AFD-4A0B-9B3C-725E7F3C216F}</Value>
            <ValueType>PythonPartReference</ValueType>
        </Parameter>
        -->

    </Page>
    <Page>
        <Name>__hiddenElem__</Name>
        <Text>__hiddenElem__</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>
        <Parameter>
            <Name>listDireccioISInv</Name>
            <Text></Text>
            <Value>[_]</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>$list_row</Visible>
        </Parameter>
        <Parameter>
            <Name>totalPeces</Name>
            <Text>Integer</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Parent:PythonPartConnection</Name>
        <Text>Crear Plancha Compuesta</Text>
        <Visible>True</Visible>

        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
        </Parameter>

        <!-- Control de rotación en el eje Z -->
         <Parameter>
            <Name>Rotaciondeeje</Name>
            <Text>Rotacion de eje</Text>
            <ValueType>Expander</ValueType>

            <!-- Nuevo parámetro de entrada para rotación Z con valores negativos -->
            <Parameter>
                <Name>ZRotationInput</Name>
                <Text>Rotación Z (-360° a 360°)</Text>
                <Value>0</Value>
                <ValueType>Integer</ValueType>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>AnchoBorde</Name>
            <Text>Ancho del borde</Text>
            <Value>255</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
        </Parameter>

    </Page>

    <!-- Medidas Plancha -->
    <Page>
        <Name>medidasPlancha</Name>
        <Text>Medidas Plancha</Text>
        <Visible>True</Visible>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Dimensiones de Plancha</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>AnchoPLD</Name>
                <Text>Ancho (FS 400-1200mm)</Text>
                <Value>1200.0</Value>
                <MinValue>400</MinValue>
                <MaxValue>1200</MaxValue>
                <ValueType>Length</ValueType>
            </Parameter>
            <Parameter>
                <Name>LargoPLD</Name>
                <Text>Largo (FS 400-3000mm)</Text>
                <Value>3000.0</Value>
                <MinValue>400</MinValue>
                <MaxValue>3000</MaxValue>
                <ValueType>Length</ValueType>
            </Parameter>
            <Parameter>
                <Name>EspesorPLD</Name>
                <Text>Espesor PLD</Text>
                <Value>15.0</Value>
                <MinValue>15</MinValue>
                <MaxValue>15</MaxValue>
                <ValueType>Length</ValueType>
                <Enable>False</Enable>
            </Parameter>

            <!-- Modified PLD Type Selector using StringComboBox -->
            <Parameter>
                <Name>TypePLD</Name>
                <Text>Tipo de PLD</Text>
                <Value>OMNIA</Value>
                <ValueList>OMNIA|HUMITAT|FOC</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>ColorPLD</Name>
                <Text>Color PLD (Automático)</Text>
                <Value>7</Value>
                <ValueType>Color</ValueType>
                <Enable>False</Enable>
                <Visible>False</Visible>
            </Parameter>
            <Parameter>
                <Name>EspesorXPS</Name>
                <Text>Espesor XPS</Text>
                <Value>120</Value>
                <ValueList>40|50|70|100|120</ValueList>
                <ValueType>LengthComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Propiedades</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>

                <!-- Propiedades para PLD (plancha inferior) -->
                <Parameter>
                    <Name>PLDPropertiesExpander</Name>
                    <Text>Propiedades PLD</Text>
                    <value>True</value>
                    <ValueType>Expander</ValueType>
                    <Visible>False</Visible>

                    <!-- Color is now automatically determined by type and dimensions -->
                </Parameter>

                <!-- Propiedades para XPS (plancha superior) -->
                <Parameter>
                    <Name>XPSPropertiesExpander</Name>
                    <Text>Propiedades XPS</Text>
                    <value>True</value>
                    <ValueType>Expander</ValueType>
                    <Visible>False</Visible>

                    <Parameter>
                        <Name>ColorXPS</Name>
                        <Text>Color XPS</Text>
                        <Value>24</Value>
                        <ValueType>Color</ValueType>
                    </Parameter>

                </Parameter>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>

            <Name>SelectorBordeAfilado</Name>
            <Text>Borde Afilado Opciones (menor a 1200 mm)</Text>
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>BordeAfiladoLeft</Name>
                <Text>Izquierdo</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>BordeAfiladoRight</Name>
                <Text>Derecho</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>LayerValueName</Name>
            <Text>Definir numero layer</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>Cavidades</Name>
        <Text>Cavidades</Text>
        <Visible>True</Visible>

        <!-- Figure selector  -->
        <Parameter>

            <Name>SelectorFigura</Name>
            <Text>Seleccione el tipo de figura</Text>
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>CuboidFigure</Name>
                <Text>Rectangular</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>CylinderFigure</Name>
                <Text>Cilindro</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

        </Parameter>
        <!-- End figure selector  -->

        <!-- Cuboid figure params  -->
        <Parameter>
            <Name>AnchoCavidadCuboid</Name>
            <Text>Ancho cuboide rectangular</Text>
            <Value>400</Value>
            <MinValue>50</MinValue>
            <MaxValue>400</MaxValue>
            <ValueType>Length</ValueType>
            <Visible>SelectorFigura == 1</Visible>
        </Parameter>
        <Parameter>
            <Name>LargoCavidadCuboid</Name>
            <Text>Largo cuboide rectangular</Text>
            <Value>800</Value>
            <MinValue>100</MinValue>
            <MaxValue>800</MaxValue>
            <ValueType>Length</ValueType>
            <Visible>SelectorFigura == 1</Visible>
        </Parameter>
        <Parameter>
            <Name>EspesorCavidadCuboid</Name>
            <Text>Espesor cuboide rectangular</Text>
            <Value>15.0</Value>
            <MinValue>15</MinValue>
            <MaxValue>15</MaxValue>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
            <Visible>SelectorFigura == 1</Visible>
        </Parameter>
        <!-- End cuboid figure params  -->

        <!-- Cylinder figure params  -->
        <Parameter>
            <Name>DiametroCavidadCylinder</Name>
            <Text>Diametro cylinder</Text>
            <Value>100</Value>
            <MinValue>100</MinValue>
            <MaxValue>400</MaxValue>
            <ValueType>Length</ValueType>
            <Visible>SelectorFigura == 2</Visible>
        </Parameter>
        <!-- End cylinder figure params  -->

        <!-- Button create figure -->
        <Parameter>
            <Name>ButtonRow</Name>
            <Text>Crear</Text>
            <ValueType>Row</ValueType>

            <Parameter>
                <Name>ButtonCreateFigure</Name>
                <Text>OK</Text>
                <EventId>1000</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- End button create figure -->

    </Page>

    <Page>
        <Name>SelectorPythonPartFS</Name>
        <Text>Selector FS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>CavidadesPythonPartFS</Name>
        <Text>Selector cavidades FS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8_cavidades_manuales.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>GIRS FS</Name>
        <Text>GIRS FS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8_inclinacion_rotacion.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>ModelizacionXPS</Name>
        <Text>Modelizacion XPS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8_modelizacion_xps.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>
</Element>