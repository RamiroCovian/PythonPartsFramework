<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Fontaneria\IS\pyp-scripts\Tub_Polietile_007_IS.py</Name>
        <Title>Tub Polietilè</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <Name>TipoTubPolietile</Name>
        <Title>Tipo de Tub Polietilè</Title>

        <!-- PRIMERO: tipo de agua -->
        <Parameter>
            <Name>TipoDeAgua</Name>
            <Text>Tipo de agua</Text>
            <Value>Fred</Value>
            <ValueList>Fred|Calent|Retorn|MC fred|MC calent</ValueList>
            <!-- Si lo quieres como radio buttons -->
            <!-- <ValueType>RadioButtonGroup</ValueType> -->
            <!-- Si lo quieres combo -->
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <!-- COMBO PARA FRIA -->
        <Parameter>
            <Name>TipoTubPolietileFred</Name>
            <Text>Medida Tub - Fred</Text>
            <Value>Ø20-5ML - Fred</Value>
            <ValueList>Ø20-5ML - Fred|Ø25-5ML - Fred</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- Solo visible cuando TipoDeAgua == Fria -->
            <Visible>TipoDeAgua == "Fred"</Visible>
        </Parameter>

        <!-- COMBO PARA CALIENTE -->
        <Parameter>
            <Name>TipoTubPolietileCalent</Name>
            <Text>Medida tubo - Calent</Text>
            <Value>Ø20-5ML - Calent</Value>
            <ValueList>Ø20-5ML - Calent|Ø25-5ML - Calent</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TipoDeAgua == "Calent"</Visible>
        </Parameter>

        <!-- COMBO PARA RETORNO -->
        <Parameter>
            <Name>TipoTubPolietileRetorn</Name>
            <Text>Medida Tub - Retorn</Text>
            <Value>Ø20-5ML - Retorn</Value>
            <ValueList>Ø20-5ML - Retorn|Ø25-5ML - Retorn</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TipoDeAgua == "Retorn"</Visible>
        </Parameter>

        <!-- COMBO PARA MC Fred -->
        <Parameter>
            <Name>TipoTubPolietileMCfred</Name>
            <Text>Medida tubo - MC fred</Text>
            <Value>Ø20-5ML - MC fred</Value>
            <ValueList>Ø20-5ML - MC fred|Ø25-5ML - MC fred</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TipoDeAgua == "MC fred"</Visible>
        </Parameter>

        <!-- COMBO PARA RETORNO -->
        <Parameter>
            <Name>TipoTubPolietileMCcalent</Name>
            <Text>Medida Tub - MC calent</Text>
            <Value>Ø20-5ML - MC calent</Value>
            <ValueList>Ø20-5ML - MC calent|Ø25-5ML - MC calent</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TipoDeAgua == "MC calent"</Visible>
        </Parameter>

    </Page>
</Element>