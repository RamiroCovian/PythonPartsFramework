<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\FS\PLD.py</Name>
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

</Element>