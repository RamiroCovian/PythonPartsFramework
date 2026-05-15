<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Clima\pyp-scripts\colze.py</Name>
        <Title>colze_implusio_retorn</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <Name>Dimensiones</Name>
        <Title>Dimensiones</Title>
    </Page>
    <Page>
        <Name>Colze</Name>
        <Title>Colze</Title>

        <Parameter>
            <Name>TypeColze</Name>
            <Text>Tipo de Colze</Text>
            <Value>Implusio</Value>
            <ValueList>Implusio|Retorn</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>TypeColzeImplusio</Name>
            <Text>Medida Colze Implusio</Text>
            <Value>150x150</Value>
            <ValueList>150x150|150x200|150x250|150x300|150x350|150x400|150x450|150x500|150x550|150x600|150x650|150x700|150x750</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeColze == "Implusio"</Visible>
        </Parameter>

        <Parameter>
            <Name>TypeColzeRetorn</Name>
            <Text>Medida Colze Retorn</Text>
            <Value>150x150</Value>
            <ValueList>150x150|150x200|150x250|150x300|150x350|150x400|150x450|150x500|150x550|150x600|150x650|150x700|150x750</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeColze == "Retorn"</Visible>
        </Parameter>

    </Page>
</Element>