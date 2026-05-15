<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>Instalaciones\Agua\pyp-scripts\agua_polyline.py</Name>
        <Title>Polyline MVP</Title>
        <Version>1.0.0</Version>
        <Interactor>False</Interactor>
    </Script>
    <!-- ══════════════════════════════════════════
         PAGE 1: Polilinea — Instalacion + dibujo + optimizacion condicional
    ══════════════════════════════════════════ -->
    <Page>
        <Name>CrearPolilinea</Name>
        <Text>Polilinea</Text>
        <!-- ── Instalación ──────────────────────── -->
        <!-- ── Tipo de polilinea (controla visibilidad de Optimizacion) ── -->
        <Parameter>
            <Name>PointModeTitle</Name>
            <Text>Polilinea</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>InstallationName</Name>
                <Text>Instalacion</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
            <Parameter>
                <Name>PolyMode</Name>
                <Text>Vista</Text>
                <Value>0</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>ManualPolyline</Name>
                    <Text>Manual</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>AutoPolyline</Name>
                    <Text>Optimizacion</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>InstallationTypeTitle</Name>
            <Text>Tipos de instalacion</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>SupportedAngles</Name>
                <Text>Angulos Soportados</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
            <Parameter>
                <Name>InstallationType</Name>
                <Text>Elegir instalacion</Text>
                <Value></Value>
                <ValueList></ValueList>
                <EventId>1002</EventId>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowCambiarTipo</Name>
                <Text>Cambiar tipo</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>CambiarTipoInstalacion</Name>
                    <Text>Cambiar tipo instalacion</Text>
                    <EventId>1045</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>DiameterType</Name>
                <Text>Diámetro a aplicar</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>IntegerComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>DiameterTypeStr</Name>
                <Text>Diámetro a aplicar</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowDiameterModify</Name>
                <Text>Modificar</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>DiameterModify</Name>
                    <Text>Modificar diámetro</Text>
                    <EventId>1007</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>FunctionalName</Name>
                <Text>Nombre PythonPartGroup</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
            <Parameter>
                <Name>DistributionType</Name>
                <Text>Tipo de Distribucion</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>WaterType</Name>
                <Text>Tipo de Agua</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <Name>FaceEN</Name>
                <Text>Cara (EN)</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
        </Parameter>
        <!-- ════════════════════════════════════════
        SECCIÓN OPTIMIZADOR  (visible solo cuando PolyMode == 1)
        ════════════════════════════════════════ -->
        <Parameter>
            <Name>SelectorElementos</Name>
            <Text>Selector de elementos</Text>
            <ValueType>Expander</ValueType>
            <Visible>PolyMode == 1</Visible>
            <Parameter>
                <Name>ModoSelectorElemento</Name>
                <Text>Modo</Text>
                <Value>0</Value>
                <EventId>1044</EventId>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>ModoSelectorDesactivado</Name>
                    <Text>Desactivado</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ModoSelectorInsertar</Name>
                    <Text>Activar selector</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>OrdenPuntosUsuario</Name>
            <Text>Puntos no definidos</Text>
            <ValueType>Expander</ValueType>
            <Visible>PolyMode == 1</Visible>
            <Parameter>
                <Name>ModoNodosOptimizador</Name>
                <Text>Modo</Text>
                <Value>0</Value>
                <EventId>1044</EventId>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>ModoNodosDesactivado</Name>
                    <Text>Desactivado</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ModoNodosInsertar</Name>
                    <Text>Insertar</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ModoNodosEditar</Name>
                    <Text>Editar / Borrar</Text>
                    <Value>2</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>SeparatorOrdenPuntos2</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowTipoPuntoOrden</Name>
                <Text>Tipo de punto</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>TipoPuntoOrden</Name>
                    <Text>Tipo de punto</Text>
                    <Value>Inicial</Value>
                    <ValueType>StringComboBox</ValueType>
                    <ValueList>Inicial|Paso_Libre|Bifurcacion_Obligado|Final</ValueList>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>SeparatorOrdenPuntos3</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowColorPuntos</Name>
                <Text>Caminos</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>ColorPuntosNoDefinidos</Name>
                    <Text>Color (distinguir caminos)</Text>
                    <Value>Negro</Value>
                    <ValueType>StringComboBox</ValueType>
                    <ValueList>Negro|Amarillo|Cyan|Verde|Magenta|Rojo|Azul</ValueList>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowDeteccionPuntosComunes</Name>
                <Text>Puntos comunes</Text>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>DeteccionPuntosComunesActiva</Name>
                    <Text>Detectar puntos comunes</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ToleranciaPuntosComunesMm</Name>
                    <Text>Tolerancia (mm)</Text>
                    <Value>5</Value>
                    <ValueType>Length</ValueType>
                </Parameter>
                <Parameter>
                    <Name>ColorResaltadoPuntosComunes</Name>
                    <Text>Color resaltado</Text>
                    <Value>Rojo</Value>
                    <ValueType>StringComboBox</ValueType>
                    <ValueList>Negro|Amarillo|Verde|Cyan|Magenta|Rojo|Azul</ValueList>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>SeparatorOrdenPuntos4</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
            <Parameter>
                <Name>RowLimpiarPuntos</Name>
                <Text>Borrar</Text>
                <ValueType>Row</ValueType>
                <Visible>PolyMode == 1</Visible>
                <Parameter>
                    <Name>LimpiarPuntosNoDefinidos</Name>
                    <Text>Borrar puntos</Text>
                    <EventId>1042</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowBtnOptimizar</Name>
                <Text>Optimizar</Text>
                <ValueType>Row</ValueType>
                <Visible>PolyMode == 1</Visible>
                <Parameter>
                    <Name>GenerarCaminoOptimo</Name>
                    <Text>Generar Camino Óptimo</Text>
                    <EventId>1041</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <!-- ── Modos de dibujo ──────────────────── -->
        <Parameter>
            <Name>PointModeTitleDraw</Name>
            <Text>Modos de dibujo</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>PointModeInfoRow</Name>
                <Text>Información</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>InfoPicture</Name>
                    <Text>
                        Modos de dibujo (Ayuda):

                        • EDICION
                            Permite estirar la polilinea desde sus vértices
                            y agregar puntos o cortes en los segmentos.
                            El CheckBox "Insertar punto / Corte" solo se habilita en este modo.

                        • CONFIGURACION
                            Permite seleccionar tubos, codos, uniones, bifurcaciones, etc,
                            para aplicar layers y atributos personalizados.
                            También permite eliminar uno o más segmentos mediante selección múltiple.

                        • CREACION - EXTENDER
                            Permite dibujar y extender la polilinea.
                    </Text>
                    <Value>AllplanSettings.PictResPalette.eHotinfo</Value>
                    <!-- ID del recurso de imagen de Allplan -->
                    <ValueType>Picture</ValueType>
                    <EventId>0</EventId>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>PointMode</Name>
                <Text>Elegir modo</Text>
                <Value>0</Value>
                <ValueType>RadioButtonGroup</ValueType>
                <Parameter>
                    <Name>ExtendPolyline</Name>
                    <Text>Modo Edicion</Text>
                    <Value>0</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>EditPolyline</Name>
                    <Text>Modo Configuracion</Text>
                    <Value>1</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
                <Parameter>
                    <Name>CreatePolyline</Name>
                    <Text>Modo Creacion - Ext</Text>
                    <Value>2</Value>
                    <ValueType>RadioButton</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowLimitAngles</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CheckBoxLimitarAngulos</Name>
                    <Text>Limitar ángulos</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <!-- <Parameter>
            <Name>RowAgregarDiametroZ</Name>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CheckBoxAgregarDiametroZ</Name>
                <Text>Agregar diámetro en Z</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter> -->
            <Parameter>
                <Name>RowInsertPoint</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CheckBoxInsertPoint</Name>
                    <Text>Insertar punto</Text>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowAddCut</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CheckBoxAddCut</Name>
                    <Text>Añadir cortes</Text>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowBorrar</Name>
                <Text>Borrar</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>borrarSeccion</Name>
                    <Text>Borrar Seccion o Corte</Text>
                    <EventId>1004</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
             <Parameter>
                <Name>RowInvertirCaval</Name>
                <Text>Invertir</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>invertirCaval</Name>
                    <Text>Invertir caval</Text>
                    <TextId>2084</TextId>
                    <EventId>1017</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
          <!-- ══════════════════════════════════════════
             TRAZADO PARALELO (solo en Modo Creacion)
        ══════════════════════════════════════════ -->
        <Parameter>
            <Name>TrazadoParaleloExpander</Name>
            <Text>Trazado Paralelo</Text>
            <ValueType>Expander</ValueType>
            <Visible>PointMode == 2</Visible>
            <Parameter>
                <Name>RowParaleloEnabled</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>TrazadoParaleloEnabled</Name>
                    <Text>Activar trazado paralelo</Text>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowParaleloDistancia</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>TrazadoParaleloDistancia</Name>
                    <Text>Distancia (mm) entre tubos</Text>
                    <Value>0</Value>
                    <MinValue>0</MinValue>
                    <ValueType>Integer</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowParaleloLado</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>TrazadoParaleloLado</Name>
                    <Text>Posicion por</Text>
                    <Value>fuera</Value>
                    <ValueList>dentro|fuera</ValueList>
                    <ValueType>StringComboBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowParaleloSeleccionMultiple</Name>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>TrazadoParaleloSeleccionMultiple</Name>
                    <Text>Selección múltiple de segmentos</Text>
                    <Value>False</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowAgregarParalela</Name>
                <Text>Agregar paralela</Text>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>AgregarParalela</Name>
                    <Text>Agregar Paralela</Text>
                    <EventId>1050</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>ElementSeleted</Name>
            <Text>Elemento seleccionado</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>ElementDescription</Name>
                <Text>Info</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>ViewInfo</Name>
                <Text>Ver Info</Text>
                <EventId>1010</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- ORIENTACIÓN 3D (para tubos verticales en paredes / paredes inclinadas) -->
        <Parameter>
            <Name>Orientacion3DExpander</Name>
            <Text>Orientación 3D (segmento unico)</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>RotationAngle</Name>
                <Text>Angulo rotacion</Text>
                <Value></Value>
                <ValueType>Text</ValueType>
                <FontSize>16</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>DefineOrientation</Name>
                <Text>Definir orientación</Text>
                <EventId>1012</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>LayersCustom</Name>
            <Text>Layers</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>LayerTypes</Name>
                <Text>Tipos de layer</Text>
                <Value></Value>
                <ValueList></ValueList>
                <ValueType>StringComboBox</ValueType>
            </Parameter>
            <Parameter>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>aplicarLayers</Name>
                    <Text>Aplicar layer</Text>
                    <EventId>1009</EventId>
                    <Value>0</Value>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowAttribute</Name>
            <Text>Atributos</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>AttributeValue</Name>
                <Text>6_CC_IS / pmp_pare</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
            <Parameter>
                <ValueType>Row</ValueType>
                <Parameter>
                    <Name>AttributeApply</Name>
                    <Text>Aplicar atributos</Text>
                    <EventId>1011</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowCodificacion</Name>
            <Text>Codificació Cajetín</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>CodificacionCajetin</Name>
                <Text>Codificació Cajetín</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>CodificacionCajetinApply</Name>
                <Text>Aplicar codificació</Text>
                <EventId>1039</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>General</Name>
            <Text>General options</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>CommonProp</Name>
                <Text></Text>
                <Value></Value>
                <Visible>False</Visible>
                <Enable>False</Enable>
                <ValueType>CommonProperties</ValueType>
            </Parameter>
            <!-- Opción para crear PythonPartGroup -->
            <Parameter>
                <Name>RowPythonPart</Name>
                <Text>PythonPartGroup</Text>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>CreatePythonPart</Name>
                    <Text>Crear como PythonPartGroup</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                    <!-- <Enable>False</Enable> -->
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>RowPolilyne</Name>
                <Text>Agregar Polilinea</Text>
                <ValueType>Row</ValueType>
                <Value>OVERALL:1</Value>
                <Parameter>
                    <Name>AddPolilyne</Name>
                    <Text>Polilinea</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
                <Parameter>
                    <Name>AddCube</Name>
                    <Text>Polilinea</Text>
                    <Value>True</Value>
                    <ValueType>CheckBox</ValueType>
                </Parameter>
            </Parameter>
            <Parameter>
                <Name>Separator</Name>
                <ValueType>Separator</ValueType>
            </Parameter>
        </Parameter>
        <!-- FINALIZAR -->
        <Parameter>
            <Name>RowFinalizar</Name>
            <Text>Finalizar</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>finalizarCreacion</Name>
                <Text>Finalizar - Crear</Text>
                <EventId>1003</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- Parámetros ocultos -->
        <Parameter>
            <Name>zUnique</Name>
            <Text>Unic</Text>
            <Value>0.0</Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>Double</ValueType>
        </Parameter>
        <!-- Parámetro oculto para guardar el estado de las polilíneas (para poder restaurar al editar) -->
        <Parameter>
            <Name>SavedState</Name>
            <Text>SavedState</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
        <Parameter>
            <Name>CopiedElementsUUIDs</Name>
            <Text>CopiedElementsUUIDs</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
        <Parameter>
            <Name>CopiedElementsFiles</Name>
            <Text>CopiedElementsFiles</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
    </Page>
    <!-- ══════════════════════════════════════════
         PAGE 2: Soportes
    ══════════════════════════════════════════ -->
    <Page>
        <Name>PageSoportes</Name>
        <Text>Soportes</Text>
        <!-- ══════════════════════════════════════════
         BLOQUE 1 · Tipo de soporte
         ══════════════════════════════════════════ -->
        <!-- Familia: Zeta / Omega -->
        <Parameter>
            <Name>TypeSupport</Name>
            <Text>Tipo de soporte</Text>
            <Value>Zeta</Value>
            <ValueType>StringComboBox</ValueType>
            <ValueList></ValueList>
            <EventId>1030</EventId>
        </Parameter>
        <!-- Subtipo semántico → campo "subtipo" del mock JSON -->
        <Parameter>
            <Name>SubtipoSoporte</Name>
            <Text>Subtipo instalación</Text>
            <Value></Value>
            <ValueType>Text</ValueType>
            <FontSize>16</FontSize>
            <FontStyle>2</FontStyle>
            <!-- <Value></Value>
            <ValueType>StringComboBox</ValueType>
            <ValueList>Ventilación|Clima|Electricidad|Agua|Saneamiento</ValueList> -->
        </Parameter>
        <!-- Superficie → campo "superficie" del mock JSON -->
        <Parameter>
            <Name>Superficie</Name>
            <Text>Superficie</Text>
            <Value>Liso</Value>
            <ValueType>StringComboBox</ValueType>
            <ValueList>Liso|Perforado</ValueList>
        </Parameter>
        <Parameter>
            <Name>SepDimensiones</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 2 · Dimensiones
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>CotaA</Name>
            <Text>Cota A (mm)</Text>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <MinValue>0.0</MinValue>
        </Parameter>
        <Parameter>
            <Name>CotaB</Name>
            <Text>Cota B (mm)</Text>
            <Value>0.0</Value>
            <ValueType>Double</ValueType>
            <MinValue>0.0</MinValue>
        </Parameter>
        <Parameter>
            <Name>AnguloInclinacion</Name>
            <Text>Ángulo inclinación (°)</Text>
            <Value>0.0</Value>
            <ValueType>Angle</ValueType>
        </Parameter>
        <Parameter>
            <Name>SepAcciones</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 5 · Acciones de inserción
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>RowInsertar</Name>
            <Text>Insertar</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>InsertarSoporte</Name>
                <Text>Insertar soporte</Text>
                <EventId>1033</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowCrear</Name>
            <Text>Crear</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>CrearSoporte</Name>
                <Text>Crear Soporte</Text>
                <EventId>1034</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- Contador de soportes acumulados -->
        <Parameter>
            <Name>RowSoporteCount</Name>
            <Text>Soportes</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>SoporteCount</Name>
                <Text>Estado</Text>
                <Value>Acumulados: 0</Value>
                <ValueType>Text</ValueType>
                <FontSize>14</FontSize>
                <FontStyle>2</FontStyle>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>SepGestion</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 6 · Gestión de soportes acumulados
         ══════════════════════════════════════════ -->
        <!-- RadioButtonGroup modo edición: 0=Desactivado, 1=Edición, 2=Edición Mover -->
        <Parameter>
            <Name>SoporteEditMode</Name>
            <Text>Modo edición</Text>
            <Value>0</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <EventId>1038</EventId>
            <Parameter>
                <Name>EditModeDisabled</Name>
                <Text>Desactivado</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>EditModeEdit</Name>
                <Text>Edición Borrar</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>EditModeMove</Name>
                <Text>Edición Mover</Text>
                <Value>2</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>SepAtributos</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- Botones gestión: borrar + insertar en plano -->
        <Parameter>
            <Name>RowBorrarSoportes</Name>
            <Text>Borrar Soporte</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>BorrarSoportes</Name>
                <Text>Borrar sel.</Text>
                <EventId>1036</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>SepAtributos2</Name>
            <ValueType>Separator</ValueType>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 7 · Atributos de soporte
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>RowSoporteAttr</Name>
            <Text>Atributo de soporte</Text>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>SoporteAttributeValue</Name>
                <Text>Valor atributo</Text>
                <Value></Value>
                <ValueType>String</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
            <Name>RowAplicarAttr</Name>
            <Text>Aplicar atributo soporte</Text>
            <ValueType>Row</ValueType>
            <Parameter>
                <Name>AplicarAtributoSoporte</Name>
                <Text>Aplicar atributo</Text>
                <EventId>1037</EventId>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>
        <!-- ══════════════════════════════════════════
         BLOQUE 8 · Estado interno (oculto)
         ══════════════════════════════════════════ -->
        <Parameter>
            <Name>SoportesSavedState</Name>
            <Text>SoportesSavedState</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
        </Parameter>
    </Page>
</Element>