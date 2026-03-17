<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>PMP\jerarquia\TD_Conjunt_8_Parent_Script copy.py</Name>
        <Title>Python Part TD Parent</Title>
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
            <Visible>True</Visible>
            <Enable>False</Enable>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- #include TD_COnjunt_8_Parent_copy.pyp;-->

        <Parameter>
            <Name>SelectorPPPare</Name>
            <Text>Selecciona PP per editar</Text>
            <Value>4</Value>
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
    <Page>
        <!--
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
        -->
    </Page>
    <!-- ************* DADES GENERALS *************-->

    <!--
    <Page>
        <Name>SelectorPythonPartTD</Name>
        <Text>Selector Child</Text>

        <Parameter>
            <Name>thirdPalette1</Name>
            <Text/>
            <Value>IS_Conjunt_8_31.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>

        <Parameter>
            <Name>thirdPalette2</Name>
            <Text/>
            <Value>IS_Conjunt_8_32.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>Femelles</Name>
        <Text>Femelles</Text>
        <Parameter>
            <Name>thirdPalette3</Name>
            <Text/>
            <Value>IS_Conjunt_8_33.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>Encaix</Name>
        <Text>Encaix</Text>

        <Parameter>
            <Name>thirdPalette4</Name>
            <Text/>
            <Value>IS_Conjunt_8_34.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>mesuresbarra</Name>
        <Text>Mesures Barra</Text>
        <Parameter>
            <Name>thirdPalette5</Name>
            <Text/>
            <Value>IS_Conjunt_8_35.incpyp</Value>
            <ValueType>Include</ValueType>
        </Parameter>

    </Page>-->


</Element>
