<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Soportes\Soportes.py</Name>
        <Title>Soportes</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <Name>TypeSupport</Name>
        <Title>Tipo de Soporte</Title>
        <Parameter>
            <Name>TypeSupport</Name>
            <Text>Tipo de Soporte</Text>
            <Value>Omega</Value>
            <!-- Lista de textos que se muestran en el ComboBox -->
            <ValueList>Omega|Zeta</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <!-- COMBO PARA Omega -->
        <Parameter>
            <Name>TypeSupportOmega</Name>
            <Text>Soporte - Omega</Text>
            <Value>Venti.(SVP)</Value>
            <ValueList>Venti.(SVP)|Electr./Clima(SEP)|Varifix</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- Solo visible cuando TypeSupport == Omega -->
            <Visible>TypeSupport == "Omega"</Visible>
        </Parameter>

        <!-- Tipo de instalación: solo para Electr./Clima (SEP) -->
        <Parameter>
            <Name>TypeInstallationSEP</Name>
            <Text>Tipo de instalación</Text>
            <Value>Electricidad</Value>
            <ValueList>Electricidad|Clima</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeSupport == "Omega" and TypeSupportOmega == "Electr./Clima(SEP)"</Visible>
        </Parameter>

        <!-- Tipo de instalación: solo para Varifix -->
        <Parameter>
            <Name>TypeInstallationVarifix</Name>
            <Text>Tipo de instalación</Text>
            <Value>Agua</Value>
            <ValueList>Agua|Saneamiento</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeSupport == "Omega" and TypeSupportOmega == "Varifix"</Visible>
        </Parameter>

        <!-- COMBO PARA Zeta -->
        <Parameter>
            <Name>TypeSupportZeta</Name>
            <Text>Soporte - Zeta</Text>
            <Value>150x150</Value>
            <ValueList>0mm|205x152.26mm|205x200mm|110x200mm</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeSupport == "Zeta"</Visible>
        </Parameter>

        <!-- Superficie del soporte: Liso (sin perforaciones) o Perforado -->
        <Parameter>
            <Name>SupportSurface</Name>
            <Text>Superficie</Text>
            <Value>Perforado</Value>
            <ValueList>Liso|Perforado</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>
    </Page>
</Element>