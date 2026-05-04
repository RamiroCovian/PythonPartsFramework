# Testing Guide: PointInput_SO Integration

## What Does PointInput_SO Do? (Simple Explanation)

**PointInput_SO** is a point capture system that lets you:
1. **Click points** one by one to build a polyline
2. **Label each point** with a "role" (Inicial, Paso, Bifurcación, Final)
3. **Group points** by "PathId" (like Route 1, Route 2, etc.)
4. **Auto-create polylines** when you click a "Final" point
5. **Export to JSON** file on your Desktop

**Think of it like this:**
- You're marking waypoints along a route
- Each point has a purpose: Start (Inicial), Middle (Paso), Branch (Bifurcación), End (Final)
- When you mark "Final", it automatically draws the polyline
- Different routes can have different PathIds (1, 2, 3...)

---

## Step-by-Step Testing Guide

### Prerequisites

1. **Copy files to Allplan:**
   - Copy `polyline_base_lib.py` to your Allplan PythonParts folder
   - Copy your `.pyp` file (e.g., `mvp_example.pyp`) to the same folder
   - Delete old versions if they exist

2. **Verify your `.pyp` file has these parameters:**
   - `PathId` (Integer, default: 1)
   - `SegmentId` (Integer, default: 1)
   - `PointRole` (RadioButtonGroup: Inicial, Paso, Bifurcación, Final)
   - `CreatePythonPartGroup` (CheckBox, optional - for edit mode)
   - `FinishNow` (CheckBox, optional - manual finalization)

---

## Test 1: Basic Point Capture (Simple Mode)

### Setup:
1. Open Allplan
2. Load your PythonPart (the one using `polyline_base_lib.py`)
3. In the palette, set:
   - `PathId` = 1
   - `PointRole` = "Inicial"
   - `CreatePythonPartGroup` = **False** (for simple elements)
   - Enable capture mode (if your config has `enable_capture_mode`)

### Test Steps:

1. **Click first point (Inicial):**
   - Set `PointRole` = "Inicial"
   - Click a point in the drawing
   - **Expected:** Point is captured, color changes to match PathId (color 1)

2. **Click middle points (Paso):**
   - Set `PointRole` = "Paso"
   - Click 3-4 more points
   - **Expected:** Each point is captured, polyline preview shows

3. **Click final point (Final):**
   - Set `PointRole` = "Final"
   - Click the last point
   - **Expected:** 
     - Polyline2D and Polyline3D are **created immediately** in the document
     - JSON file is exported to Desktop (`route_groups_XXXXXXXX.json`)
     - Message shows "Path 1 finalizado"

4. **Check results:**
   - Look in the drawing: You should see polylines created
   - Check Desktop: JSON file should exist
   - Open JSON file: Should contain path_id=1 with your points

---

## Test 2: Multiple Paths

### Test Steps:

1. **Create Path 1:**
   - Set `PathId` = 1
   - Set `PointRole` = "Inicial", click point
   - Set `PointRole` = "Paso", click 2 points
   - Set `PointRole` = "Final", click point
   - **Expected:** Path 1 polylines created

2. **Create Path 2:**
   - Set `PathId` = 2 (color should change to color 2)
   - Set `PointRole` = "Inicial", click point
   - Set `PointRole` = "Paso", click 2 points
   - Set `PointRole` = "Final", click point
   - **Expected:** Path 2 polylines created (different color)

3. **Check JSON:**
   - Open the JSON file on Desktop
   - **Expected:** Should contain BOTH path_id=1 and path_id=2
   - Structure: `[{"path_id": 1, ...}, {"path_id": 2, ...}]`

---

## Test 3: PythonPart Groups (Edit Mode)

### Setup:
1. Set `CreatePythonPartGroup` = **True**
2. Set `PathId` = 1
3. Set `PointRole` = "Inicial"

### Test Steps:

1. **Capture points:**
   - Click Inicial point
   - Click 2-3 Paso points
   - Click Final point
   - **Expected:** 
     - Data is stored (not created immediately)
     - Message: "Path 1 stored for PythonPart creation"

2. **Finalize session:**
   - Press ESC or click finalize button
   - **Expected:**
     - `execute()` is called
     - PythonPart group is created (editable)
     - 3D models are created separately

3. **Test edit mode:**
   - Double-click the PythonPart group
   - **Expected:** Should open in edit mode (if implemented)
   - You can modify attributes (diameter, system, etc.)

