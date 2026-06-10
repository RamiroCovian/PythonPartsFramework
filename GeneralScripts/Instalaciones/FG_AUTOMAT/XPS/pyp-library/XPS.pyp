<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\FG_AUTOMAT\XPS\pyp-scripts\XPS.py</Name>
        <Title>Superficie Zona XPS</Title>
        <Version>1.0</Version>
        <ReadLastInput>True</ReadLastInput>
        <Interactor>False</Interactor>
    </Script>

    <Page>
        <Name>ZoneProperties</Name>
        <Text>Propiedades de la Zona</Text>

        <Parameter>
            <Name>ShowXPS</Name>
            <Text>Mostrar XPS completa</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>wall_id</Name>
            <Text>Wall ID</Text>
            <Value></Value>
            <ValueType>String</ValueType>
        </Parameter>

        <Parameter>
            <Name>z_unique</Name>
            <Text>z_unique</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>XPSGruix</Name>
            <Text>Gruix XPS</Text>
            <Value>40</Value>
            <ValueList>40|80|100|120</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>do_walls</Name>
            <Text>Walls</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>do_mensules</Name>
            <Text>Mensules</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>AtributsExpander</Name>
            <Text>Atributs Premarcs</Text>
            <ValueType>Expander</ValueType>
            <Value>True</Value>

            <Parameter>
                <Name>INPUT_PMP_FG_AILLANT</Name>
                <Text>PMP_FG_AILLANT</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>INPUT_PMP_FG_XPS_SUP</Name>
                <Text>PMP_FG_XPS_SUP</Text>
                <Value></Value>
                <ValueType>Double</ValueType>
            </Parameter>

            <Parameter>
                <Name>INPUT_PMP_FG_PIR_SUP</Name>
                <Text>PMP_FG_PIR_SUP</Text>
                <Value></Value>
                <ValueType>Double</ValueType>
            </Parameter>

            <Parameter>
                <Name>INPUT_PMP_FG_MENSULA</Name>
                <Text>PMP_FG_MENSULA</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>INPUT_PMP_FG_MEN_SUP</Name>
                <Text>PMP_FG_MEN_SUP</Text>
                <Value></Value>
                <ValueType>Double</ValueType>
            </Parameter>
        </Parameter>

    </Page>
</Element>