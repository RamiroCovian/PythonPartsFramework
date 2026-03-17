<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>saneamiento\polilinea_base_orig.py</Name>
        <Title>Script Object</Title>
        <Version>1.0</Version>
    </Script>
    <Page>
        <!-- 0. Elegir el diametro de los objetos -->
        <Name>Dimensiones</Name>
        <Text>Parámetros del tubo</Text>


        <!-- 1. Crear Polilínea -->
        <Parameter>
            <Name>RowCrear</Name>
            <Text>Crear Polilíneas</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CrearPolylinea</Name>
                <Text>Crear polilínea</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>

        <!-- 3. Insertar Punto -->
        <Parameter>
            <Name>RowInsertarPunto</Name>
            <Text>Insertar Punto</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CheckBoxInsertarPunto</Name>
                <Text>Mode Insertar punto</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>

        <!-- 4. Borrar sección -->
        <Parameter>
            <Name>RowBorrar</Name>
            <Text>Borrar</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>borrarSeccion</Name>
                <Text>Borrar sección</Text>
                <EventId>1004</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <!-- 5. Guardar -->
        <Parameter>
            <Name>RowGenerar</Name>
            <Text>Guardar</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>generarpolilinea</Name>
                <Text>Guardar polilínea</Text>
                <EventId>1002</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <!-- 6. Finalizar -->
        <Parameter>
            <Name>RowFinalizar</Name>
            <Text>Finalizar</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>finalizarCreacion</Name>
                <Text>Finalizar y crear</Text>
                <EventId>1003</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <!-- Información de uso -->
        <Parameter>
            <Name>InfoPicture</Name>
            <Text>
Instrucciones de uso:
Crear polilínea (Checkbox):
Activa o desactiva el modo de creación de polilíneas con feedback visual.
- ✓ ON: puedes agregar puntos para crear una nueva polilínea o extender una existente.
- ☐ OFF: modo edición para modificar polilíneas guardadas.

Mode Insertar punto (CheckBox):
- ✓ ON: inserta un punto en cualquier segmento haciendo clic sobre él.
- ☐ OFF: el clic sobre un segmento solo lo selecciona.

Borrar sección (botón 1004):
Borra el segmento seleccionado o los segmentos seleccionados por marco.

Guardar polilínea (botón 1002):
Guarda la polilínea activa sin finalizar la sesión.

Finalizar y crear (botón 1003):
Guarda la polilínea activa y la crea inmediatamente en el documento.

Funciones adicionales:
- Mover vértices: arrastra vértices de polilíneas guardadas en modo edición.
- Extender polilínea: doble clic en un extremo de polilínea guardada.
- Selección por marco: clic y arrastra para seleccionar varios segmentos.

            </Text>
            <TextId>1005</TextId>
            <Value>AllplanSettings.PictResPalette.eHotinfo</Value>
            <ValueType>Picture</ValueType>
        </Parameter>


        <Parameter>
            <Name>RowLimitarAngulos</Name>
            <Text>Limitar ángulos</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>
            <Parameter>
                <Name>CheckBoxLimitarAngulos</Name>
                <Text>Limitar ángulos</Text>
                <Value>False</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>
        </Parameter>



        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>




        <!-- Tipo de saneamiento -->
        <Parameter>
            <Name>Saneamiento</Name>
            <Text>Tipo de saneamiento</Text>
            <Value>0</Value>
            <ValueType>RadioButtonGroup</ValueType>
            <Parameter>
                <Name>Pluvial</Name>
                <Text>Pluvial</Text>
                <Value>0</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
            <Parameter>
                <Name>Fecal</Name>
                <Text>Fecal</Text>
                <Value>1</Value>
                <ValueType>RadioButton</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <!-- Gestión de Secciones -->
        <Parameter>
            <Name>SeccionesHeader</Name>
            <Text>Gestión de Secciones</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>

            <!-- Selección de diámetro para aplicar - Solo Pluvial (110mm) -->
            <Parameter>
                <Name>DiametroAplicarPluvial</Name>
                <Text>Diámetro a aplicar</Text>
                <Value>110</Value>
                <ValueType>IntegerComboBox</ValueType>
                <ValueList>110</ValueList>
                <Visible>Saneamiento == 0</Visible>
            </Parameter>

            <!-- Selección de diámetro para aplicar - Fecal (25, 40, 110mm) -->
            <Parameter>
                <Name>DiametroAplicarFecal</Name>
                <Text>Diámetro a aplicar</Text>
                <Value>40</Value>
                <ValueType>IntegerComboBox</ValueType>
                <ValueList>25|40|110</ValueList>
                <Visible>Saneamiento == 1</Visible>
            </Parameter>
        </Parameter>

        <!-- Diámetro personalizado -->
        <Parameter>
            <Name>DiametroPersonalizado</Name>
            <Text>Diámetro personalizado (mm)</Text>
            <Value>0</Value>
            <ValueType>Length</ValueType>
            <MinValue>0</MinValue>
            <MaxValue>1000</MaxValue>
        </Parameter>

        <!-- Botones de gestión de secciones -->
        <Parameter>
            <Name>RowSecciones</Name>
            <Text>Acciones de Sección</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1</Value>

            <Parameter>
                <Name>aplicarSeccion</Name>
                <Text>Aplicar sección</Text>
                <EventId>1007</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>

            <Parameter>
                <Name>mostrarSecciones</Name>
                <Text>Mostrar info</Text>
                <EventId>1008</EventId>
                <Value>0</Value>
                <ValueType>Button</ValueType>
            </Parameter>
        </Parameter>

        <Parameter>
            <Name>Separator</Name>
            <ValueType>Separator</ValueType>
        </Parameter>







        <Parameter>
            <Name>NameRow</Name>
            <Text>Estado</Text>
            <ValueType>Row</ValueType>
            <Value>OVERALL:1 </Value>

        <Parameter>
            <Name>FirstText</Name>
            <Text></Text>
            <Value>Creacion off</Value>
            <ValueType>Text</ValueType>
        </Parameter>

        </Parameter>
    </Page>
</Element>
