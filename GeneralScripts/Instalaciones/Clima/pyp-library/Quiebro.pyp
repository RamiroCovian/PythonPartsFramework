<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Clima\pyp-scripts\Quiebro.py</Name>
        <Title>Quiebro</Title>
        <Version>1.1</Version>
    </Script>
    <Page>
        <Name>PageQuiebro</Name>
        <Title>Quiebro</Title>

        <Parameter>
            <Name>TypeQuiebro</Name>
            <Text>Tipo de quiebro</Text>
            <Value>Retorn</Value>
            <ValueList>Retorn|Impulsió</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>TypeQuiebroRetorn</Name>
            <Text>Medida quiebro - Retorn</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeQuiebro == "Retorn"</Visible>
        </Parameter>

        <Parameter>
            <Name>TypeQuiebroImpulsió</Name>
            <Text>Medida quiebro - Impulsió</Text>
            <Value>150x150</Value>
            <ValueList>150x150|200x150|250x150|300x150|350x150|400x150|450x150|500x150|550x150|600x150|650x150|700x150|750x150</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>TypeQuiebro == "Impulsió"</Visible>
        </Parameter>

        <Parameter>
            <Name>ExpRetGeom</Name>
            <Text>Retorn - geometría (mm)</Text>
            <ValueType>Expander</ValueType>
            <Visible>TypeQuiebro == "Retorn"</Visible>
            <Parameter>
                <Name>Ret_LengthMm</Name>
                <Text>Longitud quiebro</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>200.0</MinValue>
                <MaxValue>1000.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>Ret_WidthX</Name>
                <Text>Ancho cuerpo (X)</Text>
                <Value>457.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_LengthY</Name>
                <Text>Largo cuerpo base (Y)</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>50.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_Height</Name>
                <Text>Altura (Z)</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_DifX</Name>
                <Text>Desfase lateral (DIFX)</Text>
                <Value>0.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_CutBaseX</Name>
                <Text>Recorte diagonal - base X</Text>
                <Value>257.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CutLengthY</Name>
                <Text>Recorte diagonal - largo Y</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CutOffsetX</Name>
                <Text>Recorte diagonal - offset X</Text>
                <Value>-57.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_CapArmXBig</Name>
                <Text>Cap grande - ancho X</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CapArmYBig</Name>
                <Text>Cap grande - fondo Y</Text>
                <Value>75.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CapHeightBig</Name>
                <Text>Cap grande - altura Z</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CapArmXSmall</Name>
                <Text>Cap pequeña - ancho X</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CapArmYSmall</Name>
                <Text>Cap pequeña - fondo Y</Text>
                <Value>25.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_CapHeightSmall</Name>
                <Text>Cap pequeña - altura Z</Text>
                <Value>199.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpRetArrow</Name>
            <Text>Retorn - flecha</Text>
            <ValueType>Expander</ValueType>
            <Visible>TypeQuiebro == "Retorn"</Visible>
            <Parameter>
                <Name>Ret_ArrowLength</Name>
                <Text>Largo flecha</Text>
                <Value>140.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowWidth</Name>
                <Text>Ancho flecha</Text>
                <Value>60.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowZOffset</Name>
                <Text>Desfase Z flecha</Text>
                <Value>0.5</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowDistAnillo</Name>
                <Text>Distancia flecha al inicio</Text>
                <Value>30.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowRotationDeg</Name>
                <Text>Rotación flecha (grados)</Text>
                <Value>16.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowColor</Name>
                <Text>Color flecha (índice Allplan)</Text>
                <Value>65</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpRetData</Name>
            <Text>Retorn - datos</Text>
            <ValueType>Expander</ValueType>
            <Visible>TypeQuiebro == "Retorn"</Visible>
            <Parameter>
                <Name>Ret_Desviacio</Name>
                <Text>Desviación quiebro</Text>
                <Value>256</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_NumeroPeca</Name>
                <Text>Número pieza</Text>
                <Value>2</Value>
                <ValueType>String</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_TipusPeca</Name>
                <Text>Tipo pieza</Text>
                <Value>QUIEBRO</Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpImpGeom</Name>
            <Text>Impulsió - geometría (mm)</Text>
            <ValueType>Expander</ValueType>
            <Visible>TypeQuiebro == "Impulsió"</Visible>
            <Parameter>
                <Name>Imp_LengthMm</Name>
                <Text>Longitud quiebro</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>200.0</MinValue>
                <MaxValue>1000.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>Imp_WidthX</Name>
                <Text>Ancho cuerpo (X)</Text>
                <Value>457.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_LengthY</Name>
                <Text>Largo cuerpo base (Y)</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>50.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_Height</Name>
                <Text>Altura (Z)</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_DifX</Name>
                <Text>Desfase lateral (DIFX)</Text>
                <Value>0.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_CutBaseX</Name>
                <Text>Recorte diagonal - base X</Text>
                <Value>257.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CutLengthY</Name>
                <Text>Recorte diagonal - largo Y</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CutOffsetX</Name>
                <Text>Recorte diagonal - offset X</Text>
                <Value>-57.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_CapArmXBig</Name>
                <Text>Cap grande - ancho X</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CapArmYBig</Name>
                <Text>Cap grande - fondo Y</Text>
                <Value>75.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CapHeightBig</Name>
                <Text>Cap grande - altura Z</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CapArmXSmall</Name>
                <Text>Cap pequeña - ancho X</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CapArmYSmall</Name>
                <Text>Cap pequeña - fondo Y</Text>
                <Value>25.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_CapHeightSmall</Name>
                <Text>Cap pequeña - altura Z</Text>
                <Value>199.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpImpArrow</Name>
            <Text>Impulsió - flecha</Text>
            <ValueType>Expander</ValueType>
            <Visible>TypeQuiebro == "Impulsió"</Visible>
            <Parameter>
                <Name>Imp_ArrowLength</Name>
                <Text>Largo flecha</Text>
                <Value>140.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_ArrowWidth</Name>
                <Text>Ancho flecha</Text>
                <Value>60.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Imp_ArrowZOffset</Name>
                <Text>Desfase Z flecha</Text>
                <Value>0.5</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_ArrowDistAnillo</Name>
                <Text>Distancia flecha al inicio</Text>
                <Value>30.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_ArrowRotationDeg</Name>
                <Text>Rotación flecha (grados)</Text>
                <Value>16.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_ArrowColor</Name>
                <Text>Color flecha (índice Allplan)</Text>
                <Value>8</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpImpData</Name>
            <Text>Impulsió - datos</Text>
            <ValueType>Expander</ValueType>
            <Visible>TypeQuiebro == "Impulsió"</Visible>
            <Parameter>
                <Name>Imp_Desviacio</Name>
                <Text>Desviación quiebro</Text>
                <Value>256</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_NumeroPeca</Name>
                <Text>Número pieza</Text>
                <Value>2</Value>
                <ValueType>String</ValueType>
            </Parameter>
            <Parameter>
                <Name>Imp_TipusPeca</Name>
                <Text>Tipo pieza</Text>
                <Value>QUIEBRO</Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>
    </Page>
</Element>