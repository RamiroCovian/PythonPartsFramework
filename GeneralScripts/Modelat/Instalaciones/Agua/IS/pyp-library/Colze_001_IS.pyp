<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Fontaneria\IS\pyp-scripts\Colze_001_IS.py</Name>
        <Title>Colze 001</Title>
        <Version>1.0</Version>
    </Script>

    <Page>
        <Name>TipoCodo</Name>
        <Title>Tipo de codo</Title>
        <!-- Grupo de opciones -->
        <Parameter>
            <Name>TipoCodo</Name>
            <Text>Tipo de codo</Text>
            <Value>0</Value> <!-- 0 = C020, 1 = C025 -->
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>C020</Name>
                <Text>CØ20</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>C025</Name>
                <Text>CØ25</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
    </Page>
</Element>