<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
    <Name>Instalaciones\Saneamiento\pyp-scripts\Conjuntsreduction_006.py</Name>
        <Title>Tubo Saneamiento</Title>
        <Version>1.0</Version>
    </Script>

    <Page>
        <Name>Dimensiones</Name>
        <Text>Parámetros del tubo</Text>
        <!-- Grupo de opciones de largo y diámetro -->
        <Parameter>
            <Name>TipoTubo</Name>
            <Text>Combinación Largo y Diámetro</Text>
            <Value>0</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Parameter>
                <Name>D110</Name>
                <Text>Bifurcación 110mm a 40mm</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>D40</Name>
                <Text>Reductor 110mm a 40mm</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
    </Page>
</Element>