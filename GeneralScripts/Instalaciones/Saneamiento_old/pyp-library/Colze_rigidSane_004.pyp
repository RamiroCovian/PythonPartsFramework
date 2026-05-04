<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Saneamiento\pyp-scripts\Colze_rigidSane_004.py</Name>
        <Title>Colze Rigid</Title>
        <Version>1.6</Version>
    </Script>
    <Page>
        <Name>Dimensiones</Name>
        <Text>Parámetros del colze</Text>
        <!-- Grupo de opciones de largo y diámetro -->
        <Parameter>
            <Name>TipoColze</Name>
            <Text>Versiones</Text>
            <Value>10</Value>
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>L1000_D110</Name>
                <Text>110mm 45°</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>L3000_D45</Name>
                <Text>40mm 45°</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>

            <Parameter>
                <Name>L4000_D45</Name>
                <Text>1_40mm 87°</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>L4000_D87</Name>
                <Text>2_40mm 87°</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>

            <Parameter>
                <Name>L5000_D45</Name>
                <Text>1_110mm 87°</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>L5000_D87</Name>
                <Text>2_110mm 87°</Text>
                <Value>6</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
    </Page>
</Element>
