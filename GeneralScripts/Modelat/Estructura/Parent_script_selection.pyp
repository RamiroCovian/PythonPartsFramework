<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Modelat\Estructura\Parent_Script_selection.py</Name>
        <Title>Python Part TD Parent Script</Title>
        <Version>27.0</Version>
        <ReadLastInput>True</ReadLastInput>
        <DataColumnWidth>150</DataColumnWidth>

    </Script>
    <!-- ************* DADES GENERALS *************-->
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector Fill</Text>
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
            <Enable>False</Enable>
            <Visible>False</Visible>
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
            <Value>1</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Persistent>Model</Persistent>
            <Enable>False</Enable>


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
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>
            <Parameter>
                <Name>EN</Name>
                <Text>EN</Text>
                <Value>3</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>
            <Parameter>
                <Name>IS</Name>
                <Text>IS</Text>
                <Value>4</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
            </Parameter>
            <Parameter>
                <Name>FS</Name>
                <Text>FS</Text>
                <Value>5</Value>
                <ValueType>RadioButton</ValueType>
                <Visible>FlagEntrada != 1</Visible>
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
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1</Visible>
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
            <Name>ButtonRowAdd</Name>
            <Text>Button</Text>
            <ValueType>Row</ValueType>
            <Visible>FlagEntrada != 1 and SelectorPPPare == 4</Visible>

            <Parameter>
                <Name>ButtonAddIS</Name>
                <Text>afegirIS</Text>
                <EventId>3000</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
            <Parameter>
                <Name>ButtonAddIS</Name>
                <Text>eliminarIS</Text>
                <EventId>3001</EventId>
                <ValueType>Button</ValueType>
                <Visible>False</Visible>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RecalculIS</Name>
            <Text>recalculIS</Text>
            <EventId>1000</EventId>
            <ValueType>Button</ValueType>
            <Visible> False</Visible>
        </Parameter>

        <Parameter>
            <Name>RecalculComplet</Name>
            <Text>recalcul Inici nou</Text>
            <EventId>3002</EventId>
            <ValueType>Button</ValueType>
            <Visible>True</Visible>
        </Parameter>

        <Parameter>
            <Name>NameFilesChildren</Name>
            <Text>NameFilesChildren</Text>
            <Value>[]</Value>
            <ValueType>String</ValueType>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1</Visible>
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
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
            <Visible>FlagEntrada != 1 and SelectorPPPare == 4</Visible>
        </Parameter>
        <Parameter>
            <Name>direccioISInv</Name>
            <Text>Direccio Invertida Total</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>direccioISInvActual</Name>
            <Text>Direccio IS Invertida IS Actual</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>FlagEntrada != 1 and SelectorPPPare == 4</Visible>
        </Parameter>

        <Parameter>
            <Name>SelectorSurt1</Name>
            <Text>Selctor quin surt 1</Text>
            <Value>Dre</Value>
            <ValueList>Esq|Dre|Inf|Sup</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>
        <Parameter>
            <Name>SelectorSurt2</Name>
            <Text>Selctor quin surt 2</Text>
            <Value>Sup</Value>
            <ValueList>Esq|Dre|Inf|Sup</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>



        <!--
        <Parameter>
            <Name>MiHijoPythonPart</Name>
            <Value>{8E5F3B8A-3AFD-4A0B-9B3C-725E7F3C216F}</Value>
            <ValueType>PythonPartReference</ValueType>
        </Parameter>
        -->

    </Page>
    <Page>
        <Name>__hiddenElem__</Name>
        <Text>__hiddenElem__</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>
        <Parameter>
            <Name>listDireccioISInv</Name>
            <Text></Text>
            <Value>[_]</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>$list_row</Visible>
        </Parameter>
        <Parameter>
            <Name>totalPeces</Name>
            <Text>Integer</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
        </Parameter>

        <Parameter>
            <Name>GeometryObjectList</Name>
            <Text>GeometryObjectList</Text>
            <Value>[]</Value>
            <ValueType>GeometryObject</ValueType>
        </Parameter>
    </Page>
    <!--
    <Page>
        <Parameter>
            <Name>FirstPalette</Name>
            <Text/>
            <Value>TD_Conjunt_8_2.incpyp</Value>
            <ValueType>Include</ValueType>
            <Visible>SelectorPPPare == 2</Visible>
        </Parameter>

        <Parameter>
            <Name>SecondPalette</Name>
            <Text/>
            <Value>EN_Conjunt_8_2.incpyp</Value>
            <ValueType>Include</ValueType>
            <Visible>SelectorPPPare == 3</Visible>
        </Parameter>

        <Parameter>
            <Name>thirdPalette</Name>
            <Text/>
            <Value>IS_Conjunt_8_2.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    -->
    <!-- #TD -->
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector</Text>
        <Visible>SelectorPPPare == 2</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_1.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>

    <Page>
        <Name>PP TD Horitzontal</Name>
        <Text>Desplaçament Horitzontal</Text>
        <Visible>SelectorPPPare == 2 and (SelectorPPTD == 1 or SelectorPPTD == 2 or SelectorPPTD == 4)</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_2.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPPare == 2 and (SelectorPPTD == 1 or (SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Més Tubs...")) or SelectorPPTD == 4)</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_3.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <!-- -->
    <Page>
    <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>SelectorPPPare == 2 and (SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior')</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_4.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>SelectorPPPare == 2 and (SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior')</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_5.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>SelectorPPPare == 2 and (SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior')</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_6.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>(SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior') and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_7.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>(SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior') and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_8.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>(SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior') and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_9.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <Visible>(SelectorPPTD == 1 and SelectorTDHTD == 'TD Inferior') and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_10.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <Visible>(SelectorPPTD == 1 and SelectorTDHTD == 'TD Superior') and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_11.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <!-- -->
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Més Tubs...")) and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_12.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <!-- -->
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Més Tubs...")) and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_13.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Més Tubs...")) and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_14.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>EncaixVert</Name>
        <Text>Encaix</Text>
        <Visible>(SelectorPPTD == 2 or (SelectorPPTD == 1 and SelectorTDHTD == "Més Tubs...")) and SelectorPPPare == 2 </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_15.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>__HiddenPage__</Name>
        <Text></Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_16.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name></Name>
        <Text></Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\TD\PYP\TD_Conjunt_8_17.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <!-- -->
    <!-- #EN -->
    <Page>
        <Name>SelectorPythonPartEN</Name>
        <Text>Selector(EN)</Text>
        <Visible>SelectorPPPare == 3</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_1.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>PP EN Horitzontal</Name>
        <Text>Desplaçament Horitzontal</Text>
        <Visible>SelectorPPPare == 3 and (SelectorPPEN == 1 or SelectorPPEN == 2 or SelectorPPEN == 4 or SelectorPPEN == 5)</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_2.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>(SelectorPPEN == 1 or SelectorPPEN == 2 or SelectorPPEN == 4 or SelectorPPEN == 5) and SelectorPPPare == 3</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_3.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_4.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>CollisosPotes</Name>
        <Text>Collisos i Potes</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_5.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_6.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_7.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>False </Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_8.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_9.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <Visible>((SelectorPPEN == 1 and SelectorENH == 'EN Inferior' and TubInferior == "L") or (SelectorPPEN == 5 and TubInferior == "L")) and SelectorPPPare == 3</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_10.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_11.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Forats</Name>
        <Text>Forats</Text>
        <Visible>(SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Més Tubs...") )and SelectorPPPare == 3</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_12.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Visible>(SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Més Tubs...") ) and SelectorPPPare == 3</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_13.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>Cancams</Name>
        <Text>Cancams</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_14.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>EncaixVert</Name>
        <Text>Encaix</Text>
        <Visible>(SelectorPPEN == 2 or (SelectorPPEN == 1 and SelectorENH == "Més Tubs...")) and SelectorPPPare == 3</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_15.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>__HiddenPage__</Name>
        <Text></Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_16.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>
    <Page>
        <Name>EN</Name>
        <Text>EN</Text>
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\EN\PYP\EN_Conjunt_8_17.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>
    </Page>

    <!-- #IS-->
    <!-- ************* DADES GENERALS *************-->
    <Page>
        <Name>SelectorPythonPartIS</Name>
        <Text>Selector Child</Text>
        <Visible>SelectorPPPare == 4</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\IS\PYP\IS_Conjunt_8_31.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Visible>SelectorPPPare == 4 and SelectorPPIS == 1</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\IS\PYP\IS_Conjunt_8_32.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>
    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <!-- <Visible>SelectorPPPare == 4 </Visible>-->
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\IS\PYP\IS_Conjunt_8_33.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>
    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>
        <!-- <Visible>SelectorPPPare == 4</Visible>-->
        <Visible>False</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\IS\PYP\IS_Conjunt_8_34.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>
    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <!-- <Visible>SelectorPPPare == 4</Visible> -->
        <Visible>False</Visible>
        <Persistent>Model</Persistent>
        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\IS\PYP\IS_Conjunt_8_35.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>SelectorPythonPartFS</Name>
        <Text>Selector FS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>CavidadesPythonPartFS</Name>
        <Text>Selector cavidades FS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8_cavidades_manuales.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>GIRS FS</Name>
        <Text>GIRS FS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8_inclinacion_rotacion.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>ModelizacionXPS</Name>
        <Text>Modelizacion XPS</Text>
        <Visible>SelectorPPPare == 5</Visible>
        <Persistent>Model</Persistent>

        <Parameter>
            <Name></Name>
            <Text/>
            <Value>\FS\PYP\FS_Conjunt_8_modelizacion_xps.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

</Element>
