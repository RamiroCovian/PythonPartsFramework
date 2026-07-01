<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>Instalaciones\FG_AUTOMAT\ANGULARS\pyp-scripts\LineAngulars.py</Name>
    <Title>Simple Line Script v1</Title>
    <Version>1.0</Version>
    <ReadLastInput>True</ReadLastInput>
    <Interactor>False</Interactor>
  </Script>

  <Page>
    <Name>Angulars</Name>
    <Text>Angulars</Text>

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
      <Name>General</Name>
      <Text>Propiedades Generales</Text>
      <Visible>True</Visible>
      <ValueType>Expander</ValueType>

      <!--
      <Parameter>
        <Name>CommonProp</Name>
        <Text>Propiedades Comunes</Text>
        <Value></Value>
        <ValueType>CommonProperties</ValueType>
      </Parameter>
      -->

      <Parameter>
        <Name>Ample</Name>
        <Text>Ample</Text>
        <Value>300</Value>
        <MinValue>0</MinValue>
        <ValueType>Length</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>

      <Parameter>
        <Name>Altura</Name>
        <Text>Altura</Text>
        <Value>200</Value>
        <MinValue>0</MinValue>
        <ValueType>Length</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>

      <Parameter>
        <Name>Llargada</Name>
        <Text>Llargada</Text>
        <Value>300</Value>
        <Enable>False</Enable>
        <MinValue>1</MinValue>
        <ValueType>Length</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>

      <Parameter>
        <Name>SelectorGruix</Name>
        <Text>Selector Gruix</Text>
        <Value>Gruix 15 mm</Value>
        <ValueList>Gruix 15 mm|Gruix 20 mm|Gruix 35 mm|Gruix 120 mm</ValueList>
        <ValueType>StringComboBox</ValueType>
      </Parameter>

      <Parameter>
        <Name>Gruix</Name>
        <Text>Gruix</Text>
        <Value>15</Value>
        <Enable>False</Enable>
        <MinValue>1</MinValue>
        <ValueType>Length</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>

      <Parameter>
        <Name>nEncaixos</Name>
        <Text>nEncaixos</Text>
        <Value>1</Value>
        <MinValue>1</MinValue>
        <ValueType>Integer</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>


      <Parameter>
        <Name>invertirPared</Name>
        <Text>Pared Inv</Text>
        <Value>False</Value>
        <ValueType>CheckBox</ValueType>
      </Parameter>

    </Parameter>

    <Parameter>
      <Name>AngulsPar</Name>
      <Text>Parámetros de Angulars</Text>
      <ValueType>Expander</ValueType>

      <Parameter>
        <Name>PMP_FG_ANG_NOM</Name>
        <Text>PMP_FG_ANG_NOM</Text>
        <Value>TEXT</Value>
        <Visible>False</Visible>
        <ValueType>String</ValueType>
      </Parameter>
      <Parameter>
        <Name>PMP_FG_ANG_CARA</Name>
        <Text>PMP_FG_ANG_CARA</Text>
        <Value>LLISA/RUGOS</Value>
        <Visible>False</Visible>
        <ValueType>String</ValueType>
      </Parameter>
      <Parameter>
        <Name>PMP_FG_ANG_DETALL</Name>
        <Text>PMP_FG_ANG_DETALL</Text>
        <Value>TEXT</Value>
        <Visible>False</Visible>
        <ValueType>String</ValueType>
      </Parameter>
    </Parameter>

  </Page>
</Element>