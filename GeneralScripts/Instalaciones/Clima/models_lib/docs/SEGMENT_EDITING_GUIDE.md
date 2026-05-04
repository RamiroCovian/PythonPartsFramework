# Segment Editing Guide

This guide explains how to use the segment editing capabilities in the polyline_base_lib library.

## Overview

The library provides comprehensive segment editing capabilities through two approaches:
1. **Direct Access**: Modify segment properties directly via `script_object.saved_segments`
2. **Convenience Methods**: Use interactor methods for common editing operations

Both approaches support undo/redo functionality and follow Allplan geometry patterns.

## Table of Contents

- [Accessing Segments](#accessing-segments)
- [Property Editing](#property-editing)
- [Breakpoint and Role Management](#breakpoint-and-role-management)
- [Geometry Editing](#geometry-editing)
- [Segment Deletion and Batch Operations](#segment-deletion-and-batch-operations)
- [Utility Functions](#utility-functions)
- [Allplan Compatibility](#allplan-compatibility)

## Accessing Segments

### Query All Segments

```python
# Get all segments
segments = interactor.get_segments()
for seg in segments:
    print(f"Segment: diameter={seg.diameter}, system={seg.system}, label={seg.label}")
```

### Get Specific Segment

```python
# Get segment by index
segment = interactor.get_segment_by_index(0)
if segment:
    print(f"First segment diameter: {segment.diameter}")
```

### Get Segments for a Specific Path

```python
# Get all segments belonging to path 0
path_segments = interactor.get_segments_for_path(0)
print(f"Path 0 has {len(path_segments)} segments")
```

### Find Segment Near a Point

```python
# Find segment near coordinates (x, y, z)
result = interactor.find_segment_at_point((1000.0, 500.0, 0.0), tolerance=80.0)
if result:
    seg_idx, segment = result
    print(f"Found segment {seg_idx}: {segment.label}")
```

## Property Editing

### Direct Access Method

```python
# Access and modify segment properties directly
seg = script_object.saved_segments[0]
seg.diameter = 150.0
seg.section_type = "150mm"
seg.system = "Pluvial"
seg.label = "D150 P"
seg.custom['material'] = 'PVC'
```

### Using Convenience Methods

```python
# Update specific properties
success = interactor.update_segment_properties(
    seg_idx=0,
    diameter=150.0,
    section_type="150mm",
    system="Pluvial",
    label="D150 P"
)

# Update with custom properties
success = interactor.update_segment_properties(
    seg_idx=0,
    diameter=110.0,
    material="PVC",  # Custom property
    installation_date="2024-01-15"  # Custom property
)
```

### Replace Entire Segment Metadata

```python
from Clima.models_lib.py.polyline_base_lib import SegmentMetadata

# Create new metadata
new_meta = SegmentMetadata(
    points=[(0, 0, 0), (1000, 0, 0)],
    diameter=200.0,
    section_type="200mm",
    system="Fecal",
    label="D200 F"
)

# Replace segment
success = interactor.update_segment_by_metadata(seg_idx=0, new_metadata=new_meta)
```

## Breakpoint and Role Management

### Understanding Point Roles

Point roles determine how points are treated during capture and export:
- `CAPTURE_ROLE_INICIAL (1)`: Initial/start point
- `CAPTURE_ROLE_PASO (2)`: Intermediate/pass-through point
- `CAPTURE_ROLE_BIFURCACION (3)`: Bifurcation/branch point
- `CAPTURE_ROLE_FINAL (4)`: Final/end point

### Set Point Role

```python
from Clima.models_lib.py import polyline_base_lib as PBL

# Set point as initial
success = interactor.set_point_role(
    path_idx=0, 
    point_idx=0, 
    role=PBL.CAPTURE_ROLE_INICIAL
)

# Set point as bifurcation
success = interactor.set_point_role(
    path_idx=0, 
    point_idx=5, 
    role=PBL.CAPTURE_ROLE_BIFURCACION
)
```

### Get Point Role

```python
role = interactor.get_point_role(path_idx=0, point_idx=3)
if role == PBL.CAPTURE_ROLE_PASO:
    print("This is an intermediate point")
```

### Mark as Breakpoint

```python
# Convenience method to mark a point as breakpoint
success = interactor.mark_as_breakpoint(
    path_idx=0, 
    point_idx=3, 
    role=PBL.CAPTURE_ROLE_PASO
)
```

## Geometry Editing

All geometry operations use Allplan Point3D and automatically update affected segments.

### Move a Point

```python
# Move point to new coordinates
success = interactor.move_point(
    path_idx=0,
    point_idx=2,
    new_point=(1500.0, 750.0, 100.0)
)

# Using Allplan Point3D
import NemAll_Python_Geometry as AllplanGeo
new_pos = AllplanGeo.Point3D(1500.0, 750.0, 100.0)
success = interactor.move_point(path_idx=0, point_idx=2, new_point=new_pos)
```

### Insert a Point

```python
# Insert point after index 2 (becomes new index 3)
success = interactor.insert_point_at_position(
    path_idx=0,
    insert_after_idx=2,
    new_point=(1250.0, 500.0, 0.0)
)

# Insert at beginning of path
success = interactor.insert_point_at_position(
    path_idx=0,
    insert_after_idx=-1,  # -1 means insert at start
    new_point=(0.0, 0.0, 0.0)
)
```

### Remove a Point

```python
# Remove point (automatically merges adjacent segments)
success = interactor.remove_point(
    path_idx=0,
    point_idx=3,
    min_points=2  # Minimum points to keep in path
)
```

### Split a Segment

```python
# Split segment at a point
success = interactor.split_segment(
    path_idx=0,
    seg_idx=1,  # Segment index (0 to len(path)-2)
    split_point=(1500.0, 500.0, 0.0)
)

# This creates two segments with the same properties
```

### Merge Adjacent Segments

```python
# Merge two adjacent segments
success = interactor.merge_segments(
    path_idx=0,
    seg1_idx=1,
    seg2_idx=2  # Must be seg1_idx + 1
)

# The shared point between segments is removed
# Properties from first segment are kept
```

## Segment Deletion and Batch Operations

### Delete a Segment

```python
# Delete segment metadata only
success = interactor.delete_segment(seg_idx=2, delete_geometry=False)

# Delete segment and its geometry
success = interactor.delete_segment(seg_idx=2, delete_geometry=True)
```

### Delete All Segments for a Path

```python
# Remove all segments associated with path 0
success = interactor.delete_segments_for_path(path_idx=0)
```

### Batch Update Segments

```python
# Update multiple segments in one operation
updates = [
    (0, {'diameter': 150.0, 'system': 'Pluvial'}),
    (1, {'diameter': 110.0, 'section_type': '110mm'}),
    (2, {'label': 'D200 F', 'custom_field': 'value'})
]

count = interactor.batch_update_segments(updates)
print(f"Updated {count} segments")
```

## Utility Functions

### Calculate Segment Length

```python
from Clima.models_lib.py import polyline_base_lib as PBL

segment = interactor.get_segment_by_index(0)
length = PBL.get_segment_length(segment)
print(f"Segment length: {length} mm")
```

### Get Direction Vector

```python
segment = interactor.get_segment_by_index(0)
direction = PBL.get_segment_direction_vector(segment)
dx, dy, dz = direction
print(f"Direction: ({dx:.3f}, {dy:.3f}, {dz:.3f})")
```

### Find Closest Point on Segment

```python
segment = interactor.get_segment_by_index(0)
query_point = (1200.0, 600.0, 50.0)
closest = PBL.find_closest_point_on_segment(segment, query_point)
print(f"Closest point: {closest}")
```

## Allplan Compatibility

### Geometry Types

The library uses Allplan geometry types:
- `AllplanGeo.Point3D` for all coordinate operations
- `AllplanGeo.Line3D` for segment geometry
- `AllplanGeo.Polyline3D` for path geometry

### Distance Calculations

Distance calculations follow Allplan patterns:
- Euclidean distance for point-to-point
- Perpendicular distance for point-to-segment
- Tolerances specified in millimeters

### Properties Pattern

Property updates follow Allplan `CommonProperties` pattern:
- Properties are updated on metadata objects
- Changes are synchronized with geometry
- Undo/redo support is automatic

## Undo/Redo Support

All editing operations automatically save state snapshots for undo:

```python
# Make changes
interactor.update_segment_properties(0, diameter=150.0)
interactor.move_point(0, 2, (1500.0, 750.0, 0.0))

# Undo last operation
if interactor.can_undo():
    interactor.undo()

# Cancel all changes (restore initial state)
interactor._handle_cancel()
```

## Common Workflows

### Workflow 1: Update Pipe Diameters for Installation Type

```python
# Change all pluvial pipes to 150mm
segments = interactor.get_segments()
updates = []
for idx, seg in enumerate(segments):
    if seg.system == "Pluvial":
        updates.append((idx, {
            'diameter': 150.0,
            'section_type': '150mm',
            'label': f'D150 {seg.system[0]}'
        }))

count = interactor.batch_update_segments(updates)
print(f"Updated {count} pluvial segments to 150mm")
```

### Workflow 2: Add Breakpoints for Fixtures

```python
# Mark specific points as bifurcations for branch connections
fixture_points = [3, 7, 12, 18]  # Point indices where fixtures connect
for point_idx in fixture_points:
    interactor.mark_as_breakpoint(
        path_idx=0,
        point_idx=point_idx,
        role=PBL.CAPTURE_ROLE_BIFURCACION
    )
```

### Workflow 3: Adjust Path Geometry

```python
# Move multiple points to adjust path route
adjustments = [
    (2, (1200.0, 500.0, 0.0)),
    (3, (1500.0, 750.0, 0.0)),
    (4, (2000.0, 1000.0, 100.0))
]

for point_idx, new_pos in adjustments:
    interactor.move_point(path_idx=0, point_idx=point_idx, new_point=new_pos)
```

### Workflow 4: Split Long Segments

```python
# Split segments longer than threshold
segments = interactor.get_segments_for_path(0)
max_length = 5000.0  # mm

for seg_idx, seg in enumerate(segments):
    length = PBL.get_segment_length(seg)
    if length > max_length:
        # Calculate midpoint
        p0, p1 = seg.points[0], seg.points[1]
        mid_x = (p0[0] + p1[0]) / 2
        mid_y = (p0[1] + p1[1]) / 2
        mid_z = (p0[2] + p1[2]) / 2
        
        # Split at midpoint
        interactor.split_segment(
            path_idx=0,
            seg_idx=seg_idx,
            split_point=(mid_x, mid_y, mid_z)
        )
```

## Error Handling

All methods return `bool` for success/failure:

```python
success = interactor.update_segment_properties(0, diameter=150.0)
if not success:
    print("Failed to update segment - check index and parameters")

success = interactor.move_point(0, 999, (0, 0, 0))
if not success:
    print("Invalid point index")
```

Enable debug mode for detailed error messages:

```python
interactor._debug = True
# Now all operations will print debug information
```

## Best Practices

1. **Always check return values**: Methods return `bool` to indicate success
2. **Use undo/redo**: Save state before making multiple changes
3. **Validate indices**: Check path and segment indices before operations
4. **Batch updates**: Use `batch_update_segments()` for multiple property changes
5. **Geometry validation**: Ensure minimum segment length and point separation
6. **Custom properties**: Store installation-specific data in `segment.custom` dict
7. **Role management**: Set appropriate roles for capture/export workflows

## Integration with Installations

Installation scripts can access the interactor through the script object:

```python
def create_script_object(build_ele, script_object_data):
    script_object = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    
    # Store reference to interactor for later use
    return script_object

# In your installation logic:
interactor = script_object.script_object_interactor

# Now you can edit segments
interactor.update_segment_properties(0, diameter=installation_diameter)
```

## Additional Resources

- See `mvp_example_clean.py` for basic library usage
- See `segment_editing_example.py` for practical editing examples
- Refer to Allplan Python API documentation for geometry types
- Check `polyline_base_lib.py` source code for implementation details




