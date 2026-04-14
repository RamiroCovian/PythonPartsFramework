import NemAll_Python_Geometry as AllplanGeometry

from typing import List


class SwitchObject:

    @staticmethod
    def create_switch_geometry() -> List[AllplanGeometry.BRep3D]:
        """
        Crea la geometría 3D del interruptor doble (placa y pulsadores),
        rotada a una posición vertical.
        Retorna una lista de objetos BRep3D (cuerpos sólidos).
        """
        switch_parts_unrotated = []

        # --- Dimensiones (en mm) ---
        base_largo = 100.0
        base_ancho = 100.0
        base_alto = 10.0 # Espesor (Originalmente en Z)

        pulsador_largo = 40.0
        pulsador_ancho = 45.0
        pulsador_alto = 3.0
        espacio_central = 5.0

        # --- 1. Crear las partes en el plano XY (horizontal, sin rotar) ---

        # Placa Base Gris
        base_body = AllplanGeometry.Polyhedron3D.CreateCuboid(
            base_largo, base_ancho, base_alto
        )
        # Crear elemento 3D con estas propiedades

        # Añadirlo a la lista
        switch_parts_unrotated.append(base_body)

        # Cálculo de posiciones para centrar los pulsadores
        total_largo_ocupado = (2 * pulsador_largo) + espacio_central
        inicio_x_conjunto = (base_largo - total_largo_ocupado) / 2
        inicio_y_conjunto = (base_ancho - pulsador_ancho) / 2
        inicio_z = base_alto

        # Pulsador 1 (Izquierdo)
        pulsador_1 = AllplanGeometry.Polyhedron3D.CreateCuboid(
            pulsador_largo, pulsador_ancho, pulsador_alto
        )
        trans_pulsador_1 = AllplanGeometry.Vector3D(
            inicio_x_conjunto, inicio_y_conjunto, inicio_z
        )
        pulsador_1_movido = AllplanGeometry.Move(pulsador_1, trans_pulsador_1)
        switch_parts_unrotated.append(pulsador_1_movido)

        # Pulsador 2 (Derecho)
        pulsador_2 = AllplanGeometry.Polyhedron3D.CreateCuboid(
            pulsador_largo, pulsador_ancho, pulsador_alto
        )
        trans_pulsador_2 = AllplanGeometry.Vector3D(
            inicio_x_conjunto + pulsador_largo + espacio_central,
            inicio_y_conjunto,
            inicio_z
        )
        pulsador_2_movido = AllplanGeometry.Move(pulsador_2, trans_pulsador_2)
        switch_parts_unrotated.append(pulsador_2_movido)

        # --- 2. Aplicar la Rotación y Traslación para Verticalidad en Z ---
        rotation_matrix = AllplanGeometry.Matrix3D()
        eje_rotacion = AllplanGeometry.Line3D(
            AllplanGeometry.Point3D(0, 0, 0), # Punto base
            AllplanGeometry.Point3D(1, 0, 0), # Dirección del Eje X
        )
        #Rotar -90 grados
        rotation_matrix.SetRotation(eje_rotacion, AllplanGeometry.Angle.FromDeg(-90))

        switch_parts_rotated = []

        # Moverlo en Z por base_ancho / 2
        translation_vector = AllplanGeometry.Vector3D(0, 0, base_ancho / 2) # 50.0 mm

        # Aplicar la rotación y traslación a cada parte
        for geo in switch_parts_unrotated:
            # 1. Aplicar la rotación
            rotated_geo = AllplanGeometry.Transform(geo, rotation_matrix)

            # 2. Aplicar la traslación (opcional, para posicionar en Z=0)
            final_geo = AllplanGeometry.Move(rotated_geo, translation_vector)

            switch_parts_rotated.append(final_geo)

        return switch_parts_rotated