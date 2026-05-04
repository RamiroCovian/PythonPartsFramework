<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>Instalaciones\Clima\models_lib\pyp\minimal_polyline.py</Name>
    <Title>Minimal Polyline (Mock Duct)</Title>
    <Version>1.0</Version>
  </Script>

  <Page>
    <Name>Page1</Name>
    <Text>Controls</Text>

    <Parameter>
      <Name>CrearPolylinea</Name>
      <Text>Create Polyline</Text>
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
  </Page>
</Element>
