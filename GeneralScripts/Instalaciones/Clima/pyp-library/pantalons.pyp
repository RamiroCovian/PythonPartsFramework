<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Clima\pyp-scripts\pantalons.py</Name>
        <Title>Pantalons (perfil 2D + extrusión + flechas)</Title>
        <Version>1.1</Version>
    </Script>
    <Page>
        <Name>PagePantalons</Name>
        <Title>Pantalons</Title>

        <Parameter>
            <Name>ExpPerfilMm</Name>
            <Text>Perfil 2D — longitudes (mm)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>TopLen</Name>
                <Text>Tramo superior (Top)</Text>
                <Value>348.53</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>LongDiagLen</Name>
                <Text>Diagonal larga</Text>
                <Value>663.71</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>ShortDiagLen</Name>
                <Text>Diagonal corta</Text>
                <Value>98.03</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>RightTopLen</Name>
                <Text>Derecha — tramo horizontal superior</Text>
                <Value>182.84</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>RightVertLen</Name>
                <Text>Derecha — vertical</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>RightBottomLen</Name>
                <Text>Derecha — base horizontal</Text>
                <Value>100.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>RightBottomDiagLen</Name>
                <Text>Derecha — diagonal inferior</Text>
                <Value>120.21</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>BottomRightVertLen</Name>
                <Text>Inferior derecha — vertical</Text>
                <Value>100.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>BottomLen</Name>
                <Text>Inferior — horizontal largo</Text>
                <Value>700.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>BottomLeftVertLen</Name>
                <Text>Inferior izquierda — vertical</Text>
                <Value>100.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>BottomLeftDiagLen</Name>
                <Text>Inferior izquierda — diagonal</Text>
                <Value>120.21</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>BottomLeftLen</Name>
                <Text>Izquierda — tramo horizontal corto</Text>
                <Value>100.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
            <Parameter>
                <Name>LeftVertLen</Name>
                <Text>Izquierda — vertical larga</Text>
                <Value>600.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.01</MinValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpAngulosDeg</Name>
            <Text>Dirección de cada tramo (°, matemáticas: desde +X)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>AngleSegTopDeg</Name>
                <Text>Ángulo tramo Top</Text>
                <Value>0.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegLongDiagDeg</Name>
                <Text>Ángulo diagonal larga</Text>
                <Value>-45.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegShortDiagDeg</Name>
                <Text>Ángulo diagonal corta</Text>
                <Value>45.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegRightTopDeg</Name>
                <Text>Ángulo derecha — horizontal sup.</Text>
                <Value>0.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegRightVertDeg</Name>
                <Text>Ángulo derecha — vertical</Text>
                <Value>-90.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegRightBottomDeg</Name>
                <Text>Ángulo derecha — base</Text>
                <Value>180.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegRightBottomDiagDeg</Name>
                <Text>Ángulo derecha — diagonal inf.</Text>
                <Value>-135.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegBottomRightVertDeg</Name>
                <Text>Ángulo inf. der. — vertical</Text>
                <Value>-90.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegBottomDeg</Name>
                <Text>Ángulo inferior — horizontal</Text>
                <Value>180.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegBottomLeftVertDeg</Name>
                <Text>Ángulo inf. izq. — vertical</Text>
                <Value>90.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegBottomLeftDiagDeg</Name>
                <Text>Ángulo inf. izq. — diagonal</Text>
                <Value>135.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegBottomLeftHorDeg</Name>
                <Text>Ángulo izq. — horizontal corto</Text>
                <Value>180.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>AngleSegLeftVertDeg</Name>
                <Text>Ángulo izq. — vertical larga</Text>
                <Value>90.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>-360.0</MinValue>
                <MaxValue>360.0</MaxValue>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpExtrusion</Name>
            <Text>Extrusión y cuerpo</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>Height</Name>
                <Text>Altura extrusión Z (mm)</Text>
                <Value>200.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.1</MinValue>
            </Parameter>
            <Parameter>
                <Name>BodyColor</Name>
                <Text>Color cuerpo (índice Allplan)</Text>
                <Value>207</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
            <Parameter>
                <Name>ClosePolygon</Name>
                <Text>Cerrar perfil repetido punto inicial</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ExpFlechas</Name>
            <Text>Flechas 3D (mm y factores 0–1 sobre caja XY)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>ArrowLengthMm</Name>
                <Text>Largo flecha</Text>
                <Value>140.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>1.0</MinValue>
            </Parameter>
            <Parameter>
                <Name>ArrowHalfWidthMm</Name>
                <Text>Media anchura punta</Text>
                <Value>30.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.1</MinValue>
            </Parameter>
            <Parameter>
                <Name>ArrowThickMm</Name>
                <Text>Grosor extrusión flecha</Text>
                <Value>5.0</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.1</MinValue>
            </Parameter>
            <Parameter>
                <Name>ArrowZOffsetMm</Name>
                <Text>Desfase Z sobre la tapa</Text>
                <Value>5.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>ArrowColor</Name>
                <Text>Color flechas (índice Allplan)</Text>
                <Value>65</Value>
                <ValueType>Integer</ValueType>
                <MinValue>1</MinValue>
                <MaxValue>255</MaxValue>
            </Parameter>
            <Parameter>
                <Name>Arrow1AngleDeg</Name>
                <Text>Flecha 1 — rotación (°)</Text>
                <Value>45.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Arrow2AngleDeg</Name>
                <Text>Flecha 2 — rotación (°)</Text>
                <Value>-45.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>
            <Parameter>
                <Name>Arrow1PosXFactor</Name>
                <Text>Flecha 1 — posición X (0–1 en envolvente)</Text>
                <Value>0.32</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
                <MaxValue>1.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>Arrow1PosYFactor</Name>
                <Text>Flecha 1 — posición Y</Text>
                <Value>0.62</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
                <MaxValue>1.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>Arrow2PosXFactor</Name>
                <Text>Flecha 2 — posición X</Text>
                <Value>0.83</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
                <MaxValue>1.0</MaxValue>
            </Parameter>
            <Parameter>
                <Name>Arrow2PosYFactor</Name>
                <Text>Flecha 2 — posición Y</Text>
                <Value>0.30</Value>
                <ValueType>Double</ValueType>
                <MinValue>0.0</MinValue>
                <MaxValue>1.0</MaxValue>
            </Parameter>
        </Parameter>
    </Page>
</Element>
