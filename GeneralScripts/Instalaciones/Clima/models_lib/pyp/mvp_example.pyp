<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>Instalaciones\Clima\models_lib\pyp\mvp_example.py</Name>
    <Title>MVP Polyline Example (Full Test)</Title>
    <Version>1.0</Version>
    <ShowFavoriteButtons>True</ShowFavoriteButtons>
  </Script>

  <Page>
    <Name>Page1</Name>
    <Text>Controls</Text>

    <!-- STATUS & INFO SECTION -->
    <Parameter>
      <Name>FirstText</Name>
      <Text>Status</Text>
      <Value>Ready to draw</Value>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>CoordInfo</Name>
      <Text>Coordinates</Text>
      <Value>X: 0, Y: 0, Z: 0</Value>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>SectionInfo</Name>
      <Text>Section</Text>
      <Value>Segments: 0 | Total: 0mm</Value>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator1</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- ACTIONS SECTION (PROMINENT) -->
    <Parameter>
      <Name>CrearPolylinea</Name>
      <Text>✓ Create Polylines</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>RowActions</Name>
      <Text> </Text>
      <ValueType>Row</ValueType>
      <Value>OVERALL:1</Value>

      <Parameter>
        <Name>generarpolilinea</Name>
        <Text>Save Polyline</Text>
        <EventId>1002</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>

      <Parameter>
        <Name>finalizarCreacion</Name>
        <Text>Finalize &amp; Create</Text>
        <EventId>1003</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>CreatePythonPartGroup</Name>
      <Text>Create as PythonPart Group</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator2</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- ORIGIN SETUP (EXPANDER) -->
    <Parameter>
      <Name>OriginExpander</Name>
      <Text>Origin Setup</Text>
      <ValueType>Expander</ValueType>

      <Parameter>
        <Name>StartX</Name>
        <Text>Origin X (mm)</Text>
        <Value>0</Value>
        <ValueType>Length</ValueType>
      </Parameter>

      <Parameter>
        <Name>StartY</Name>
        <Text>Origin Y (mm)</Text>
        <Value>0</Value>
        <ValueType>Length</ValueType>
      </Parameter>

      <Parameter>
        <Name>StartZ</Name>
        <Text>Origin Z (mm)</Text>
        <Value>0</Value>
        <ValueType>Length</ValueType>
      </Parameter>

      <Parameter>
        <Name>RowSetOrigin</Name>
        <Text> </Text>
        <ValueType>Row</ValueType>
        <Value>OVERALL:1</Value>
        
        <Parameter>
          <Name>SetOriginButton</Name>
          <Text>Set Current as Origin</Text>
          <EventId>1010</EventId>
          <Value>0</Value>
          <ValueType>Button</ValueType>
        </Parameter>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>Separator3</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- DRAWING OPTIONS -->
    <Parameter>
      <Name>DrawingOptionsHeader</Name>
      <Text>Drawing Options</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>CheckBoxInsertarPunto</Name>
      <Text>Insert Point Mode</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>CheckBoxLimitarAngulos</Name>
      <Text>Limit Angles</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>EnableZCoordinate</Name>
      <Text>Enable Z Coordinate</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator4</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- SYSTEM CONFIGURATION -->
    <Parameter>
      <Name>SystemConfigHeader</Name>
      <Text>System Configuration</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>Saneamiento</Name>
      <Text>System Type</Text>
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
      <Name>DiametroAplicarPluvial</Name>
      <Text>Diameter (Pluvial)</Text>
      <Value>110</Value>
      <ValueType>IntegerComboBox</ValueType>
      <ValueList>110</ValueList>
      <Visible>Saneamiento == 0</Visible>
    </Parameter>

    <Parameter>
      <Name>DiametroAplicarFecal</Name>
      <Text>Diameter (Fecal)</Text>
      <Value>40</Value>
      <ValueType>IntegerComboBox</ValueType>
      <ValueList>25|40|110</ValueList>
      <Visible>Saneamiento == 1</Visible>
    </Parameter>

    <Parameter>
      <Name>Separator5</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- INSTALLATION REGISTRY SECTION -->
    <Parameter>
      <Name>RegistryHeader</Name>
      <Text>Installation Registry</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>InstallationName</Name>
      <Text>Installation</Text>
      <Value>Pluvial_Test</Value>
      <ValueType>StringComboBox</ValueType>
      <ValueList>Pluvial_Test|Fecal_Test</ValueList>
    </Parameter>

    <Parameter>
      <Name>RefreshInstallationsBtn</Name>
      <Text>Refresh Registry</Text>
      <EventId>2030</EventId>
      <Value>0</Value>
      <ValueType>Button</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator5b</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- CAPTURE MODE (EXPANDER - COLLAPSED BY DEFAULT) -->
    <Parameter>
      <Name>CaptureExpander</Name>
      <Text>Capture Mode (Advanced)</Text>
      <ValueType>Expander</ValueType>
      <Value>False</Value>

      <Parameter>
        <Name>PathId</Name>
        <Text>Path ID</Text>
        <Value>1</Value>
        <ValueType>Integer</ValueType>
      </Parameter>

      <Parameter>
        <Name>SegmentId</Name>
        <Text>Segment ID</Text>
        <Value>1</Value>
        <ValueType>Integer</ValueType>
      </Parameter>

      <Parameter>
        <Name>PointRole</Name>
        <Text>Point Role</Text>
        <Value>1</Value>
        <ValueType>IntegerComboBox</ValueType>
        <ValueList>0|1|2|3</ValueList>
        <ValueTextList>Inicial|Paso|Bifurcacion|Final</ValueTextList>
      </Parameter>
    </Parameter>
  </Page>

  <Page>
    <Name>Page2</Name>
    <Text>Info</Text>

    <Parameter>
      <Name>InfoPicture</Name>
      <Text>