---

## Test 4: FinishNow Parameter

### Test Steps:

1. **Start capturing:**
   - Set `PathId` = 1
   - Set `PointRole` = "Inicial", click point
   - Set `PointRole` = "Paso", click 2 points
   - **Don't click Final yet!**

2. **Use FinishNow:**
   - Set `FinishNow` = **True** (checkbox)
   - **Expected:**
     - Path 1 is finalized immediately
     - Polylines are created
     - JSON is exported
     - `FinishNow` resets to False

---

## Test 5: ESC Key (Cancel/Finalize All)

### Test Steps:

1. **Capture multiple paths without Final:**
   - Path 1: Inicial + 2 Paso points (no Final)
   - Change `PathId` = 2
   - Path 2: Inicial + 2 Paso points (no Final)

2. **Press ESC:**
   - **Expected:**
     - All pending paths are finalized
     - Polylines created for both paths
     - JSON exported with both paths

---

## What to Check (Verification)

### ✅ Success Indicators:

1. **In Drawing:**
   - Polylines appear when Final is clicked
   - Different colors for different PathIds
   - Polylines are visible and selectable

2. **In Console/Output:**
   - Messages like: `[CAPTURE] Created X polylines for path Y`
   - Messages like: `Path X finalizado (Final)`
   - No error messages

3. **In JSON File (Desktop):**
   - File exists: `route_groups_XXXXXXXX.json`
   - Contains structure:
     ```json
     [
       {
         "path_id": 1,
         "iniciales": [...],
         "intermedios": [...],
         "finales": [...]
       }
     ]
     ```
   - Points have correct coordinates
   - Points have correct roles

4. **Color Behavior:**
   - PathId 1 → Color 1
   - PathId 2 → Color 2
   - PathId 3 → Color 3
   - (Color = PathId, max 255)

---

## Troubleshooting

### Problem: Polylines not created

**Check:**
- Is `capture_auto_commit_on_final` enabled in config?
- Is `CreatePythonPartGroup` set correctly?
- Check console for error messages
- Verify `_capture_create_polylines_for_path()` is being called

### Problem: JSON not exported

**Check:**
- Is `capture_auto_export_json` enabled in config?
- Check Desktop folder permissions
- Look for error messages in console
- Verify `export_capture_records_to_json()` is being called

### Problem: Colors not changing

**Check:**
- Is `_capture_apply_color_to_commonprops()` being called?
- Verify `PathId` parameter exists in palette
- Check if CommonProp parameter exists

### Problem: FinishNow not working

**Check:**
- Is `modify_element_property()` method in PolylineScriptObject?
- Is `PALETTE_PROP_FINISH_NOW` constant defined?
- Check console for `[SO] modify_element_property` messages

---

## Quick Test Checklist

- [ ] Test 1: Basic capture with Inicial → Paso → Final
- [ ] Test 2: Multiple paths (PathId 1, 2, 3)
- [ ] Test 3: PythonPart groups (CreatePythonPartGroup = True)
- [ ] Test 4: FinishNow parameter
- [ ] Test 5: ESC key finalizes all paths
- [ ] Verify JSON file on Desktop
- [ ] Verify polylines in drawing
- [ ] Verify colors match PathIds

---

## Example Workflow (Real Usage)

```
1. Open Allplan, load PythonPart
2. Set PathId = 1, PointRole = "Inicial"
3. Click start point of route
4. Set PointRole = "Paso"
5. Click waypoints along route (3-5 points)
6. Set PointRole = "Final"
7. Click end point
   → Polyline created! JSON exported!
8. Set PathId = 2 (for next route)
9. Repeat steps 3-7 for second route
10. Press ESC to finalize any remaining paths
11. Check Desktop for JSON file with all routes
```

---

## Configuration Needed in Your Code

Make sure your installation script enables capture mode:

```python
from Clima.models_lib.py import polyline_base_lib

# Create config
config = polyline_base_lib.PolylineBaseConfig(
    enable_capture_mode=True,              # Enable capture mode
    capture_auto_commit_on_final=True,     # Create polylines on Final click
    capture_auto_export_json=True,         # Export JSON automatically
    capture_finish_on_cancel=True,         # Finalize all on ESC
)

# Apply to script object
script_object.set_config(config)
```

---

**Good luck testing!** 🚀

If something doesn't work, check the console output for error messages and compare with the expected behavior above.
