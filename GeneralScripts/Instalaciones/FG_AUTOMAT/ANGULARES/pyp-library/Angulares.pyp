<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>Instalaciones\FG_AUTOMAT\ANGULARES\pyp-scripts\Angulares.py</Name>
    <Title>Angulars Catálogo sobre Línea</Title>
    <Version>1.1</Version>
    <Interactor>False</Interactor>
    <ScriptObject>True</ScriptObject>
    <Text>Genera angulares prefijados a partir de una línea base</Text>
  </Script>

  <Page>
    <Name>Individual</Name>
    <Text>Individual</Text>
    <TextId>1000</TextId>

    <Parameter>
      <Name>TipoAngular</Name>
      <Text>Tipos de angulares</Text>
      <Value>ANG200_L460</Value>
      <ValueType>RadioButtonGroup</ValueType>
      <TextId>1001</TextId>
      <Persistent>Model</Persistent>

      <Parameter>
        <Name>Separador1</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2001</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloSerie200</Name>
        <Text>Serie 200mm × 200mm × 20mm</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2002</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_200_460</Name>
        <Text>460mm</Text>
        <Value>ANG200_L460</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1010</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_200_310</Name>
        <Text>310mm</Text>
        <Value>ANG200_L310</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1011</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_200_150</Name>
        <Text>150mm</Text>
        <Value>ANG200_L150</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1012</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador2</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2003</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloSerie250</Name>
        <Text>Serie 250mm × 250mm × 25mm</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2004</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_250_460</Name>
        <Text>460mm</Text>
        <Value>ANG250_L460</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1020</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_250_310</Name>
        <Text>310mm</Text>
        <Value>ANG250_L310</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1021</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_250_150</Name>
        <Text>150mm</Text>
        <Value>ANG250_L150</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1022</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador3</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2005</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloTensor</Name>
        <Text>Serie tensores</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2010</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_Tensor</Name>
        <Text>Tensor Estandar</Text>
        <Value>TENSOR</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1023</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador4</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2008</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloAngularJuntaD</Name>
        <Text>Angular de junta D.</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2011</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_Junta_D</Name>
        <Text>200x200x20 (310)</Text>
        <Value>ANG_JUNTA_D</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1024</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador5</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2009</TextId>
      </Parameter>

    </Parameter>

    <Parameter>
      <Name>TipoDistribucion</Name>
      <Text>Distribución activa</Text>
      <Value>Individual</Value>
      <ValueList>Individual|Grupal</ValueList>
      <ValueType>StringComboBox</ValueType>
      <Visible>False</Visible>
      <Enable>False</Enable>
      <TextId>1043</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>RowSeleccionAngularIndividual</Name>
      <Text>Edición</Text>
      <ValueType>Row</ValueType>
      <Visible>PermitirCambiarMuro == True or AngularSeleccionado == True</Visible>
      <Parameter>
        <Name>SeleccionarAngularIndividual</Name>
        <Text>Seleccionar</Text>
        <EventId>1048</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
        <Enable>True</Enable>
        <Visible>PermitirCambiarMuro == True</Visible>
        <TextId>1048</TextId>
        <Persistent>No</Persistent>
      </Parameter>
      <Parameter>
        <Name>DeseleccionarAngularIndividual</Name>
        <Text>Deseleccionar</Text>
        <EventId>1049</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
        <Enable>True</Enable>
        <Visible>PermitirCambiarMuro == True</Visible>
        <TextId>1049</TextId>
        <Persistent>No</Persistent>
      </Parameter>
      <Parameter>
        <Name>EliminarAngularIndividual</Name>
        <Text>Eliminar</Text>
        <EventId>1051</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
        <Enable>True</Enable>
        <Visible>AngularSeleccionado == True</Visible>
        <TextId>1051</TextId>
        <Persistent>No</Persistent>
      </Parameter>
      <Parameter>
        <Name>CambiarMuroIndividual</Name>
        <Text>Cambiar muro</Text>
        <EventId>1050</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
        <Enable>True</Enable>
        <Visible>PermitirCambiarMuro == True</Visible>
        <TextId>1050</TextId>
        <Persistent>No</Persistent>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>SeparacionAngulares</Name>
      <Text>Separación entre angulares</Text>
      <Value>10</Value>
      <ValueType>Length</ValueType>
      <Visible>False</Visible>
      <TextId>1005</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>CrecimientoIncremental</Name>
      <Text>Incremento de crecimiento de línea</Text>
      <Value>0.0</Value>
      <ValueType>Length</ValueType>
      <TextId>1007</TextId>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <ReadOnly>True</ReadOnly>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>LongitudLinea</Name>
      <Text>Longitud de línea</Text>
      <Value>0</Value>
      <ValueType>Length</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1004</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>UsarValorZManual</Name>
      <Text>Usar Valor Z manual</Text>
      <Value>false</Value>
      <ValueType>CheckBox</ValueType>
      <Visible>True</Visible>
      <TextId>1047</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>ValorZIndividual</Name>
      <Text>Cota Z desde el origen del muro</Text>
      <Value>0</Value>
      <ValueType>Length</ValueType>
      <Enable>True</Enable>
      <Visible>True</Visible>
      <TextId>1044</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>SeparatorModo</Name>
      <Text>Modo de Posicionamiento</Text>
      <ValueType>Separator</ValueType>
      <TextId>2006</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>angular_libre</Name>
      <Text>Posicionamiento libre</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
      <Visible>True</Visible>
      <Enable>False</Enable>
      <ReadOnly>z_unique > 0</ReadOnly>
      <TextId>2007</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>RotacionManual</Name>
      <Text>Rotación manual (°)</Text>
      <ValueType>Angle</ValueType>
      <Value>0.0</Value>
      <Enable>angular_libre == True</Enable>
      <Visible>False</Visible>
      <TextId>1002</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>RotacionEjeX</Name>
      <Text>Rotación eje Y (Plano ZX)</Text>
      <ValueType>Angle</ValueType>
      <Value>0.0</Value>
      <Enable>True</Enable>
      <Visible>True</Visible>
      <TextId>1045</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>RotacionEjeY</Name>
      <Text>Rotación eje Z (Plano XY)</Text>
      <ValueType>Angle</ValueType>
      <Value>0.0</Value>
      <Enable>True</Enable>
      <Visible>True</Visible>
      <TextId>1046</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>InvertirAngular</Name>
      <Text>Invertir orientación</Text>
      <Value>false</Value>
      <ValueType>CheckBox</ValueType>
      <Enable>True</Enable>
      <Visible>True</Visible>
      <TextId>1003</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>SiLlevaNeopreno</Name>
      <Text>Si lleva Neopreno</Text>
      <Value>true</Value>
      <ValueType>CheckBox</ValueType>
      <Visible>True</Visible>
      <TextId>1008</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

  </Page>

  <Page>
    <Name>Grupal</Name>
    <Text>Grupal</Text>
    <TextId>1100</TextId>

    <Parameter>
      <Name>TipoAngular</Name>
      <Text>Tipos de angulares</Text>
      <Value>ANG200_L460</Value>
      <ValueType>RadioButtonGroup</ValueType>
      <TextId>1001</TextId>
      <Persistent>Model</Persistent>

      <Parameter>
        <Name>Separador1_Grupal</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2101</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloSerie200_Grupal</Name>
        <Text>Serie 200mm × 200mm × 20mm</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2102</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_200_460_Grupal</Name>
        <Text>460mm</Text>
        <Value>ANG200_L460</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1110</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_200_310_Grupal</Name>
        <Text>310mm</Text>
        <Value>ANG200_L310</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1111</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_200_150_Grupal</Name>
        <Text>150mm</Text>
        <Value>ANG200_L150</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1112</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador2_Grupal</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2103</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloSerie250_Grupal</Name>
        <Text>Serie 250mm × 250mm × 25mm</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2104</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_250_460_Grupal</Name>
        <Text>460mm</Text>
        <Value>ANG250_L460</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1120</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_250_310_Grupal</Name>
        <Text>310mm</Text>
        <Value>ANG250_L310</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1121</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_250_150_Grupal</Name>
        <Text>150mm</Text>
        <Value>ANG250_L150</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1122</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador3_Grupal</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2105</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloTensor_Grupal</Name>
        <Text>Serie tensores</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2110</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_Tensor_Grupal</Name>
        <Text>Tensor Estandar</Text>
        <Value>TENSOR</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1123</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador4_Grupal</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2108</TextId>
      </Parameter>

      <Parameter>
        <Name>TituloAngularJuntaD_Grupal</Name>
        <Text>Angular de junta D.</Text>
        <ValueType>Text</ValueType>
        <Enable>False</Enable>
        <TextId>2111</TextId>
      </Parameter>

      <Parameter>
        <Name>TipoAngular_Junta_D_Grupal</Name>
        <Text>200x200x20 (310)</Text>
        <Value>ANG_JUNTA_D</Value>
        <ValueType>RadioButton</ValueType>
        <TextId>1124</TextId>
        <Persistent>No</Persistent>
      </Parameter>

      <Parameter>
        <Name>Separador5_Grupal</Name>
        <Text>─────────────────────</Text>
        <ValueType>Separator</ValueType>
        <TextId>2109</TextId>
      </Parameter>

    </Parameter>

    <Parameter>
      <Name>ModoGrupalTitulo</Name>
      <Text>Distribución grupal</Text>
      <ValueType>Text</ValueType>
      <Enable>False</Enable>
      <TextId>1101</TextId>
    </Parameter>

    <Parameter>
      <Name>RowEliminarAngularGrupal</Name>
      <Text>Eliminar grupo</Text>
      <ValueType>Row</ValueType>
      <Visible>AngularSeleccionado == True</Visible>
      <Parameter>
        <Name>EliminarAngularGrupal</Name>
        <Text>Eliminar</Text>
        <EventId>1051</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
        <Enable>True</Enable>
        <TextId>1151</TextId>
        <Persistent>No</Persistent>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>SeparacionAngulares</Name>
      <Text>Separación entre angulares</Text>
      <Value>10</Value>
      <ValueType>Length</ValueType>
      <TextId>1005</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>CrecimientoIncremental</Name>
      <Text>Incremento de crecimiento de línea</Text>
      <Value>0.0</Value>
      <ValueType>Length</ValueType>
      <Enable>False</Enable>
      <ReadOnly>True</ReadOnly>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>LongitudLinea</Name>
      <Text>Longitud de línea</Text>
      <Value>0</Value>
      <ValueType>Length</ValueType>
      <Enable>False</Enable>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>SeparatorModoGrupal</Name>
      <Text>Modo de Posicionamiento</Text>
      <ValueType>Separator</ValueType>
      <TextId>1102</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>angular_libre</Name>
      <Text>Posicionamiento libre</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
      <Visible>True</Visible>
      <Enable>False</Enable>
      <ReadOnly>z_unique > 0</ReadOnly>
      <TextId>2007</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>RotacionManual</Name>
      <Text>Rotación manual (°)</Text>
      <ValueType>Angle</ValueType>
      <Value>0.0</Value>
      <Enable>angular_libre == True</Enable>
      <Visible>True</Visible>
      <TextId>1002</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>InvertirAngular</Name>
      <Text>Invertir orientación</Text>
      <Value>false</Value>
      <ValueType>CheckBox</ValueType>
      <Enable>angular_libre == True</Enable>
      <Visible>True</Visible>
      <TextId>1003</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <!-- <Parameter>
      <Name>GrosorNeopreno</Name>
      <Text>Grosor de Neopreno</Text>
      <Value>0.05</Value>
      <ValueType>RadioButtonGroup</ValueType>
      <Enable>SiLlevaNeopreno</Enable>
      <Visible>True</Visible>
      <TextId>1042</TextId>

      <Parameter>
        <Name>GrosorNeopreno_005</Name>
        <Text>0.5</Text>
        <Value>0.05</Value>
        <ValueType>RadioButton</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>
      <Parameter>
        <Name>GrosorNeopreno_010</Name>
        <Text>0.10</Text>
        <Value>0.10</Value>
        <ValueType>RadioButton</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>
      <Parameter>
        <Name>GrosorNeopreno_020</Name>
        <Text>0.20</Text>
        <Value>0.20</Value>
        <ValueType>RadioButton</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>
      <Parameter>
        <Name>GrosorNeopreno_030</Name>
        <Text>0.30</Text>
        <Value>0.30</Value>
        <ValueType>RadioButton</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>
      <Parameter>
        <Name>GrosorNeopreno_040</Name>
        <Text>0.40</Text>
        <Value>0.40</Value>
        <ValueType>RadioButton</ValueType>
        <Persistent>Model</Persistent>
      </Parameter>
    </Parameter> -->

    <Parameter>
      <Name>MuroGUID</Name>
      <Text>GUID del muro</Text>
      <Value></Value>
      <ValueType>Text</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1006</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>LegacyWallReferenceDisabled</Name>
      <Text>Conexión con muro</Text>
      <TextId>1009</TextId>
      <Value></Value>
      <Visible>False</Visible>
      <Enable>False</Enable>
      <ValueType>Text</ValueType>
      <Persistent>No</Persistent>
    </Parameter>

    <Parameter>
      <Name>PuntoInicial</Name>
      <Text>Punto Inicial</Text>
      <Value>Point3D(0,0,0)</Value>
      <ValueType>Point3D</ValueType>
      <Visible>False</Visible>
      <TextId>1034</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PuntoFinal</Name>
      <Text>Punto Final</Text>
      <Value>Point3D(1000,0,0)</Value>
      <ValueType>Point3D</ValueType>
      <Visible>False</Visible>
      <TextId>1035</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaU</Name>
      <Text>Posición relativa U</Text>
      <Value>0.5</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1010</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaV</Name>
      <Text>Posición relativa V</Text>
      <Value>0.5</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1011</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>LineaOrientacionU</Name>
      <Text>Orientación línea U</Text>
      <Value>1.0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1012</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>LineaOrientacionV</Name>
      <Text>Orientación línea V</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1013</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>CaraNormalX</Name>
      <Text>Normal cara X</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1014</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>CaraNormalY</Name>
      <Text>Normal cara Y</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1015</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>CaraNormalZ</Name>
      <Text>Normal cara Z</Text>
      <Value>1</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1016</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PuntoClicX</Name>
      <Text>Punto clic X</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1017</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PuntoClicY</Name>
      <Text>Punto clic Y</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1018</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PuntoClicZ</Name>
      <Text>Punto clic Z</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1019</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>CaraIndice</Name>
      <Text>Índice de cara</Text>
      <Value>-1</Value>
      <ValueType>Integer</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1020</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>AxisU_X</Name>
      <Text>Eje U X</Text>
      <Value>1</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1021</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>AxisU_Y</Name>
      <Text>Eje U Y</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1022</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>AxisU_Z</Name>
      <Text>Eje U Z</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1023</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>AxisV_X</Name>
      <Text>Eje V X</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1024</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>AxisV_Y</Name>
      <Text>Eje V Y</Text>
      <Value>1</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1025</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>AxisV_Z</Name>
      <Text>Eje V Z</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Enable>False</Enable>
      <Visible>False</Visible>
      <TextId>1026</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PythonPartUUID</Name>
      <Text>PythonPartUUID</Text>
      <Value></Value>
      <ValueType>Text</ValueType>
      <Visible>False</Visible>
      <TextId>1029</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>z_unique</Name>
      <Text>z_unique</Text>
      <Value>0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PermitirCambiarMuro</Name>
      <Text>Permitir cambiar muro</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
      <Visible>False</Visible>
      <Persistent>No</Persistent>
    </Parameter>

    <Parameter>
      <Name>AngularSeleccionado</Name>
      <Text>Angular seleccionado</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
      <Visible>False</Visible>
      <Persistent>No</Persistent>
    </Parameter>

    <Parameter>
      <Name>pmp_pare</Name>
      <Text>pmp_pare</Text>
      <Value></Value>
      <ValueType>String</ValueType>
      <Visible>False</Visible>
      <Persistent>Model</Persistent>
      <Persistent>Model</Persistent>
    </Parameter>
    <Parameter>
      <Name>pmp_pare_name</Name>
      <Text>pmp_pare_name</Text>
      <Value></Value>
      <ValueType>String</ValueType>
      <Visible>False</Visible>
      <Persistent>Model</Persistent>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>SeparatorPosicionRelativa</Name>
      <Text>Posicionamiento Relativo</Text>
      <ValueType>Separator</ValueType>
      <Visible>False</Visible>
      <TextId>1031</TextId>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaU_Inicio</Name>
      <Text>Posición Relativa U Inicio</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1030</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaV_Inicio</Name>
      <Text>Posición Relativa V Inicio</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1031</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaU_Fin</Name>
      <Text>Posición Relativa U Fin</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1032</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaV_Fin</Name>
      <Text>Posición Relativa V Fin</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1033</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaU_BBox</Name>
      <Text>Posición Relativa U BBox</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1036</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaV_BBox</Name>
      <Text>Posición Relativa V BBox</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1037</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaU_Inicio_BBox</Name>
      <Text>Posición Relativa U Inicio BBox</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1038</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaV_Inicio_BBox</Name>
      <Text>Posición Relativa V Inicio BBox</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1039</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaU_Fin_BBox</Name>
      <Text>Posición Relativa U Fin BBox</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1040</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>PosicionRelativaV_Fin_BBox</Name>
      <Text>Posición Relativa V Fin BBox</Text>
      <Value>0.0</Value>
      <ValueType>Double</ValueType>
      <Visible>False</Visible>
      <TextId>1041</TextId>
      <Persistent>Model</Persistent>
    </Parameter>

    <Parameter>
      <Name>SavedState</Name>
      <Text>SavedState</Text>
      <TextId>e_ANG_SS_001</TextId>
      <Value></Value>
      <ValueType>String</ValueType>
      <Visible>False</Visible>
      <Enable>False</Enable>
      <Persistent>Model</Persistent>
    </Parameter>

  </Page>
</Element>
