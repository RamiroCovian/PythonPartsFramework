<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Clima\pyp-scripts\quiebro2.py</Name>
        <Title>Quiebro2 (S — cotas hendidura / recto / oblicuo)</Title>
        <Version>1.0.5</Version>
    </Script>
    <Page>
        <Name>PageQuiebro2</Name>
        <Title>Quiebro2</Title>

        <Parameter>
            <Name>Q2_Type</Name>
            <Text>Tipo de instalación</Text>
            <Value>Retorn</Value>
            <ValueList>Retorn|Impulsió</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>Q2_DiameterRetorn</Name>
            <Text>Medida quiebro2 - Retorn</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>Q2_Type == "Retorn"</Visible>
        </Parameter>
        <Parameter>
            <Name>Q2_DiameterImpulsio</Name>
            <Text>Medida quiebro2 - Impulsió</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>Q2_Type == "Impulsió"</Visible>
        </Parameter>

        <Parameter>
            <Name>ExpQ2Geom</Name>
            <Text>Figura 2D (mm)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Q2_GrooveLen_mm</Name>
                <Text>Largo hendidura (0,025 m)</Text>
                <Value>25.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Q2_GrooveWidth_mm</Name>
                <Text>Altura sección Z en hendidura (0,199 m; con ancho 0,200 m define Z hend/Z total)</Text>
                <Value>199.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Q2_StraightLen_mm</Name>
                <Text>Largo tramo recto antes de hendidura (0,075 m)</Text>
                <Value>75.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Q2_MainWidth_mm</Name>
                <Text>Ancho horizontal tramo recto (0,200 m)</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Q2_SlantEdgeLen_mm</Name>
                <Text>Longitud arista tramo oblicuo (1,03235 m)</Text>
                <Value>1032.35</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Q2_InclinationFromHorizontal_deg</Name>
                <Text>Inclinación tramo oblicuo respecto a la horizontal (90°=vertical; 45°–90°)</Text>
                <Value>75.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>45.0</MinValue>
                <MaxValue>90.0</MaxValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpQ2Solid</Name>
            <Text>Sólido 3D</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Q2_ExtrudeZ_mm</Name>
                <Text>Extrusión Z — tramo central (p. ej. 0,200 m; hendidura usa 199/200 de este valor)</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Q2_Color</Name>
                <Text>Color (índice Allplan)</Text>
                <Value>207</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
        </Parameter>
    </Page>
</Element>
