<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\FS\FS_inclination_rotate.py</Name>
        <Title>Plancha PLD-XPS</Title>
        <Version>1.0</Version>
        <ReadLastInput>False</ReadLastInput>
    </Script>
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
        <Name>InclinacionRotacion</Name>
        <Text>Inclinacion/Rotacion</Text>
        <Visible>True</Visible>

        <!-- Control de rotación inclinacion -->
         <Parameter>
            <Name>RotacionInclinacion</Name>
            <Text>Rotacion Inclinacion</Text>
            <ValueType>Expander</ValueType>

            <!-- Nuevo parámetro de entrada para rotación Z con valores negativos -->
            <Parameter>
                <Name>RotationInputAngle</Name>
                <Text>Rotación (-360° a 360°)</Text>
                <Value>0</Value>
                <ValueType>Integer</ValueType>
                <MinValue>-360</MinValue>
                <MaxValue>360</MaxValue>
            </Parameter>

        </Parameter>

        <!-- Axis selector  -->
        <Parameter>

            <Name>SelectorAxis</Name>
            <Text>Seleccione el axis de inclinacion</Text>
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>InclinacionAxisX</Name>
                <Text>Axis X</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>InclinacionAxisY</Name>
                <Text>Axis Y</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>InclinacionAxisZ</Name>
                <Text>Axis Z</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

        </Parameter>
        <!-- End figure selector  -->

        <!-- Button create inclination -->
        <Parameter>
            <Name>ButtonRow</Name>
            <Text>Crear</Text>
            <ValueType>Row</ValueType>

            <Parameter>
                <Name>ButtonCreateInclination</Name>
                <Text>OK</Text>
                <EventId>1001</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- End button create inclination -->

    </Page>

</Element>