MVP Polyline Example - Library Demo

CONTROLS:
• Create Mode: Enable to draw new polylines
• Insert Point: Add points to existing segments
• Limit Angles: Snap to angles configured by installation (90°, 45°, or custom)
• Z Coordinate: Enable 3D vertical segments
• System Type: Choose Pluvial or Fecal
• Diameter: Select pipe diameter (mm)

ACTIONS:
• Save: Store polyline without creating
• Finalize: Create 3D models in document

3D MODELS (from Saneamiento):
1. TuboPVCConFlecha - Pipes with arrows
2. CodoBasico - Elbow fittings (45° or 90°)
3. Manguito - Coupling connections

This demonstrates the library can:
✓ Import real PythonPart models
✓ Work with any palette configuration
✓ Be reused across installations
✓ Use installation-specific angle snap values
      </Text>
      <TextId>1005</TextId>
      <Value>AllplanSettings.PictResPalette.eHotinfo</Value>
      <ValueType>Picture</ValueType>
    </Parameter>
  </Page>

  <Page>
    <Name>Page3</Name>
    <Text>Advanced Features</Text>

    <!-- SEGMENT EDITING SECTION -->
    <Parameter>
      <Name>SegEditHeader</Name>
      <Text>Segment Editing</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <!-- Data-driven segment index list - updated when segments change -->
    <Parameter>
      <Name>SegmentIndicesList</Name>
      <Text>Segment Indices List</Text>
      <Value>0</Value>
      <ValueType>Integer</ValueType>
      <Visible>False</Visible>
    </Parameter>

    <Parameter>
      <Name>SegmentIndex</Name>
      <Text>Segment Index</Text>
      <Value>0</Value>
      <ValueType>IntegerComboBox</ValueType>
      <ValueList>0</ValueList>
    </Parameter>

    <Parameter>
      <Name>NewDiameter</Name>
      <Text>New Diameter (mm)</Text>
      <Value>160</Value>
      <ValueType>IntegerComboBox</ValueType>
      <ValueList>40|110|160</ValueList>
    </Parameter>

    <Parameter>
      <Name>RowSegmentEdit</Name>
      <Text> </Text>
      <ValueType>Row</ValueType>
      <Value>OVERALL:1</Value>

      <Parameter>
        <Name>UpdateSegmentBtn</Name>
        <Text>Update Segment</Text>
        <EventId>2001</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>

      <Parameter>
        <Name>DeleteSegmentBtn</Name>
        <Text>Delete Segment</Text>
        <EventId>2002</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>Separator6</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- BRANCHING & FITTINGS SECTION -->
    <Parameter>
      <Name>FittingsHeader</Name>
      <Text>Branching &amp; Fittings</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>TestElbowsCheckbox</Name>
      <Text>Auto-create Elbows at angles</Text>
      <Value>True</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>TestReducersCheckbox</Name>
      <Text>Auto-create Reducers</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>FittingsInstructions</Name>
      <Text>Fittings hooks are now active. Elbows/reducers will be created automatically at junctions based on hooks.</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator7</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- INSERT POINT MODE SECTION -->
    <Parameter>
      <Name>InsertModeHeader</Name>
      <Text>Insert Point Mode</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>InsertModeInstructions</Name>
      <Text>Enable Insert Point Mode (Page 1), then click on existing segment to add point.</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>InsertTestSegmentIndex</Name>
      <Text>Test Segment Index</Text>
      <Value>0</Value>
      <ValueType>Integer</ValueType>
    </Parameter>

    <Parameter>
      <Name>InsertAtMidpointBtn</Name>
      <Text>Insert at Midpoint</Text>
      <EventId>2020</EventId>
      <Value>0</Value>
      <ValueType>Button</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator8</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- FUSION & EXTENSION SECTION -->
    <Parameter>
      <Name>FusionHeader</Name>
      <Text>Fusion &amp; Extension</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>FusionTolerance</Name>
      <Text>Fusion Tolerance (mm)</Text>
      <Value>50</Value>
      <ValueType>Length</ValueType>
    </Parameter>

    <Parameter>
      <Name>ShowFusionZonesCheckbox</Name>
      <Text>Show Fusion Zones (Debug)</Text>
      <Value>False</Value>
      <ValueType>CheckBox</ValueType>
    </Parameter>

    <Parameter>
      <Name>FusionInstructions</Name>
      <Text>Draw a new line near the end of existing path. Library will auto-merge within tolerance.</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator9</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- CUSTOM METADATA SECTION -->
    <Parameter>
      <Name>MetadataHeader</Name>
      <Text>Custom Metadata</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>ViewMetadataSegmentIndex</Name>
      <Text>Segment Index</Text>
      <Value>0</Value>
      <ValueType>Integer</ValueType>
    </Parameter>

    <Parameter>
      <Name>ViewMetadataBtn</Name>
      <Text>Show Metadata</Text>
      <EventId>2040</EventId>
      <Value>0</Value>
      <ValueType>Button</ValueType>
    </Parameter>

    <Parameter>
      <Name>MetadataDisplay</Name>
      <Text>Metadata</Text>
      <Value>(Select segment and click Show)</Value>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>Separator10</Name>
      <ValueType>Separator</ValueType>
    </Parameter>

    <!-- JSON IMPORT/EXPORT SECTION -->
    <Parameter>
      <Name>JSONHeader</Name>
      <Text>JSON Import/Export</Text>
      <ValueType>Text</ValueType>
    </Parameter>

    <Parameter>
      <Name>JSONPathID</Name>
      <Text>Path ID (for export/import)</Text>
      <Value>1</Value>
      <ValueType>Integer</ValueType>
    </Parameter>

    <Parameter>
      <Name>RowJSON</Name>
      <Text> </Text>
      <ValueType>Row</ValueType>
      <Value>OVERALL:1</Value>

      <Parameter>
        <Name>ExportJSONBtn</Name>
        <Text>Export to JSON</Text>
        <EventId>2050</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>

      <Parameter>
        <Name>ImportJSONBtn</Name>
        <Text>Import from JSON</Text>
        <EventId>2051</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>

      <Parameter>
        <Name>GenerateOptimalBtn</Name>
        <Text>Generar Camino Optimo</Text>
        <EventId>2052</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
      </Parameter>
    </Parameter>

    <Parameter>
      <Name>JSONStatus</Name>
      <Text>JSON Status</Text>
      <Value>Ready</Value>
      <ValueType>Text</ValueType>
    </Parameter>
  </Page>
</Element>
