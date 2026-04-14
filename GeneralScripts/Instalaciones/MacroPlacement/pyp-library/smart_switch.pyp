<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Techtiva\test_locales\pyp-scripts\smart_switch.py</Name>
        <Title>Interruptor de Pared</Title>
        <Version>1.0</Version>
        <ReadLastInput>False</ReadLastInput>
    </Script>
    <Page>
        <Name>Properties</Name>
        <Text>Propiedades</Text>
        <Parameter>
            <Name>FLOOR_COUNT</Name>
            <Text>Cantidad de plantas</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
        </Parameter>
        <Parameter>
            <Name>FLOOR_INDEX</Name>
            <Text>Piso detectado</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
        </Parameter>
        <Parameter>
            <Name>Z_ABSOLUTE</Name>
            <Text>Altura absoluta (mts)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
        </Parameter>
        <Parameter>
            <Name>Z_RELATIVE</Name>
            <Text>Altura relativa (mts)</Text>
            <Value>1000</Value>
            <ValueType>Length</ValueType>
            <ReadOnly>True</ReadOnly>
        </Parameter>
        <Parameter>
            <Name>DEVICE_TYPE</Name>
            <Text>Tipo de Dispositivo</Text>
            <Value></Value>
            <ValueType>String</ValueType>
            <ReadOnly>True</ReadOnly>
        </Parameter>
    </Page>
</Element>