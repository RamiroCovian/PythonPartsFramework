<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Clima\pyp-scripts\Tram_recte.py</Name>
        <Title>Tram recte retorn</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <Name>TypeTramRecte</Name>
        <Title>Tipo de Tramo</Title>

        <!-- PRIMERO: tipo de Tramo -->
        <Parameter>
            <Name>TypeTramRecte</Name>
            <Text>Tipo de Tramo</Text>
            <Value>Retorn</Value>
            <ValueList>Retorn|Impulsió|Retorn Amb Tapa|Impulsió Amb Tapa</ValueList>
            <!-- Si lo quieres como radio buttons -->
            <!-- <ValueType>RadioButtonGroup</ValueType> -->
            <!-- Si lo quieres combo -->
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <!-- COMBO PARA RETORN -->
        <Parameter>
            <Name>TypeTramRecteRetorn</Name>
            <Text>Medida Tram - Retorn</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- Solo visible cuando TipoDeAgua == Fria -->
            <Visible>TypeTramRecte == "Retorn"</Visible>
        </Parameter>

        <!-- COMBO PARA IMPULSIÓ -->
        <Parameter>
            <Name>TypeTramRecteImpulsió</Name>
            <Text>Medida Tram - Impulsió</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeTramRecte == "Impulsió"</Visible>
        </Parameter>

        <!-- COMBO PARA RETORNO AMB TAPA -->
        <Parameter>
            <Name>TypeTramRecteRetornAmbTapa</Name>
            <Text>Medida Tram - Retorn Amb Tapa</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeTramRecte == "Retorn Amb Tapa"</Visible>
        </Parameter>

        <!-- COMBO PARA MC IMPULSIÓ AMB TAPA -->
        <Parameter>
            <Name>TypeTramRecteImpulsióAmbTapa</Name>
            <Text>Medida Tram - Impulsió Amb Tapa</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeTramRecte == "Impulsió Amb Tapa"</Visible>
        </Parameter>
    </Page>
</Element>