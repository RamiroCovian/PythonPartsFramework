<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>PythonPartsTraining\PointInput_SO.py</Name>
    <Title>PointInput_SO_Roles</Title>
    <Version>1.1</Version>   <!-- ↑ fuerza recarga -->
    <Interactor>False</Interactor>
    <ShowFavoriteButtons>False</ShowFavoriteButtons>
  </Script>

  <Page>
    <Name>PointInput</Name>
    <Text>Point input</Text>

    <Parameter>
      <Name>PointInputOptions</Name>
      <Text>Tipo de Punto / Agrupación</Text>
      <ValueType>Expander</ValueType>

      <!-- GRUPO: mismo tipo/valores que los hijos -->
      <Parameter>
        <Name>PointRole</Name>
        <Text>Rol del punto</Text>
        <Value>Inicial</Value>
        <ValueType>RadioButtonGroup</ValueType>

        <Parameter>
          <Name>RolInicial</Name>
          <Text>Inicial</Text>
          <Value>Inicial</Value>
          <ValueType>RadioButton</ValueType>
        </Parameter>
        <Parameter>
          <Name>RolPaso</Name>
          <Text>Paso</Text>
          <Value>Paso</Value>
          <ValueType>RadioButton</ValueType>
        </Parameter>
        <Parameter>
          <Name>RolBif</Name>
          <Text>Bifurcación</Text>
          <Value>Bifurcacion</Value>
          <ValueType>RadioButton</ValueType>
        </Parameter>
        <Parameter>
          <Name>RolFinal</Name>
          <Text>Final</Text>
          <Value>Final</Value>
          <ValueType>RadioButton</ValueType>
        </Parameter>
      </Parameter>

      <Parameter>
        <Name>PathId</Name>
        <Text>Camino</Text>
        <Value>1</Value>
        <ValueType>Integer</ValueType>
        <MinValue>1</MinValue>
      </Parameter>

      <Parameter>
        <Name>SegmentId</Name>
        <Text>Segmento</Text>
        <Value>1</Value>
        <ValueType>Integer</ValueType>
        <MinValue>1</MinValue>
      </Parameter>
    </Parameter>

    <!-- Propiedades y símbolo -->
    <Parameter>
      <Name>General</Name>
      <Text>General options</Text>
      <ValueType>Expander</ValueType>

      <Parameter>
        <Name>CommonProp</Name>
        <Text></Text>
        <Value></Value>
        <ValueType>CommonProperties</ValueType>
      </Parameter>

      <Parameter>
        <Name>CreateSymbol</Name>
        <Text>Create symbol on mouse click</Text>
        <Value>True</Value>
        <ValueType>CheckBox</ValueType>
      </Parameter>

      <Parameter>
        <Name>SymbolCommonProps</Name>
        <Text></Text>
        <Value></Value>
        <ValueType>CommonProperties</ValueType>
        <Visible>CreateSymbol</Visible>
      </Parameter>
    </Parameter>
  </Page>
</Element>
