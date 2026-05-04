<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>FG_AUTOMAT\FERRALLA\pyp-scripts\Ferralla.py</Name>
    <Title>Simple Line Script v1</Title>
    <Version>1.0</Version>
    <ReadLastInput>True</ReadLastInput>
    <Interactor>False</Interactor>
  </Script>

  <Page>
    <Name>SimpleLine</Name>
    <Text>Línea Simple</Text>

    <Parameter>
      <Name>General</Name>
      <Text>Propiedades Generales</Text>
      <Visible>False</Visible>
      <ValueType>Expander</ValueType>

      <Parameter>
        <Name>CommonProp</Name>
        <Text>Propiedades Comunes</Text>
        <Value></Value>
        <ValueType>CommonProperties</ValueType>
      </Parameter>

      <Parameter>
        <Name>LineColor</Name>
        <Text>Color de la Línea</Text>
        <Value>1</Value>
        <ValueType>Integer</ValueType>
        <MinValue>1</MinValue>
        <MaxValue>255</MaxValue>
      </Parameter>

      <Parameter>
        <Name>LineThickness</Name>
        <Text>Grosor de la Línea</Text>
        <Value>1</Value>
        <ValueType>Integer</ValueType>
        <MinValue>1</MinValue>
        <MaxValue>10</MaxValue>
      </Parameter>

    </Parameter>
    <Parameter>
      <Name>Hormigon</Name>
      <Text>Parámetros de Hormigón</Text>
      <ValueType>Expander</ValueType>

      <!-- Elemento: extremo_izq -->
      <Parameter>
          <Name>base_extremo_izq</Name>
          <Text>base_extremo_izq</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>altura_extremo_izq</Name>
          <Text>altura_extremo_izq</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>largo_extremo_izq</Name>
          <Text>largo_extremo_izq</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>


      <!-- Elemento: extremo_der -->
      <Parameter>
          <Name>base_extremo_der</Name>
          <Text>base_extremo_der</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>altura_extremo_der</Name>
          <Text>altura_extremo_der</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>largo_extremo_der</Name>
          <Text>largo_extremo_der</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>

      <!-- Elemento: eje_izq -->
      <Parameter>
          <Name>base_eje_izq</Name>
          <Text>base_eje_izq</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>altura_eje_izq</Name>
          <Text>altura_eje_izq</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>largo_eje_izq</Name>
          <Text>largo_eje_izq</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>

      <!-- Elemento: eje_der -->
      <Parameter>
          <Name>base_eje_der</Name>
          <Text>base_eje_der</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>altura_eje_der</Name>
          <Text>altura_eje_der</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>
      <Parameter>
          <Name>largo_eje_der</Name>
          <Text>largo_eje_der</Text>
          <Visible>False</Visible>
          <ValueType>Double</ValueType>
          <Value></Value>
      </Parameter>

      <Parameter>
        <Name>A1sabEsq</Name>
        <Text>A1sab. esq. (m)</Text>
        <ValueType>Double</ValueType>
        <Value>1.07</Value>
      </Parameter>

      <Parameter>
        <Name>Leixos</Name>
        <Text>Leixos (m)</Text>
        <ValueType>Double</ValueType>
        <Value>6</Value>
      </Parameter>

      <Parameter>
        <Name>A2sabD</Name>
        <Text>A2sab. d. (m)</Text>
        <ValueType>Double</ValueType>
        <Value>1.07</Value>
      </Parameter>

      <Parameter>
            <Name>ArmSuperior</Name>
            <Text>Armadura Superior</Text>
            <Label>Armadura</Label>
            <ValueType>Integer</ValueType>
            <Value>3</Value>
      </Parameter>
      <Parameter>
          <Name>ArmInferior</Name>
          <Text>Armadura Inferior</Text>
          <Label>Armadura</Label>
          <ValueType>Integer</ValueType>
          <Value>3</Value>
      </Parameter>
      <Parameter>
          <Name>Separator</Name>
          <Text>Separador</Text>
          <ValueType>Separator</ValueType>
      </Parameter>
      <Parameter>
          <Name>CantoSabata</Name>
          <Text>Canto Sabata</Text>
          <Label>Sabata</Label>
          <ValueType>Double</ValueType>
          <Value>0.25</Value>
      </Parameter>

      <!-- Lista de Elementos Dinamicos -->
      <Parameter>
          <Name>ListaElementosDinamica</Name>
          <Text>Listadinamica</Text>
          <Value>[]</Value>
          <ValueType>String</ValueType>
          <Visible>False</Visible>
          <!-- <Persistent>Model</Persistent> -->
      </Parameter>
      <Parameter>
          <Name>SelectorElemento</Name>
          <Text>Seleccionar Elemento</Text>
          <Value>Rango 1</Value>
          <ValueList>[str(value) for value in ListaElementosDinamica]</ValueList>
          <ValueType>StringComboBox</ValueType>
      </Parameter>

      <Parameter>
          <Name>RadioGroupValue</Name>
          <Text>RadioGroup</Text>
          <Value>1</Value>
          <ValueType>RadioButtonGroup</ValueType>

          <Parameter>
              <Name>RadioButtonValue1</Name>
              <Text>S/Pared</Text>
              <Value>1</Value>
              <ValueType>RadioButton</ValueType>
          </Parameter>
          <Parameter>
              <Name>RadioButtonValue2</Name>
              <Text>C/Pared</Text>
              <Value>2</Value>
              <ValueType>RadioButton</ValueType>
          </Parameter>
      </Parameter>
    </Parameter>
  </Page>
</Element>
