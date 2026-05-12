<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
    <Name>Instalaciones\Saneamiento\pyp-scripts\Colze_basic_001.py</Name>
        <Title>Tubo Saneamiento</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <Name>Dimensiones</Name>
        <Text>Parámetros</Text>
        <!-- Tipo de saneamiento -->
        <Parameter>
            <Name>TipoSaneamiento</Name>
            <Text>Tipo de saneamiento</Text>
            <Value>0</Value> <!-- 0 = Pluvial, 1 = Fecal -->
            <ValueType>RadioButtonGroup</ValueType>
            <Parameter>
                <Name>45</Name>
                <Text>45°</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>90</Name>
                <Text>90°</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
    </Page>
</Element>