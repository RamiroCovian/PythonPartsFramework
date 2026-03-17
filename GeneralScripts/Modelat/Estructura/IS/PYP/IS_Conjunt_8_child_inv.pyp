<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\Estructura\IS\PY\IS_Conjunt_8_clase_PPIS_Tubes_Solids_from2023.py</Name>
        <Title>Python Part IS</Title>
        <Version>1.0</Version>
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
            <Value>4</Value>
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
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>PositionChilds</Name>
            <Text>PositionChilds</Text>
            <ValueType>ListGroup</ValueType>
            <ValueType>Column</ValueType>
            <Parameter>
                <Name>listofPositionsChilds</Name>
                <Text>Position $list_row </Text>
                <Value>[]</Value>
                <ValueType>Point3D</ValueType>
                <Visible>FlagEntrada != 1 and $list_row == int(SelectorPPPFill)</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>listofMesuresChilds</Name>
                <Text>Mesura $list_row</Text>
                <Value>[_]</Value>
                <ValueType>Point3D</ValueType>
                <Visible>FlagEntrada != 1 and $list_row == int(SelectorPPPFill)</Visible>
                <!-- <Enable>False</Enable> -->
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>listofVisibleChilds</Name>
                <Text>Mostrar $list_row</Text>
                <Value>[_]</Value>
                <ValueType>Checkbox</ValueType>
                <Visible>FlagEntrada != 1 and $list_row == int(SelectorPPPFill)</Visible>
                <!-- <Enable>False</Enable> -->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>direccioISInv</Name>
            <Text>Direccio IS Invertida</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

    </Page>
    <!-- ************* DADES GENERALS *************-->
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector</Text>
        <!-- <Persistent>Model</Persistent> -->

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
            <Name>refactor</Name>
            <Text>refactor</Text>
            <Value>False</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Integer</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ExteriorEsquerra</Name>
            <Text>ExteriorEsquerraUnic</Text>
            <Value>4</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Integer</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>ExteriorDreta</Name>
            <Text>ExteriorDretaUnic</Text>
            <Value>5</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Integer</ValueType>
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

        <!--
        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>True</Visible>
        </Parameter>
        <Parameter>
            <Name>mostrarNomIS</Name>
            <Text>Mostrar Nom IS</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        -->
        <Parameter>
            <Name>NomIS</Name>
            <Text>NomIS</Text>
            <Value>IS</Value>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>




        <!-- Distancia entre TD/Barres Verticals-->
        <!--
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
            <Name>DistanciaEntreTD</Name>
            <Text>Dist. entre Barres Vert</Text>
            <Value>500</Value>
            <MinValue>0</MinValue>
            <ValueType>Length</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->
        <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Mesures IS</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>
                <Visible>True</Visible>

                <Parameter>
                    <Name>ISllargada</Name>
                    <Text>Llargada IS</Text>
                    <!-- <Value>5650</Value>-->
                    <Value>2150</Value>
                    <MinValue>0</MinValue>
                    <ValueType>Length</ValueType>
                    <Persistent>Model</Persistent>
                    <Visible>False</Visible>
                    <!-- <MinValue>1450</MinValue>
                    <MaxValue>5650</MaxValue>-->
                </Parameter>

                <Parameter>
                    <Name>ISAmplada</Name>
                    <Text>Amplada IS</Text>
                    <!-- <Value>1450</Value>-->
                    <!-- <Value>2150</Value>-->
                    <Value>5650</Value>
                    <MinValue>0</MinValue>
                    <ValueType>Length</ValueType>
                    <Persistent>Model</Persistent>
                    <Visible>False</Visible>
                    <!-- <MinValue>1450</MinValue>
                    <MaxValue>2150</MaxValue>-->
                </Parameter>

                <Parameter>
                    <Name>ButtonRow</Name>
                    <Text>Button</Text>
                    <ValueType>Row</ValueType>

                    <Parameter>
                        <Name>Recalcular</Name>
                        <Text>Recalcular IS complet</Text>
                        <EventId>1000</EventId>
                        <ValueType>Button</ValueType>
                    </Parameter>
                </Parameter>


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
            <Name>SelectorPPIS</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>


            <Parameter>
                <Name>BarraHor</Name>
                <Text>Tubs</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Auto1</Name>
                <Text>Forat 1</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Auto3</Name>
                <Text>Forat 2</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Auto4</Name>
                <Text>Forat 3</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Auto2</Name>
                <Text>Creu</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Auto5</Name>
                <Text>Creu sense tubs exteriors</Text>
                <Value>6</Value>
                <ValueType>RadioButton</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <!--
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
            -->
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

        <Parameter>
            <Name>actualitzaTubs</Name>
            <Text>Actualitzar Tubs</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
            <Visible>False</Visible>
        </Parameter>

        <!-- linia Automatització-->
        <Parameter>
            <Name>PosicioXlinia</Name>
            <Text>PosicioXlinia</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPIS != 1</Visible>
            <Persistent>Model</Persistent>
            <!-- <MinValue>2</MinValue>
            <MaxValue>50</MaxValue>-->
        </Parameter>

        <Parameter>
            <Name>PosicioYlinia</Name>
            <Text>PosicioYlinia</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPIS != 1</Visible>
            <Persistent>Model</Persistent>
            <!-- <MinValue>2</MinValue>
            <MaxValue>50</MaxValue>-->
        </Parameter>

        <Parameter>
            <Name>Amplelinia</Name>
            <Text>Amplelinia (distX)</Text>
            <Value>300</Value>
            <ValueType>Double</ValueType>
            <Visible>SelectorPPIS != 1</Visible>
            <Persistent>Model</Persistent>
            <!-- <MinValue>2</MinValue>
            <MaxValue>50</MaxValue>-->
        </Parameter>

        <Parameter>
            <Name>Llargadalinia</Name>
            <Text>Llargadalinia (distY)</Text>
            <Value>400</Value>
            <ValueType>Double</ValueType>
            <Visible>SelectorPPIS != 1</Visible>
            <Persistent>Model</Persistent>
            <!-- <MinValue>2</MinValue>
            <MaxValue>50</MaxValue>-->
        </Parameter>

        <Parameter>
            <Name>crearForat</Name>
            <Text>crearForat</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>crearForat2</Name>
            <Text>crearForat</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>crearForat3</Name>
            <Text>crearForat</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>crearCreu</Name>
            <Text>crearCreu</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>crearCreuSenseTubsExteriors</Name>
            <Text>crearCreuSenseTubsExteriors</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ButtonRow</Name>
            <Text>Crear</Text>
            <ValueType>Row</ValueType>

            <Parameter>
                <Name>ButtonForat</Name>
                <Text>Forat</Text>
                <EventId>1001</EventId>
                <ValueType>Button</ValueType>
                <Visible>SelectorPPIS == 2</Visible>
            </Parameter>
            <Parameter>
                <Name>ButtonForat2</Name>
                <Text>Forat 2</Text>
                <EventId>1003</EventId>
                <ValueType>Button</ValueType>
                <Visible>SelectorPPIS == 3</Visible>
            </Parameter>
            <Parameter>
                <Name>ButtonForat3</Name>
                <Text>Forat 3</Text>
                <EventId>1004</EventId>
                <ValueType>Button</ValueType>
                <Visible>SelectorPPIS == 4</Visible>
            </Parameter>
            <Parameter>
                <Name>ButtonCreu</Name>
                <Text>Creu</Text>
                <EventId>1002</EventId>
                <ValueType>Button</ValueType>
                <Visible>SelectorPPIS == 5</Visible>
            </Parameter>
            <Parameter>
                <Name>ButtonCreu</Name>
                <Text>Creu</Text>
                <EventId>1005</EventId>
                <ValueType>Button</ValueType>
                <Visible>SelectorPPIS == 6</Visible>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>IntegerISSelectorHor</Name>
            <Text>Nº barres</Text>
            <Value>27</Value>
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPIS == 1</Visible>
            <Persistent>Model</Persistent>
            <MinValue>2</MinValue>
        </Parameter>

        <Parameter>
            <Name>TubAnt</Name>
            <Text>TubAnt</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>SelectorTubHor</Name>
            <Text>Select</Text>
            <Value>Tub 0</Value>
              <ValueList>['Tub '+str(value) for value in range(0, IntegerISSelectorHor)]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPIS == 1</Visible>
            <BackgroundColor>(252, 186, 3)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
        </Parameter>

        <Parameter>
            <Name>esProvisional</Name>
            <Text>es provisional</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPIS == 1</Visible>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>provSupEsq</Name>
            <Text>L Sup Esq</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>provSupDre</Name>
            <Text>L Sup Dre</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>provInfEsq</Name>
            <Text>L Inf Esq</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>provInfDre</Name>
            <Text>L Inf Dre</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
        </Parameter>

        <Parameter>
            <Name>provInfCen</Name>
            <Text>L Inf Cen</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPIS == 1 and esProvisional</Visible>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>SelectorPPIS == 1 and not tipusTubAuto</Visible>
        </Parameter>

        <Parameter>
            <Name>tipusTubAuto</Name>
            <Text>Tipus tub Auto.</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPIS == 1</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>TipusTUB</Name>
            <Text>TipusTUB</Text>
            <Value>TUB E</Value>
            <ValueList>TUB A|TUB B|TUB C|TUB D|TUB E|TUB F</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPIS == 1 and not tipusTubAuto</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>SelectorPPIS == 1 and not tipusTubAuto</Visible>
        </Parameter>

        <Parameter>
            <Name>MostrarTub</Name>
            <Text>Mostrar Tub</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPIS == 1</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>RotarTub</Name>
            <Text>Rotar Tub</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPIS == 1</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>RotarTubAnt</Name>
            <Text>Rotar Tub</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>valueListBarresHorBalcOnlyNum</Name>
            <Text>valueListBarresHorBalc</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
         <Parameter>
            <Name>valueListBarresHorBalcOnlyNumVert</Name>
            <Text>valueListBarresHorBalc</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- <Parameter>
            <Name>SelectorTDHTotalAnt</Name>
            <Text>valueListBarresHorBalc</Text>
            <Value></Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>-->

        <Parameter>
            <Name>posAutomatica</Name>
            <Text>pos Automatica</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>(RotarTub == True and SelectorPPIS == 1) or (RotarTub == False and SelectorPPIS == 1)</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTubInferior</Name>
            <Text>Select Inferior</Text>
            <Value>Tub 0</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcOnlyNum]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>RotarTub == True and SelectorPPIS == 1</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTubSuperior</Name>
            <Text>Select Superior</Text>
            <Value>Tub 1</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcOnlyNum]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>RotarTub == True and SelectorPPIS == 1</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTubInferiorHor</Name>
            <Text>Select Esquerra</Text>
            <Value>Tub 0</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcOnlyNumVert]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>RotarTub == False and SelectorPPIS == 1</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTubSuperiorHor</Name>
            <Text>Select Dreta</Text>
            <Value>Tub 1</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcOnlyNumVert]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>RotarTub == False and SelectorPPIS == 1</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
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


    </Page>
    <!-- Mesures Barra Hor i vert-->
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPIS == 1 </Visible>
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
            </Parameter>


            <Parameter>
                <Name>BarraLlargadaIS</Name>
                <Text>Llargada</Text>
                <Value>5550.0</Value>
                <MinValue>1</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPIS == 1</Visible>
                <Enable>llargadaAutomatica == False</Enable>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraLlargadaReal</Name>
                <Text>Llargada Real</Text>
                <Value>5550.0</Value>
                <MinValue>1</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPIS == 1</Visible>
                <Enable>False</Enable>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaOriginal</Name>
                <Text>Llargada Original Tub</Text>
                <Value>5550.0</Value>
                <MinValue>1</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPIS == 1</Visible>
                <Enable>False</Enable>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Retalls</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>
                <Visible>IsUseGlobalProp == False and SelectorPPIS == 1</Visible>

                <Parameter>
                    <Name>retallInicial</Name>
                    <Text>Retall Inicial</Text>
                    <Value>0</Value>
                    <ValueType>Double</ValueType>
                    <Visible>True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>retallFinal</Name>
                    <Text>Retall Final</Text>
                    <Value>0</Value>
                    <ValueType>Double</ValueType>
                    <Visible>True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
            </Parameter>


            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Properties</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>
                <Visible>IsUseGlobalProp == False and SelectorPPIS == 1</Visible>

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
                    <Visible>True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>BarraLayer</Name>
                    <Text>Layer</Text>
                    <Value>40068</Value>
                    <ValueType>Layer</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>TipusLinia</Name>
                    <Text>Tipus Eix</Text>
                    <Value>Tipus 1</Value>
                    <ValueList>Tipus 1|Tipus 2</ValueList>
                    <ValueType>StringComboBox</ValueType>
                    <Visible>True</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>


            </Parameter>



        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>desplX</Name>
            <Text>despl X</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>desplY</Name>
            <Text>despl Y</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>mostrarEix</Name>
            <Text>Mostrar tots els eixos</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Persistent>Model</Persistent>
            <Visible>True</Visible>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaA</Name>
            <Text>Linia Interior 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>mostrarEix</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix X Barra Vertical-->
        <Parameter>
            <Name>desplLinA</Name>
            <Text>desplaçament linia 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>mostrarEix and mostrarLiniaA</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>mostrarLiniaB</Name>
            <Text>Linia Interior 2</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>mostrarEix</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplLinB</Name>
            <Text>desplaçament linia 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>mostrarEix and mostrarLiniaB</Visible>
            <Persistent>Model</Persistent>
        </Parameter>




    </Page>
    <!--FEMELLES -->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <!-- <Visible>SelectorPPIS == 1 and SelectorTDH == 'EN Inferior'</Visible>
        <Visible>SelectorPPIS == 1 </Visible>-->
        <Visible>False </Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>FemellesExpander</Name>
            <Text></Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>Ample_forat_femella</Name>
                <Text>Ample Forat Femella</Text>
                <Value>15</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Altura_forat_femella</Name>
                <Text>Altura Forat Femella</Text>
                <Value>3.75</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separacio_forat_femella</Name>
                <Text>Separació Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>


        </Parameter>
    </Page>
     <!--Encaix HOR INF-->
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <!-- <Visible>SelectorPPIS == 1 and SelectorTDH == 'EN Inferior'</Visible>-->
        <!-- <Visible>SelectorPPIS == 1 </Visible>-->
        <Visible>False</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>EncaixExpander</Name>
            <Text>Encaix</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>PestanyaSuperior</Name>
                <Text>Pestanya Superior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>PestanyaInferior</Name>
                <Text>Pestanya Inferior</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PestanyesInv</Name>
                <Text>Pestanya Invertides</Text>
                <Value>False</Value>
                <ValueType>Checkbox</ValueType>
                <Persistent>Model</Persistent>
                <Visible>False</Visible>
            </Parameter>


            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>


        </Parameter>
    </Page>
    <!-- Matrius-->
    <Page>
        <Name>__HiddenPage__</Name>
        <Text></Text>
        <Visible>False</Visible>


        <Parameter>
            <Name>DENHorInt</Name>
            <Text>DenHorInt</Text>
            <Value>This is a string</Value>
            <ValueType>String</ValueType>
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


        <!-- valors Barra Horitzontal Intermitja-->
        <Parameter>
            <!-- <Name>dadesTDHortInter</Name>-->
            <Name>dadesTubHor</Name>
            <Text>Mostrar, Ample, Altura, Llargada, LlargadaAut, Gruix,
                desplX, desplY,
                mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                Is Global Prop Vert, Color, Layer,
                Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                PestanyaSup, PestanyaInf,FemellaSup, FemellaInf, Canviar Pestanyes,
                esProvisional,
                provSupEsq, provSupDre, provInfEsq, provInfDre, provInfCen,
                linia, layer , TipusTub, rotar, tipusTubAuto,
                tubInferior, tubSuperior, posAutomatica,
                retallInicial, retallFinal
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Length,Length,Length,Checkbox,Length,
                                Length,Length,
                                Checkbox,Length, Checkbox,Length,
                                Checkbox, Color, Layer,
                                Length, Length, Length,
                                Checkbox, Checkbox, Checkbox, Checkbox, Checkbox,
                                Checkbox,
                                Checkbox, Checkbox, Checkbox, Checkbox, Checkbox,
                                String, String, String, Checkbox, Checkbox,
                                String, String, Checkbox,
                                Length, Length)
            </ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Mostrar, Ample, Altura, Llargada, LlargadaAut, Gruix,
                            desplX, desplY,
                            mostrarLiniaA,desplLinA,mostrarLiniaB,desplLinB,
                            IsUseGlobalProp, FounColor, BarraLayer,
                            Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                            PestanyaSuperior, PestanyaInferior, femellaSup, femellaInf, PestanyesInv,
                            esProvisional,
                            provSupEsq, provSupDre, provInfEsq, provInfDre, provInfCen,
                            linia, layer, TipusTub, RotarTub, tipusTubAuto,
                            tubInferior, tubSuperior, posAutomatica,
                            retallInicial, retallFinal
                </FieldNames>
            </NamedTuple>
            <Visible>False, False,  False, False,False, False, False,False, False, False, False, False, False, False,False,False,False,False,False,False,False, False, False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>


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
            <Visible>False, False, False, False,False, False, False, False, False, False, False, False, False, False, False</Visible>
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
            <Visible>False, False, False,False, False, False, False, False, False, False, False</Visible>
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







    </Page>
</Element>
