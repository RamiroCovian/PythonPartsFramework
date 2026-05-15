<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Saneamiento\pyp-scripts\Tub_PVC_Tricapa_005.py</Name>
        <Title>Tubo Saneamiento</Title>
        <Version>1.6</Version>
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
                <Name>L1000_D110</Name>
                <Text>110D 1m</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>L3000_D110</Name>
                <Text>110D 3m</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>L1000_D40</Name>
                <Text>40D 1m</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>L3000_D40</Name>
                <Text>40D 3m</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
    </Page>
</Element>
