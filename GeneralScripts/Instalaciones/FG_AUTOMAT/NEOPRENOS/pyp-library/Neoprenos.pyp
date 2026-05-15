<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>FG_AUTOMAT\NEOPRENO\pyp-scripts\Neoprenos.py</Name>
        <Title>Neopreno</Title>
        <Version>1.0</Version>
        <ReadLastInput>True</ReadLastInput>
        <Interactor>False</Interactor>
        <ScriptObject>True</ScriptObject>
        <Text>Crea neopreno 3D con posicionamiento libre o sobre sólido</Text>
        <TextId>e_NEO_PP_301</TextId>
    </Script>

    <Page>
        <Name>Propiedades</Name>
        <Text>Propiedades</Text>
        <TextId>e_NEO_PP_302</TextId>

        <Parameter>
            <Name>z_unique</Name>
            <Text>ID Único</Text>
            <TextId>e_NEO_PP_303</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Persistent>MODEL_AND_FAVORITE</Persistent>
        </Parameter>

        <Parameter>
            <Name>PythonPartUUID</Name>
            <Text>UUID del PythonPart</Text>
            <TextId>e_NEO_PP_304</TextId>
            <Value></Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>SeparatorModo</Name>
            <Text>Modo de Posicionamiento</Text>
            <TextId>e_NEO_PP_305</TextId>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>neopreno_libre</Name>
            <Text>Posicionamiento libre</Text>
            <TextId>e_NEO_PP_306</TextId>
            <Value>true</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>True</Visible>
            <Enable>False</Enable>
            <ReadOnly>z_unique > 0</ReadOnly>
        </Parameter>

        <Parameter>
            <Name>SolidoConnection</Name>
            <Text>Conexión al Sólido</Text>
            <TextId>e_NEO_PP_307</TextId>
            <Value></Value>
            <ValueType>TimeStampConnection</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>SolidoGUID</Name>
            <Text>GUID del Sólido (backup)</Text>
            <TextId>e_NEO_PP_308</TextId>
            <Value></Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>CaraIndice</Name>
            <Text>Índice de Cara</Text>
            <TextId>e_NEO_PP_309</TextId>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>CaraNormalX</Name>
            <Text>Normal X</Text>
            <TextId>e_NEO_PP_310</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>CaraNormalY</Name>
            <Text>Normal Y</Text>
            <TextId>e_NEO_PP_311</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>CaraNormalZ</Name>
            <Text>Normal Z</Text>
            <TextId>e_NEO_PP_312</TextId>
            <Value>1.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>PuntoClicX</Name>
            <Text>Punto Clic X</Text>
            <TextId>e_NEO_PP_313</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>PuntoClicY</Name>
            <Text>Punto Clic Y</Text>
            <TextId>e_NEO_PP_314</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>PuntoClicZ</Name>
            <Text>Punto Clic Z</Text>
            <TextId>e_NEO_PP_315</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>PuntoInicial</Name>
            <Text>Punto Inicial</Text>
            <TextId>e_NEO_PP_316</TextId>
            <Value>Point3D(0,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>PuntoFinal</Name>
            <Text>Punto Final</Text>
            <TextId>e_NEO_PP_317</TextId>
            <Value>Point3D(1000,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>SeparatorPosicionRelativa</Name>
            <Text>Posicionamiento Relativo</Text>
            <TextId>e_NEO_PP_318</TextId>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>PosicionRelativaU</Name>
            <Text>Posición Relativa U (0-1)</Text>
            <TextId>e_NEO_PP_319</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>True</Visible>
            <Enable>False</Enable>
            <ValueTextId>1000</ValueTextId>
        </Parameter>

        <Parameter>
            <Name>PosicionRelativaV</Name>
            <Text>Posición Relativa V (0-1)</Text>
            <TextId>e_NEO_PP_320</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>True</Visible>
            <Enable>False</Enable>
            <ValueTextId>1001</ValueTextId>
        </Parameter>

        <Parameter>
            <Name>PosicionRelativaU_Inicio</Name>
            <Text>Posición Relativa U Inicio</Text>
            <TextId>e_NEO_PP_321</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>PosicionRelativaV_Inicio</Name>
            <Text>Posición Relativa V Inicio</Text>
            <TextId>e_NEO_PP_322</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>PosicionRelativaU_Fin</Name>
            <Text>Posición Relativa U Fin</Text>
            <TextId>e_NEO_PP_323</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>PosicionRelativaV_Fin</Name>
            <Text>Posición Relativa V Fin</Text>
            <TextId>e_NEO_PP_324</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>LineaOrientacionU</Name>
            <Text>Orientación Línea U</Text>
            <TextId>e_NEO_PP_325</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>LineaOrientacionV</Name>
            <Text>Orientación Línea V</Text>
            <TextId>e_NEO_PP_326</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>AxisU_X</Name>
            <Text>Eje U - X</Text>
            <TextId>e_NEO_PP_327</TextId>
            <Value>1.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>AxisU_Y</Name>
            <Text>Eje U - Y</Text>
            <TextId>e_NEO_PP_328</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>AxisU_Z</Name>
            <Text>Eje U - Z</Text>
            <TextId>e_NEO_PP_329</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>AxisV_X</Name>
            <Text>Eje V - X</Text>
            <TextId>e_NEO_PP_330</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>AxisV_Y</Name>
            <Text>Eje V - Y</Text>
            <TextId>e_NEO_PP_331</TextId>
            <Value>1.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>AxisV_Z</Name>
            <Text>Eje V - Z</Text>
            <TextId>e_NEO_PP_332</TextId>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>DistanciaDesdeOrigen</Name>
            <Text>Distancia desde Centro</Text>
            <TextId>e_NEO_PP_333</TextId>
            <Value>0.0</Value>
            <ValueType>Length</ValueType>
            <Visible>True</Visible>
            <Enable>False</Enable>
            <ValueTextId>1002</ValueTextId>
        </Parameter>

        <Parameter>
            <Name>SeparatorInfo</Name>
            <Text>Información</Text>
            <TextId>e_NEO_PP_334</TextId>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>Longitud</Name>
            <Text>Longitud</Text>
            <TextId>e_NEO_PP_335</TextId>
            <Value>1000.00</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>Ancho</Name>
            <Text>Ancho</Text>
            <TextId>e_NEO_PP_336</TextId>
            <Value>50</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
        </Parameter>

        <Parameter>
            <Name>SeparatorGrosor</Name>
            <Text>Grosor del Neopreno</Text>
            <TextId>e_NEO_PP_337</TextId>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>GrosorSeleccionado</Name>
            <Text>Seleccione grosor</Text>
            <TextId>e_NEO_PP_338</TextId>
            <Value>5</Value>
            <ValueType>RadioButtonGroup</ValueType>

            <Parameter>
                <Name>Grosor5mm</Name>
                <Text>5mm - Fuxia</Text>
                <TextId>e_NEO_PP_339</TextId>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor10mm</Name>
                <Text>10mm - Verde</Text>
                <TextId>e_NEO_PP_340</TextId>
                <Value>10</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor20mm</Name>
                <Text>20mm - Rosa</Text>
                <TextId>e_NEO_PP_341</TextId>
                <Value>20</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor30mm</Name>
                <Text>30mm - Naranja</Text>
                <TextId>e_NEO_PP_342</TextId>
                <Value>30</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

            <Parameter>
                <Name>Grosor40mm</Name>
                <Text>40mm - Turquesa</Text>
                <TextId>e_NEO_PP_343</TextId>
                <Value>40</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>RotacionManual</Name>
            <Text>Rotación manual (°)</Text>
            <TextId>e_NEO_PP_344</TextId>
            <Value>0</Value>
            <ValueType>Angle</ValueType>
            <Visible>neopreno_libre == True</Visible>
        </Parameter>

        <Parameter>
            <Name>InvertirGrosor</Name>
            <Text>Invertir dirección del grosor</Text>
            <TextId>e_NEO_PP_345</TextId>
            <Value>false</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>neopreno_libre == True</Visible>
        </Parameter>

        <Parameter>
            <Name>MuroConnection</Name>
            <Text>Conexión al Muro</Text>
            <TextId>e_NEO_PP_350</TextId>
            <Value></Value>
            <ValueType>TimeStampConnection</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ReadOnly>False</ReadOnly>
        </Parameter>

        <Parameter>
            <Name>MuroGUID</Name>
            <Text>GUID del Muro (backup)</Text>
            <TextId>e_NEO_PP_351</TextId>
            <Value></Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>SeparatorFormato</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>Color</Name>
            <Text>Color</Text>
            <TextId>e_NEO_PP_346</TextId>
            <Value>15</Value>
            <ValueType>Color</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Pen</Name>
            <Text>Grosor de pluma</Text>
            <TextId>e_NEO_PP_347</TextId>
            <Value>1</Value>
            <ValueType>Pen</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Stroke</Name>
            <Text>Tipo de línea</Text>
            <TextId>e_NEO_PP_348</TextId>
            <Value>1</Value>
            <ValueType>Stroke</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>Layer</Name>
            <Text>Capa</Text>
            <TextId>e_NEO_PP_349</TextId>
            <Value>-1</Value>
            <ValueType>Layer</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>pmp_pare</Name>
            <Text>pmp_pare</Text>
            <TextId>e_NEO_PP_352</TextId>
            <Value></Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>MODEL_AND_FAVORITE</Persistent>
        </Parameter>

        <Parameter>
            <Name>SavedState</Name>
            <Text>SavedState</Text>
            <TextId>e_NEO_SS_001</TextId>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

    </Page>

</Element>
