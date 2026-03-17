<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\FS\Polyline_test_cuboid.py</Name>
        <Title>Polyline</Title>
        <Version>1.0</Version>
        <ReadLastInput>False</ReadLastInput>
    </Script>

    <Page>
        <Name>Page1</Name>
        <Text>2D polyline</Text>

        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Format2D</Name>
            <Text>Format</Text>
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

            <Parameter>
                <Name>CommonProp2D</Name>
                <Text></Text>
                <Value></Value>
                <ValueType>CommonProperties</ValueType>
            </Parameter>
        </Parameter>

    </Page>

</Element>
