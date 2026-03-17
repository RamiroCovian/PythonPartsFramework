"""Implementation of the rotation utility"""

import NemAll_Python_Geometry as AllplanGeo


class RotationUtil():
    """Class used to describe the rotation around the three axes (X,Y,Z) in order to
    transform a geometry from local to global coordinate system or the other way around.

    Often used in context of transforming a bending shape (rebar or mesh) from/to its local
    coordinate system.
    """

    def __init__(self,
                 angle_x: float,
                 angle_y: float,
                 angle_z: float):
        """Construct the object by setting all three angles. The angles are given in degrees.

        Args:
            angle_x:    Rotation angle (degree) around the local x axis
            angle_y:    Rotation angle (degree) around the local y axis
            angle_z:    Rotation angle (degree) around the local z axis
        """

        self.prop_angle_x = angle_x
        self.prop_angle_y = angle_y
        self.prop_angle_z = angle_z


    @property
    def angle_x(self) -> float:
        """Rotation angle around the X axis (in degrees)
        """
        return self.prop_angle_x


    @property
    def angle_y(self) -> float:
        """Rotation angle around the Y axis (in degrees)
        """
        return self.prop_angle_y


    @property
    def angle_z(self) -> float:
        """Rotation angle around the Z axis (in degrees)
        """
        return self.prop_angle_z


    def get_rotation_matrix(self,
                            axis_point: AllplanGeo.Point3D = AllplanGeo.Point3D()) -> AllplanGeo.Matrix3D:
        """Get a 3D transformation matrix (4x4) describing the rotation around the given point
        by all three angles: x, y and z.

        Args:
            axis_point: Rotation point. Defaults to the origin (0,0,0).

        Returns:
            Transformation matrix describing the rotation
        """

        rot_mat = AllplanGeo.Matrix3D()

        rot_mat.Rotation(AllplanGeo.Line3D(axis_point, axis_point + AllplanGeo.Point3D( 1000, 0, 0)),
                         AllplanGeo.Angle.FromDeg(self.angle_x))

        rot_mat.Rotation(AllplanGeo.Line3D(axis_point, axis_point + AllplanGeo.Point3D( 0, 1000, 0)),
                         AllplanGeo.Angle.FromDeg(self.angle_y))

        rot_mat.Rotation(AllplanGeo.Line3D(axis_point, axis_point + AllplanGeo.Point3D( 0, 0, 1000)),
                         AllplanGeo.Angle.FromDeg(self.angle_z))

        return rot_mat


    def __repr__(self) -> str:
        """ create a string from the object data

        Returns:
            string with the object data
        """

        return f"<{self.__class__.__name__}>\n"  \
                "   x-angle = {self.angle_x}\n" \
                "   y-angle = {self.angle_y}\n" \
                "   z-angle = {self.angle_z}\n"
