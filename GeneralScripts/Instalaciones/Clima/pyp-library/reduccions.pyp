<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Clima\pyp-scripts\reduccions.py</Name>
        <Title>Reduccions</Title>
        <Version>1.1.0</Version>
    </Script>
    <Page>
        <Name>PageReduccion</Name>
        <Title>Reducción rectangular</Title>
        <Parameter>
            <Name>TypeReduccionUp</Name>
            <Text>Tipo de reducción</Text>
            <Value>redimplusio</Value>
            <ValueList>redimplusio|redretorn</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>ExpImpl</Name>
            <Text>Implusio — geometría (mm)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Impl_WidthBottom</Name>
                <Text>Ancho base</Text>
                <Value>400.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Impl_WidthTop</Name>
                <Text>Ancho reducido (arriba)</Text>
                <Value>300.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Impl_LengthTotal</Name>
                <Text>Largo total (Y)</Text>
                <Value>1200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>50.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Impl_StraightLen</Name>
                <Text>Tramo recto inicial/final (cada extremo)</Text>
                <Value>300.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Impl_Height</Name>
                <Text>Altura (Z) sección</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>ExpImplArrow</Name>
            <Text>Implusio — flecha (mm / color)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Impl_ArrowLength</Name>
                <Text>Largo flecha</Text>
                <Value>140.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Impl_ArrowHalfWidth</Name>
                <Text>Media anchura flecha</Text>
                <Value>30.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.1</MinValue>
            </Parameter>
            <Parameter>
                <Name>Impl_ArrowZOffset</Name>
                <Text>Desfase Z sobre la tapa</Text>
                <Value>5.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Impl_ArrowColor</Name>
                <Text>Color flecha (índice Allplan)</Text>
                <Value>65</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>ExpRet</Name>
            <Text>Retorn — geometría (mm)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Ret_WidthBottom</Name>
                <Text>Ancho base</Text>
                <Value>400.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_WidthTop</Name>
                <Text>Ancho reducido (arriba)</Text>
                <Value>300.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_LengthTotal</Name>
                <Text>Largo total (Y)</Text>
                <Value>1000.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>50.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_StraightLen</Name>
                <Text>Tramo recto inicial/final (cada extremo)</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_Height</Name>
                <Text>Altura (Z) sección</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>10.0</MinValue>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>ExpRetArrow</Name>
            <Text>Retorn — flecha (mm / color)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Ret_ArrowLength</Name>
                <Text>Largo flecha</Text>
                <Value>140.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowHalfWidth</Name>
                <Text>Media anchura flecha</Text>
                <Value>30.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.1</MinValue>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowZOffset</Name>
                <Text>Desfase Z sobre la tapa</Text>
                <Value>5.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Ret_ArrowColor</Name>
                <Text>Color flecha (índice Allplan)</Text>
                <Value>8</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
        </Parameter>
    </Page>
</Element>
