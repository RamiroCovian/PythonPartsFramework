<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\Estructura\EN\PY\EN_Conjunt_8_clase_PPEN_solids.py</Name>
        <Title>Python Part EN 8</Title>
        <Version>3.2.2</Version>
        <ReadLastInput>True</ReadLastInput>
        <DataColumnWidth>150</DataColumnWidth>
    </Script>
    <Page>
        <Name>SelectorPythonPartEN</Name>
        <Text>Selector Fill</Text>
        <!-- <Persistent>Model</Persistent> -->


        <Parameter>
            <Name>FlagEntrada</Name>
            <Text>FlagEntrada</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>inputPoint</Name>
            <Text>Point POsicio</Text>
            <Value>Point3D(0,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>llargadaPared</Name>
            <Text>llargadaPared</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>ampladaPared</Name>
            <Text>ampladaPared</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>alcadaPared</Name>
            <Text>alcadaPared</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>listUUIDElements</Name>
            <Text></Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- #include TD_COnjunt_8_Parent_copy.pyp;-->

        <Parameter>
            <Name>SelectorPPPare</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>3</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>
            <Enable>False</Enable>


            <Parameter>
                <Name>Pare</Name>
                <Text>Pare</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
                <Enable>False</Enable>
            </Parameter>
            <Parameter>
                <Name>TD</Name>
                <Text>TD</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
                <Enable>False</Enable>
            </Parameter>
            <Parameter>
                <Name>EN</Name>
                <Text>EN</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
                <Enable>False</Enable>
            </Parameter>
            <Parameter>
                <Name>IS</Name>
                <Text>IS</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
                <Enable>False</Enable>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1</Visible>
        </Parameter>


        <Parameter>
            <Name>listofPythonChilds</Name>
            <Text>selector de Python Fills</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorPPPFill</Name>
            <Text>Selector Python Fill</Text>
            <Value>0</Value>
            <ValueList>[str(value) for value in listofPythonChilds]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>FlagEntrada != 1</Visible>
            <BackgroundColor>(0, 175, 255)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>NameFilesChildren</Name>
            <Text>NameFilesChildren</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>listofPositionsChilds</Name>
            <Text>PositionChilds</Text>
            <Value>[_]</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>listofMesuresChilds</Name>
            <Text>MesuresChilds</Text>
            <Value>[_]</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!--
        <Parameter>
            <Name>direccioISInv</Name>
            <Text>CheckBox</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        -->

    </Page>
    <!-- ************* DADES GENERALS *************-->
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector</Text>
        <!-- <Persistent>Model</Persistent> -->

        <!--
        <Parameter>
            <Name>crearInterator</Name>
            <Text>Reconeixer atributs tubs</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        -->

        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

        <!--
        <Parameter>
            <Name>ElementAttributes</Name>
            <Text>Element attribute</Text>
            <Value>[(0,)]</Value>
            <ValueType>AttributeIdValue</ValueType>
            <ValueDialog>AttributeSelectionElements</ValueDialog>
            <Visible>False</Visible>
        </Parameter>
        -->

        <Parameter>
            <Name>reconeixerDen</Name>
            <Text>Reconeixer atributs tubs</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- Selector Barra Horitzontals / Verticals-->
        <Parameter>
            <Name>NomTDEN</Name>
            <Text>NomTDEN</Text>
            <Value>EN</Value>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Distancia entre TD/Barres Verticals-->
        <Parameter>
            <Name>DistanciaEntreTDAnt</Name>
            <Text>Dist. entre Barres Vert</Text>
            <Value>1170</Value>
            <MinValue>0</MinValue>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
            <Visible>False</Visible>
        </Parameter>


        <Parameter>
            <Name>DistanciaEntreEN</Name>
            <Text>Dist. entre Barres Vert</Text>
            <Value>500</Value>
            <MinValue>0</MinValue>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>SelectorPPAnt</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorPPEN</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>


            <Parameter>
                <Name>BarraHor</Name>
                <Text>Horitzontal</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraVer</Name>
                <Text>Vertical</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BalconeraFinestra</Name>
                <Text>Premarc</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarresReforc</Name>
                <Text>Varifix</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
                <BackgroundColor>(0, 255, 150)</BackgroundColor>
            </Parameter>
            <Parameter>
                <Name>BarraHorInfSeparatSelect</Name>
                <Text>Multiple INF Horitzontal</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <!--
            <Parameter>
                <Name>BarraHorInfSeparat</Name>
                <Text>Multiple INF Horitzontal</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            -->
        </Parameter>



        <!-- Selector Barra Inferior / Superior -->
        <Parameter>
            <Name>SelectorENH</Name>
            <Text>Select EN Horitzontal</Text>
            <Value>EN Inferior</Value>
              <ValueList>EN Inferior|EN Superior|Mes Tubs...</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTDHAnt</Name>
            <Text>Select Horitzontal</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!--
        <Parameter>
            <Name>IntegerSelectorTDH</Name>
            <Text>length</Text>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->
        <Parameter>
            <Name>valueListBarresHorBalcOnlyNum</Name>
            <Text>valueListBarresHorBalcEN</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHTotalAntEN</Name>
            <Text>valueListBarresHorBalcEN</Text>
            <Value></Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHTotalEN</Name>
            <Text>Select Horitzontal</Text>
            <Value>EN Inferior</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcOnlyNum]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- Numero indicador de les Barres verticals-->
        <Parameter>
            <Name>IntegerENSelector</Name>
            <Text>Nº barres Vert</Text>
            <Value>10</Value>
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPEN == 1 or SelectorPPEN == 2</Visible>
            <Persistent>Model</Persistent>
            <MinValue>3</MinValue>
            <MaxValue>50</MaxValue>
        </Parameter>
        <Parameter>
            <Name>esVermellHor</Name>
            <Text>vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
        </Parameter>
        <!-- Numero indicador de la Barra Anterior Seleccionada -->
        <Parameter>
            <Name>IntegerTDSelectorAnterior</Name>
            <Text>length</Text>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Selector de Barra Vertical-->
        <Parameter>
            <Name>SelectorENVAnt</Name>
            <Text>Select Vertical</Text>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorENV</Name>
            <Text>Select Vertical</Text>
            <Value>TDVer</Value>
              <ValueList>['TDVer '+str(value) for value in range(0, IntegerENSelector)]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <BackgroundColor>(252, 186, 3)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Selector Balconera / Finestra-->
        <Parameter>
            <Name>IntegerBalcFinSelector</Name>
            <Text>Nº Balconeres</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorBalcFinAnt</Name>
            <Text>Select Premarc Anterior</Text>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorBalcFinEN</Name>
            <Text>Select Premarc</Text>
            <Value>PREMARC 0</Value>
              <ValueList>['Premarc '+str(value) for value in range(0, IntegerBalcFinSelector)]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3</Visible>
            <BackgroundColor>(191, 2, 119)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>llargadaigualHor</Name>
            <Text>Mantenir llargades Iguals</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH != "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!--
        <Parameter>
            <Name>MostrarENVertical</Name>
            <Text>Mostrar Vertical</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->


        <Parameter>
            <Name>MostrarENVertical</Name>
            <Text>Mostrar Vertical</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>esVermellVert</Name>
            <Text>Vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>valueVertListBarresHorInfEN</Name>
            <Text>valueVertListBarresHorInfEN</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorENHorInf</Name>
            <Text>Tub Hor Inferior</Text>
            <Value>EN Inferior</Value>
            <ValueList>[str(value) for value in valueVertListBarresHorInfEN]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>valueVertListBarresHorSupEN</Name>
            <Text>valueVertListBarresHorSupEN</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorENHorSup</Name>
            <Text>Tub Hor Superior</Text>
            <Value>EN Superior</Value>
            <ValueList>[str(value) for value in valueVertListBarresHorSupEN]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>MostrarTDHoritzontalSup</Name>
            <Text>Mostrar Horitzontal Sup</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>VermellSup</Name>
            <Text>Vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>MostrarTDHoritzontalInf</Name>
            <Text>Mostrar Horitzontal Inf</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>VermellInf</Name>
            <Text>Vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SepararTDHoritzontalInf</Name>
            <Text>Mostrar Multiples Hor. Inf</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 5</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>nBarresTDHoritzontalInf</Name>
            <Text>nº Barres Horitzontal Inf</Text>
            <Value>2</Value>
            <MinValue>1</MinValue>
            <!-- <MaxValue>3</MaxValue>-->
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPEN == 5 and SepararTDHoritzontalInf == 1</Visible>
            <!-- <Visible>True</Visible>-->
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>esProvisional</Name>
            <Text>es provisional</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <!-- <Visible>SelectorPPEN == 2</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <Parameter>
            <Name>AtrPersAutomatic</Name>
            <Text>Atrib Personalizado Auto.</Text>
            <Value>True</Value>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>AtributPersonTub</Name>
            <Text>Atribut Personalizado</Text>
            <Value>EXD</Value>
            <ValueList>EXD|LB Complet|LB Curta|Tub Dalt|Tub Baix|L Dalt|LB Llarga|Xapa Frontal|Tub Horitzontal|Tub Frontal</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
            <Enable>AtrPersAutomatic == False</Enable>
        </Parameter>
        <Parameter>
            <Name>AtrPersAutomaticSup</Name>
            <Text>Atrib Personalizado Auto.</Text>
            <Value>True</Value>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>AtributPersonTubSup</Name>
            <Text>Atribut Personalizado</Text>
            <Value>EXD</Value>
            <ValueList>EXD|LB Complet|LB Curta|Tub Dalt|Tub Baix|L Dalt|LB Llarga|Xapa Frontal|Tub Horitzontal|Tub Frontal</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
            <Enable>AtrPersAutomaticSup == False</Enable>
        </Parameter>
        <Parameter>
            <Name>AtrPersAutomaticInf</Name>
            <Text>Atrib Personalizado Auto.</Text>
            <Value>True</Value>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
            <ValueType>CheckBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>AtributPersonTubInf</Name>
            <Text>Atribut Personalizado</Text>
            <Value>EXD</Value>
            <ValueList>EXD|LB Complet|LB Curta|Tub Dalt|Tub Baix|L Dalt|LB Llarga|Xapa Frontal|Tub Horitzontal|Tub Frontal</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
            <Enable>AtrPersAutomaticInf == False</Enable>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>TubInferior</Name>
            <Text>Tub Inferior</Text>
            <Value>L</Value>
            <ValueList>L|TUB</ValueList>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
            <ValueType>StringComboBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>TubSuperior</Name>
            <Text>Tub Superior</Text>
            <Value>L</Value>
            <ValueList>EXD|L|TUB|TUB Interior</ValueList>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>mostrarL</Name>
            <Text>Mostrar L</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'EXD' or TubSuperior == 'TUB Interior')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>InvertirENHoritzontalSup</Name>
            <Text>Invertir Sup</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and TubSuperior == 'EXD'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>InvertirENHoritzontalSupL</Name>
            <Text>Invertir Sup L(←,→)</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>InvertirENHoritzontalSupLUpDown</Name>
            <Text>Invertir Sup L(↑,↓)</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>InteriorENHoritzontalSupL</Name>
            <Text>L Interior</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and TubSuperior == 'EXD'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>InvertirENHoritzontalInf</Name>
            <Text>Invertir Inf</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Visible>True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>(SelectorPPEN == 1 and SelectorENH == 'EN Inferior') or (SelectorPPEN == 1 and SelectorENH == 'EN Superior')</Visible>
        </Parameter>




        <Parameter>
            <Name>ButtonRow</Name>
            <Text> SAVE/UPDATE </Text>
            <ValueType>Row</ValueType>

            <Parameter>
                <Name>Button</Name>
                <Text>Actualitzar</Text>
                <EventId>1000</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>NumerosIDParameterExpander</Name>
            <Text>Numeros Identificatius</Text>
            <ValueType>Expander</ValueType>
            <Value>False</Value>

            <Parameter>
                <Name>MostrarTDNums</Name>
                <Text>Mostrar Numeros Id</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>tamanyNumId</Name>
                <Text>Tamany Numeros Id</Text>
                <Value>5</Value>
                <ValueType>Integer</ValueType>
                <ValueSlider>True</ValueSlider>
                <MinValue>1</MinValue>
                <MaxValue>10</MaxValue>
                <IntervalValue>1</IntervalValue>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>FemellesEncaixosParameterExpander</Name>
            <Text>Femelles i Encaixos</Text>
            <ValueType>Expander</ValueType>
            <Value>False</Value>
            <Visible>SelectorPPEN == 2 or SelectorPPEN == 1</Visible>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>encaixSup</Name>
                <Text>Treure Encaix Sup</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPEN == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>invertirEncaixVertSup</Name>
                <Text>Invertir Encaix Sup</Text>
                <Value>False</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPEN == 2 and not encaixSup</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>encaixInf</Name>
                <Text>Treure Encaix Inf</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPEN == 2</Visible>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>


            <Parameter>
                <Name>invertirEncaixVertInf</Name>
                <Text>Invertir Encaix Inf</Text>
                <Value>False</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPEN == 2 and not encaixInf</Visible>
                <Persistent>Model</Persistent>
            </Parameter>




            <Parameter>
                <Name>VertEditant</Name>
                <Text>Hi ha una barra vertical editnaat</Text>
                <Value>False</Value>
                <ValueType>checkbox</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>femellaSup</Name>
                <Text>Femella Sup</Text>
                <Value>False</Value>
                <ValueType>checkbox</ValueType>
                <Visible>(SelectorPPEN == 2 and VertEditant == False) or (SelectorPPEN == 1 and SelectorENH == 'Mes Tubs...')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>femellaInf</Name>
                <Text>Femella Inf</Text>
                <Value>False</Value>
                <ValueType>checkbox</ValueType>
                <Visible>(SelectorPPEN == 2 and VertEditant == False) or (SelectorPPEN == 1 and SelectorENH == 'Mes Tubs...')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>



            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
        </Parameter>




        <Parameter>
            <Name>CopiarPegarExpander</Name>
            <Text>Copiar i Pegar</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>SelectorPPEN == 2</Visible>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>CopyButton</Name>
                <Text> Copiar Valors </Text>
                <ValueType>Row</ValueType>

                <Parameter>
                    <Name>Button</Name>
                    <Text>Copiar</Text>
                    <EventId>1001</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>

            <Parameter>
                <Name>teValorsCopiats</Name>
                <Text>teValorsCopiats</Text>
                <Value>False</Value>
                <Visible>False</Visible>
                <ValueType>CheckBox</ValueType>
                <Enable>False</Enable>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PasteButton</Name>
                <Text> Pegar Valors </Text>
                <ValueType>Row</ValueType>

                <Parameter>
                    <Name>Button</Name>
                    <Text>Pegar</Text>
                    <EventId>1002</EventId>
                    <ValueType>Button</ValueType>
                    <Enable>teValorsCopiats</Enable>
                </Parameter>
            </Parameter>
        </Parameter>
        <!-- ******** Barres Inermitges *********-->
         <!-- Llista de Barres Horitzontals Vertical-->
        <!-- <Name>Parent:PythonPartConnection</Name>-->
        <Name>Barres Horitzontal</Name>
        <Text>Intermitges Horitzontal</Text>
        <!-- <Persistent>Model</Persistent>
        <Parameter>
            <Name>ExtensioInferior</Name>
            <Text>ExtensioInferior</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>False</ExcludeIdentical>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>

            <Parameter>
                <Name>ExtenderInf</Name>
                <Text>Extensio Inf</Text>
                <Value>0.0</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>


        </Parameter>

        -->

        <!-- ******** Barres Inermitges *********-->
         <!-- Llista de Barres Horitzontals Vertical-->
        <!-- <Name>Parent:PythonPartConnection</Name>-->
        <Name>Barres Horitzontal</Name>
        <Text>Intermitges Horitzontal</Text>
        <ValueType>ListGroup</ValueType>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>BarresHorParameterExpander</Name>
            <Text>Barres Horitzontals</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Persistent>Model</Persistent>
            <!-- <Persistent>Model</Persistent> -->


            <Parameter>
                <Name>valueListBarresComboBox</Name>
                <Text>valueListBarresComboBox</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>


            <Parameter>
                <Name>BarresHorListEN</Name>
                <Text>Barra Horitzontal,Orientació,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</FieldNames>
                </NamedTuple>
                <!-- <Visible>SelectorPPEN == 2, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True,False, SelectorPPEN == 2</Visible>-->
                <!-- <Visible>SelectorPPEN == 1, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True,SelectorPPEN == 1 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 1</Visible>-->
                <Visible> False,False, False, False, False, False, False, False,False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>


            <!--
            <Parameter>
                <Name>Expander2</Name>
                <Text>Barres Horitzontals</Text>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>Row2</Name>
                    <Text>$list_row</Text>

                    <Parameter>
                        <Name>BarraHor</Name>
                        <Value>"Barra Horitzontal" + $list_row</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>Orientacio</Name>
                        <Value>Orientació</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>Posicio</Name>
                        <Value>Posicio</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>AutoLongitud</Name>
                        <Value>AutoLongitud</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>Longitud</Name>
                        <Value>Longitud</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>BarraInici</Name>
                        <Value>BarraInici</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>BarraFinal</Name>
                        <Value>BarraFinal</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>Edit</Name>
                        <Value>Edit</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                    <Parameter>
                        <Name>acabatEditar</Name>
                        <Value>acabatEditar</Value>
                        <ValueType>Text</ValueType>
                    </Parameter>
                </Parameter>

                 <Parameter>
                    <Name>BarresHorListEN</Name>
                    <Text>"Barra Horitzontal "+ ($list_row),Orientació,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
                    <Value>[False|Sup|400|True|2500|EN Inferior|EN Superior|False|False]*30</Value>
                    <ValueType>tuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Separator)</ValueType>
                    <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,</ValueList>
                    <Visible>SelectorPPEN == 2, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True,False, SelectorPPEN == 2</Visible>
                    <ValueListStartRow>0</ValueListStartRow>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>BarresHorListEN</Name>
                    <Text>"Barra Horitzontal " + str($list_row),Orientació,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
                    <Value>[]</Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Separator)</ValueType>
                    <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,</ValueList>
                    <NamedTuple>
                        <TypeName>StirrupList</TypeName>
                        <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar,Separator</FieldNames>
                    </NamedTuple>
                    <Visible>SelectorPPEN == 2, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True and BarresHorListEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListEN[$list_row][0] == True,False, SelectorPPEN == 2</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

            </Parameter>
            -->
        </Parameter>

        <Name>BarresReforç</Name>
        <Text>Varifix</Text>
        <ValueType>ListGroup</ValueType>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>BarresRefParameterExpander</Name>
            <Text>Varifix</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPEN == 4</Visible>

            <Parameter>
                <Name>NumBarresRef</Name>
                <Text>Num Varifix</Text>
                <Value>10</Value>
                <ValueType>Integer</ValueType>
            </Parameter>

            <Parameter>
                <Name>valueAntReforc</Name>
                <Text>valueAntReforc</Text>
                <Value>0</Value>
                <ValueType>Integer</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>valueListReforcComboBoxEN</Name>
                <Text>valueListReforcComboBoxEN</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>SelectorReforcEN</Name>
                <Text>Select Varifix</Text>
                <Value>Varifix 0</Value>
                <ValueList>[str(value) for value in valueListReforcComboBoxEN]</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>SelectorPPEN == 4</Visible>
                <BackgroundColor>(0, 155, 155)</BackgroundColor>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible> SelectorPPEN == 4 </Visible>
            </Parameter>


            <Parameter>
                <Name>BarresRefListToShowEN</Name>
                <Text>Varifix,Orientació,Posicio,Barra Ini,Barra Fin,Long. Automatica,Longitud,Edit,acabatEditar</Text>
                <Value>[False|Inf|100|Tub 0|Tub 1|True|100|False|False]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,StringComboBox,StringComboBox,Checkbox, Length,Checkbox,Checkbox)</ValueType>
                <ValueList>,Sup|Inf|Esq|Dre,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraRef,Orientacio,Posicio,BarraIni,BarraFin,AutoLongitud,Longitud,Edit,acabatEditar</FieldNames>
                </NamedTuple>
                <Visible> SelectorPPEN == 4, SelectorPPEN == 4 and BarresRefListToShowEN[$list_row][0] == True, SelectorPPEN == 4 and BarresRefListToShowEN[$list_row][0] == True, SelectorPPEN == 4 and   BarresRefListToShowEN[$list_row][0] == True, SelectorPPEN == 4 and   BarresRefListToShowEN[$list_row][0] == True, SelectorPPEN == 4 and   BarresRefListToShowEN[$list_row][0] == True, SelectorPPEN == 4 and   BarresRefListToShowEN[$list_row][0] == True and BarresRefListToShowEN[$list_row][5] == False, False, False, SelectorPPEN == 4</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarresRefListEN</Name>
                <Text>Varifix,Orientació,Posicio,Barra Ini,Barra Fin,Long. Automatica,Longitud,Edit,acabatEditar</Text>
                <Value>[False|Inf|100|Tub 0|Tub 1|True|100|False|False]</Value>
                <!-- <Value>[]</Value>-->
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,StringComboBox,StringComboBox,Checkbox, Length,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Sup|Inf|Esq|Dre,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraRef,Orientacio,Posicio,BarraIni,BarraFin,AutoLongitud,Longitud,Edit,acabatEditar</FieldNames>
                </NamedTuple>
                <!-- <Visible> SelectorPPEN == 4, False, SelectorPPEN == 4 and BarresRefListEN[$list_row][0] == True, SelectorPPEN == 4 and BarresRefListEN[$list_row][0] == True, SelectorPPEN == 4 and BarresRefListEN[$list_row][0] == True, SelectorPPEN == 4 and BarresRefListEN[$list_row][0] == True, SelectorPPEN == 4 and BarresRefListEN[$list_row][0] == True and BarresRefListEN[$list_row][5] == False, False, False, SelectorPPEN == 4</Visible>-->
                <Visible> False, False, False, False, False, False, False, False, False, False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>


        <!-- ******** Barres Inermitges *********-->
         <!-- Llista de Barres Horitzontals Vertical-->
        <!-- <Name>Parent:PythonPartConnection</Name>-->
        <Name>Barres Horitzontal</Name>
        <Text>Intermitges Horitzontal</Text>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>ExtensioInferior</Name>
            <Text>ExtensioInferior</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>False</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>

            <Parameter>
                <Name>ExtenderInf</Name>
                <Text>Extensio Inf</Text>
                <Value>0.0</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>


        </Parameter>


        <Name>Barres Horitzontal</Name>
        <Text>Intermitges Horitzontal</Text>
        <ValueType>ListGroup</ValueType>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>BarresHorParameterExpander</Name>
            <Text>Barres Horitzontals Int</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'Mes Tubs...'</Visible>
            <Parameter>
                <Name>BarresHorListToShowEN</Name>
                <Text>Barra Horitzontal,Orientació,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
                <Value>[False|Inf|0|True|0|Tub 0|Tub 1|False|False]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</FieldNames>
                </NamedTuple>
                <!-- <Visible>SelectorPPEN == 2, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True and BarresHorListToShowEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True and BarresHorListToShowEN[$list_row][3] == False, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True, SelectorPPEN == 2 and BarresHorListToShowEN[$list_row][0] == True,False, SelectorPPEN == 2</Visible>-->
                <Visible>SelectorPPEN == 1, SelectorPPEN == 1 and BarresHorListToShowEN[$list_row][0] == True and BarresHorListToShowEN[$list_row][3] == False, False, SelectorPPEN == 1 and BarresHorListToShowEN[$list_row][0] == True, SelectorPPEN == 1 and BarresHorListToShowEN[$list_row][0] == True and BarresHorListToShowEN[$list_row][3] == False, SelectorPPEN == 1 and BarresHorListToShowEN[$list_row][0] == True, SelectorPPEN == 1 and BarresHorListToShowEN[$list_row][0] == True, False ,False</Visible><!-- False-->
                <!-- <Visible> False,False, False, False, False, False, False, False,False, False</Visible>-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <!-- Posicio barra TDV Interior-->
        <Parameter>
            <Name>BarresVerParameterExpander</Name>
            <Text>Barres Verticals</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False</Visible>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>BarresVertListToShow</Name>
                <Text>Barra Vertical,Posicio,Posicio Abs ,PosicioZ,Long. Automatica, Longitud, Barra Inici, Edit TIS, Edit,Encaix Inf, Encaix Sup, acabatEditar, editiantFrontals,PestanyaSup, PestanyaInf, FemellaSup, FemellaInf</Text>
                <Value>[False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True;
                        False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True;
                        False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True;
                        False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True]
                </Value>
                <ValueType>namedtuple(Checkbox,Length,Length,Length,Checkbox,Length,StringComboBox,Checkbox, Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,,,,,,Inferior|Barra1|Barra2|Barra3,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraVert,Posicio,PosicioAbs,PosicioZ,AutoLongitud,Longitud,BarraInici,EditFront,Edit,EncaixInf,EncaixSup,acabatEditar,editiantFrontals,PestanyaSup,PestanyaInf,FemellaSup,FemellaInf</FieldNames>
                </NamedTuple>
                <Visible>SelectorPPEN == 2, False,SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True,False, False, False ,SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True,SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True,SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True,False,False,False,False, SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPEN == 2 and BarresVertListToShow[$list_row][0] == True</Visible> <!-- , SelectorPPEN == 2-->
                <!-- <Visible>False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False</Visible>-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>


        <!-- ******** Barres Adjacents *********-->
        <Name>Barres Adjacents</Name>
        <Text>Intermitges Adjacents</Text>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>BarresAdjParameterExpander</Name>
            <Text>Barres Adjacents</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Visible>SelectorPPEN == 2</Visible>-->
            <Visible>False</Visible>

            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>BarresAdjListToShowEN</Name>
                <Text>Barra Adjacent,Orientació,Posicio,Longitud,Profunditat,Show,Save,acabatEditar</Text>
                <Value>[False|Inf|0|100|0|False|False|False]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraAdj,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</FieldNames>
                </NamedTuple>
                <Visible>SelectorPPEN == 2, SelectorPPEN == 2 and BarresAdjListToShowEN[$list_row][0] == True, SelectorPPEN == 2 and BarresAdjListToShowEN[$list_row][0] == True, SelectorPPEN == 2 and BarresAdjListToShowEN[$list_row][0] == True,SelectorPPEN == 2 and BarresAdjListToShowEN[$list_row][0] == True, False, SelectorPPEN == 2,False</Visible> <!-- , SelectorPPEN == 2-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>BarresAdjListEN</Name>
            <Text>BarraAdj,Orientació,Posicio,Longitud,Profunditat,Edit,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraAdj,Orientacio,Posicio,Longitud,Profunditat,Edit,acabatEditar</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- ******** Barres Frontals *********-->
        <!--
        <Name>Barres Frontals</Name>
        <Text>TIS</Text>
        <Parameter>
            <Name>BarresFrontParameterExpander</Name>
            <Text>TIS</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>SelectorPPEN == 2</Visible>


            <Parameter>
                <Name>BarresFrontListToShow</Name>
                <Text>TIS,Ample,Altura,Orientació,Posicio,Longitud,Profunditat,Show,Save,acabatEditar</Text>
                <Value>[False|30|40|Inf|100|100|10|False|False|False;
                        False|30|40|Inf|200|100|10|False|False|False;
                        False|30|40|Inf|300|100|10|False|False|False;
                        False|30|40|Inf|400|100|10|False|False|False;
                        False|30|40|Inf|500|100|10|False|False|False;
                        False|30|40|Inf|600|100|10|False|False|False;
                        False|30|40|Inf|300|100|10|False|False|False;
                        False|30|40|Inf|400|100|10|False|False|False;
                        False|30|40|Inf|500|100|10|False|False|False;
                        False|30|40|Inf|600|100|10|False|False|False]
                </Value>
                <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox,Separator)</ValueType>
                <ValueList>,,,Esq|Dre,,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraFront,Amplitud,Altura,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar, Separator</FieldNames>
                </NamedTuple>
                <Visible>SelectorPPEN == 2, SelectorPPEN == 2 and BarresFrontListToShow[$list_row][0] == True,SelectorPPEN == 2 and BarresFrontListToShow[$list_row][0] == True,SelectorPPEN == 2 and BarresFrontListToShow[$list_row][0] == True, SelectorPPEN == 2 and BarresFrontListToShow[$list_row][0] == True, SelectorPPEN == 2 and BarresFrontListToShow[$list_row][0] == True, SelectorPPEN == 2 and BarresFrontListToShow[$list_row][0] == True, False, False,False, SelectorPPEN == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        -->

        <!--
        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        -->

        <Parameter>
            <Name>BarresFrontList</Name>
            <Text>TISS,Ample,Forat,Orientació,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,,,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraFront,Amplitud,Altura,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ReduirTempsCarrega</Name>
            <Text>Reduir Temps Carrega</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 3</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>intervalTempsCarrega</Name>
            <Text>intervalTempsCarrega</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>PointXTempsCarrega</Name>
            <Text>intervalTempsCarrega</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>PointYTempsCarrega</Name>
            <Text>intervalTempsCarrega</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>PointZTempsCarrega</Name>
            <Text>intervalTempsCarrega</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>dadesBalcFinesEN</Name>
            <Text>Mostrar,AmpleBalconeraEN,LlargadaBalconeraEN,PosicioXBalconeraEN,PosicioZBalconeraEN,BarraHorSup,BarraHorInf,BarraVertEsq,BarraVertDre</Text><!-- ,Separator-->
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,Length,Length,String,String,String,String)</ValueType>
            <ValueList>False,400,400,600,800,EN Superior,EN Inferior,Tub 0,Tub 1</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Mostrar,AmpleBalconeraEN,LlargadaBalconeraEN,PosicioXBalconeraEN,PosicioZBalconeraEN,BarraHorSup,BarraHorInf,BarraVertEsq,BarraVertDre</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- Balconera Finestra-->
        <Parameter>
            <Name>PosiDimensBalcFinesParameterExpander</Name>
            <Text>Posicio i Dimensions Balconera i Finestra</Text>
            <ValueType>Expander</ValueType>
            <Visible>SelectorPPEN == 3</Visible>
            <!-- <Value>False</Value>-->

            <Parameter>
                <Name>MostrarBalconeraEN</Name>
                <Text>Mostrar Premarc</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>nomPremarcEN</Name>
                <Text>Nom premarc</Text>
                <Value>Premarc.</Value>
                <ValueType>String</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>TipusPortaEN</Name>
                <Text>Tipus Porta</Text>
                <Value>Porta 1</Value>
                <ValueList>Porta 1|Corredissa</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>


            <Parameter>
                <Name>UpdateBalconera</Name>
                <Text>Premarc</Text>
                <ValueType>Row</ValueType>
                <Visible>SelectorPPEN == 3</Visible>

                <Parameter>
                    <Name>CreateBalconera</Name>
                    <Text>Create</Text>
                    <EventId>1003</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>

            <Parameter>
                <Name>UpdateBalconeraFinestraEN</Name>
                <Text>Crear Balconera / Finestra</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
                <Enable>False</Enable>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>RotarPremarcEN</Name>
                <Text>Rotar</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>AmpleBalconeraEN</Name>
                <Text>Ample</Text>
                <Value>100</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>LlargadaBalconeraEN</Name>
                <Text>Llargada</Text>
                <Value>200</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>ProfBalconeraEN</Name>
                <Text>Profunditat</Text>
                <Value>30</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>PosicioXBalconeraEN</Name>
                <Text>Posicio X</Text>
                <Value>300</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>PosicioYBalconeraEN</Name>
                <Text>Posicio Y</Text>
                <Value>0</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>PosicioZBalconeraEN</Name>
                <Text>Posicio Z</Text>
                <Value>400</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 3</Visible>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>


        <Parameter>
            <Name>valueListBarresHorBalcEN</Name>
            <Text>valueListBarresHorBalcEN</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>valueListBarresRefBalc</Name>
            <Text>valueListBarresREfBalc</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!--
        <Parameter>
            <Name>valueListBarresHorBalcSup</Name>
            <Text>valueListBarresHorBalcSup</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->

        <Parameter>
            <Name>SelectorENHorSupBalcCorredisa</Name>
            <Text>Tub Horitzontal SUP 2 </Text>
            <Value>Tub 1</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcEN]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3 and TipusPortaEN == 'Corredissa'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>VerticalAutoBalcCorred</Name>
            <Text>Auto interiors</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPEN == 3 and TipusPortaEN == 'Corredissa'</Visible>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorCorred1</Name>
            <Text>Tub Vertical 1 </Text>
            <Value>Tub 3</Value>
            <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3 and TipusPortaEN == 'Corredissa' and VerticalAutoBalcCorred == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTDHorCorred2</Name>
            <Text>Tub Vertical 2 </Text>
            <Value>Tub 4</Value>
            <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3 and TipusPortaEN == 'Corredissa' and VerticalAutoBalcCorred == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTDHorCorred3</Name>
            <Text>Tub Vertical 3 </Text>
            <Value>Tub 5</Value>
            <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3 and TipusPortaEN == 'Corredissa' and VerticalAutoBalcCorred == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>SelectorPPEN == 3 and TipusPortaEN == 'Corredissa'</Visible>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorSupBalcEN</Name>
            <Text>Tub Horitzontal SUP </Text>
            <Value>Tub 0</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcEN]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!--
        <Parameter>
            <Name>valueListBarresHorBalcInf</Name>
            <Text>valueListBarresHorBalcInf</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->
        <Parameter>
            <Name>SelectorTDHorInfBalcEN</Name>
            <Text>Tub Horitzontal INF </Text>
            <Value>EN Inferior</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcEN]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorREFInfBalcEN</Name>
            <Text>Tub Horitzontal INF</Text>
            <Value>EN Inferior</Value>
            <ValueList>[str(value) for value in valueListReforcComboBoxEN]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>VerticalAutoBalcEN</Name>
            <Text>Vertical Auto</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPEN == 3</Visible>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorEsqBalcEN</Name>
            <Text>Tub Horitzontal ESQ </Text>
            <Value>Tub 1</Value>
            <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3 and VerticalAutoBalcEN == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorDreBalcEN</Name>
            <Text>Tub Horitzontal DRE </Text>
            <Value>Tub 2</Value>
            <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 3 and VerticalAutoBalcEN == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

    </Page>

    <!-- ************* Desplaçament *************-->
    <Page>
        <!-- <Name>Parent:PythonPartConnection</Name>-->
        <Name>PP EN Horitzontal</Name>
        <Text>Desplaçament Horitzontal</Text>
        <Visible> SelectorPPEN == 1 or SelectorPPEN == 2 or SelectorPPEN == 4 or SelectorPPEN == 5</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <!-- Desplaçament en l'eix X en de la barra Horitzontal Inferior -->
        <Parameter>
            <Name>desplXI</Name>
            <Text>desplaçament X</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior' or SelectorPPEN == 5 </Visible>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament en l'eix Y en de la barra Horitzontal Inferior -->
        <Parameter>
            <Name>desplYI</Name>
            <Text>desplaçament Y</Text>
            <Value>0.0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior' or SelectorPPEN == 5</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>DimensionsParameterExpanderInf</Name>
            <Text>Barres Hor. Inferiors</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>listDesplHoritzontalsInfEN</Name>
                <Text>Ample,Altura,Llargada,desplX,desplY,mostrarLiniaA,desplLinA,mostrarLiniaB,desplLinB</Text>
                <Value>[30|30|1000|0|0|True|0|False|0;
                        30|30|1000|0|0|True|0|False|0;
                        30|30|1000|0|0|True|0|False|0]
                </Value>
                <ValueList>,,,,,,,,,,</ValueList>
                <ValueType>namedtuple(Length,Length,Length,Length,Length,Checkbox,Length,Checkbox,Length)</ValueType><!-- ,Separator-->
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraAmpleInf,BarraAlturaInf,BarraLlargadaInf,desplX,desplY,mostrar Linia A,desplLinA,mostrar Linia B,desplLinB</FieldNames>
                </NamedTuple>
                <!-- <Visible>False, False, False, False,False, False,False, False</Visible>-->
                <Visible>False, False, SelectorPPEN == 5 and SepararTDHoritzontalInf == 1, SelectorPPEN == 5 and SepararTDHoritzontalInf == 1, False, SelectorPPEN == 5 and SepararTDHoritzontalInf == 1, SelectorPPEN == 5 and SepararTDHoritzontalInf == 1 and listDesplHoritzontalsInfEN[$list_row][5] == True,SelectorPPEN == 5 and SepararTDHoritzontalInf == 1, SelectorPPEN == 5 and SepararTDHoritzontalInf == 1 and listDesplHoritzontalsInfEN[$list_row][7] == True</Visible><!-- , SelectorPPEN == 5 and SepararTDHoritzontalInf == 1-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>


        <Parameter>
            <Name>EncaixHorInf</Name>
            <Text>Encaix Horitzontal</Text>
            <Value>True</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Desplaçament en l'eix X en de la barra Horitzontal Superior -->
        <Parameter>
            <Name>desplXS</Name>
            <Text>desplaçament X</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament en l'eix Y en de la barra Horitzontal Superior -->
        <Parameter>
            <Name>desplYS</Name>
            <Text>desplaçament Y</Text>
            <Value>1.5</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>desplZS</Name>
            <Text>desplaçament Z</Text>
            <Value>2600</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplXSL</Name>
            <Text>desplaçament X (L)</Text>
            <Value>2.5</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'TUB Interior')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament en l'eix Y en de la barra Horitzontal Superior -->
        <Parameter>
            <Name>desplYSL</Name>
            <Text>desplaçament Y (L)</Text>
            <Value>1.5</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'TUB Interior')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>desplZSL</Name>
            <Text>desplaçament Z (L)</Text>
            <Value>2600</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'TUB Interior')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixHorSup</Name>
            <Text>Encaix Horitzontal</Text>
            <Value>True</Value>
            <ValueType>Checkbox</ValueType>
            <!--<Visible>False</Visible>-->
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>invertirEncaixInf</Name>
            <Text>Invertir Encaix (Inf)</Text>
            <Value>1</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>invertirEncaixSup</Name>
            <Text>Invertir Encaix (Sup)</Text>
            <Value>1</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>listDesplVerticalsEN</Name>
            <Text> desplX,desplXAbs,desplY,desplYAbs,desplZAbs,mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Length,Length,Length,Length,Length,Checkbox,Length,Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>desplX,desplXAbs,desplY,desplYAbs,desplZAbs,mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- LLista de Barres TDV Interiors-->


        <Parameter>
            <Name>listDesplVerticalsInteriorsEN</Name>
            <Text>desplX,desplY,mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Length,Length,Checkbox,Length,Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>desplX,desplY,mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Desplaçament Eix X Barra Vertical-->
        <Parameter>
            <Name>desplXVert</Name>
            <Text>desplaçament X</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <!-- <Visible>SelectorPPEN == 2</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYVert</Name>
            <Text>desplaçament Y</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <!--<Visible>SelectorPPEN == 2</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Desplaçament Absolut Eix X Barra Vertical-->
        <Parameter>
            <Name>desplXVertAbs</Name>
            <Text>despl X (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 2 </Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYVertAbs</Name>
            <Text>despl Y (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 2 </Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Z Barra Vertical-->
        <Parameter>
            <Name>desplZVertAbs</Name>
            <Text>despl Z (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 2 and SelectorENHorInf == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix X Barra Horitzontal-->
        <Parameter>
            <Name>desplXHorAbs</Name>
            <Text>despl X (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Y Barra Horitzontal-->
        <Parameter>
            <Name>desplYHorAbs</Name>
            <Text>despl Y (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>desplZHorAbs</Name>
            <Text>despl Z (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplXVertAbsRef</Name>
            <Text>despl X (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 4</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYVertAbsRef</Name>
            <Text>despl Y (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 4</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaIntInf1</Name>
            <Text>Linia Interior 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 5 and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntInf1</Name>
            <Text>Desplaçament 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 5 and mostrarLiniaIntInf1 == True and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaIntInf2</Name>
            <Text>Linia Interior 2</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 5 and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntInf2</Name>
            <Text>Desplaçament 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 5 and mostrarLiniaIntInf2 == True and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorLiniaInf</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerInfEN</Name>
            <Text>Layer Eix</Text>
            <Value>EN_FIXACIO_X</Value>
            <ValueList>EN_FIXACIO_X|EN_FIXACIO_Y</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'TD Inferior'</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>mostrarLiniaIntSup1</Name>
            <Text>Linia Interior 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntSup1</Name>
            <Text>Desplaçament 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and mostrarLiniaIntSup1 == True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaIntSup2</Name>
            <Text>Linia Interior 2</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntSup2</Name>
            <Text>Desplaçament 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and mostrarLiniaIntSup2 == True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLiniaSup</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerSupEN</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'TD Superior' </Visible>-->
            <Visible>False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>mostrarLiniaVertA</Name>
            <Text>Linia Interior 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 2 or SelectorPPEN == 4 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix X Barra Vertical-->
        <Parameter>
            <Name>desplVertLinA</Name>
            <Text>desplaçament linia 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>(SelectorPPEN == 2 and mostrarLiniaVertA == True) or (SelectorPPEN == 4 and mostrarLiniaVertA == True) or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs..." and mostrarLiniaVertA == True)</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>mostrarLiniaVertB</Name>
            <Text>Linia Interior 2</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPEN == 2 or SelectorPPEN == 4 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplVertLinB</Name>
            <Text>desplaçament linia 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>(SelectorPPEN == 2 and mostrarLiniaVertB == True) or (SelectorPPEN == 4 and mostrarLiniaVertB == True) or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs..." and mostrarLiniaVertB == True)</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorLiniaVert</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerVertEN</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- <Visible>SelectorPPEN == 2</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLiniaHor</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerHorEN</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <!-- <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!--
        <Parameter>
            <Name>AttributeID</Name>
            <Text>All attributes ID</Text>
            <Value></Value>
            <ValueType>AttributeID</ValueType>
            <ValueDialog>AttributeSelection</ValueDialog>
        </Parameter>
        -->

    </Page>

    <!-- Mesures Barra Hor i vert-->
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPEN == 1 or SelectorPPEN == 2 or SelectorPPEN == 4 or SelectorPPEN == 5</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Mesures Barra</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>


            <!-- ##################################################-->
            <Parameter>
                <Name>llargadaAutomatica</Name>
                <Text>Llargada Automatica</Text>
                <Value>True</Value>
                <ValueType>Checkbox</ValueType>
                <ExcludeIdentical>True</ExcludeIdentical>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2 </Visible>
            </Parameter>


            <Parameter>
                <Name>BarraAmpleVert</Name>
                <Text>Ample</Text>
                <Value>40.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2 </Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAmpleHor</Name>
                <Text>Ample</Text>
                <Value>10.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAmpleRef</Name>
                <Text>Ample</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 4</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaVert</Name>
                <Text>Altura</Text>
                <Value>50</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2 </Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaHor</Name>
                <Text>Altura</Text>
                <Value>50</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaRef</Name>
                <Text>Altura</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 4</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaVert</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <!-- <Visible>llargadaAutomatica == True</Visible>-->
                <Visible>False</Visible>
                <enable>False</enable>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaIndiv</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <!-- <Visible>llargadaAutomatica == False</Visible>-->
                <Visible>SelectorPPEN == 2</Visible>
                <Persistent>Model</Persistent>
                <enable>False</enable>
            </Parameter>
            <Parameter>
                <Name>BarraGruixVert</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2 </Visible>
            </Parameter>
            <Parameter>
                <Name>BarraGruixHor</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraGruixRef</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 4</Visible>
            </Parameter>

            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Properties</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>
                <Visible>SelectorPPEN == 2</Visible>

                <Parameter>
                    <Name>IsUseGlobalPropVert</Name>
                    <Text>Use Global Propierties</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                    <!-- <Visible>SelectorPPEN == 2</Visible>-->
                    <Visible>False</Visible>
                </Parameter>

                <Parameter>
                    <Name>FounColorVert</Name>
                    <Text>Color</Text>
                    <Value>1</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPEN == 2</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>BarraLayerVert</Name>
                    <Text>Layer</Text>
                    <Value>40076</Value>
                    <ValueType>Layer</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <!-- <Visible>IsUseGlobalPropVert == False and SelectorPPEN == 2</Visible>-->
                    <Persistent>Model</Persistent>
                    <Visible>False</Visible>
                </Parameter>

            </Parameter>
            <!-- ##################################################-->

            <Parameter>
                <Name>BarraAmpleInf</Name>
                <Text>Ample</Text>
                <Value>50</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior' or SelectorPPEN == 5</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaInf</Name>
                <Text>Altura</Text>
                <Value>35</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'  or SelectorPPEN == 5 </Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraAmpleSup</Name>
                <Text>Ample</Text>
                <Value>27.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'EXD' or TubSuperior == 'TUB')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAmpleSupL</Name>
                <Text>Ample L</Text>
                <Value>50</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'L' or TubSuperior == 'EXD' )</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraAmpleSupTubInt</Name>
                <Text>Ample</Text>
                <Value>10</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior' and (TubSuperior == 'TUB Interior')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaSup</Name>
                <Text>Altura</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaAnt</Name>
                <Text>Llargada</Text>
                <Value>4400.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaEN</Name>
                <Text>Llargada</Text>
                <Value>1200.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH != "Mes Tubs..."</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaInfEN</Name>
                <Text>Llargada Inf</Text>
                <Value>4400.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH == "EN Inferior" and llargadaigualHor == False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraGruix</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPEN == 1 and SelectorENH != "Mes Tubs..."</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Properties</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>
                <Visible>IsUseGlobalProp == False and SelectorPPEN == 1</Visible>

                <Parameter>
                    <Name>IsUseGlobalProp</Name>
                    <Text>Use Global Propierties</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>FounColor</Name>
                    <Text>Color</Text>
                    <Value>1</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>FounColorHor</Name>
                    <Text>Color</Text>
                    <Value>1</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>FounColorSup</Name>
                    <Text>Color</Text>
                    <Value>1</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPEN == 1 and SelectorENH == "EN Superior"</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>FounColorInf</Name>
                    <Text>Color</Text>
                    <Value>1</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPEN == 1 and SelectorENH == "EN Inferior"</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>BarraLayer</Name>
                    <Text>Layer</Text>
                    <Value>40076</Value>
                    <ValueType>Layer</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <!--
                <Parameter>
                    <Name>NomTDEN</Name>
                    <Text>NomTDEN</Text>
                    <Value>TD</Value>
                    <ValueType>String</ValueType>
                    <Persistent>Model</Persistent>
                </Parameter>


                <Parameter>
                    <Name>AttributeID</Name>
                    <Text>All attributes ID</Text>
                    <Value></Value>
                    <ValueType>AttributeID</ValueType>
                    <ValueDialog>AttributeSelection</ValueDialog>
                </Parameter>
                -->

                <Parameter>
                    <Name>DENInf</Name>
                    <Text>Denominació INF</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>DENSup</Name>
                    <Text>Denominació SUP</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>DENVert</Name>
                    <Text>Denominació Vert</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPEN == 2 and SelectorENH == 'EN Inferior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>DENHorInt</Name>
                    <Text>Denominació Hor Int</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPEN == 2 and SelectorENH == 'EN Inferior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>
            </Parameter>
        </Parameter>


    </Page>

    <!--Collisos i Potes HOR INFERIOR-->
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->
        <!-- INFerior-->
        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Colís</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>


            <Parameter>
                <Name>ColisParINF</Name>
                <Text>Colís,Orientació,Posició,Llargada,Amplada,Reforç Colís</Text>
                <Value>[False|Sup|400.|150|12|True;
                        False|Sup|800.|150|12|True;
                        False|Sup|1200.|150|12|True;
                        False|Sup|1600.|150|12|True]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,MostrarBox</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ColisParINF[$list_row][0] == True, ColisParINF[$list_row][0] == True, ColisParINF[$list_row][0] == True, ColisParINF[$list_row][0] == True</Visible><!-- ,ColisParINF[$list_row][0] == True-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Potes</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>


            <Parameter>
                <Name>PotaParINF</Name>
                <Text>Pota,Posició</Text>
                <Value>[False|400.;
                        False|800.;
                        False|1200.;
                        False|1600.]
                </Value>
                <EventId>0,0,0,0,0,1000,0</EventId>
                <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Pota,Posicio</FieldNames>
                </NamedTuple>
                <MinValue>,0</MinValue>
                <Visible>True, PotaParINF[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>ForatsParINF</Name>
                <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada</Text>
                <Value>[False|Sup|200.|40|15|True|20|10;
                        False|Sup|400.|40|15|True|20|10;
                        False|Sup|600.|40|15|True|20|10;
                        False|Sup|800.|40|15|True|20|10;
                        False|Sup|1200.|40|15|True|20|10;
                        False|Sup|1200.|40|15|True|20|10;
                        False|Sup|1400.|40|15|True|20|10;
                        False|Sup|1600.|40|15|True|20|10;
                        False|Sup|1800.|40|15|True|20|10;
                        False|Sup|2000.|40|15|True|20|10]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True and ForatsParINF[$list_row][5] == True,ForatsParINF[$list_row][0] == True and ForatsParINF[$list_row][5] == True</Visible><!-- ,False-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
    </Page>

    <!--Collisos i Potes HOR Superior-->
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <!-- SUPerior-->
        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Colís</Text>
            <ValueType>Expander</ValueType>


            <Parameter>
                <Name>ColisParSUP</Name>
                <Text>Colís,Orientació,Posició,Llargada,Amplada,Reforç Colís</Text>
                <Value>[False|Sup|400.|150|12|True;
                    False|Sup|800.|150|12|True;
                    False|Sup|1200.|150|12|True;
                    False|Sup|1600.|150|12|True]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,MostrarBox</FieldNames><!-- ,Separator-->
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True</Visible><!-- , ColisParSUP[$list_row][0] == True-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Potes</Text>
            <ValueType>Expander</ValueType>


            <Parameter>
                <Name>PotaParSUP</Name>
                <Text>Pota,Posició</Text>
                <Value>[False|400.;
                        False|1200.;
                        False|2400.;
                        False|4600.]
                </Value>
                <EventId>0,0,0,0,0,1000,0</EventId>
                <ValueType>namedtuple(Checkbox,Length)</ValueType>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Pota,Posicio</FieldNames><!-- ,Separator-->
                </NamedTuple>
                <MinValue>,0</MinValue>
                <Visible>True, PotaParSUP[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>ForatsParSUP</Name>
                <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,LLargada,Amplada, TFF</Text>
                <Value>[False|Sup|200.|20|15|True|20|10;
                        False|Sup|400.|20|15|True|20|10;
                        False|Sup|600.|20|15|True|20|10;
                        False|Sup|800.|20|15|True|20|10;
                        False|Sup|1000.|20|15|True|20|10;
                        False|Sup|1200.|20|15|True|20|10;
                        False|Sup|1400.|20|15|True|20|10;
                        False|Sup|1600.|20|15|True|20|10;
                        False|Sup|1800.|20|15|True|20|10;
                        False|Sup|2000.|20|15|True|20|10]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True,ForatsParSUP[$list_row][0] == True and ForatsParSUP[$list_row][5] == True,ForatsParSUP[$list_row][0] == True and ForatsParSUP[$list_row][5] == True</Visible><!-- ,False-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
    </Page>

    <!--FEMELLES INFerior-->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>FemellesExpander</Name>
            <Text></Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>Ample_forat_femellaINF</Name>
                <Text>Ample Forat Femella</Text>
                <Value>15</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Altura_forat_femellaINF</Name>
                <Text>Altura Forat Femella</Text>
                <Value>3.75</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separacio_forat_femellaINF</Name>
                <Text>Separació Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PosicioExpander</Name>
                <Text>Posició femelles</Text>
                <ValueType>Expander</ValueType>
                <!-- FEMELLES-->
                <!-- *********************************** -->
                <Parameter>
                    <Name>Separator</Name>
                    <ValueType>Separator</ValueType>
                </Parameter>


                <Parameter>
                    <Name>FemellesINF</Name>
                    <Text>Femella,Orientació,Posició X,Posició Y,Separacio</Text>
                    <Value>[False|Esq|400|0|100;
                            False|Esq|800|0|100;
                            False|Esq|1200|0|100]
                    </Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
                    <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
                    <NamedTuple>
                        <TypeName>UShape</TypeName>
                        <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
                    </NamedTuple>
                    <MinValue>,,0,0</MinValue>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True, FemellesINF[$list_row][0] == True, FemellesINF[$list_row][0] == True, FemellesINF[$list_row][0] == True</Visible><!-- ,False-->
                    <Persistent>Model</Persistent>
                </Parameter>

            </Parameter>
        </Parameter>
    </Page>

    <!--FEMELLES SUPerior-->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>FemellesExpander</Name>
            <Text></Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>Ample_forat_femellaSUP</Name>
                <Text>Ample Forat Femella</Text>
                <Value>15</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Altura_forat_femellaSUP</Name>
                <Text>Altura Forat Femella</Text>
                <Value>3.75</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separacio_forat_femellaSUP</Name>
                <Text>Separació Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PosicioExpander</Name>
                <Text>Posició femelles</Text>
                <ValueType>Expander</ValueType>
                <!-- FEMELLES-->
                <!-- *********************************** -->
                <Parameter>
                    <Name>Separator</Name>
                    <ValueType>Separator</ValueType>
                </Parameter>

                <Parameter>
                    <Name>FemellesSUP</Name>
                    <Text>Femella,Orientació,Posició X,Posició Y,Separacio</Text>
                    <Value>[False|Esq|400|0|100;
                            False|Esq|800|0|100;
                            False|Esq|1200|0|100]
                    </Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
                    <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
                    <NamedTuple>
                        <TypeName>UShape</TypeName>
                        <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
                    </NamedTuple>
                    <MinValue>,,0,0</MinValue>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True, FemellesSUP[$list_row][0] == True, FemellesSUP[$list_row][0] == True, FemellesSUP[$list_row][0] == True</Visible><!-- ,False-->
                    <Persistent>Model</Persistent>
                </Parameter>



            </Parameter>
        </Parameter>
    </Page>

    <!--CANCANMS HOR INF-->
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Inferior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>CancamsExpander</Name>
            <Text>Cancams</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>posicio_centre_massesINF</Name>
                <Text>Posició centre de masses</Text>
                <Value>1500.00</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>CancamsExpander</Name>
                <Text></Text>
                <value>True</value>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>IsFirstCancamINF</Name>
                    <Text>1r cancam</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>Dis1cancamINF</Name>
                    <Text>Distància</Text>
                    <Value>500</Value>
                    <ValueType>Length</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsFirstCancamINF == True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>IsSecondCancamINF</Name>
                    <Text>2n cancam</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>Dis2cancamINF</Name>
                    <Text>Distància</Text>
                    <Value>1000</Value>
                    <ValueType>Length</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsSecondCancamINF == True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
            </Parameter>
        </Parameter>
    </Page>

    <!--CANCANMS HOR SUP-->
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>CancamsExpander</Name>
            <Text>Cancams</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>posicio_centre_massesSUP</Name>
                <Text>Posició centre de masses</Text>
                <Value>1500.00</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>CancamsExpander</Name>
                <Text></Text>
                <value>True</value>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>IsFirstCancamSUP</Name>
                    <Text>1r cancam</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>Dis1cancamSUP</Name>
                    <Text>Distància</Text>
                    <Value>500</Value>
                    <ValueType>Length</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsFirstCancamSUP == True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>IsSecondCancamSUP</Name>
                    <Text>2n cancam</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>Dis2cancamSUP</Name>
                    <Text>Distància</Text>
                    <Value>1000</Value>
                    <ValueType>Length</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsSecondCancamSUP == True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
            </Parameter>
        </Parameter>
    </Page>

    <!--Encaix HOR INF-->
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <Visible>(SelectorPPEN == 1 and SelectorENH == 'EN Inferior' and TubInferior == "L") or (SelectorPPEN == 5 and TubInferior == "L")</Visible>
        <!-- <Visible>False</Visible>-->
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>EncaixExpander</Name>
            <Text>Encaix</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>PestanyaSuperiorINF</Name>
                <Text>Pestanya Superior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>False</Visible>
            </Parameter>
            <Parameter>
                <Name>PestanyaInferiorINF</Name>
                <Text>Pestanya Inferior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>False</Visible>
            </Parameter>

            <Name>EncaixTransversal</Name>
            <Text>Encaixos Tranversals</Text>


            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>False</Visible>
            </Parameter>


            <Parameter>
                <Name>EncaixosParINF</Name>
                <Text>Encaix,Orientació,Longitud,Amplitud,Posició,Profunditat,Pestanya,Despl</Text>
                <Value>[False|Esq|31.|30|200|11|False|0;
                        False|Esq|31.|30|400|11|False|0;
                        False|Esq|31.|30|600|11|False|0]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Length)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,PosY</FieldNames>
                </NamedTuple>
                <MinValue>,,,,,</MinValue>
                <!-- <Visible>True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True</Visible>-->
                <Visible>True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, False</Visible> <!-- , EncaixosParINF[$list_row][0] == True-->
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>
    </Page>

    <!--Encaix HOR SUP-->
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <!-- <Visible>SelectorPPEN == 1 and SelectorENH == 'EN Superior'</Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>EncaixExpander</Name>
            <Text>Encaix</Text>
            <ValueType>Expander</ValueType>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>PestanyaSuperiorSUP</Name>
                <Text>Pestanya Superior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>PestanyaInferiorSUP</Name>
                <Text>Pestanya Inferior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Name>EncaixTransversal</Name>
            <Text>Encaixos Tranversals</Text>


            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>


            <Parameter>
                <Name>EncaixosParSUP</Name>
                <Text>Encaix,Orientació,Longitud,Amplitud,Posició,Profunditat,Pestanya</Text>
                <Value>[False|Esq|31.|30|15.5|11|False;
                        False|Esq|80.|30|0.|11|False;
                        False|Esq|120.|0.|30|11|False]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
                </NamedTuple>
                <MinValue>,,,,,</MinValue>
                <Visible>True, EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True,EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True</Visible><!-- , EncaixosParSUP[$list_row][0] == True-->
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>
    </Page>

    <!-- Mesures Barra Vert
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPEN == 2 or SelectorPPEN == 4 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Mesures Barra Vert</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>


        </Parameter>

    </Page>
    -->
    <!--Collisos i Potes Vert FALTA-->
    <Page>
        <!--<Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>False</Visible>
        <Visible>SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>-->
        <Name>Forats</Name>
        <Text>Forats</Text>
        <Visible>SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Colís</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False</Visible>
            <!-- <Persistent>Model</Persistent> -->


            <Parameter>
                <Name>ColisVertListToShow</Name>
                <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
                <Value>[False|Sup|400.|150|12;
                        False|Sup|800.|150|12;
                        False|Sup|1200.|150|12;
                        False|Sup|1600.|150|12]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ColisVertListToShow[$list_row][0] == True, ColisVertListToShow[$list_row][0] == True, ColisVertListToShow[$list_row][0] == True</Visible><!--, ColisVertListToShow[$list_row][0] == True-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Potes</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False</Visible>

            <Parameter>
                <Name>PotesVertListToShow</Name>
                <Text>Pota,Posició</Text>
                <!-- <Text>Pota,Posició</Text>-->
                <Value>[False|400.;
                    False|1200.;
                    False|2400.;
                    False|4600.]
                </Value>
                <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Pota,Posicio</FieldNames>
                </NamedTuple>
                <MinValue>,0</MinValue>
                <ExcludeIdentical>True</ExcludeIdentical>
                <Visible>True, PotesVertListToShow[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>ForatsVertListToShowEN</Name>
                <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada, TFF,Separator</Text>
                <Value>[False|Sup|200.|25|25|True|3|3|False;
                        False|Sup|400.|25|25|True|3|3|False;
                        False|Sup|600.|25|25|True|3|3|False;
                        False|Sup|800.|25|25|True|3|3|False;
                        False|Sup|1000.|25|25|True|3|3|False;
                        False|Sup|1200.|25|25|True|3|3|False;
                        False|Sup|1400.|25|25|True|3|3|False;
                        False|Sup|1600.|25|25|True|3|3|False;
                        False|Sup|1800.|25|25|True|3|3|False;
                        False|Sup|2000.|25|25|True|3|3|False]
                </Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,Separator</FieldNames><!-- ,Separator-->
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ForatsVertListToShowEN[$list_row][0] == True, ForatsVertListToShowEN[$list_row][0] == True, ForatsVertListToShowEN[$list_row][0] == True, ForatsVertListToShowEN[$list_row][0] == True, ForatsVertListToShowEN[$list_row][0] == True,ForatsVertListToShowEN[$list_row][0] == True and ForatsVertListToShowEN[$list_row][5] == True,ForatsVertListToShowEN[$list_row][0] == True and ForatsVertListToShowEN[$list_row][5] == True, False,ForatsVertListToShowEN[$list_row][0] == True</Visible><!-- ,False-->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
    </Page>

    <!--FEMELLES Vert FALTA MATRIU FemellesVert-->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>FemellesExpander</Name>
            <Text></Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>Ample_forat_femellaVert</Name>
                <Text>Ample Forat Femella</Text>
                <Value>15</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Altura_forat_femellaVert</Name>
                <Text>Altura Forat Femella</Text>
                <Value>3.75</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separacio_forat_femellaVert</Name>
                <Text>Separació Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>FemellesExpanderVert</Name>
                <Text>Posició femelles</Text>
                <ValueType>Expander</ValueType>
                <!-- FEMELLES-->
                <!-- ********************************************************************** -->
                <Parameter>
                    <Name>Separator</Name>
                    <ValueType>Separator</ValueType>
                </Parameter>

                <Parameter>
                    <Name>FemellesVertListToShow</Name>
                    <Text>Femella,Orientació,Posició X,Posició Y, PosFemellaXOri,Separacio</Text>
                    <!-- <Value>[False|Esq|400|0|400;
                            False|Esq|800|0|800;
                            False|Esq|1200|0|1200]
                    </Value>-->
                    <Value>[]</Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length, Length)</ValueType>
                    <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
                    <NamedTuple>
                        <TypeName>StirrupList</TypeName>
                        <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,PosFemellaXOri</FieldNames><!-- ,Separator-->
                    </NamedTuple>
                    <MinValue>,,0,,</MinValue>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True, FemellesVertListToShow[$list_row][0] == True, FemellesVertListToShow[$list_row][0] == True, FemellesVertListToShow[$list_row][0] == True, False</Visible><!-- ,False-->
                    <Persistent>Model</Persistent>
                </Parameter>



            </Parameter>
        </Parameter>
    </Page>

    <!--CANCANMS Vert PASSAT-->
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>False</Visible>
        <!-- <Visible>SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>-->
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>CancamsExpander</Name>
            <Text>Cancams</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>posicio_centre_massesVert</Name>
                <Text>Posició centre de masses</Text>
                <Value>150</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>CancamsExpander</Name>
                <Text></Text>
                <value>True</value>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>IsFirstCancamVert</Name>
                    <Text>1r cancam</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>Dis1cancamVert</Name>
                    <Text>Distància</Text>
                    <Value>500</Value>
                    <ValueType>Length</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsFirstCancamVert == True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>IsSecondCancamVert</Name>
                    <Text>2n cancam</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>Dis2cancamVert</Name>
                    <Text>Distància</Text>
                    <Value>1000</Value>
                    <ValueType>Length</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsSecondCancamVert == True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
            </Parameter>
        </Parameter>
    </Page>

    <!--Encaix Vert-->
    <Page>
        <Name>EncaixVert</Name>
        <Text>Encaix</Text>
        <Visible>SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Mes Tubs...")</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>EncaixExpander</Name>
            <Text>Encaix</Text>
            <ValueType>Expander</ValueType>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>PestanyaSuperiorVert</Name>
                <Text>Pestanya Superior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2</Visible>
            </Parameter>
            <Parameter>
                <Name>PestanyaSuperiorHor</Name>
                <Text>Pestanya Superior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            </Parameter>
            <Parameter>
                <Name>PestanyaInferiorVert</Name>
                <Text>Pestanya Inferior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2</Visible>
            </Parameter>
            <Parameter>
                <Name>pestanyesInvVert</Name>
                <Text>Invertir Pestanyes</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 2</Visible>
            </Parameter>
            <Parameter>
                <Name>PestanyaInferiorHor</Name>
                <Text>Pestanya Inferior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            </Parameter>

            <Parameter>
                <Name>pestanyesInv</Name>
                <Text>Invertir Pestanyes</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPEN == 1 and SelectorENH == "Mes Tubs..."</Visible>
            </Parameter>

            <Name>EncaixTransversal</Name>
            <Text>Encaixos Tranversals</Text>


            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>

            <!-- llista que es mostra per pantalla -->
            <Parameter>
                <Name>EncaixVertListToShow</Name>
                <Text>Encaix,Orientació,Longitud,Amplitud,Posició,Profunditat,Pestanya</Text>
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
                </NamedTuple>
                <Visible>True, EncaixVertListToShow[$list_row][0] == True,EncaixVertListToShow[$list_row][0] == True,EncaixVertListToShow[$list_row][0] == True, EncaixVertListToShow[$list_row][0] == True, EncaixVertListToShow[$list_row][0] == True</Visible><!-- , EncaixVertListToShow[$list_row][0] == True-->
                <Persistent>Model</Persistent>
            </Parameter>



        </Parameter>
    </Page>

    <!-- Matrius-->
    <Page>
        <Name>__HiddenPage__</Name>
        <Text></Text>
        <Visible>False</Visible>

        <!-- *******************  MATRIU DADES UNIQUES **************************-->
        <Parameter>
            <Name>dadesTDVertEN</Name>
            <Text>Mostrar, BarraAmple, BarraAltura, LlargadaAut, BarraAlcada, BarraSuperior, BarraInferior, Gruix,
                EncaixSup, EncaixInf, FemellaSup, FemellaInf,invertirEncaixSup,invertirEncaixInf,
                Ample Forat Femella, Altura Forat Femella, Separació Forat Femella,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                Pestanya Superior, Pestanya Inferior, Pestayes Invertides,
                esProvisional,
                linia, layer, vermell,
                Color
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Length, Length, Checkbox, Length, String, String, Length,
                                Checkbox,Checkbox, Checkbox,Checkbox,Checkbox,Checkbox,
                                Length, Length, Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox, Checkbox,
                                Checkbox,
                                String, String, Checkbox,
                                Color)
            </ValueType>
            <ValueList>,,,,,'EN Superior',,,True,True,,,,,,,,,,,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>MostrarTDVertical, BarraAmple, BarraAltura, LlargadaAut, BarraAlcada, BarraSuperior, BarraInferior, Gruix,
                            EncaixSup, EncaixInf, FemellaSup, FemellaInf,invertirEncaixSup,invertirEncaixInf,
                            Ample_forat_femellaVert,Altura_forat_femellaVert,Separacio_forat_femellaVert,
                            posicio_centre_massesVert, IsFirstCancamVert, Dis1cancamVert, IsSecondCancamVert, Dis2cancamVert,
                            PestanyaSuperiorVert, PestanyaInferiorVert, PestanyesInv,
                            esProvisional,
                            linia, layer, vermell,
                            FounColor
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- *******************  Colis Vert **************************-->
        <Parameter>
            <Name>LengthListColisVert</Name>
            <Text>LengthListColisVert</Text>
            <Value>14</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la ColisVertList-->
        <Parameter>
            <Name>nListColisVert</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Colis verticals-->
        <Parameter>
            <Name>ColisVertList</Name>
            <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType>, EncaixVertListToShow[$list_row][0] == True
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- *******************  Potes Vert **************************-->
        <Parameter>
            <Name>LengthListPotesVert</Name>
            <Text>LengthListPotesVert</Text>
            <Value>14</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la PotesVertList-->
        <Parameter>
            <Name>nListPotesVert</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Potes verticals-->
        <Parameter>
            <Name>PotesVertList</Name>
            <Text>Pota,Posició</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
            <ValueList>,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames><!-- ,Separator-->
            </NamedTuple>
            <Visible>False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- *******************  Forats Vert **************************-->
        <Parameter>
            <Name>LengthListForatsVert</Name>
            <Text>LengthListForatsVert</Text>
            <Value>14</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la ForatsVertListEN-->
        <Parameter>
            <Name>nListForatsVert</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Forats verticals-->
        <Parameter>
            <Name>ForatsVertListEN</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,LlargadaB,AmpladaB,TFF</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- *******************  Femelles Vert **************************-->
        <Parameter>
            <Name>LengthListFemellesVert</Name>
            <Text>LengthListFemellesVert</Text>
            <Value>14</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la FemellesVertListEN-->
        <Parameter>
            <Name>nListFemellesVert</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Femellesos verticals-->
        <Parameter>
            <Name>FemellesVertListEN</Name>
            <Text>Femella,Orientació,Posició X,Posició Y,PosFemellaXOri,Ample_forat_femella, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length, Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,PosFemellaXOri,Ample_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- *******************  Encaixos Vert **************************-->
        <Parameter>
            <Name>LengthListEncaixVert</Name>
            <Text>LengthListEncaixVert</Text>
            <Value>14</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la EncaixVertList-->
        <Parameter>
            <Name>nListEncaixVert</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible> False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Llista de Encaixos verticals-->
        <Parameter>
            <Name>EncaixVertList</Name>
            <Text>EncaixVertList </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- *******************  Barres Interiors hor **************************-->
        <Parameter>
            <Name>LengthListBarresIntHor</Name>
            <Text>LengthListBarresIntHor</Text>
            <Value>5</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la BarresHoritzontals-->
        <Parameter>
            <Name>nListBarresHor</Name>
            <Text>Posicio,nTotal</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible> False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Llista de Barres Horitzontals-->
        <!--
        <Parameter>
            <Name>BarresHorListEN</Name>
            <Text>BarraHor,Orientació,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Separator)</ValueType>
            <ValueList>,Sup|Inf,,,,[valueListBarres],[valueListBarres],,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar,Separator</FieldNames>
            </NamedTuple>
            <Visible> False,False, False, False, False, False, False, False,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->

        <!-- valors Barra Horitzontal Intermitja-->
        <Parameter>
            <Name>dadesTDHortInterEN</Name>
            <Text>Ample, Altura, Llargada, Gruix,
                desplX, desplY,
                mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                se esta editant, acabat editar,
                Is Global Prop Vert, Color, Layer,
                Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                PestanyaSup, PestanyaInf,FemellaSup, FemellaInf, Canviar Pestanyes,
                AtrPersAutomatic, AtributPersonTub,
                linia, layer, vermell
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Length,Length,Length,Length,
                                Length,Length,
                                Checkbox,Length, Checkbox,Length,
                                Checkbox, Checkbox,
                                Checkbox, Color, Layer,
                                Length, Length, Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox, Checkbox, Checkbox, Checkbox,
                                Checkbox, String,
                                String, String, Checkbox)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Ample, Altura, Llargada, Gruix,
                            desplX, desplY,
                            mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                            estaEditant, acabatEditar,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            PestanyaSup, PestanyaInf, femellaSup, femellaInf, pestanyesInv,
                            AtrPersAutomatic, AtributPersonTub,
                            linia, layer, vermell
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False,False,False,False,False,False,False,False, False, False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisHorInt</Name>
            <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesHorInt</Name>
            <Text>Pota,Posició</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False,</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsHorInt</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorInt</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorIntAux</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorIntAuxInf</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorIntAuxSup</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixHorInt</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- *******************  Barres Interiors Verticals **************************-->
        <Parameter>
            <Name>LengthListBarresIntVert</Name>
            <Text>LengthListBarresIntVert</Text>
            <Value>5</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la BarresVertitzontals-->
        <Parameter>
            <Name>nListBarresVert</Name>
            <Text>Posicio,nTotal</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible> False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Llista de Barres Vertitzontals-->
        <Parameter>
            <Name>BarresVertList</Name>
            <Text>Barra Vertical,Posicio,Posicio Abs ,PosicioZ,Long. Automatica, Longitud, Barra Inici, EditFront, Edit,Encaix Inf, Encaix Sup, acabatEditar, editiantFrontals, PestanyaSup, PestanyaInf, FemellaSup, FemellaInf</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,Length,Length,Length,Checkbox,Length,StringComboBox,Checkbox, Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,,,,,,Inferior|Barra1|Barra2|Barra3,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraVert,Posicio,PosicioAbs,PosicioZ,AutoLongitud,Longitud,BarraInici,EditFront, Edit,EncaixInf,EncaixSup,acabatEditar,editiantFrontals,PestanyaSup,PestanyaInf,FemellaSup, FemellaInf</FieldNames>
            </NamedTuple>
            <Visible> False,False, False, False,False, False,False,False,False,False,False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- valors Barra Vertitzontal Intermitja-->
        <Parameter>
            <Name>dadesTDVertInter</Name>
            <Text>se esta editant, acabat editar,
                BarraAmple, BarraAltura, BarraGruix,
                desplX, desplY, desplXAbs, desplYAbs,
                Is Global Prop Vert, Color, Layer,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                pestanyaSup, pestanyaInf,
                FemellaSup, FemellaInf, FemellaSup, FemellaInf
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Checkbox,
                                Length,Length,Length,
                                Length,Length,Length,Length,
                                Checkbox, Color, Layer,
                                Length,Length,Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox, Checkbox, Checkbox,
                                Checkbox, Checkbox)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>estaEditant, acabatEditar,
                            BarraAmple, BarraAltura, BarraGruix,
                            desplX, desplY, desplXAbs, desplYAbs,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella,Altura_forat_femella,Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            pestanyaSup, pestanyaInf,
                            FemellaSupe, FemellaInfe, FemellaSup, FemellaInf
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False,False, False,False,False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Barres Frontals en Vert Aux-->
        <!-- Dades Frontals AUX-->
        <Parameter>
            <Name>nListBarresFrontAux</Name>
            <Text>Posicio,nTotal</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible> False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- valors Barra Vertitzontal Intermitja-->
        <Parameter>
            <Name>dadesFrontAux</Name>
            <Text>se esta editant, acabat editar,
                Ample, Altura, Gruix,
                desplX, desplY,
                Is Global Prop Vert, Color, Layer,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                pestanyaSup, pestanyaInf
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Checkbox,
                                Length,Length,Length,
                                Length,Length,
                                Checkbox, Color, Layer,
                                Length,Length,Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>estaEditant, acabatEditar,
                            Ample, Altura, Gruix,
                            desplX, desplY,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella,Altura_forat_femella,Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            pestanyaSup, pestanyaInf
                </FieldNames>
            </NamedTuple>
            <Visible>False, False,
                    False,False, False,
                    False,False,
                    False, False, False,
                    False, False, False, False, False,
                    False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>BarresFrontListAux</Name>
            <Text>BarraFront,Ample,Altura,Orientació,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,,,Esq|Dre,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraFront,Amplitud,Altura,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisVertInt</Name>
            <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesVertInt</Name>
            <Text>Pota,Posició</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsVertInt</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada,MostrarBox</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesVertInt</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixVertInt</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- Dades Adjacents-->
        <!-- valors Barra Vertitical Intermitja-->
        <Parameter>
            <Name>dadesAdj</Name>
            <Text>se esta editant, acabat editar,
                Ample, Altura, Gruix,
                desplX, desplY,
                Is Global Prop Vert, Color, Layer,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                pestanyaSup, pestanyaInf
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Checkbox,
                                Length,Length,Length,
                                Length,Length,
                                Checkbox, Color, Layer,
                                Length,Length,Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>estaEditant, acabatEditar,
                            Ample, Altura, Gruix,
                            desplX, desplY,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella,Altura_forat_femella,Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            pestanyaSup, pestanyaInf
                </FieldNames>
            </NamedTuple>
            <Visible>False, False,
                    False,False, False,
                    False,False,
                    False, False, False,
                    False, False, False, False, False,
                    False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisAdj</Name>
            <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesAdj</Name>
            <Text>Pota,Posició</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsAdj</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada,</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesAdj</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixAdj</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Dades Frontals-->
        <Parameter>
            <Name>nListBarresFront</Name>
            <Text>Posicio,nTotal</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible> False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- valors Barra Vertitzontal Intermitja-->
        <Parameter>
            <Name>dadesFront</Name>
            <Text>se esta editant, acabat editar,
                Ample, Altura, Gruix,
                desplX, desplY,
                Is Global Prop Vert, Color, Layer,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                pestanyaSup, pestanyaInf
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Checkbox,
                                Length,Length,Length,
                                Length,Length,
                                Checkbox, Color, Layer,
                                Length,Length,Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>estaEditant, acabatEditar,
                            Ample, Altura, Gruix,
                            desplX, desplY,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella,Altura_forat_femella,Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            pestanyaSup, pestanyaInf
                </FieldNames>
            </NamedTuple>
            <Visible>False, False,
                    False,False, False,
                    False,False,
                    False, False, False,
                    False, False, False, False, False,
                    False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisFront</Name>
            <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesFront</Name>
            <Text>Pota,Posició</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsFront</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesFront</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixFront</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



    </Page>

    <Page>
        <Visible>False</Visible>
        <Parameter>
            <Name>DadesVertCopy</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Length,Length,Length,Length,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>nBarraGuardada,BarraAmple,BarraAltura,BarraLlargada,desplY,esProvisional,LlargadaAut,TreureEncaixSup,TreureEncaixInf,FemellaSup,FemellaInf,invertirEncaixSup,invertirEncaixInf</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsVertListCopy</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada, TFF</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <!-- <Visible>False, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True,ForatsVertListCopy[$list_row][0] == True and ForatsVertListCopy[$list_row][5] == True,ForatsVertListCopy[$list_row][0] == True and ForatsVertListCopy[$list_row][5] == True, ForatsVertListCopy[$list_row][0] == True, False</Visible>-->
            <Visible>False, False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>BarresFrontListCopy</Name>
            <Text>TIS,Ample,Forat,Orientació,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,,,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraFront,Amplitud,Altura,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- *******************  Barres Interiors Ref **************************-->
        <Parameter>
            <Name>LengthListBarresIntRef</Name>
            <Text>LengthListBarresIntRef</Text>
            <Value>5</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de indexació a la BarresRefitzontals-->
        <Parameter>
            <Name>nListBarresRef</Name>
            <Text>Posicio,nTotal</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Integer)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Posicio,nTotal</FieldNames>
            </NamedTuple>
            <Visible> False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Llista de Barres Refitzontals-->
        <!--
        <Parameter>
            <Name>BarresRefListEN</Name>
            <Text>Barra Reforç,Orientació,Posicio,BarraIni,Long. Automatica,Longitud,Edit,acabatEditar</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,StringComboBox,Checkbox, Length,Checkbox,Checkbox,Separator)</ValueType>
            <ValueList>,Sup|Inf,,Barra0|Barra1|Barra2|Barra3|Barra4,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraRef,Orientacio,Posicio,BarraIni,AutoLongitud,Longitud,Edit,acabatEditar,Separator</FieldNames>
            </NamedTuple>
            <Visible> False,False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->

        <!-- valors Barra Refitzontal Intermitja-->
        <Parameter>
            <Name>dadesENReftInter</Name>
            <Text>Ample, Altura, Llargada, Gruix,
                desplX, desplY,
                mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                se esta editant, acabat editar,
                Is Global Prop Vert, Color, Layer,
                Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                PestanyaSup, PestanyaInf,
                linia, layer
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Length,Length,Length,Length,
                                Length,Length,
                                Checkbox,Length, Checkbox,Length,
                                Checkbox, Checkbox,
                                Checkbox, Color, Layer,
                                Length, Length, Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox,
                                String, String)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Ample, Altura, Llargada, Gruix,
                            desplX, desplY,
                            mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                            estaEditant, acabatEditar,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            PestanyaSup, PestanyaInf,
                            linia, layer
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False,False,False,False,False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisRefInt</Name>
            <Text>Colís,Orientació,Posició,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesRefInt</Name>
            <Text>Pota,Posició</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType><!-- ,Separator-->
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsRefInt</Name>
            <Text>Forat,Orientació,Posició,Llargada,Amplada,Completa,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefInt</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefIntAux</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefIntAuxInf</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefIntAuxSup</Name>
            <Text>Femella,Orientació,Posició X,Posició Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixRefInt</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox)</ValueType><!-- ,Separator-->
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <!-- valors Barra Inclinades-->
        <Parameter>
            <!-- <Name>dadesTDInclinades</Name>-->
            <Name>dadesENInclinades</Name>
            <Text>MostrarInclinat, nom,
                Ample, Altura, Llargada, Gruix,
                desplX, desplY,
                mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                se esta editant, acabat editar,
                Is Global Prop Vert, Color, Layer,
                Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                Posició centre de masses, 1r cancam, Distància, 2n cancam, Distància,
                PestanyaSup, PestanyaInf,FemellaSup, FemellaInf,
                Posicio, Angle
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, String,
                                Length,Length,Length,Length,
                                Length,Length,
                                Checkbox,Length, Checkbox,Length,
                                Checkbox, Checkbox,
                                Checkbox, Color, Layer,
                                Length, Length, Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox, Checkbox, Checkbox,
                                Length, Length)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>MostrarInclinat, nom,
                            Ample, Altura, Llargada, Gruix,
                            desplX, desplY,
                            mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                            estaEditant, acabatEditar,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                            posicio_centre_masses, IsFirstCancam, Dis1cancam, IsSecondCancam, Dis2cancam,
                            PestanyaSup, PestanyaInf, femellaSup, femellaInf,
                            Posicio, Angle
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False,False,False,False,False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>


    </Page>
</Element>
