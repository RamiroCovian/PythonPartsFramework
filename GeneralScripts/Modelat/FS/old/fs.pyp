<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Formas\fs_v1\fs.py</Name>
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
            <Parameter>
                <Name>ZRotation</Name>
                <Text>Rotación Z (0-360°)</Text>
                <Value>0</Value>
                <ValueType>Integer</ValueType>
                <ValueSlider>True</ValueSlider>
                <MinValue>0</MinValue>
                <MaxValue>360</MaxValue>
                <ExcludeIdentical>True</ExcludeIdentical>
                <IntervalValue>15</IntervalValue>
            </Parameter>
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

        <!-- Parámetro simple para cambiar bordes -->
        <Parameter>
            <Name>BordesExpander</Name>
            <Text>Configuración de Bordes</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>CambiarBorde</Name>
                <Text>Cambiar posición del borde</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Enable>True</Enable>
            </Parameter>
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
                <Name>PlanchaAncho</Name>
                <Text>Ancho (PLD 900-1200mm)</Text>
                <Value>1200.0</Value>
                <MinValue>900</MinValue>
                <MaxValue>1200</MaxValue>
                <ValueType>Length</ValueType>
            </Parameter>
            <Parameter>
                <Name>PlanchaLargo</Name>
                <Text>Largo (900-3000mm)</Text>
                <Value>3000.0</Value>
                <MinValue>900</MinValue>
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
                <Name>PLDType</Name>
                <Text>Tipo de PLD</Text>
                <Value>OMNIA</Value>
                <ValueList>OMNIA|HUMITAT|R_FOC</ValueList>
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
                <Value>40</Value>
                <ValueList>40|50|70|80|100|120</ValueList>
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


                    <Parameter>
                        <Name>LayerPLD</Name>
                        <Text>Capa PLD</Text>
                        <Value>1</Value>
                        <ValueType>Layer</ValueType>
                    </Parameter>
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

                    <Parameter>
                        <Name>LayerXPS</Name>
                        <Text>Capa XPS</Text>
                        <Value>2</Value>
                        <ValueType>Layer</ValueType>
                        <Visible>False</Visible>
                    </Parameter>
                </Parameter>
            </Parameter>
        </Parameter>
    </Page>
</Element>