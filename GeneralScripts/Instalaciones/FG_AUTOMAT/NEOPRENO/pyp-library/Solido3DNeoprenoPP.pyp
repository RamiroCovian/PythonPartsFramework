<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\FG_AUTOMAT\NEOPRENO\pyp-scripts\Solido3DNeoprenoPP.py</Name>
        <Title>Sólido 3D Neopreno PythonPart</Title>
        <Version>1.0</Version>
        <ReadLastInput>True</ReadLastInput>
        <Interactor>True</Interactor>
        <Text>Crea sólido 3D de neopreno con selección de grosor mediante radio buttons</Text>
    </Script>

    <Page>
        <Name>Propiedades</Name>
        <Text>Propiedades</Text>

        <!-- Parametros necesarios internamente pero ocultos en la paleta -->
        <Parameter>
            <Name>PuntoInicial</Name>
            <Text>Punto Inicial</Text>
            <Value>Point3D(0,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>PuntoFinal</Name>
            <Text>Punto Final</Text>
            <Value>Point3D(1000,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Separator1</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>Longitud</Name>
            <Text>Longitud</Text>
            <Value>1000.00</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>Ancho</Name>
            <Text>Ancho</Text>
            <Value>50</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>Separator2</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>SeparatorGrosor</Name>
            <Text>Grosor</Text>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>GrosorSeleccionado</Name>
            <Text>Grosor</Text>
            <Value>5</Value>
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>Grosor5mm</Name>
                <Text>5mm - Fuxia</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor10mm</Name>
                <Text>10mm - Verde</Text>
                <Value>10</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor20mm</Name>
                <Text>20mm - Rosa</Text>
                <Value>20</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor30mm</Name>
                <Text>30mm - Naranja</Text>
                <Value>30</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor40mm</Name>
                <Text>40mm - Turquesa</Text>
                <Value>40</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator3</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <!-- Parametros necesarios internamente pero ocultos - el color cambia automaticamente con
        el grosor -->
        <Parameter>
            <Name>Color</Name>
            <Text>Color</Text>
            <Value>15</Value>
            <ValueType>Color</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Pen</Name>
            <Text>Grosor de pluma</Text>
            <Value>1</Value>
            <ValueType>Pen</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Stroke</Name>
            <Text>Tipo de linea</Text>
            <Value>1</Value>
            <ValueType>Stroke</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Layer</Name>
            <Text>Capa</Text>
            <Value>-1</Value>
            <ValueType>Layer</ValueType>
            <Visible>False</Visible>
        </Parameter>

    </Page>

</Element>