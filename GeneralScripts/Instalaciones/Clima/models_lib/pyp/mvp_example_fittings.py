# -*- coding: utf-8 -*-
"""Fitting hooks for MVP testing - demonstrates branching & fittings API."""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import math

# Import existing model builders with robust error handling
CodoBasico = None
Manguito = None

try:
    from Colze_basic_001 import CodoBasico
    print("[Fittings] ✓ Imported CodoBasico")
except ImportError as e:
    print(f"[Fittings] ⚠ CodoBasico not available: {e}")
except Exception as e:
    print(f"[Fittings] ⚠ Error importing CodoBasico: {e}")

try:
    from ManguitoBasic_003 import Manguito
    print("[Fittings] ✓ Imported Manguito")
except ImportError as e:
    print(f"[Fittings] ⚠ Manguito not available: {e}")
except Exception as e:
    print(f"[Fittings] ⚠ Error importing Manguito: {e}")


def create_elbow_fitting(segment1, segment2, angle_deg):
    """Create elbow fitting between two segments.
    
    Args:
        segment1, segment2: SegmentMetadata objects
        angle_deg: Angle between segments in degrees
    
    Returns:
        List of ModelElement3D for the elbow
    """
    print(f"[Fittings] Creating elbow at angle {angle_deg:.1f}°")
    
    if not CodoBasico:
        print("[Fittings] CodoBasico not available, creating placeholder")
        return _create_placeholder_elbow(segment1, segment2)
    
    try:
        # Get junction point (end of segment1 / start of segment2)
        p1_end = segment1.points[1]
        
        # Determine elbow angle category (based on Allplan standards)
        if 40 <= angle_deg <= 50:
            elbow_angle = 45
        elif 85 <= angle_deg <= 95:
            elbow_angle = 90
        else:
            elbow_angle = int(round(angle_deg / 15) * 15)  # Round to nearest 15°
        
        # Create elbow instance
        elbow = CodoBasico(
            diameter=segment1.diameter,
            angle=elbow_angle,
            position=p1_end
        )
        
        # Build geometry
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        
        elements = elbow.create_element(com_prop)
        print(f"[Fittings] ✓ Created {elbow_angle}° elbow")
        return elements if isinstance(elements, list) else [elements]
        
    except Exception as ex:
        print(f"[Fittings] Error creating elbow: {ex}")
        return []


def create_reducer_fitting(segment1, segment2, diameter1, diameter2):
    """Create reducer fitting between segments with different diameters."""
    print(f"[Fittings] Creating reducer {diameter1}mm -> {diameter2}mm")
    
    if not Manguito:
        print("[Fittings] Manguito not available")
        return []
    
    try:
        # Get junction point
        junction = segment1.points[1]
        
        # Create manguito (coupling) as reducer
        manguito = Manguito(
            diameter1=diameter1,
            diameter2=diameter2,
            position=junction
        )
        
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        
        elements = manguito.create_element(com_prop)
        print(f"[Fittings] ✓ Created reducer")
        return elements if isinstance(elements, list) else [elements]
        
    except Exception as ex:
        print(f"[Fittings] Error creating reducer: {ex}")
        return []


def _create_placeholder_elbow(segment1, segment2):
    """Create simple placeholder sphere at elbow location."""
    try:
        junction = segment1.points[1]
        radius = segment1.diameter / 2
        
        sphere = AllplanGeo.Sphere(
            AllplanGeo.AxisPlacement3D(junction, AllplanGeo.Vector3D(0, 0, 1)),
            radius * 1.5  # Slightly larger than pipe
        )
        
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.Color = 4  # Blue for placeholder
        
        return [AllplanBasisElements.ModelElement3D(com_prop, sphere)]
    except:
        return []
