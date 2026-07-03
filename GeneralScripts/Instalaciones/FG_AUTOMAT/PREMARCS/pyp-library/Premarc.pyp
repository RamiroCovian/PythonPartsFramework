<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\FG_AUTOMAT\PREMARCS\pyp-scripts\Premarc.py</Name>
        <!-- <Name>PP\PREMARCS_improve\pyp-scripts\Premarc.py</Name> -->
        <Title>Superficie Zona XPS</Title>
        <Version>1.0</Version>
        <!-- <ReadLastInput>True</ReadLastInput> -->
        <Interactor>False</Interactor>
    </Script>

    <Page>
        <Name>ZoneProperties</Name>
        <Text>Propiedades de la Zona</Text>

        <Parameter>
            <Name>z_unique</Name>
            <Text>z_unique</Text>
            <Value>0</Value>
            <ValueType>Integer</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>ShowSessionControls</Name>
            <Text>ShowSessionControls</Text>
            <Value>True</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>ShowModificationControls</Name>
            <Text>ShowModificationControls</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Visible>False</Visible>
        </Parameter>

        <Parameter>
            <Name>DisableTopXPS</Name>
            <Text>Deshabilitar XPS superior</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableBottomXPS</Name>
            <Text>Deshabilitar XPS inferior</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableLeftXPS</Name>
            <Text>Deshabilitar XPS izquierda</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableRightXPS</Name>
            <Text>Deshabilitar XPS derecha</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>NextPremarcPlacementRow</Name>
            <Text>Colocación</Text>
            <ValueType>Row</ValueType>
            <Visible>ShowSessionControls</Visible>

            <Parameter>
                <Name>NextPremarcPlacement</Name>
                <Text>Posicionar otro premarco</Text>
                <EventId>1001</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>RowSeleccionPremarc</Name>
            <Text>Edición</Text>
            <ValueType>Row</ValueType>
            <Visible>ShowSessionControls</Visible>

            <Parameter>
                <Name>SeleccionarPremarc</Name>
                <Text>Seleccionar</Text>
                <EventId>1055</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
                <Enable>True</Enable>
                <Persistent>No</Persistent>
            </Parameter>

            <Parameter>
                <Name>DeseleccionarPremarc</Name>
                <Text>Deseleccionar</Text>
                <EventId>1056</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
                <Enable>True</Enable>
                <Persistent>No</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>RowEliminarPremarcSesion</Name>
            <Text>Eliminar premarco</Text>
            <ValueType>Row</ValueType>
            <Visible>ShowSessionControls</Visible>

            <Parameter>
                <Name>EliminarPremarcSesion</Name>
                <Text>Eliminar</Text>
                <EventId>1003</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
                <Enable>True</Enable>
                <Persistent>No</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>RowReubicarPremarc</Name>
            <Text>Reubicar premarco</Text>
            <ValueType>Row</ValueType>

            <Parameter>
                <Name>ReubicarPremarc</Name>
                <Text>Mover posición</Text>
                <EventId>1002</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
                <Enable>True</Enable>
                <Persistent>No</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>RowEliminarPremarc</Name>
            <Text>Eliminar premarco</Text>
            <ValueType>Row</ValueType>
            <Visible>ShowModificationControls</Visible>

            <Parameter>
                <Name>EliminarPremarc</Name>
                <Text>Eliminar</Text>
                <EventId>1003</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
                <Enable>True</Enable>
                <Persistent>No</Persistent>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>medidas</Name>
            <Text>Medidas (mm)</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>XPSthickness</Name>
                <Text>Grosor</Text>
                <Value>295</Value>
                <ValueList>120|100|80|60</ValueList>
                <ValueType>IntegerComboBox</ValueType>
                <Visible>XPSthicknessInd</Visible>
            </Parameter>

            <Parameter>
                <Name>heigh</Name>
                <Text>Alto</Text>
                <Value>1410</Value>
                <ValueType>Double</ValueType>
                <Visible>True</Visible>
            </Parameter>

            <Parameter>
                <Name>width</Name>
                <Text>Ancho</Text>
                <Value>1200</Value>
                <ValueType>Double</ValueType>
                <Visible>True</Visible>
            </Parameter>

            <Parameter>
                <Name>thickness</Name>
                <Text>Fondo</Text>
                <Value>295</Value>
                <ValueList>[str(value) for value in valueListaGrosor] if valueListaGrosor else []</ValueList>
                <ValueType>IntegerComboBox</ValueType>
                <Visible>not(enable_manual_thickness)</Visible>
            </Parameter>

            <!-- Enable manual thickness -->
            <Parameter>
                <Name>enable_manual_thickness</Name>
                <Text>Habilitar fondo manual</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>manual_thickness</Name>
                <Text>Fondo manual Premarco</Text>
                <Value>295</Value>
                <ValueType>Double</ValueType>
                <Visible>enable_manual_thickness</Visible>
                <MinValue>thickness_wall</MinValue>
            </Parameter>

            <Parameter>
                <Name>color_manual_thickness_visible</Name>
                <Text>Color fondo manual visible</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>color_manual_thickness</Name>
                <Text>Color fondo manual</Text>
                <Value>-1</Value>
                <ValueType>Color</ValueType>
                <Visible>color_manual_thickness_visible</Visible>
            </Parameter>
            <!-- End manual color -->

            <Parameter>
                <Name>thickness_wall</Name>
                <Text>Grosor pared</Text>
                <Value>160</Value>
                <ValueType>Double</ValueType>
            </Parameter>

            <Parameter>
                <Name>ButtonWallSelection</Name>
                <Text>Volver seleccionar muro</Text>
                <ValueType>Row</ValueType>

                <Parameter>
                    <Name>Button</Name>
                    <Text>Reset</Text>
                    <EventId>1000</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>

            <Parameter>
                <Name>SelectionWall</Name>
                <Text>Estado selección muro</Text>
                <Value>No seleccionado</Value>
                <ValueType>String</ValueType>
            </Parameter>
            <!-- persistent Model -->
            <Parameter>
                <Name>opening_guid</Name>
                <Text>opening_guid</Text>
                <Value></Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>niche_guid</Name>
                <Text>opening_guid</Text>
                <Value></Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>valueListaGrosor</Name>
                <Text>Lista dinámica Grosor</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>SelectionWall</Name>
                <Text>Muro</Text>
                <Value>No seleccionado</Value>
                <ValueType>String</ValueType>
                <Enable>False</Enable>
            </Parameter>

            <Parameter>
                <Name>rotation</Name>
                <Text>Rotación</Text>
                <Value>0.0</Value>
                <ValueType>Double</ValueType>
            </Parameter>


            <Parameter>
                <Name>id_premarc</Name>
                <Text>ID Premarc</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>wall_id</Name>
                <Text>Wall ID</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>modificaciones</Name>
            <Text>Modificaciones Extra</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>premarc_PE</Name>
                <Text>(PE) Premarc Porta d’Entrada</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>ShowAccessorUPerimeter</Name>
                <Text>Accesorio perfil U (solo inferior del premarco)</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>ComboBoxUChannelYAnchor</Name>
                <Text>Perfil U: cara del llindar rosa (back = vora finestra/azul; front = vora
                    contrària)</Text>
                <Value>pit_span_from_outer_lip</Value>
                <ValueList>
                    pit_span_from_outer_lip|pit_into_opening|pit_inward|pit_outer_face|half_embed</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>False</Visible>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>configuraciones</Name>
            <Text>Config - Abierto/Cerrado</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaAbiertoCerrado</Name>
                <Text>Listadinamica</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>ComboBoxAbiertoCerrado</Name>
                <Text>Abierto/Cerrado</Text>
                <Value>Cerrado</Value>
                <ValueList>[str(value) for value in valueListaAbiertoCerrado]</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>ComboBoxREAEspecial</Name>
                <Text>REA especial</Text>
                <Value>REAs en L (Estandar)</Value>
                <ValueList>REAs en C|REAs en L (Estandar)|REAs en L 340|REAs en L 450|REAs en L dinamica</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>ComboBoxAbiertoCerrado != "TANCAT" and "+ REA" not in ComboBoxAbiertoCerrado</Visible>
            </Parameter>

            <Parameter>
                <Name>LongitudREAEspecialLDinamica</Name>
                <Text>Sobresaliente REA L</Text>
                <Value>280</Value>
                <ValueType>Double</ValueType>
                <Visible>ComboBoxAbiertoCerrado != "TANCAT" and "+ REA" not in ComboBoxAbiertoCerrado and ComboBoxREAEspecial == "REAs en L dinamica"</Visible>
            </Parameter>


            <Parameter>
                <Name>EnableRetallGanxo</Name>
                <Text>Habilitar Retall Ganxo</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>Z_RetallGanxo</Name>
                <Text>Altura Ganxo (Desde arriba)</Text>
                <Value>100</Value>
                <ValueType>Double</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ConfigPendiente</Name>
            <Text>Config - Pendiente</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaPendiente</Name>
                <Text>Listadinamica</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>ComboBoxPendiente</Name>
                <Text>Pendiente</Text>
                <Value>Pendiente</Value>
                <ValueList>[str(value) for value in valueListaPendiente]</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Enable>EnablePendiente</Enable>
            </Parameter>

            <Parameter>
                <Name>EnablePendiente</Name>
                <Text>Habilitar Pendiente</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <!-- <Parameter>
                <Name>ImportPendent</Name>
                <Text>Import file</Text>
                <Value>0</Value>
                <ValueType>RadioButtonGroup</ValueType>

                <Parameter>
                    <Name>ImportPendentSelection</Name>
                    <Text>Import</Text>
                    <Value>[_]</Value>
                    <ValueType>namedtuple(DisplayText,RadioButton)</ValueType>
                    <NamedTuple>
                        <TypeName>ImportPendentSelection</TypeName>
                        <FieldNames>RowText,FileSelection</FieldNames>
                    </NamedTuple>
                </Parameter>
            </Parameter> -->
        </Parameter>

        <Parameter>
            <Name>ConfigFalcas</Name>
            <Text>Config - Falcas</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaPassama</Name>
                <Text>Lista dinámica Passama</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>PassamaOptions</Name>
                <Text>Opciones Passama</Text>
                <TextDyn>valueListaPassama[$list_row] if valueListaPassama and len(valueListaPassama) > $list_row else ""</TextDyn>
                <Value>[False, False, False, False, False]</Value>
                <ValueType>CheckBox</ValueType>
                <Dimensions>len(valueListaPassama) if valueListaPassama else 0</Dimensions>
                <ValueListStartRow>1</ValueListStartRow>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ConfigEncajes</Name>
            <Text>Config - Encajes</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaEncajes</Name>
                <Text>Listadinamica</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>ComboBoxEncajes</Name>
                <Text>Encajes</Text>
                <Value>Encajes</Value>
                <ValueList>[str(value) for value in valueListaEncajes]</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Visible>not(EnableManualEncaje)</Visible>
                <Enable>EnableEncajes</Enable>
            </Parameter>

            <Parameter>
                <Name>EnableEncajes</Name>
                <Text>Habilitar Escuadras</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>EnableManualEncaje</Name>
                <Text>Medidas manuales</Text>
                <Value>0</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>


            <Parameter>
                <Name>EncajeBase</Name>
                <Text>Base</Text>
                <Value>70</Value>
                <ValueType>Double</ValueType>
                <Visible>EnableManualEncaje</Visible>
            </Parameter>

            <Parameter>
                <Name>EncajeAltura</Name>
                <Text>Altura</Text>
                <Value>30</Value>
                <ValueType>Double</ValueType>
                <Visible>EnableManualEncaje</Visible>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>ConfigRebajes</Name>
            <Text>Config - Rebajes</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaRebajes</Name>
                <Text>Lista dinámica Rebajes</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>RebajesOptions</Name>
                <Text>Opciones Rebajes</Text>
                <TextDyn>valueListaRebajes[$list_row] if valueListaRebajes and len(valueListaRebajes) > $list_row else ""</TextDyn>
                <Value>[False, False, False, False, False, False, False]</Value>
                <ValueType>CheckBox</ValueType>
                <Dimensions>len(valueListaRebajes) if valueListaRebajes else 0</Dimensions>
                <ValueListStartRow>1</ValueListStartRow>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>ConfigPersianas</Name>
            <Text>Config - Persianas</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaPersianas</Name>
                <Text>Listadinamica</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>ComboBoxPersianas</Name>
                <Text>Persianas</Text>
                <Value>Persianas</Value>
                <ValueList>[str(value) for value in valueListaPersianas]</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Enable>EnablePersianas</Enable>
            </Parameter>

            <Parameter>
                <Name>EnablePersianas</Name>
                <Text>Habilitar Persianas</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>PersianaHeight</Name>
                <Text>Altura Persianas</Text>
                <Value>260</Value>
                <ValueType>Double</ValueType>
                <Persistent>Model</Persistent>
            </Parameter>

            <Parameter>
                <Name>PersianaWidth</Name>
                <Text>Grosor Persianas</Text>
                <Value>136</Value>
                <ValueType>Double</ValueType>
                <Enable>ComboBoxPersianas != "LAMISOL VIST"</Enable>
                <MaxValue>(manual_thickness if enable_manual_thickness else thickness) - thickness_wall if ComboBoxPersianas == "METALUNIC VIST" else 100000</MaxValue>
                <Persistent>Model</Persistent>
            </Parameter>


        </Parameter>

        <Parameter>
            <Name>ConfigEscuadras</Name>
            <Text>Config - Escuadras</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaEscuadras</Name>
                <Text>Listadinamica</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>ComboBoxEscuadras</Name>
                <Text>Escuadras</Text>
                <Value>Escuadras</Value>
                <ValueList>[str(value) for value in valueListaEscuadras]</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>ConfigTubos</Name>
            <Text>Config - Tubos</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>valueListaTubos</Name>
                <Text>Listadinamica</Text>
                <Value>[]</Value>
                <ValueType>String</ValueType>
                <Visible>False</Visible>
            </Parameter>

            <Parameter>
                <Name>ComboBoxTubos</Name>
                <Text>Tubos</Text>
                <Value>Tubos</Value>
                <ValueList>[str(value) for value in valueListaTubos]</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>TypeTubos</Name>
                <Text>Tipo de Tubo</Text>
                <Value>FABRICA</Value>
                <ValueList>OBRA|FABRICA</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>PositionTubos</Name>
                <Text>Posicionamiento</Text>
                <Value>CENTER</Value>
                <ValueList>CENTER|OFFSET</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>OffsetTubos</Name>
                <Text>Desplazamiento</Text>
                <Value>0</Value>
                <ValueType>Double</ValueType>
                <Visible>PositionTubos == "OFFSET"</Visible>
                <MaxValue>thickness</MaxValue>
            </Parameter>

        </Parameter>

        <Parameter>
            <Name>ConfigSpace</Name>
            <Text>Config - Espacios</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>CheckBoxRealSpace</Name>
                <Text>Real</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>CheckBoxInnerSpace</Name>
                <Text>Dentro</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

        </Parameter>


        <!-- Datos persistentes para modo modificación -->
        <Parameter>
            <Name>PlacementPnt</Name>
            <Text>Punto de Colocación</Text>
            <Value>Point3D(0,0,0)</Value>
            <ValueType>Point3D</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SavedState</Name>
            <Text>SavedState</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>

        <Parameter>
            <Name>PlacementPntY</Name>
            <Text>Punto de Colocación Y</Text>
            <Value>0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>PlacementPntZ</Name>
            <Text>Punto de Colocación Z</Text>
            <Value>0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <Parameter>
            <Name>SavedWallThickness</Name>
            <Text>Grosor de Muro Guardado</Text>
            <Value>0</Value>
            <ValueType>Double</ValueType>
            <Visible>False</Visible>
            <Persistent>Model</Persistent>
        </Parameter>

        <!-- Atributs Premarcs -->
        <Parameter>
            <Name>AtributsExpander</Name>
            <Text>Atributs Premarcs</Text>
            <ValueType>Expander</ValueType>
            <Value>False</Value>
            <Visible>True</Visible>

            <Parameter>
                <Name>INPUT_PMP_ID_PREMARC</Name>
                <Text>PMP_ID_PREMARC</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>INPUT_PMP_PREMARC_LABELS</Name>
                <Text>PMP_PREMARC_LABELS</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>ComboBoxDEN</Name>
                <Text>DEN</Text>
                <Value>XBANDERA</Value>
                <ValueList>XVENTANA|XBANDERA</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

        </Parameter>


    </Page>

    <Page>
        <Name>AmpitsProperties</Name>
        <Text>Ampits</Text>

        <Parameter>
            <Name>ampits</Name>
            <Text>Ampits</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>EnableAmpit</Name>
                <Text>Mostrar Ampit</Text>
                <Value>1</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>fondo_ampits</Name>
                <Text>Fondo Ampits</Text>
                <Value>330</Value>
                <ValueType>Double</ValueType>
                <Enable>EnableAmpit</Enable>
            </Parameter>

            <Parameter>
                <Name>llarg_ampits</Name>
                <Text>Llarg Ampits</Text>
                <Value>1000</Value>
                <ValueType>Double</ValueType>
                <Enable>EnableAmpit</Enable>
            </Parameter>

            <Parameter>
                <Name>afegit_ampits</Name>
                <Text>Afegit Ampits</Text>
                <Value>0</Value>
                <ValueType>Double</ValueType>
                <Enable>EnableAmpit</Enable>
            </Parameter>

            <Parameter>
                <Name>retall_ampits</Name>
                <Text>Retall Ampits</Text>
                <Value>0</Value>
                <ValueType>Double</ValueType>
                <Enable>EnableAmpit</Enable>
            </Parameter>

            <Parameter>
                <Name>ampit_material</Name>
                <Text>Ampit Material</Text>
                <Value>CERAMIC</Value>
                <ValueList>CERAMIC|CERAMICA_MAYOR|XAPA|PAVIMENTO</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>ampit_muntatge</Name>
                <Text>Ampit Muntatge</Text>
                <Value>OBRA</Value>
                <ValueList>OBRA|FABRICA</ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>ampit_parts</Name>
                <Text>ID Fusteria (PARTS)</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>ampit_ref_1</Name>
                <Text>ID Premarc (REF_1)</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>

            <Parameter>
                <Name>is_puerta_entrada</Name>
                <Text>Premarco Puerta Entrada</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>
    </Page>

    <Page>
        <Name>ImpermeabilizacionesProperties</Name>
        <Text>Impermeabilizaciones</Text>

        <Parameter>
            <Name>impermeabilizaciones</Name>
            <Text>Impermeabilizaciones</Text>
            <Value>False</Value>
            <ValueType>Expander</ValueType>
            <Visible>True</Visible>

            <Parameter>
                <Name>EnableImpermeabilizacio</Name>
                <Text>Mostrar Impermeabilización</Text>
                <Value>1</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>imperm_type</Name>
                <Text>Tipus Impermeabilització</Text>
                <Value>Water-Stop</Value>
                <ValueList>Water-Stop|PVC|Tela Asfàltica</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Enable>EnableImpermeabilizacio</Enable>
            </Parameter>

            <Parameter>
                <Name>EnableImpermPliegue90</Name>
                <Text>Pliegue a 90°</Text>
                <Value>0</Value>
                <ValueType>CheckBox</ValueType>
                <Enable>EnableImpermeabilizacio</Enable>
            </Parameter>

            <Parameter>
                <Name>imperm_muntatge</Name>
                <Text>Imperm. Muntatge</Text>
                <Value>OBRA</Value>
                <ValueList>OBRA|FABRICA</ValueList>
                <ValueType>StringComboBox</ValueType>
                <Enable>EnableImpermeabilizacio</Enable>
            </Parameter>
        </Parameter>
    </Page>

    <Page>
        <Name>XPS_zone</Name>
        <Text>Propiedades XPS </Text>

        <Parameter>
            <Name>xps_type</Name>
            <Text>Type</Text>
            <Value>XPS</Value>
            <ValueList>XPS|PIR</ValueList>
            <ValueType>StringComboBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>XPSthicknessInd</Name>
            <Text>XPS gruix manual</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>ShowXPS</Name>
            <Text>Mostrar XPS completa</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableTopXPS</Name>
            <Text>Deshabilitar XPS superior</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableBottomXPS</Name>
            <Text>Deshabilitar XPS inferior</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableLeftXPS</Name>
            <Text>Deshabilitar XPS izquierda</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>DisableRightXPS</Name>
            <Text>Deshabilitar XPS derecha</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

    </Page>

    <Page>
        <Name>__HiddenPage__</Name>
        <Text></Text>
        <Parameter>
            <Name>PlacementPnt</Name>
            <Text>Punto de Colocación</Text>
            <Value></Value>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>

    </Page>

</Element>
