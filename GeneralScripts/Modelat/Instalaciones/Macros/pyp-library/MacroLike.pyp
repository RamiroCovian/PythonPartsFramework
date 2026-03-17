<Element>
	<Script>
		<Name>MacroLike.py</Name>
		<Title>Bloque + Mástil (2D simbólico / 3D real)</Title>
		<Version>1.1</Version>
		<Interactor>False</Interactor>
		<ReadLastInput>True</ReadLastInput>
	</Script>

	<Page>
		<Name>Main</Name>
		<Text>Planta 2D simbólica • Animación 3D con sólidos</Text>

		<Parameter>
			<Name>CommonProp</Name>
			<Text>Propiedades</Text>
			<ValueType>CommonProperties</ValueType>
		</Parameter>

		<!-- 3D reales -->
		<Parameter>
			<Name>HeadSide</Name>
			<Text>Lado bloque (mm)</Text>
			<Value>120</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>HeadThk</Name>
			<Text>Espesor bloque (mm)</Text>
			<Value>30</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>RodLen</Name>
			<Text>Largo mástil (mm)</Text>
			<Value>600</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>RodWidth</Name>
			<Text>Ancho mástil (mm)</Text>
			<Value>20</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>RodHeight</Name>
			<Text>Alto mástil (mm)</Text>
			<Value>20</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>HoleRadius</Name>
			<Text>Radio cazoleta (mm)</Text>
			<Value>35</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>HoleDepth</Name>
			<Text>Profundidad cazoleta (mm)</Text>
			<Value>18</Value>
			<ValueType>Length</ValueType>
		</Parameter>

		<!-- 2D simbólico (independiente) -->
		<Parameter>
			<Name>SymSide</Name>
			<Text>Tamaño símbolo (mm)</Text>
			<Value>100</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>SymBowlR</Name>
			<Text>Radio media circunferencia (mm)</Text>
			<Value>30</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>SymStemW</Name>
			<Text>Ancho patita (mm)</Text>
			<Value>10</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>SymStemLen</Name>
			<Text>Largo patita (mm)</Text>
			<Value>20</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>Link2DTo3D</Name>
			<Text>Usar tamaño del símbolo 2D para la cabeza 3D</Text>
			<ValueType>CheckBox</ValueType>
			<Value>True</Value>
		</Parameter>
		<Parameter>
			<Name>Orientation</Name>
			<Text>Orientación mástil</Text>
			<ValueType>ListBox</ValueType>
			<Value>Horizontal|Vertical</Value>
			<DefaultValue>Horizontal</DefaultValue>
		</Parameter>

		<!-- Cilindro de la punta -->
		<Parameter>
			<Name>CapRadius</Name>
			<Text>Radio cilindro punta (mm)</Text>
			<Value>12</Value>
			<ValueType>Length</ValueType>
		</Parameter>
		<Parameter>
			<Name>CapLen</Name>
			<Text>Largo cilindro punta (mm)</Text>
			<Value>20</Value>
			<ValueType>Length</ValueType>
		</Parameter>
	</Page>
</Element>