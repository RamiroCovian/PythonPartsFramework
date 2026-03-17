<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\Estructura\TD\PY\TD_Conjunt_8_clase_PPTD.py</Name>
        <Title>Python Part TD 27.0</Title>
        <Version>27.0</Version>
        <ReadLastInput>True</ReadLastInput>
        <DataColumnWidth>150</DataColumnWidth>
    </Script>
    <!--
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector</Text>
        <Persistent>Model</Persistent>

        <Item>
            <TextId>1002</TextId>
            <Text>links</Text>
        </Item>

        <Parameter>
            <Name>FlagEntrada</Name>
            <Text>FlagEntrada</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
            <Visible>True</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorPPPare</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>2</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>


            <Parameter>
                <Name>Pare</Name>
                <Text>Pare</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>TD</Name>
                <Text>TD</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>EN</Name>
                <Text>EN</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>IS</Name>
                <Text>IS</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

        </Parameter>

    </Page>
    -->
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

        <!--
        <Parameter>
            <Name>AttributeID</Name>
            <Text>All attributes ID</Text>
            <Value></Value>
            <ValueType>AttributeID</ValueType>
            <ValueDialog>AttributeSelection</ValueDialog>
        </Parameter>
        -->

        <Parameter>
            <Name>comprovarDEN</Name>
            <Text>Comparar Atributs DEN</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <BackgroundColor>(255, 0, 0)</BackgroundColor>
        </Parameter>

        <!-- Selector Barra Horitzontals / Verticals-->
        <Parameter>
            <Name>NomTD</Name>
            <Text>NomTD</Text>
            <Value>TD</Value>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>



        <!-- Distancia entre TD/Barres Verticals-->
        <Parameter>
            <Name>DistanciaEntreTDAnt</Name>
            <Text>Dist. entre Barres Vert</Text>
            <Value>100</Value>
            <MinValue>0</MinValue>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>DistanciaEntreTD</Name>
            <Text>Dist. entre Barres Vert</Text>
            <Value>1170</Value>
            <MinValue>0</MinValue>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
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
            <Name>SelectorPPTD</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>


            <Parameter>
                <Name>BarraHor</Name>
                <Text>Horitzontal</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>BarraVer</Name>
                <Text>Vertical</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>BalconeraFinestra</Name>
                <Text>Balconera / Finestra</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>BarraReforc</Name>
                <Text>Barra Reforç</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>

        </Parameter>



        <!-- Selector Barra Inferior / Superior -->
        <Parameter>
            <Name>SelectorTDHTD</Name>
            <Text>Select TD Horitzontal</Text>
            <Value>TD Inferior</Value>
              <ValueList>TD Inferior|TD Superior|Mes Tubs...</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHInf</Name>
            <Text>Select Tipus Inf</Text>
            <Value>Tub</Value>
              <ValueList>Tub|L|</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>SelectorTDHSup</Name>
            <Text>Select Tipus Sup</Text>
            <Value>Tub</Value>
              <ValueList>Tub|L|Tub + L</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
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
            <Name>SelectorTDHTotalAnt</Name>
            <Text>valueListBarresHorBalc</Text>
            <Value>-1</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDTipusHor</Name>
            <Text>valueTipusListBarresHor</Text>
            <Value>-1</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHTotal</Name>
            <Text>Select Horitzontal</Text>
            <Value>TD Inferior</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalcOnlyNum]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Numero indicador de les Barres verticals-->
        <Parameter>
            <Name>IntegerTDSelector</Name>
            <Text>Nº barres</Text>
            <Value>10</Value>
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPTD == 1 or SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>esVermellHor</Name>
            <Text>vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>
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
            <Name>SelectorTDVAnt</Name>
            <Text>Select Vertical</Text>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorTDV</Name>
            <Text>Select Vertical</Text>
            <Value>TDVer</Value>
              <ValueList>['TDVer '+str(value) for value in range(0, IntegerTDSelector)]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <BackgroundColor>(252, 186, 3)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Selector Balconera / Finestra-->
        <Parameter>
            <Name>IntegerBalcFinSelector</Name>
            <Text>Nº balconeres</Text>
            <Value>1</Value>
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPTD == 3</Visible>
            <!-- <Visible>False</Visible>-->
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorBalcFinAnt</Name>
            <Text>Select Balc/Fin Anterior</Text>
            <Value>-1</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorBalcFin</Name>
            <Text>Select Balconera/Finestra</Text>
            <Value>Balc/Fin</Value>
              <ValueList>['Balc/Fin '+str(value) for value in range(0, IntegerBalcFinSelector)]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 3</Visible>
            <BackgroundColor>(191, 2, 119)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>True</Visible>
        </Parameter>

        <Parameter>
            <Name>MesuraXPS</Name>
            <Text>MesuraXPS</Text>
            <Value>120</Value>
            <MinValue>0</MinValue>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>



        <Parameter>
            <Name>MostrarTDVertical</Name>
            <Text>Mostrar Vertical</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>valueVertListBarresHorInf</Name>
            <Text>valueVertListBarresHorInf</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorInf</Name>
            <Text>Tub Hor Inferior</Text>
            <Value>TD Inferior</Value>
            <ValueList>[str(value) for value in valueVertListBarresHorInf]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>valueVertListBarresHorSup</Name>
            <Text>valueVertListBarresHorSup</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorSup</Name>
            <Text>Tub Hor Superior</Text>
            <Value>TD Superior</Value>
            <ValueList>[str(value) for value in valueVertListBarresHorSup]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <BackgroundColor>(0, 255, 0)</BackgroundColor>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>MostrarTDHoritzontalSup</Name>
            <Text>Mostrar Horitzontal Sup</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>MostrarFemellesSup</Name>
            <Text>Mostrar Femelles Sup</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SelectorTDHSup == 'L'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>VermellSup</Name>
            <Text>Vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>MostrarTDHoritzontalInf</Name>
            <Text>Mostrar Horitzontal Inf</Text>
            <Value>True</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>VermellInf</Name>
            <Text>Vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>InvertirTDHoritzontalInf</Name>
            <Text>Invertir Inf(ESQ/DRE)</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SelectorTDHInf == 'L'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>InvertirTDHoritzontalInf2</Name>
            <Text>Invertir Inf(SUP/INF)</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SelectorTDHInf == 'L'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>InvertirTDHoritzontalSup</Name>
            <Text>Invertir Sup(ESQ/DRE)</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>InvertirTDHoritzontalSup2</Name>
            <Text>Invertir Sup(SUP/INF)</Text>
            <Value>True</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SepararTDHoritzontalInf</Name>
            <Text>Separar Horitzontal Inf</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SepararTDHoritzontalSup</Name>
            <Text>Separar Horitzontal Sup</Text>
            <Value>False</Value>
            <ValueType>checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>nBarresTDHoritzontalInf</Name>
            <Text>nº Barres Horitzontal Inf</Text>
            <Value>3</Value>
            <MinValue>1</MinValue>
            <!-- <MaxValue>3</MaxValue>-->
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1</Visible>
            <!-- <Visible>True</Visible>-->
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>nBarresTDHoritzontalSup</Name>
            <Text>nº Barres Horitzontal SUp</Text>
            <Value>3</Value>
            <MinValue>1</MinValue>
            <ValueType>Integer</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>esProvisional</Name>
            <Text>es provisional</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>esProvisionalAuto</Name>
            <Text>L automatiques</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2 and esProvisional</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>esExtrem</Name>
            <Text>Provisional Extrem</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2 and esProvisional</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>esProvisionalAuto1</Name>
            <Text>L Dre Inf</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2 and not esProvisionalAuto</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>esProvisionalAuto4</Name>
            <Text>L Esq Inf</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2 and not esProvisionalAuto</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>esProvisionalAuto2</Name>
            <Text>L Esq Sup</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2 and not esProvisionalAuto</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>esProvisionalAuto3</Name>
            <Text>L Dre SUP</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>True</Enable>
            <Visible>SelectorPPTD == 2 and not esProvisionalAuto</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <Parameter>
            <Name>esVermellVert</Name>
            <Text>Vermell</Text>
            <Value>False</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
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

            <!--
            <Parameter>
                <Name>detectarLocal</Name>
                <Text>Detectar Local</Text>
                <EventId>1005</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
            -->
        </Parameter>


        <Parameter>
            <Name>MostrarOcultarLayers</Name>
            <Text>Mostra/Ocultar Layers</Text>
            <ValueType>Expander</ValueType>
            <Value>True</Value>

            <Parameter>
                <Name>MostrarCavitatsRecess</Name>
                <Text>Mostrar Cavitats (KN_XPS_RECESS)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>MostrarCavitats</Name>
                <Text>Mostrar Cavitats (KN_XPS_CAVITAT)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            </Parameter>

            <Parameter>
                <Name>MostrarRecessInf</Name>
                <Text>Mostrar Cavitat Tub Inferior (KN_XPS_RECESS)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>MostrarCavitatInf</Name>
                <Text>Mostrar Cavitats Tub Inferior (KN_XPS_CAVITAT)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
            </Parameter>

            <Parameter>
                <Name>MostrarRecessSup</Name>
                <Text>Mostrar Cavitat Tub Superior (KN_XPS_RECESS)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>MostrarCavitatSup</Name>
                <Text>Mostrar Cavitats Tub Superior (KN_XPS_CAVITAT)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
            </Parameter>

            <Parameter>
                <Name>MostrarRecessVert</Name>
                <Text>Mostrar Cavitat Tub Vertical (KN_XPS_RECESS)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>MostrarCavitatVert</Name>
                <Text>Mostrar Cavitats Tub Vertical (KN_XPS_CAVITAT)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
            </Parameter>

            <Parameter>
                <Name>MostrarEsponja</Name>
                <Text>Mostrar Fresades Esponja (KN_ESPONJA)</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>True</Visible>
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

            <Parameter>
                <Name>InvertirTDNums</Name>
                <Text>Invertir Numeros Id</Text>
                <Value>False</Value>
                <ValueType>checkbox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>FemellesEncaixosParameterExpander</Name>
            <Text>Femelles i Encaixos</Text>
            <ValueType>Expander</ValueType>
            <Value>False</Value>
            <Visible>SelectorPPTD == 2</Visible>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>encaixSup</Name>
                <Text>Treure Encaix Sup</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>encaixInf</Name>
                <Text>Treure Encaix Inf</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
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
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 2 and VertEditant == False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>femellaInf</Name>
                <Text>Femella Inf</Text>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
                <Visible>SelectorPPTD == 2 and VertEditant == False</Visible>
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
            <Visible>SelectorPPTD == 2</Visible>
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
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>ExtensioInferior</Name>
            <Text>ExtensioInferior</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>False</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>

            <Parameter>
                <Name>ExtenderInf</Name>
                <Text>Extensio Inf</Text>
                <Value>0.0</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>


        </Parameter>



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
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'Mes Tubs...'</Visible>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>valueListBarresComboBox</Name>
                <Text>valueListBarresComboBox</Text>
                <Value>[_]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarresHorListToShowTD</Name>
                <Text>Barra Horitzontal,Orientacio,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar,Mostrar Cavitat (KN_XPS_RECESS),Mostrar Cavitat (KN_XPS_CAVITAT),Es Xapa, Profunitat Cavitat Xapa,Layer,Separator</Text>
                <!-- <Value>[False|Inf|0|True|0|Tub 0|Tub 1|False|False|True|True|False|5|TD_ESTRUCTURA|]</Value>
                <Value>[]</Value>-->
                <Value>[False|Inf|400|True|0|Tub 0|Tub 1|False|False|True|True|False|5|TD_ESTRUCTURA|]</Value>

                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Length,StringComboBox,Separator)</ValueType>
                <!-- <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,,,,,,TD_ESTRUCTURA|KN_ELECTRICITAT_REINFORCEMENT|KN_AIGUA_REINFORCEMENT,</ValueList>-->
                <ValueList>,Sup|Inf,,,,valueListBarresComboBox,valueListBarresComboBox,,,,,,,TD_ESTRUCTURA|KN_ELECTRICITAT_REINFORCEMENT|KN_AIGUA_REINFORCEMENT,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar,MostrarRecess,MostrarCavitat,Xapa,ProfunditatXapa,Layer,Separator</FieldNames>
                </NamedTuple>
                <!-- <Visible>SelectorPPTD == 2, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][3] == False, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][3] == False, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 2 and BarresHorListToShowTD[$list_row][0] == True,False, SelectorPPTD == 2</Visible>-->
                <Visible>SelectorPPTD == 1, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][3] == False, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][3] == False, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True,False,False, False, False, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True,  SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][11] == True, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][11] == True,SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True and BarresHorListToShowTD[$list_row][11] == True, SelectorPPTD == 1 and BarresHorListToShowTD[$list_row][0] == True</Visible>
                <!-- <Visible> False,False, False, False, False, False, False, False,False, False</Visible>-->
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>

            <Parameter>
                <Name>BarresHorList</Name>
                <Text>Barra Horitzontal,Orientacio,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar, Mostrar Cavitat (KN_XPS_RECESS) Mostrar Cavitat (KN_XPS_CAVITAT),Es Xapa, Profunitat Cavitat Xapa,Layer,</Text>
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Length,StringComboBox,Separator)</ValueType>
                <!-- <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,,,,,,TD_ESTRUCTURA|KN_ELECTRICITAT_REINFORCEMENT|KN_AIGUA_REINFORCEMENT</ValueList>-->
                <ValueList>,Sup|Inf,,,,valueListBarresComboBox,valueListBarresComboBox,,,,,,,TD_ESTRUCTURA|KN_ELECTRICITAT_REINFORCEMENT|KN_AIGUA_REINFORCEMENT</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar,MostrarRecess,MostrarCavitat,Xapa,ProfunditatXapa,Layer,Separator</FieldNames>
                </NamedTuple>
                <!-- <Visible>SelectorPPTD == 2, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True,False, SelectorPPTD == 2</Visible>-->
                <!--<Visible>SelectorPPTD == 1, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True, SelectorPPTD == 1 and BarresHorList[$list_row][0] == True,False, SelectorPPTD == 1</Visible>-->
                <Visible>False, False, False, False, False, False, False, False,False, False,False,False,False,False,False</Visible>
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
                        <Value>Orientacio</Value>
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
                    <Name>BarresHorList</Name>
                    <Text>"Barra Horitzontal "+ ($list_row),Orientacio,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
                    <Value>[False|Sup|400|True|2500|TD Inferior|TD Superior|False|False]*30</Value>
                    <ValueType>tuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Separator)</ValueType>
                    <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,</ValueList>
                    <Visible>SelectorPPTD == 2, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True,False, SelectorPPTD == 2</Visible>
                    <ValueListStartRow>0</ValueListStartRow>
                    <Persistent>Model</Persistent>
                </Parameter>
                <Parameter>
                    <Name>BarresHorList</Name>
                    <Text>"Barra Horitzontal " + str($list_row),Orientacio,Posicio,Long. Automatica,Longitud,BarraInici,BarraFinal,Edit,acabatEditar</Text>
                    <Value>[]</Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Checkbox,Length,StringComboBox,StringComboBox,Checkbox,Checkbox,Separator)</ValueType>
                    <ValueList>,Sup|Inf,,,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,</ValueList>
                    <NamedTuple>
                        <TypeName>StirrupList</TypeName>
                        <FieldNames>BarraHor,Orientacio,Posicio,AutoLongitud,Longitud,BarraInici,BarraFinal,Edit,acabatEditar,Separator</FieldNames>
                    </NamedTuple>
                    <Visible>SelectorPPTD == 2, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True and BarresHorList[$list_row][3] == False, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True, SelectorPPTD == 2 and BarresHorList[$list_row][0] == True,False, SelectorPPTD == 2</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

            </Parameter>
            -->
        </Parameter>

        <Name>BarresReforç</Name>
        <Text>Barres Reforç</Text>
        <ValueType>ListGroup</ValueType>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>BarresRefParameterExpander</Name>
            <Text>Barres reforç</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Persistent>Model</Persistent>
            <Visible>SelectorPPTD == 4</Visible>

            <Parameter>
                <Name>NumBarresRef</Name>
                <Text>Num Barres Reforc</Text>
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
                <Name>valueListReforcComboBox</Name>
                <Text>valueListReforcComboBox</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>SelectorReforc</Name>
                <Text>Select Reforç</Text>
                <Value>Reforç 0</Value>
                <ValueList>[str(value) for value in valueListReforcComboBox]</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>SelectorPPTD == 4</Visible>
                <BackgroundColor>(0, 155, 155)</BackgroundColor>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible> SelectorPPTD == 4 </Visible>
            </Parameter>


            <Parameter>
                <Name>BarresRefListToShowTD</Name>
                <Text>Barra Reforç,Orientacio,Posicio,Barra Ini,Barra Fin,Long. Automatica,Longitud,Edit,acabatEditar</Text>
                <Value>[False|Sup|100|Tub 0|Tub 1|True|100|False|False]</Value>
                <!-- <Value>[]</Value>-->
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,StringComboBox,StringComboBox,Checkbox, Length,Checkbox,Checkbox)</ValueType>
                <!-- <ValueList>,Sup|Inf,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,,,,</ValueList>-->
                <ValueList>,Sup|Inf,,valueListBarresComboBox,valueListBarresComboBox,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraRef,Orientacio,Posicio,BarraIni,BarraFin,AutoLongitud,Longitud,Edit,acabatEditar</FieldNames>
                </NamedTuple>
                <Visible> SelectorPPTD == 4, False, SelectorPPTD == 4 and BarresRefListToShowTD[$list_row][0] == True, SelectorPPTD == 4 and   BarresRefListToShowTD[$list_row][0] == True, SelectorPPTD == 4 and   BarresRefListToShowTD[$list_row][0] == True, SelectorPPTD == 4 and   BarresRefListToShowTD[$list_row][0] == True, SelectorPPTD == 4 and   BarresRefListToShowTD[$list_row][0] == True and BarresRefListToShowTD[$list_row][5] == False, False, False, SelectorPPTD == 4</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible> SelectorPPTD == 4 </Visible>
            </Parameter>


            <Parameter>
                <Name>BarresRefListTD</Name>
                <Text>Barra Reforç,Orientacio,Posicio,Barra Ini,Barra Fin,Long. Automatica,Longitud,Edit,acabatEditar</Text>
                <!-- <Value>[False|Sup|100|Tub 0|Tub 1|True|100|False|False]</Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,StringComboBox,StringComboBox,Checkbox, Length,Checkbox,Checkbox,Separator)</ValueType>
                <!-- <ValueList>,Sup|Inf,,[str(value) for value in valueListBarresComboBox],[str(value) for value in valueListBarresComboBox],,,,,</ValueList>-->
                <ValueList>,Sup|Inf,,valueListBarresComboBox,valueListBarresComboBox,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraRef,Orientacio,Posicio,BarraIni,BarraFin,AutoLongitud,Longitud,Edit,acabatEditar,Separator</FieldNames>
                </NamedTuple>
                <!-- <Visible> SelectorPPTD == 4, False, SelectorPPTD == 4 and BarresRefListTD[$list_row][0] == True, SelectorPPTD == 4 and BarresRefListTD[$list_row][0] == True, SelectorPPTD == 4 and BarresRefListTD[$list_row][0] == True, SelectorPPTD == 4 and BarresRefListTD[$list_row][0] == True, SelectorPPTD == 4 and BarresRefListTD[$list_row][0] == True and BarresRefListTD[$list_row][5] == False, False, False, SelectorPPTD == 4</Visible>-->
                <Visible> False, False, False, False, False, False, False, False, False, False</Visible>
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
                <!--
                <Value>[False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True;
                        False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True;
                        False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True;
                        False|0|0|0|True|100|Inferior|False|False|False|False|False|False|False|False|True|True]
                </Value>
                -->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,Length,Length,Length,Checkbox,Length,StringComboBox,Checkbox, Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Separator)</ValueType>
                <ValueList>,,,,,,Inferior|Barra1|Barra2|Barra3,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraVert,Posicio,PosicioAbs,PosicioZ,AutoLongitud,Longitud,BarraInici,EditFront,Edit,EncaixInf,EncaixSup,acabatEditar,editiantFrontals,PestanyaSup,PestanyaInf,FemellaSup,FemellaInf, Separator</FieldNames>
                </NamedTuple>
                <Visible>SelectorPPTD == 2, False,SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True,False, False, False ,SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True,SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True,SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True,False,False,False,False, SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPTD == 2 and BarresVertListToShow[$list_row][0] == True, SelectorPPTD == 2</Visible>
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
            <Visible>SelectorPPTD == 1 </Visible>

            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>BarresAdjListToShow</Name>
                <Text>Barra Adjacent,Orientacio,Posicio,Longitud,Profunditat,Show,Save,acabatEditar</Text>
                <!-- <Value>[False|Inf|0|100|0|False|False|False]</Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraAdj,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar, Separator</FieldNames>
                </NamedTuple>
                <Visible>SelectorPPTD == 1, SelectorPPTD == 1 and BarresAdjListToShow[$list_row][0] == True, SelectorPPTD == 1 and BarresAdjListToShow[$list_row][0] == True, SelectorPPTD == 1 and BarresAdjListToShow[$list_row][0] == True,SelectorPPTD == 1 and BarresAdjListToShow[$list_row][0] == True, False, SelectorPPTD == 1,False, SelectorPPTD == 1</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>BarresAdjList</Name>
            <Text>BarraAdj,Orientacio,Posicio,Longitud,Profunditat,Edit,acabatEditar</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraAdj,Orientacio,Posicio,Longitud,Profunditat,Edit,acabatEditar, Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- ******** Barres Frontals *********-->
        <Name>Barres Frontals</Name>
        <Text>TIS</Text>
        <!-- <Persistent>Model</Persistent> -->
        <Parameter>
            <Name>BarresFrontParameterExpander</Name>
            <Text>TIS</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>SelectorPPTD == 2</Visible>

            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>BarresFrontListToShow</Name>
                <Text>TIS,Longitud,Altura,Orientacio,Posicio,Ample,Profunditat,Show,Save,acabatEditar</Text>
                <!-- <Value>[False|30|40|Inf|100|100|10|False|False|False;
                        False|30|40|Inf|200|100|10|False|False|False;
                        False|30|40|Inf|300|100|10|False|False|False;
                        False|30|40|Inf|400|100|10|False|False|False;
                        False|30|40|Inf|500|100|10|False|False|False;
                        False|30|40|Inf|600|100|10|False|False|False;
                        False|30|40|Inf|300|100|10|False|False|False;
                        False|30|40|Inf|400|100|10|False|False|False;
                        False|30|40|Inf|500|100|10|False|False|False;
                        False|30|40|Inf|600|100|10|False|False|False]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox,Separator)</ValueType>
                <ValueList>,,,Esq|Dre,,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraFront,Amplitud,Altura,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar,Separator</FieldNames>
                </NamedTuple>
                <Visible>SelectorPPTD == 2, SelectorPPTD == 2 and BarresFrontListToShow[$list_row][0] == True,SelectorPPTD == 2 and BarresFrontListToShow[$list_row][0] == True,SelectorPPTD == 2 and BarresFrontListToShow[$list_row][0] == True, SelectorPPTD == 2 and BarresFrontListToShow[$list_row][0] == True, SelectorPPTD == 2 and BarresFrontListToShow[$list_row][0] == True, SelectorPPTD == 2 and BarresFrontListToShow[$list_row][0] == True, False, False,False, SelectorPPTD == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <!--
        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        -->

        <Parameter>
            <Name>BarresFrontList</Name>
            <Text>TISS,Ample,Forat,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType>
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
            <Name>dadesBalcFines</Name>
            <Text>Mostrar,AmpleBalconera,LlargadaBalconera,PosicioXBalconera,PosicioZBalconera,BarraHorSup,BarraHorInf,BarraVertEsq,BarraVertDre,Separator</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,Length,Length,Length,Length,String,String,String,String,Separator)</ValueType>
            <ValueList>False,400,400,600,800,TD Superior,TD Inferior,Tub 0,Tub 1</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Mostrar,AmpleBalconera,LlargadaBalconera,PosicioXBalconera,PosicioZBalconera,BarraHorSup,BarraHorInf,BarraVertEsq,BarraVertDre, Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!--
        <Parameter>
            <Name>MostrarBalconera</Name>
            <Text>Mostrar Balconera / Finestra</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        -->

        <!-- Balconera Finestra-->
        <Parameter>
            <Name>PosiDimensBalcFinesParameterExpander</Name>
            <Text>Posicio i Dimensions Balconera i Finestra</Text>
            <ValueType>Expander</ValueType>
            <Value>False</Value>
            <Visible>SelectorPPTD == 3</Visible>

            <Parameter>
                <Name>MostrarBalconera</Name>
                <Text>Mostrar Premarc</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>nomPremarc</Name>
                <Text>Nom premarc</Text>
                <Value>Premarc.</Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>UpdateBalconera</Name>
                <Text>Balconera</Text>
                <ValueType>Row</ValueType>
                <Visible>SelectorPPTD == 3</Visible>

                <Parameter>
                    <Name>CreateBalconera</Name>
                    <Text>Create</Text>
                    <EventId>1003</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
                <Parameter>
                    <Name>DeleteBalconera</Name>
                    <Text>Delete</Text>
                    <EventId>1004</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>

            <Parameter>
                <Name>UpdateBalconeraFinestra</Name>
                <Text>Crear Balconera / Finestra</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
                <Enable>False</Enable>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>AmpleBalconera</Name>
                <Text>Ample</Text>
                <Value>100</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>LlargadaBalconera</Name>
                <Text>Llargada</Text>
                <Value>200</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>PosicioXBalconera</Name>
                <Text>Posicio X</Text>
                <Value>300</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 3</Visible>
            </Parameter>

            <Parameter>
                <Name>PosicioZBalconera</Name>
                <Text>Posicio Z</Text>
                <Value>400</Value>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 3</Visible>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>SelectorPPTD == 3</Visible>
        </Parameter>


        <Parameter>
            <Name>valueListBarresHorBalc</Name>
            <Text>valueListBarresHorBalc</Text>
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
            <Name>SelectorTDHorSupBalc</Name>
            <Text>Tub Horitzontal SUP Balc/Fin</Text>
            <Value>TD Inferior</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalc]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 3</Visible>
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
            <Name>SelectorTDHorInfBalc</Name>
            <Text>Tub Horitzontal INF Balc/Fin</Text>
            <Value>TD Inferior</Value>
            <ValueList>[str(value) for value in valueListBarresHorBalc]</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 3</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>VerticalAutoBalc</Name>
            <Text>Vertical Auto</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 3</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorEsqBalc</Name>
            <Text>Tub Horitzontal ESQ Balc/Fin</Text>
            <Value>TD Inferior</Value>
            <!-- <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>-->
            <ValueList>valueListBarresComboBox</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 3 and VerticalAutoBalc == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorTDHorDreBalc</Name>
            <Text>Tub Horitzontal DRE Balc/Fin</Text>
            <Value>TD Inferior</Value>
            <!-- <ValueList>[str(value) for value in valueListBarresComboBox]</ValueList>-->
            <ValueList>valueListBarresComboBox</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 3 and VerticalAutoBalc == False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

    </Page>

    <!-- ************* Desplaçament *************-->
    <Page>
        <!-- <Name>Parent:PythonPartConnection</Name>-->
        <Name>PP TD Horitzontal</Name>
        <Text>Desplaçament Horitzontal</Text>
        <Visible> SelectorPPTD == 1 or SelectorPPTD == 2 or SelectorPPTD == 4</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <!-- Desplaçament en l'eix X en de la barra Horitzontal Inferior -->
        <Parameter>
            <Name>desplXI</Name>
            <Text>desplaçament X</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' </Visible>
            <ValueType>Length</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament en l'eix Y en de la barra Horitzontal Inferior -->
        <Parameter>
            <Name>desplYI</Name>
            <Text>desplaçament Y</Text>
            <Value>0.0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <Parameter>
            <Name>DimensionsParameterExpanderInf</Name>
            <Text>Barres Hor. Inferiors</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>listDesplHoritzontalsInf</Name>
                <Text>Ample,Altura,Llargada,desplX,desplY,mostrarLiniaA,desplLinA,mostrarLiniaB,desplLinB,Separator</Text>
                <Value>[30|30|1000|0|0|True|0|False|0;
                        30|30|1000|0|0|True|0|False|0;
                        30|30|1000|0|0|True|0|False|0]
                </Value>
                <ValueList>,,,,,,,,,,</ValueList>
                <ValueType>namedtuple(Length,Length,Length,Length,Length,Checkbox,Length,Checkbox,Length,Separator)</ValueType>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraAmpleInf,BarraAlturaInf,BarraLlargadaInf,desplX,desplY,mostrarLiniaA,desplLinA,mostrarLiniaB,desplLinB,Separator</FieldNames>
                </NamedTuple>
                <!-- <Visible>False, False, False, False,False, False,False, False</Visible>-->
                <Visible>False, False, SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1, False, SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1,SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and SepararTDHoritzontalInf == 1</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>listDesplHoritzontalsSup</Name>
                <Text>Ample,Altura,Llargada,desplX,desplY,mostrarLiniaA,desplLinA,mostrarLiniaB,desplLinB,Separator</Text>
                <!-- <Value>[30|30|1000|0|0|True|0|False|0;
                        30|30|1000|0|0|True|0|False|0;
                        30|30|1000|0|0|True|0|False|0]
                </Value>-->
                <Value>[]</Value>
                <ValueList>,,,,,,,,,,</ValueList>
                <ValueType>namedtuple(Length,Length,Length,Length,Length,Checkbox,Length,Checkbox,Length,Separator)</ValueType>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>BarraAmpleSup,BarraAlturaSup,BarraLlargadaSup,desplX,desplY,mostrarLiniaA,desplLinA,mostrarLiniaB,desplLinB,Separator</FieldNames>
                </NamedTuple>
                <!-- <Visible>False, False, False, False,False, False,False, False</Visible>-->
                <Visible>False, False, SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1, False, SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1,SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1, SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and SepararTDHoritzontalSup == 1</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>


        <Parameter>
            <Name>EncaixHorInf</Name>
            <Text>Encaix Horitzontal</Text>
            <Value>True</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Desplaçament en l'eix X en de la barra Horitzontal Superior -->
        <Parameter>
            <Name>desplXS</Name>
            <Text>desplaçament X</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'Tub' or SelectorTDHSup == 'Tub + L')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament en l'eix Y en de la barra L Superior -->
        <Parameter>
            <Name>desplYS</Name>
            <Text>desplaçament Y </Text>
            <Value>30</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'Tub' or SelectorTDHSup == 'Tub + L')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>desplXSL</Name>
            <Text>desplaçament X(L)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament en l'eix Y en de la barra L Superior -->
        <Parameter>
            <Name>desplYSL</Name>
            <Text>desplaçament Y (L)</Text>
            <Value>30</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>EncaixHorSup</Name>
            <Text>Encaix Horitzontal</Text>
            <Value>True</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <!--<Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>-->
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>invertirEncaixInf</Name>
            <Text>Invertir Encaix (Inf)</Text>
            <Value>1</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>invertirEncaixSup</Name>
            <Text>Invertir Encaix (Sup)</Text>
            <Value>1</Value>
            <ValueType>Checkbox</ValueType>
            <Visible>False</Visible>
            <!--<Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>-->
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>listDesplVerticalsTD</Name>
            <Text> desplX,desplXAbs,desplY,desplYAbs,mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Length,Length,Length,Length,Checkbox,Length,Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>desplX,desplXAbs,desplY,desplYAbs,mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- LLista de Barres TDV Interiors-->


        <Parameter>
            <Name>listDesplVerticalsInteriors</Name>
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
            <!-- <Visible>SelectorPPTD == 2</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYVert</Name>
            <Text>desplaçament Y</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <!--<Visible>SelectorPPTD == 2</Visible>-->
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Desplaçament Absolut Eix X Barra Vertical-->
        <Parameter>
            <Name>desplXVertAbs</Name>
            <Text>despl X (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYVertAbs</Name>
            <Text>despl Y (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Desplaçament Absolut Eix X Barra Vertical-->
        <Parameter>
            <Name>desplXHorAbs</Name>
            <Text>despl X (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>(SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYHorAbs</Name>
            <Text>despl Y (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>(SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplXVertAbsRef</Name>
            <Text>despl X (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 4</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Absolut Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplYVertAbsRef</Name>
            <Text>despl Y (Abs)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 4</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaIntInf1</Name>
            <Text>Eix 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntInf1</Name>
            <Text>Desplaçament 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and mostrarLiniaIntInf1 == True and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



        <Parameter>
            <Name>mostrarLiniaIntInf2</Name>
            <Text>Eix 2</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntInf2</Name>
            <Text>Desplaçament 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior' and mostrarLiniaIntInf2 == True and not SepararTDHoritzontalInf</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorLiniaInf</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerInf</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaIntSup1</Name>
            <Text>Eix 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntSup1</Name>
            <Text>Desplaçament 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and mostrarLiniaIntSup1 == True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaIntSup2</Name>
            <Text>Eix 2</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>desplLiniaIntSup2</Name>
            <Text>Desplaçament 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and mostrarLiniaIntSup2 == True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorLiniaSup</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerSup</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>mostrarLiniaVertA</Name>
            <Text>Eix 1</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix X Barra Vertical-->
        <Parameter>
            <Name>desplVertLinA</Name>
            <Text>desplaçament linia 1</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) and mostrarLiniaVertA == True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>mostrarLiniaVertB</Name>
            <Text>Eix 2</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <!-- Desplaçament Eix Y Barra Vertical-->
        <Parameter>
            <Name>desplVertLinB</Name>
            <Text>desplaçament linia 2</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) and mostrarLiniaVertB == True</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SelectorLiniaVert</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerVert</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 2</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLiniaHor</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerHor</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>SelectorLiniaRef</Name>
            <Text>Tipus Eix</Text>
            <Value>Tipus 1</Value>
            <ValueList>Tipus 1|Tipus 2</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 4</Visible>
            <Persistent>Model</Persistent>
        </Parameter>
        <Parameter>
            <Name>SelectorLayerRef</Name>
            <Text>Layer Eix</Text>
            <Value>TD_FIXACIO</Value>
            <ValueList>TD_FIXACIO|TD_NO_CARAGOLAR</ValueList>
            <ValueType>StringComboBox</ValueType>
            <Visible>SelectorPPTD == 4</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


    </Page>

    <!-- Mesures Barra Hor-->
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPTD == 1 or (SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) or SelectorPPTD == 4</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Mesures Barra Vert</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>llargadaAutomatica</Name>
                <Text>Llargada Automatica</Text>
                <Value>True</Value>
                <ValueType>Checkbox</ValueType>
                <ExcludeIdentical>True</ExcludeIdentical>
                <Visible>SelectorPPTD == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>


            <Parameter>
                <Name>BarraAmpleVert</Name>
                <Text>Ample</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 2 </Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAmpleHor</Name>
                <Text>Ample</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAmpleRef</Name>
                <Text>Ample</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 4</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaVert</Name>
                <Text>Altura</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 2 </Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaHor</Name>
                <Text>Altura</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaRef</Name>
                <Text>Altura</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 4</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaVert</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>(SelectorPPTD == 2 ) and llargadaAutomatica == True</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaHor</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible> (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...") and llargadaAutomatica == True</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaIndiv</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>(SelectorPPTD == 2 ) and llargadaAutomatica == False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraLlargadaIndivHor</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>(SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...") and llargadaAutomatica == False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraGruixVert</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 2</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraGruixHor</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>(SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraGruixRef</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>SelectorPPTD == 4</Visible>
            </Parameter>




            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Properties</Text>
                <value>True</value>
                <Visible>SelectorPPTD == 2</Visible>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>IsUseGlobalPropVert</Name>
                    <Text>Use Global Propierties</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <!-- <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>-->
                    <Visible>False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>FounColorVert</Name>
                    <Text>Color</Text>
                    <Value>23</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <!-- <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) and IsUseGlobalPropVert == False</Visible>-->
                    <Visible>SelectorPPTD == 2</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>BarraLayerVert</Name>
                    <Text>Layer</Text>
                    <Value>40001</Value>
                    <ValueType>Layer</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <!-- <Visible>IsUseGlobalPropVert == False and (SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."))</Visible>-->
                    <Visible>False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Mesures Barra Hor</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>BarraAmpleInf</Name>
                <Text>Ample</Text>
                <Value>40.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaInf</Name>
                <Text>Altura</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraAmpleSup</Name>
                <Text>Ample</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'Tub' or SelectorTDHSup == 'Tub + L')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaSup</Name>
                <Text>Altura</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'Tub' or SelectorTDHSup == 'Tub + L')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraAmpleSupL</Name>
                <Text>Ample L</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaSupL</Name>
                <Text>Altura L</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
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
                <Name>mantenirLlargadaSup</Name>
                <Text>Llargada igual a Inf</Text>
                <Value>True</Value>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' </Visible>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>BarraLlargadaTD</Name>
                <Text>Llargada</Text>
                <Value>4400.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and mantenirLlargadaSup</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraLlargadaSupInd</Name>
                <Text>Llargada</Text>
                <Value>4400.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and not mantenirLlargadaSup</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <!--
            <Parameter>
                <Name>BarraGruix</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and (SelectorTDHTD == "Mes Tubs...")</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            -->
            <Parameter>
                <Name>BarraGruixInf</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <!-- <Visible>SelectorPPTD == 1 and SelectorTDHTD = "TD Inferior"</Visible>-->
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraGruixSup</Name>
                <Text>Gruix SUP</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'Tub' or SelectorTDHSup == 'Tub + L')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>BarraGruixSupL</Name>
                <Text>Gruix L</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior' and (SelectorTDHSup == 'L' or SelectorTDHSup == 'Tub + L')</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Properties</Text>
                <value>True</value>
                <Visible>True</Visible>
                <ValueType>Expander</ValueType>

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
                    <Name>FounColorHor</Name>
                    <Text>Color</Text>
                    <Value>23</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible> SelectorPPTD == 1 and (SelectorTDHTD == "Mes Tubs...")</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>FounColorSup</Name>
                    <Text>Color</Text>
                    <Value>23</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPTD == 1 and (SelectorTDHTD == "TD Superior")</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>FounColorInf</Name>
                    <Text>Color</Text>
                    <Value>23</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPTD == 1 and (SelectorTDHTD == "TD Inferior")</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>BarraLayer</Name>
                    <Text>Layer</Text>
                    <Value>40001</Value>
                    <ValueType>Layer</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>False  </Visible>
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

                <Parameter>
                    <Name>DENInf</Name>
                    <Text>Denominacio INF</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>DENSup</Name>
                    <Text>Denominacio SUP</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>DENVert</Name>
                    <Text>Denominacio Vert</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPTD == 2 and SelectorTDHTD == 'TD Inferior'</Visible>-->
                    <Visible>False</Visible>
                    <enable>False</enable>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>DENHorInt</Name>
                    <Text>Denominacio Hor Int</Text>
                    <Value></Value>
                    <ValueType>String</ValueType>
                    <!-- <Visible>SelectorPPTD == 2 and SelectorTDHTD == 'TD Inferior'</Visible>-->
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
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
        <!-- <Persistent>Model</Persistent> -->
        <!-- INFerior-->
        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Colis</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>


            <Parameter>
                <Name>ColisParINF</Name>
                <Text>Colis,Orientacio,Posicio,Llargada,Amplada,Reforç Colis</Text>
                <!-- <Value>[False|Sup|400.|150|12|True;
                        False|Sup|800.|150|12|True;
                        False|Sup|1200.|150|12|True;
                        False|Sup|1600.|150|12|True]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,MostrarBox,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ColisParINF[$list_row][0] == True, ColisParINF[$list_row][0] == True, ColisParINF[$list_row][0] == True, ColisParINF[$list_row][0] == True,ColisParINF[$list_row][0] == True</Visible>
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
                <Text>Pota,Posicio,Separator</Text>
                <!--
                <Value>[False|400.;
                        False|800.;
                        False|1200.;
                        False|1600.]
                </Value>
                -->
                <Value>[]</Value>
                <EventId>,,</EventId>
                <ValueType>namedtuple(Checkbox,Length,Separator)</ValueType>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Pota,Posicio,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,0,</MinValue>
                <Visible>True, PotaParINF[$list_row][0] == True,True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>ForatsParINF</Name>
                <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada</Text>
                <!--
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
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True, ForatsParINF[$list_row][0] == True and ForatsParINF[$list_row][5] == True,ForatsParINF[$list_row][0] == True and ForatsParINF[$list_row][5] == True, False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
    </Page>

    <!--Collisos i Potes HOR Superior-->
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <!-- SUPerior-->
        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Colis</Text>
            <ValueType>Expander</ValueType>


            <Parameter>
                <Name>ColisParSUP</Name>
                <Text>Colis,Orientacio,Posicio,Llargada,Amplada,Reforç Colis</Text>
                <!--
                <Value>[False|Sup|400.|150|12|True;
                    False|Sup|800.|150|12|True;
                    False|Sup|1200.|150|12|True;
                    False|Sup|1600.|150|12|True]
                </Value>
                -->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,MostrarBox,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True, ColisParSUP[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Potes</Text>
            <ValueType>Expander</ValueType>


            <Parameter>
                <Name>PotaParSUP</Name>
                <Text>Pota,Posicio,Separator</Text>
                <!--
                <Value>[False|400.;
                        False|1200.;
                        False|2400.;
                        False|4600.]
                </Value>
                -->
                <Value>[]</Value>
                <EventId>,,</EventId>
                <ValueType>namedtuple(Checkbox,Length,Separator)</ValueType>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Pota,Posicio,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,0,</MinValue>
                <Visible>True, PotaParSUP[$list_row][0] == True,True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>
            <Visible>(SelectorTDHSup == "Tub" or SelectorTDHSup == "Tub + L")</Visible>


            <Parameter>
                <Name>ForatsParSUP</Name>
                <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,LLargada,Amplada, TFF</Text>
                <!--
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
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True, ForatsParSUP[$list_row][0] == True,ForatsParSUP[$list_row][0] == True and ForatsParSUP[$list_row][5] == True,ForatsParSUP[$list_row][0] == True and ForatsParSUP[$list_row][5] == True, False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>(SelectorTDHSup == "L" or SelectorTDHSup == "Tub + L")</Visible>
        </Parameter>

        <Parameter>
            <Name>foratsAutomatics</Name>
            <Text>Automatitzacio Forats</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>(SelectorTDHSup == "L" or SelectorTDHSup == "Tub + L")</Visible>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpanderAuto</Name>
            <Text>Automatitzacio Forats L</Text>
            <ValueType>Expander</ValueType>
            <Visible>foratsAutomatics</Visible>


            <Parameter>
                <Name>nForatsAutoL</Name>
                <Text>nForats</Text>
                <Value>5</Value>
                <MinValue>0</MinValue>
                <ValueType>Integer</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>orientacioAutoL</Name>
                <Text>Orientacio</Text>
                <Value>Sup</Value>
                <ValueList>Esq|Dre|Sup|Inf</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>posIniAutoL</Name>
                <Text>Posicio Inicial</Text>
                <Value>150</Value>
                <ValueType>Length</ValueType>
            </Parameter>

            <Parameter>
                <Name>distanciaAutoL</Name>
                <Text>Distancia entre Forats</Text>
                <Value>100</Value>
                <ValueType>Length</ValueType>
            </Parameter>

            <Parameter>
                <Name>llargadaAutoL</Name>
                <Text>Llargada Forats</Text>
                <Value>20</Value>
                <ValueType>Length</ValueType>
            </Parameter>

            <Parameter>
                <Name>ampladaAutoL</Name>
                <Text>AmpladaForats</Text>
                <Value>20</Value>
                <ValueType>Length</ValueType>
            </Parameter>


            <Parameter>
                <Name>posYAutoL</Name>
                <Text>posicio Altura</Text>
                <Value>15</Value>
                <ValueType>Length</ValueType>
            </Parameter>

            <Parameter>
                <Name>ButtonRow</Name>
                <Text> Forats auto </Text>
                <ValueType>Row</ValueType>

                <Parameter>
                    <Name>createAutoL</Name>
                    <Text>Crear</Text>
                    <EventId>1006</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>

        </Parameter>


        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats L</Text>
            <ValueType>Expander</ValueType>
            <Visible>(SelectorTDHSup == "L" or SelectorTDHSup == "Tub + L")</Visible>



            <Parameter>
                <Name>ForatsParSUPL</Name>
                <Text>Forat,Orientacio,Posicio,Posicio Ample,Llargada,Amplada,Completa,LLargada,Amplada, TFF</Text>
                <!-- <Value>[False|Sup|200.|15|20|15|False|20|10;
                        False|Sup|400.|15|20|15|False|20|10;
                        False|Sup|600.|15|20|15|False|20|10;
                        False|Sup|800.|15|20|15|False|20|10;
                        False|Sup|1000.|15|20|15|False|20|10;
                        False|Sup|1200.|15|20|15|False|20|10;
                        False|Sup|1400.|15|20|15|False|20|10;
                        False|Sup|1600.|15|20|15|False|20|10;
                        False|Sup|1800.|15|20|15|False|20|10;
                        False|Sup|2000.|15|20|15|False|20|10]
                </Value>
                -->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,PosicioY,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ForatsParSUPL[$list_row][0] == True, ForatsParSUPL[$list_row][0] == True, ForatsParSUPL[$list_row][0] == True, ForatsParSUPL[$list_row][0] == True, ForatsParSUPL[$list_row][0] == True, False, False, False, False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
    </Page>

    <!--FEMELLES INFerior-->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
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
                <Text>Separacio Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PosicioExpander</Name>
                <Text>Posicio femelles</Text>
                <ValueType>Expander</ValueType>
                <!-- FEMELLES-->
                <!-- *********************************** -->
                <Parameter>
                    <Name>Separator</Name>
                    <ValueType>Separator</ValueType>
                </Parameter>


                <Parameter>
                    <Name>FemellesINF</Name>
                    <Text>Femella,Orientacio,Posicio X,Posicio Y,Separacio</Text>
                    <!--
                    <Value>[False|Esq|400|0|100;
                            False|Esq|800|0|100;
                            False|Esq|1200|0|100]
                    </Value>
                    -->
                    <Value>[]</Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
                    <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
                    <NamedTuple>
                        <TypeName>UShape</TypeName>
                        <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
                    </NamedTuple>
                    <MinValue>,,0,</MinValue>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True, FemellesINF[$list_row][0] == True, FemellesINF[$list_row][0] == True, FemellesINF[$list_row][0] == True, False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

            </Parameter>
        </Parameter>
    </Page>

    <!--FEMELLES SUPerior-->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
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
                <Text>Separacio Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PosicioExpander</Name>
                <Text>Posicio femelles</Text>
                <ValueType>Expander</ValueType>
                <!-- FEMELLES-->
                <!-- *********************************** -->
                <Parameter>
                    <Name>Separator</Name>
                    <ValueType>Separator</ValueType>
                </Parameter>

                <Parameter>
                    <Name>FemellesSUP</Name>
                    <Text>Femella,Orientacio,Posicio X,Posicio Y,Separacio</Text>
                    <!-- <Value>[False|Esq|400|0|100;
                            False|Esq|800|0|100;
                            False|Esq|1200|0|100]
                    </Value>-->
                    <Value>[]</Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
                    <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
                    <NamedTuple>
                        <TypeName>UShape</TypeName>
                        <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
                    </NamedTuple>
                    <MinValue>,,0,</MinValue>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True, FemellesSUP[$list_row][0] == True, FemellesSUP[$list_row][0] == True, FemellesSUP[$list_row][0] == True, False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>



            </Parameter>
        </Parameter>
    </Page>

    <!--CANCANMS HOR INF-->
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>CancamsExpander</Name>
            <Text>Cancams</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>posicio_centre_massesINF</Name>
                <Text>Posicio centre de masses</Text>
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
                    <Text>Distancia</Text>
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
                    <Text>Distancia</Text>
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
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>CancamsExpander</Name>
            <Text>Cancams</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>posicio_centre_massesSUP</Name>
                <Text>Posicio centre de masses</Text>
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
                    <Text>Distancia</Text>
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
                    <Text>Distancia</Text>
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
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior'</Visible>
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
            </Parameter>
            <Parameter>
                <Name>PestanyaInferiorINF</Name>
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
                <Name>EncaixosParINF</Name>
                <Text>Encaix,Orientacio,Longitud,Amplitud,Posicio,Profunditat,Pestanya</Text>
                <!-- <Value>[False|Esq|31.|30|15.5|11|False;
                        False|Esq|31.|30|15.5|11|False;
                        False|Esq|31.|30|15.5|11|False]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0,,1,</MinValue>
                <Visible>True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True, EncaixosParINF[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>
    </Page>

    <!--Encaix HOR SUP-->
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <Visible>SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior'</Visible>
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
                <Text>Encaix,Orientacio,Longitud,Amplitud,Posicio,Profunditat,Pestanya</Text>
                <!-- <Value>[False|Esq|31.|30|15.5|11|False;
                        False|Esq|80.|30|0.|11|False;
                        False|Esq|120.|0.|30|11|False]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0,,1,</MinValue>
                <Visible>True, EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True,EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True, EncaixosParSUP[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

        </Parameter>
    </Page>

    <!-- Mesures Barra Vert
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Mesures Barra Vert</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>llargadaAutomatica</Name>
                <Text>Llargada Automatica</Text>
                <Value>True</Value>
                <ValueType>Checkbox</ValueType>
                <ExcludeIdentical>True</ExcludeIdentical>
                <Persistent>Model</Persistent>
            </Parameter>


            <Parameter>
                <Name>BarraAmpleVert</Name>
                <Text>Ample</Text>
                <Value>30.</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraAlturaVert</Name>
                <Text>Altura</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaVert</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
                <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) and llargadaAutomatica == True</Visible>
            </Parameter>
            <Parameter>
                <Name>BarraLlargadaIndiv</Name>
                <Text>Alçada</Text>
                <Value>2600.0</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) and llargadaAutomatica == False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
            <Parameter>
                <Name>BarraGruixVert</Name>
                <Text>Gruix</Text>
                <Value>1.5</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PropertiesExpander</Name>
                <Text>Properties</Text>
                <value>True</value>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>IsUseGlobalPropVert</Name>
                    <Text>Use Global Propierties</Text>
                    <Value>False</Value>
                    <ValueType>Checkbox</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>FounColorVert</Name>
                    <Text>Color</Text>
                    <Value>23</Value>
                    <ValueType>Color</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")) and IsUseGlobalPropVert == False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

                <Parameter>
                    <Name>BarraLayerVert</Name>
                    <Text>Layer</Text>
                    <Value>40001</Value>
                    <ValueType>Layer</ValueType>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>IsUseGlobalPropVert == False and (SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."))</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>

            </Parameter>
        </Parameter>

    </Page>-->

    <!--Collisos i Potes Vert FALTA-->
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Colis</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->


            <Parameter>
                <Name>ColisVertListToShow</Name>
                <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
                <!-- <Value>[False|Sup|400.|150|12;
                        False|Sup|800.|150|12;
                        False|Sup|1200.|150|12;
                        False|Sup|1600.|150|12]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,,0</MinValue>
                <Visible>True, ColisVertListToShow[$list_row][0] == True, ColisVertListToShow[$list_row][0] == True, ColisVertListToShow[$list_row][0] == True, ColisVertListToShow[$list_row][0] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Potes</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>

            <Parameter>
                <Name>PotesVertListToShow</Name>
                <Text>Pota,Posicio,Separator</Text>
                <!-- <Text>Pota,Posicio</Text>-->
                <!-- <Value>[False|400.;
                    False|1200.;
                    False|2400.;
                    False|4600.]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,Length,Separator)</ValueType>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Pota,Posicio,Separator</FieldNames>
                </NamedTuple>
                <MinValue>,0,</MinValue>
                <ExcludeIdentical>True</ExcludeIdentical>
                <Visible>True, PotesVertListToShow[$list_row][0] == True,True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>
            <Visible>SelectorPPTD == 2</Visible>

            <Parameter>
                <Name>tipusCavitatTFFVert</Name>
                <Text>Tipus Cavitat TFF</Text>
                <Value>40</Value>
                <ValueList>40|60</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>False</Visible>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>

            <Parameter>
                <Name>ForatsVertListToShow</Name>
                <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,TFF,Profunditat TFF</Text>
                <!-- <Value>[False|Sup|200.|10|10|True|50|20|True|15;
                        False|Sup|400.|10|10|True|50|20|True|15;
                        False|Sup|600.|10|10|True|50|20|True|15;
                        False|Sup|800.|10|10|True|50|20|True|15;
                        False|Sup|1000.|10|10|True|50|20|True|15;
                        False|Sup|1200.|10|10|True|50|20|True|15;
                        False|Sup|1400.|10|10|True|50|20|True|15;
                        False|Sup|1600.|10|10|True|50|20|True|15;
                        False|Sup|1800.|10|10|True|50|20|True|15;
                        False|Sup|2000.|10|10|True|50|20|True|15]
                </Value>-->
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Length)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</FieldNames><!-- ,Separator-->
                </NamedTuple>
                <MinValue>,,0,,,,,,,,</MinValue>
                <Visible>True, ForatsVertListToShow[$list_row][0] == True, ForatsVertListToShow[$list_row][0] == True, ForatsVertListToShow[$list_row][0] == True, ForatsVertListToShow[$list_row][0] == True, ForatsVertListToShow[$list_row][0] == True,ForatsVertListToShow[$list_row][0] == True and ForatsVertListToShow[$list_row][5] == True,ForatsVertListToShow[$list_row][0] == True and ForatsVertListToShow[$list_row][5] == True, ForatsVertListToShow[$list_row][0] == True</Visible><!-- , ForatsVertListToShow[$list_row][0] == True and ForatsVertListToShow[$list_row][8] == True -->
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>


        <Parameter>
            <Name>DimensionsParameterExpander</Name>
            <Text>Forats</Text>
            <ValueType>Expander</ValueType>
            <Visible>SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs..."</Visible>

            <Parameter>
                <Name>tipusCavitatTFFHor</Name>
                <Text>Tipus Cavitat TFF</Text>
                <Value>40</Value>
                <ValueList>40|60</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>

            <Parameter>
                <Name>ForatsHorListToShow</Name>
                <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,TFF,Profunditat TFF</Text>
                <Value>[False|Sup|200|10|10|True|50|20|True|15;
                        False|Sup|400|10|10|True|50|20|True|15;
                        False|Sup|600|10|10|True|50|20|True|15;
                        False|Sup|800|10|10|True|50|20|True|15;
                        False|Sup|1000|10|10|True|50|20|True|15;
                        False|Sup|1200|10|10|True|50|20|True|15;
                        False|Sup|1400|10|10|True|50|20|True|15;
                        False|Sup|1600|10|10|True|50|20|True|15;
                        False|Sup|1800|10|10|True|50|20|True|15;
                        False|Sup|2000|10|10|True|50|20|True|15]
                </Value>
                <!-- <Value>[]</Value>-->
                <ValueType>namedtuple(CheckBox,StringComboBox,Length,Length,Length,CheckBox,Length,Length,CheckBox,Length)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>UShape</TypeName>
                    <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</FieldNames><!-- ,Separator-->
                </NamedTuple>
                <MinValue>,,0,,,,,,,</MinValue>
                <Visible>True, ForatsHorListToShow[$list_row][0] == True, ForatsHorListToShow[$list_row][0] == True, ForatsHorListToShow[$list_row][0] == True, ForatsHorListToShow[$list_row][0] == True, ForatsHorListToShow[$list_row][0] == True,ForatsHorListToShow[$list_row][0] == True and ForatsHorListToShow[$list_row][5] == True,ForatsHorListToShow[$list_row][0] == True and ForatsHorListToShow[$list_row][5] == True, ForatsHorListToShow[$list_row][0] == True, ForatsHorListToShow[$list_row][0] == True and ForatsHorListToShow[$list_row][8] == True</Visible>
                <Persistent>Model</Persistent>
            </Parameter>
        </Parameter>
    </Page>

    <!--FEMELLES Vert FALTA MATRIU FemellesVert-->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
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
                <Text>Separacio Forat Femella</Text>
                <Value>30</Value>
                <MinValue>0</MinValue>
                <ValueType>Length</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>FemellesExpanderVert</Name>
                <Text>Posicio femelles</Text>
                <ValueType>Expander</ValueType>
                <!-- FEMELLES-->
                <!-- ********************************************************************** -->
                <Parameter>
                    <Name>Separator</Name>
                    <ValueType>Separator</ValueType>
                </Parameter>

                <Parameter>
                    <Name>FemellesVertListToShow</Name>
                    <Text>Femella,Orientacio,Posicio X,Posicio Y, PosFemellaXOri,Separacio</Text>
                    <!-- <Value>[False|Esq|400|0|400;
                            False|Esq|800|0|800;
                            False|Esq|1200|0|1200]
                    </Value>-->
                    <Value>[]</Value>
                    <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length, Length,Separator)</ValueType>
                    <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
                    <NamedTuple>
                        <TypeName>StirrupList</TypeName>
                        <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,PosFemellaXOri,Separator</FieldNames>
                    </NamedTuple>
                    <MinValue>,,0,,</MinValue>
                    <ExcludeIdentical>True</ExcludeIdentical>
                    <Visible>True, FemellesVertListToShow[$list_row][0] == True, FemellesVertListToShow[$list_row][0] == True, FemellesVertListToShow[$list_row][0] == True, False, False</Visible>
                    <Persistent>Model</Persistent>
                </Parameter>



            </Parameter>
        </Parameter>
    </Page>

    <!--CANCANMS Vert PASSAT-->
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
        <!-- <Persistent>Model</Persistent> -->

        <Parameter>
            <Name>CancamsExpander</Name>
            <Text>Cancams</Text>
            <ValueType>Expander</ValueType>
            <ExcludeIdentical>True</ExcludeIdentical>
            <!-- <Persistent>Model</Persistent> -->

            <Parameter>
                <Name>posicio_centre_massesVert</Name>
                <Text>Posicio centre de masses</Text>
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
                    <Text>Distancia</Text>
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
                    <Text>Distancia</Text>
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
        <Visible>SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Mes Tubs...")</Visible>
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
            </Parameter>
            <Parameter>
                <Name>PestanyaInferiorVert</Name>
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

            <!-- llista que es mostra per pantalla -->
            <Parameter>
                <Name>EncaixVertListToShow</Name>
                <Text>Encaix ,Orientacio,Longitud,Amplitud,Posicio,Profunditat,Pestanya</Text>
                <Value>[]</Value>
                <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
                <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
                <NamedTuple>
                    <TypeName>StirrupList</TypeName>
                    <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
                </NamedTuple>
                <Visible>True, EncaixVertListToShow[$list_row][0] == True,EncaixVertListToShow[$list_row][0] == True,EncaixVertListToShow[$list_row][0] == True, EncaixVertListToShow[$list_row][0] == True, EncaixVertListToShow[$list_row][0] == True, EncaixVertListToShow[$list_row][0] == True</Visible>
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
            <Name>dadesTDVertTD</Name>
            <Text>Mostrar, BarraAmple, BarraAltura, LlargadaAut, BarraAlcada, BarraSuperior, BarraInferior, Gruix,
                EncaixSup, EncaixInf, FemellaSup, FemellaInf,
                Ample Forat Femella, Altura Forat Femella, Separacio Forat Femella,
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
                Pestanya Superior, Pestanya Inferior,
                esProvisional, esExtrem,
                MostrarRecess, MostrarCavitat,
                linia, layer, vermell,
                Color,
                esProvisionalAuto, esProvisionalAuto1, esProvisionalAuto2, esProvisionalAuto3, esProvisionalAuto4
            </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox, Length, Length, Checkbox, Length, String, String, Length,
                                Checkbox,Checkbox, Checkbox,Checkbox,
                                Length, Length, Length,
                                Length, Checkbox, Length , Checkbox, Length,
                                Checkbox, Checkbox,
                                Checkbox, Checkbox,
                                Checkbox, Checkbox,
                                String, String, Checkbox,
                                Color,
                                Checkbox, Checkbox, Checkbox, Checkbox, Checkbox)
            </ValueType>
            <ValueList>,,,,,'TD Superior',,,True,True,,,,,,,,,,,,,,,True,True,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>MostrarTDVertical, BarraAmple, BarraAltura, LlargadaAut, BarraAlcada, BarraSuperior, BarraInferior, Gruix,
                            EncaixSup, EncaixInf, FemellaSup, FemellaInf,
                            Ample_forat_femellaVert,Altura_forat_femellaVert,Separacio_forat_femellaVert,
                            posicio_centre_massesVert, IsFirstCancamVert, Dis1cancamVert, IsSecondCancamVert, Dis2cancamVert,
                            PestanyaSuperiorVert, PestanyaInferiorVert,esProvisional, esExtrem,
                            MostrarRecess, MostrarCavitat,
                            linia, layer, vermell,
                            FounColor,
                            esProvisionalAuto, esProvisionalAuto1, esProvisionalAuto2, esProvisionalAuto3, esProvisionalAuto4
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False</Visible>
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

        <!-- Llista de indexacio a la ColisVertList-->
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
            <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
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

        <!-- Llista de indexacio a la PotesVertList-->
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
            <Text>Pota,Posicio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType>
            <ValueList>,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <Visible>False, False</Visible>
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

        <!-- Llista de indexacio a la ForatsVertList-->
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
            <Name>ForatsVertList</Name>
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,LlargadaB,AmpladaB,TFF,ProfunditatTFF</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Length)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,,,15,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</FieldNames><!--,Separator-->
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False, False,False,False,False</Visible>
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

        <!-- Llista de indexacio a la FemellesVertList-->
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
            <Name>FemellesVertListTD</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y,PosFemellaXOri, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length, Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,PosFemellaXOri,Separator</FieldNames>
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

        <!-- Llista de indexacio a la EncaixVertList-->
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
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False, False, False</Visible>
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

        <!-- Llista de indexacio a la BarresHoritzontals-->
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
        <!-- valors Barra Horitzontal Intermitja-->
        <Parameter>
            <Name>dadesTDHortInter</Name>
            <Text>Ample, Altura, Llargada, Gruix,
                desplX, desplY,
                mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                se esta editant, acabat editar,
                Is Global Prop Vert, Color, Layer,
                Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
                PestanyaSup, PestanyaInf,
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
                                Checkbox, Checkbox,
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
                            PestanyaSup, PestanyaInf,
                            linia, layer, vermell
                </FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False,False,False,False,False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisHorInt</Name>
            <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesHorInt</Name>
            <Text>Pota,Posicio</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0,</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsHorInt</Name>
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Length)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorInt</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorIntAux</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorIntAuxInf</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesHorIntAuxSup</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixHorInt</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False</Visible>
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

        <!-- Llista de indexacio a la BarresVertitzontals-->
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
            <ValueType>namedtuple(Checkbox,Length,Length,Length,Checkbox,Length,StringComboBox,Checkbox, Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Checkbox,Separator)</ValueType>
            <ValueList>,,,,,,Inferior|Barra1|Barra2|Barra3,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>BarraVert,Posicio,PosicioAbs,PosicioZ,AutoLongitud,Longitud,BarraInici,EditFront, Edit,EncaixInf,EncaixSup,acabatEditar,editiantFrontals,PestanyaSup,PestanyaInf,FemellaSup, FemellaInf, Separator</FieldNames>
            </NamedTuple>
            <Visible> False,False, False, False,False, False,False,False,False,False,False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- valors Barra Vertitzontal Intermitja-->
        <Parameter>
            <Name>dadesTDVertInter</Name>
            <Text>se esta editant, acabat editar,
                BarraAmple, BarraAltura, BarraGruix,
                desplX, desplY, desplXAbs, desplYAbs,
                Is Global Prop Vert, Color, Layer,
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
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
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
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
            <Text>BarraFront,Ample,Altura,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType>
            <ValueList>,,,Esq|Dre,,,,,,,,</ValueList>
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
            <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesVertInt</Name>
            <Text>Pota,Posicio</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType>
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
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,MostrarBox,ProfunditatTFF</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Length)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</FieldNames><!-- ,Separator-->
            </NamedTuple>
            <Visible>False,False,False,False,False,False,False,False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesVertInt</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixVertInt</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False, False</Visible>
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
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
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
            <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesAdj</Name>
            <Text>Pota,Posicio</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0,</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsAdj</Name>
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,Box,Separator</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesAdj</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixAdj</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False, False</Visible>
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
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
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
            <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesFront</Name>
            <Text>Pota,Posicio</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0,</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsFront</Name>
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,MostrarBox,Separator</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesFront</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixFront</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>



    </Page>

    <Page>
        <Visible>False</Visible>
        <Parameter>
            <Name>DadesVertCopy</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Integer,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>nBarraGuardada,BarraAmple,BarraAltura,BarraLlargada,desplY,esProvisional,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False,False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsVertListCopy</Name>
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,TFF,ProfunditatTFF</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Checkbox,Length)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,MostrarBox,ProfunditatTFF</FieldNames><!-- ,Separator-->
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <!-- <Visible>False, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True, ForatsVertListCopy[$list_row][0] == True,ForatsVertListCopy[$list_row][0] == True and ForatsVertListCopy[$list_row][5] == True,ForatsVertListCopy[$list_row][0] == True and ForatsVertListCopy[$list_row][5] == True, ForatsVertListCopy[$list_row][0] == True,False</Visible>-->
            <Visible>False, False, False, False, False, False, False, False, False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>BarresFrontListCopy</Name>
            <Text>TIS,Ample,Forat,Orientacio,Posicio,Longitud,Profunditat,Edit,Save,acabatEditar</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length,Length,StringComboBox,Length,Length,Length,Checkbox,Checkbox,Checkbox)</ValueType>
            <ValueList>,,,Esq|Dre|Sup|Inf,,,,,,</ValueList>
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

        <!-- Llista de indexacio a la BarresRefitzontals-->
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


        <!-- valors Barra Refitzontal Intermitja-->
        <Parameter>
            <Name>dadesENReftInterTD</Name>
            <Text>Ample, Altura, Llargada, Gruix,
                desplX, desplY,
                mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
                se esta editant, acabat editar,
                Is Global Prop Vert, Color, Layer,
                Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
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
            <Visible>False, False, False, False, False, False, False,False,False,False,False,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False </Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Llista de Colis Interiors-->
        <Parameter>
            <Name>ColisRefInt</Name>
            <Text>Colis,Orientacio,Posicio,Llargada,Amplada</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Colis,orientacio,Posicio,Llargada,Amplada,Separator</FieldNames>
            </NamedTuple>
            <MinValue>,,0</MinValue>
            <Visible>False, False, False,False,False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>


        <Parameter>
            <Name>PotesRefInt</Name>
            <Text>Pota,Posicio</Text>
            <Value>[]
            </Value>
            <ValueType>namedtuple(Checkbox,Length)</ValueType>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Pota,Posicio</FieldNames>
            </NamedTuple>
            <MinValue>,0,</MinValue>
            <ExcludeIdentical>True</ExcludeIdentical>
            <Visible>False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>ForatsRefInt</Name>
            <Text>Forat,Orientacio,Posicio,Llargada,Amplada,Completa,Llargada,Amplada,Separator</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Checkbox,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,</ValueList>
            <NamedTuple>
                <TypeName>UShape</TypeName>
                <FieldNames>Forat,orientacio,Posicio,Llargada,Amplada,Complet,LlargadaB,AmpladaB,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False,False, False, False,False, False,False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefInt</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefIntAux</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefIntAuxInf</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>FemellesRefIntAuxSup</Name>
            <Text>Femella,Orientacio,Posicio X,Posicio Y, Separacio</Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Femella,FemellaOr,PosFemellaX,PosFemellaY,Separacio_forat_femella,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False ,False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>EncaixRefInt</Name>
            <Text> </Text>
            <Value>[]</Value>
            <ValueType>namedtuple(Checkbox,StringComboBox,Length,Length,Length,Length,Checkbox,Separator)</ValueType>
            <ValueList>,Esq|Dre|Sup|Inf,,,,,</ValueList>
            <NamedTuple>
                <TypeName>StirrupList</TypeName>
                <FieldNames>Encaix,EncaixOr,Longitud,Amplitud,Posicio,Profunditat,Pestanya,Separator</FieldNames>
            </NamedTuple>
            <Visible>False, False, False, False, False, False, False, False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

    <!-- valors Barra Inclinades-->
    <Parameter>
        <Name>dadesTDInclinades</Name>
        <Text>MostrarInclinat, nom,
            Ample, Altura, Llargada, Gruix,
            desplX, desplY,
            mostrarLiniaVertA,desplLinA,mostrarLiniaVertB,desplLinB,
            se esta editant, acabat editar,
            Is Global Prop Vert, Color, Layer,
            Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
            Posicio centre de masses, 1r cancam, Distancia, 2n cancam, Distancia,
            PestanyaSup, PestanyaInf,FemellaSup, FemellaInf,
            Posicio, Angle
        </Text>
        <Value>[]</Value>
        <ValueType>namedtuple(Checkbox,String,
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
            <FieldNames>MostrarInclinat,nom,
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
