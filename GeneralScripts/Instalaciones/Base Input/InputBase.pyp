<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>PythonPartsTraining\InputBase.py</Name>
    <Title>Input BAse</Title>
    <Version>4.0</Version>
    <Interactor>False</Interactor>
    <ShowFavoriteButtons>False</ShowFavoriteButtons>
  </Script>

  <Page>
    <Name>PointInput</Name>
    <Text>Capturá por roles (Final crea y exporta). Editá con los botones de abajo.</Text>

    <!-- ===== CAPTURA ===== -->
    <Parameter>
      <Name>PathId</Name>
      <Text>Path Id (color)</Text>
      <Value>1</Value>
      <MinValue>1</MinValue>
      <MaxValue>255</MaxValue>
      <ValueType>Integer</ValueType>
    </Parameter>

    <Parameter>
      <Name>SegmentId</Name>
      <Text>Segmento</Text>
      <Value>1</Value>
      <MinValue>1</MinValue>
      <MaxValue>9999</MaxValue>
      <ValueType>Integer</ValueType>
    </Parameter>

    <!-- 0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final -->
    <Parameter>
      <Name>PointRole</Name>
      <Text>Rol del punto (0..3)</Text>
      <Value>1</Value>
      <MinValue>0</MinValue>
      <MaxValue>3</MaxValue>
      <ValueType>Integer</ValueType>
    </Parameter>

    <Parameter>
      <Name>RowRoles</Name>
      <Text>Setear rol</Text>
      <ValueType>Row</ValueType>
      <Parameter>
        <Name>BtnRolInicial</Name>
        <Text>Inicial</Text>
        <EventId>2100</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
      <Parameter>
        <Name>BtnRolPaso</Name>
        <Text>Paso</Text>
        <EventId>2101</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
      <Parameter>
        <Name>BtnRolBif</Name>
        <Text>Bifurcación</Text>
        <EventId>2102</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
      <Parameter>
        <Name>BtnRolFinal</Name>
        <Text>Final</Text>
        <EventId>2103</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <!-- Opciones de CoordinateInput -->
    <Parameter>
      <Name>EnableAssistWndClick</Name>
      <Text>Permitir click en Assist window</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>
    <Parameter>
      <Name>EnableZCoordinate</Name>
      <Text>Permitir coordenada Z</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>
    <Parameter>
      <Name>EnableUndoStep</Name>
      <Text>Habilitar undo step</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>
    <Parameter>
      <Name>SetProjectionBase0</Name>
      <Text>Proyección base 0</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <!-- Propiedades comunes -->
    <Parameter>
      <Name>CommonProp</Name>
      <Text>Propiedades comunes</Text>
      <Value></Value>
      <ValueType>CommonProperties</ValueType>
    </Parameter>

    <!-- Símbolo opcional por click -->
    <Parameter>
      <Name>CreateSymbol</Name>
      <Text>Crear símbolo al click</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>
    <Parameter>
      <Name>SymbolCommonProps</Name>
      <Text>Propiedades del símbolo</Text>
      <Value></Value>
      <ValueType>CommonProperties</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator1</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- ===== EDITOR ===== -->
    <Parameter>
      <Name>RowCrear</Name>
      <Text>Crear Polilíneas</Text>
      <ValueType>Row</ValueType>
      <Parameter>
        <Name>CrearPolylinea</Name>
        <Text>Crear polilínea</Text>
        <EventId>1001</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>RowGenerar</Name>
      <Text>Generar</Text>
      <ValueType>Row</ValueType>
      <Parameter>
        <Name>generarpolilinea</Name>
        <Text>Guardar polilínea</Text>
        <EventId>1002</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>RowFinalizar</Name>
      <Text>Finalizar</Text>
      <ValueType>Row</ValueType>
      <Parameter>
        <Name>finalizarCreacion</Name>
        <Text>Finalizar y crear</Text>
        <EventId>1003</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>RowBorrar</Name>
      <Text>Borrar</Text>
      <ValueType>Row</ValueType>
      <Parameter>
        <Name>borrarSeccion</Name>
        <Text>Borrar sección</Text>
        <EventId>1004</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>RowCrearBifurcacion</Name>
      <Text>Crear Bifurcación</Text>
      <ValueType>Row</ValueType>
      <Parameter>
        <Name>crearBifurcacion</Name>
        <Text>Bifurcar</Text>
        <EventId>1006</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>Separator2</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <Parameter>
      <Parameter>
        <Name>CheckBoxValue</Name>
        <Text>Mode Insertar punto</Text>
        <Value>False</Value>
        <ValueType>CheckBox</ValueType>
      </Parameter>
    </Parameter>

  </Page>
</Element>
