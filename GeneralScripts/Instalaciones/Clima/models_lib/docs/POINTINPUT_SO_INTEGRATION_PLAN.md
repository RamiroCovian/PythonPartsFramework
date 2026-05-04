# PointInput_SO Integration Plan for polyline_base_lib.py

## Executive Summary

This document analyzes `PointInput_SO.py` and outlines how its functionality can be integrated into `polyline_base_lib.py`. The analysis reveals that `polyline_base_lib.py` already has partial capture mode support, but needs enhancements to fully match `PointInput_SO.py`'s workflow.

**Important Context:** The integration must also support **PythonPart groups** and **edit mode**, allowing users to click on existing PythonPart groups after creation to modify attributes and geometry. This affects how immediate polyline creation should work in capture mode.

---

## 1. Analysis of PointInput_SO.py

### 1.1 Core Functionality

`PointInput_SO.py` implements a **point capture workflow** with the following key features:

#### **Architecture:**
- **ScriptObject**: `PointInputSO` (extends `BaseScriptObject`)
- **Interactor**: `PointInputSOInteractor` (handles all user interaction)
- **Data Model**: `Capture` dataclass stores point information

#### **Key Features:**

1. **Role-Based Point Capture**
   - Roles: `Inicial (0)`, `Paso (1)`, `Bifurcación (2)`, `Final (3)`
   - Each point captured with role, path_id, segment_id, and color_id

2. **Path-Based Organization**
   - Points grouped by `PathId` (from palette parameter)
   - Multiple paths can be captured in one session
   - Color automatically synced with PathId (color = PathId, clamped 1-255)

3. **Auto-Commit on Final Role**
   - When a point with role `Final (3)` is clicked:
     - Automatically creates unified Polyline2D and Polyline3D for that PathId
     - Exports JSON for that PathId (merges with existing JSON)
     - Creates polylines in document immediately

4. **JSON Export**
   - Single JSON file: `route_groups_XXXXXXXX.json` on Desktop
   - Merges by PathId (multiple paths in one file)
   - Structure: `{"path_id": N, "iniciales": [...], "intermedios": [...], "finales": [...]}`
   - Points grouped by role within each path

5. **Polyline Creation Logic**
   - Splits captures into "runs" delimited by roles:
     - `Inicial` starts a new run
     - `Paso`/`Bifurcación` continue current run
     - `Final` closes current run
   - Creates one Polyline2D and one Polyline3D per run
   - Deduplicates consecutive duplicate points

6. **Fallback on Cancel (ESC)**
   - `on_cancel_function()` finalizes all pending paths
   - Creates polylines and exports JSON for all captured paths

7. **Optional Features**
   - `FinishNow` parameter: manually trigger finalization of current path
   - Point symbols: optional creation of 3D symbols at capture points
   - Color synchronization: CommonProp.Color synced with PathId

### 1.2 Palette Parameters Required

```python
# Required parameters in .pyp file:
PathId: int (default: 1)
SegmentId: int (default: 1)
PointRole: int/string (0="Inicial", 1="Paso", 2="Bifurcacion", 3="Final")
EnableAssistWndClick: bool
EnableZCoordinate: bool
EnableUndoStep: bool
SetProjectionBase0: bool
CommonProp: CommonProperties
CreateSymbol: bool (optional)
SymbolCommonProps: CommonProperties (optional)
FinishNow: bool (optional, triggers finalization)
```

### 1.3 Key Methods

**PointInputSO:**
- `start_input()`: Creates interactor
- `start_next_input()`: Cleanup, finalizes all paths
- `modify_element_property()`: Handles palette changes

**PointInputSOInteractor:**
- `start_input(coord_input)`: Initializes CoordinateInput with flags
- `process_mouse_msg()`: Handles clicks, captures points
- `_export_json_for_path(pid)`: Exports/merges JSON for one path
- `_create_unified_polylines_for_path(pid)`: Creates 2D/3D polylines
- `_finish_all_paths()`: Finalizes all pending paths
- `_capture_split_runs()`: Splits captures into runs by roles

---

## 2. Current State of polyline_base_lib.py

### 2.1 Existing Capture Mode Support

**Good News:** `polyline_base_lib.py` already has partial capture mode implementation!

#### **Already Implemented:**

1. **CapturePoint Dataclass** (lines 414-445)
   - Similar structure to `PointInput_SO.Capture`
   - Includes: point, path_id, segment_id, role, color_id, order_index
   - Additional fields: diameter, system, section_type, exported, element_key, installation

2. **Capture Configuration** (lines 486-490)
   ```python
   enable_capture_mode: bool = False
   capture_auto_commit_on_final: bool = True
   capture_auto_export_json: bool = True
   capture_finish_on_cancel: bool = True
   capture_json_path: Optional[str] = None
   ```

3. **Capture Methods in PolylineInteractor** (lines 1451-1754)
   - `_capture_enabled()`: Check if capture mode active
   - `_capture_get_path_id()`, `_capture_get_segment_id()`, `_capture_get_point_role()`
   - `_capture_handle_left_click()`: Handles point capture
   - `_capture_finalize_path()`: Finalizes one path
   - `_capture_split_runs()`: Splits into runs by roles
   - `_capture_store_run()`: Stores finalized runs
   - `finalize_capture_on_shutdown()`: Cleanup on exit

4. **JSON Export Function** (likely exists, need to verify)
   - `export_capture_records_to_json()` referenced in line 1655

### 2.2 Gaps and Differences

#### **Missing/Incomplete Features:**

1. **Immediate Polyline Creation** ⚠️ **PRIMARY GAP**
   - `PointInput_SO` creates Polyline2D/3D **immediately** when Final role clicked
   - `polyline_base_lib` stores runs to `saved_paths` but does NOT create polylines immediately
   - **Need:** `_capture_create_polylines_for_path()` method to create polylines immediately
   - **Location:** Call from `_capture_finalize_path()` when `capture_auto_commit_on_final == True`

2. **JSON Export Structure** ✅ **ALREADY MATCHES**
   - `PointInput_SO` uses: `{"path_id": N, "iniciales": [], "intermedios": [], "finales": []}`
   - `polyline_base_lib` uses **exact same structure** (verified in `export_capture_records_to_json()`)
   - Both merge by PathId in single file on Desktop

3. **Color Synchronization** ✅ **IMPLEMENTED**
   - `PointInput_SO` syncs CommonProp.Color with PathId automatically
   - `polyline_base_lib` has `_capture_apply_color_to_commonprops()` 
   - **Need to verify:** Called in `start_input()` and when PathId changes

4. **CoordinateInput Flags** ✅ **IMPLEMENTED**
   - `PointInput_SO` sets flags in `start_input()`:
     - `EnableAssistWndClick`, `EnableZCoord`, `EnableUndoStep`, `SetProjectionBase0`
   - `polyline_base_lib` has `_capture_apply_coord_flags()` (line 1505)
   - **Need to verify:** Called in `start_input()` when capture mode enabled

5. **FinishNow Parameter** ⚠️ **PARTIALLY IMPLEMENTED**
   - `PointInput_SO` supports `FinishNow` boolean to manually finalize
   - `polyline_base_lib` has `_capture_check_finish_now()` method (line 1736)
   - **Need:** Call `_capture_check_finish_now()` from `modify_element_property()` in `PolylineScriptObject`

6. **Point Symbol Creation** ✅ **IMPLEMENTED**
   - `PointInput_SO` optionally creates 3D symbols at capture points
   - `polyline_base_lib` has `_capture_create_point_symbol()` (line 1601)
   - Uses `AllplanBaseElements.CreateElements()` directly (matches pattern)

---

## 3. Integration Approach

### 3.1 Strategy: Enhance Existing Capture Mode

**Recommendation:** Enhance the existing capture mode in `polyline_base_lib.py` rather than adding a separate implementation. This maintains consistency and leverages existing infrastructure.

### 3.2 Implementation Plan

#### **Phase 1: Verify and Complete Core Features**

1. **Verify JSON Export**
   - Check if `export_capture_records_to_json()` exists and matches `PointInput_SO` structure
   - Ensure it merges by PathId in single file
   - Location: Desktop, filename: `route_groups_XXXXXXXX.json`

2. **Add Immediate Polyline Creation**
   - Implement `_capture_create_polylines_for_path(path_id)` method
   - Creates Polyline2D and Polyline3D immediately when Final role clicked
   - Uses `_commit_elements()` to create in document
   - Should match `PointInput_SO._create_unified_polylines_for_path()`

3. **Enhance Color Synchronization**
   - Ensure `_capture_apply_color_to_commonprops()` is called:
     - On `start_input()` (when PathId changes)
     - On each point capture (if PathId changes)
   - Verify it updates both `CommonProp` and `SymbolCommonProps`

#### **Phase 2: Add Missing Features**

4. **Implement FinishNow Support**
   - Add `FinishNow` parameter handling in `modify_element_property()`
   - When `FinishNow == True`, call `_capture_finalize_path()` for current path

5. **Complete CoordinateInput Flags**
   - Verify `_capture_apply_coord_flags()` sets all flags correctly
   - Ensure flags are read from palette parameters

6. **Verify Point Symbol Creation**
   - Check `_capture_create_point_symbol()` matches `PointInput_SO` implementation
   - Ensure it respects `CreateSymbol` palette parameter

#### **Phase 3: Testing and Validation**

7. **Test Workflow**
   - Test point capture with different roles
   - Test auto-commit on Final role
   - Test JSON export and merge
   - Test ESC (cancel) finalizes all paths
   - Test FinishNow parameter
   - Test multiple paths in one session

---

## 4. Detailed Implementation Checklist

### 4.1 Immediate Polyline Creation ⚠️ **REQUIRED**

**Location:** Add method to `PolylineInteractor` class (after line 1663)

**Important:** This method should respect `CreatePythonPartGroup` setting:
- If `True`: Store data for `execute()` to create editable PythonPart (don't create immediately)
- If `False`: Create simple Polyline2D/3D immediately (matches `PointInput_SO` behavior)

```python
def _capture_create_polylines_for_path(self, path_id: int) -> None:
    """Create Polyline2D and Polyline3D for a finalized path.
    
    Behavior depends on CreatePythonPartGroup setting:
    - If False: Creates polylines immediately (matches PointInput_SO)
    - If True: Stores data for execute() to create editable PythonPart
    
    Args:
        path_id: Path identifier to create polylines for
    """
    if not self._capture_enabled() or not self.coord_input:
        return
    
    try:
        # Check if PythonPart groups are enabled
        create_pythonpart = False
        try:
            create_pythonpart_prop = getattr(self.script_object.build_ele, "CreatePythonPartGroup", None)
            if create_pythonpart_prop:
                create_pythonpart = bool(create_pythonpart_prop.value)
        except Exception:
            pass
        
        # Get all captures for this path_id (already finalized)
        captures = [c for c in self.capture_records if c.path_id == path_id]
        if not captures:
            return
        
        # Split into runs (Inicial...Final sequences)
        runs = self._capture_split_runs(captures)
        if not runs:
            runs = [captures]
        
        if create_pythonpart:
            # PythonPart mode: Data already stored by _capture_store_run()
            # execute() will create the PythonPart blueprint
            # 3D models are created separately by _create_elements_immediately()
            print(f"[CAPTURE] Path {path_id} stored for PythonPart creation (edit mode enabled)")
            return
        
        # Simple mode: Create Polyline2D/3D immediately (PointInput_SO behavior)
        doc = None
        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            return
        if not doc:
            return
        
        # Get common properties with color
        color_id = self._capture_color_from_path(path_id)
        common_prop = self._capture_get_common_props_with_color(color_id)
        
        elements = []
        
        # For each run, create Polyline2D and Polyline3D
        for run_idx, run in enumerate(runs):
            if len(run) < 2:
                continue
            
            # Deduplicate points
            deduped = self._capture_dedupe_run(run)
            if len(deduped) < 2:
                continue
            
            # Build point lists
            points_2d = []
            points_3d = []
            
            for record in deduped:
                pt = record.point
                # Extract 2D point
                points_2d.append(AllplanGeo.Point2D(pt.X, pt.Y))
                # Extract 3D point with Z
                points_3d.append(AllplanGeo.Point3D(pt.X, pt.Y, pt.Z))
            
            # Create Polyline2D
            if len(points_2d) >= 2:
                pl2d = AllplanGeo.Polyline2D()
                for p in points_2d:
                    pl2d += p
                elements.append(AllplanBasisElements.ModelElement2D(common_prop, pl2d))
            
            # Create Polyline3D
            if len(points_3d) >= 2:
                pl3d = AllplanGeo.Polyline3D()
                for p in points_3d:
                    pl3d += p
                elements.append(AllplanBasisElements.ModelElement3D(common_prop, pl3d))
        
        # Commit elements to document
        if elements:
            AllplanBaseElements.CreateElements(
                doc,
                AllplanGeo.Matrix3D(),
                elements,
                [],
                None
            )
            print(f"[CAPTURE] Created {len(elements)} polylines for path {path_id} (simple mode)")
    except Exception as e:
        print(f"[CAPTURE] Error creating polylines for path {path_id}: {e}")

def _capture_get_common_props_with_color(self, color_id: int) -> Any:
    """Get CommonProperties with specified color.
    
    Matches PointInput_SO._clone_common_with_color() behavior.
    """
    try:
        # Try to get from build_ele
        base = getattr(getattr(self.script_object.build_ele, "CommonProp", None), "value", None)
        if base is None:
            base = getattr(getattr(self.script_object.build_ele, "SymbolCommonProps", None), "value", None)
        
        if base is None:
            # Fallback: create new
            common_prop = AllplanBaseElements.CommonProperties()
            common_prop.GetGlobalProperties()
        else:
            # Clone
            try:
                common_prop = base.__class__()
                # Copy attributes
                for attr in ("Pen", "Stroke", "LineStyle", "Layer", "Transparency", "DrawOrder", "Fill", "Color"):
                    try:
                        setattr(common_prop, attr, getattr(base, attr))
                    except Exception:
                        pass
            except Exception:
                common_prop = base
        
        # Apply color
        try:
            common_prop.Color = color_id
        except Exception:
            pass
        
        return common_prop
    except Exception:
        # Ultimate fallback
        common_prop = AllplanBaseElements.CommonProperties()
        common_prop.GetGlobalProperties()
        try:
            common_prop.Color = color_id
        except Exception:
            pass
        return common_prop
```

**Integration Point:**
- Call from `_capture_finalize_path()` when `self.config.capture_auto_commit_on_final == True`
- Add after line 1652 (after storing runs, before JSON export)
- **Note:** If PythonPart groups are enabled, this method will return early and let `execute()` handle creation

**PythonPart Group Workflow:**
- When `CreatePythonPartGroup == True`:
  1. `_capture_store_run()` stores data in `saved_paths` and `saved_segments`
  2. `_capture_create_polylines_for_path()` returns early (no immediate creation)
  3. User finalizes session → `on_cancel_function()` returns `CREATE_ELEMENTS`
  4. Allplan calls `execute()` → creates PythonPart blueprint (simple lines)
  5. User can click PythonPart group to edit attributes

### 4.2 JSON Export Verification ✅ **ALREADY COMPLETE**

**Verified:**
- ✅ `export_capture_records_to_json()` exists at line 5791
- ✅ Uses structure: `{"path_id": N, "iniciales": [], "intermedios": [], "finales": []}`
- ✅ Merges by PathId in single file (uses index dictionary)
- ✅ Writes to Desktop via `ensure_route_groups_json_path()` (creates random filename)
- ✅ Marks records as exported after writing

**No action needed** - JSON export fully matches `PointInput_SO` implementation.

### 4.3 FinishNow Parameter ⚠️ **NEEDS INTEGRATION**

**Add to `modify_element_property()` in `PolylineScriptObject`:**

**Location:** Find `modify_element_property()` method in `PolylineScriptObject` class

```python
def modify_element_property(self, *args):
    """Handle palette property changes."""
    # ... existing code ...
    
    # Add this check (after existing property handlers):
    if len(args) >= 2:
        name = args[0] if len(args) == 2 else args[1]
        value = args[1] if len(args) == 2 else args[2]
        
        if name == PALETTE_PROP_FINISH_NOW and bool(value):
            if self.script_object_interactor and self.script_object_interactor._capture_enabled():
                # Delegate to interactor's method
                self.script_object_interactor._capture_check_finish_now()
                return True
    
    # ... rest of existing code ...
```

**Note:** `_capture_check_finish_now()` already exists (line 1736) but needs to be called from `modify_element_property()`.

### 4.4 Color Synchronization

**Verify these calls exist:**
- `_capture_apply_color_to_commonprops()` in `start_input()` (after reading PathId)
- `_capture_apply_color_to_commonprops()` in `_capture_handle_left_click()` (if PathId changed)

### 4.5 CoordinateInput Flags

**Verify `_capture_apply_coord_flags()` sets:**
- `EnableAssistWndClick` (from palette)
- `EnableZCoord` (from palette)
- `EnableUndoStep` (from palette)
- `SetProjectionBase0` (from palette)

**Called from:** `start_input()` when capture mode enabled

---

## 5. Usage Pattern Comparison

### 5.1 PointInput_SO Usage

```python
# User workflow:
1. Set PathId = 1, PointRole = "Inicial"
2. Click point → captured
3. Set PointRole = "Paso", click more points
4. Set PointRole = "Final", click point
   → Auto-creates polylines, exports JSON
5. Set PathId = 2, PointRole = "Inicial", repeat...
6. ESC → finalizes all pending paths
```

### 5.2 polyline_base_lib Usage (Current)

```python
# User workflow (if capture mode enabled):
1. Set PathId = 1, PointRole = "Inicial"
2. Click point → captured
3. Set PointRole = "Paso", click more points
4. Set PointRole = "Final", click point
   → Stores run, exports JSON (but no immediate polylines?)
5. ESC → finalizes all paths (but creates polylines?)
```

**Key Difference:** `PointInput_SO` creates polylines **immediately** on Final click, while `polyline_base_lib` may defer creation.

---

## 6. Recommendations

### 6.1 Priority Actions

1. **HIGH:** Implement polyline creation (`_capture_create_polylines_for_path()`) ⚠️
   - This is the main missing feature
   - Add method to `PolylineInteractor` class
   - **Support both modes:** Simple elements (PointInput_SO style) and PythonPart groups (edit mode)
   - Check `CreatePythonPartGroup` parameter to determine behavior
   - Call from `_capture_finalize_path()` when auto-commit enabled

2. **HIGH:** Add FinishNow parameter support in `modify_element_property()` ⚠️
   - Method `_capture_check_finish_now()` exists but not called
   - Add handler in `PolylineScriptObject.modify_element_property()`

3. **MEDIUM:** Verify color synchronization timing ✅
   - Method exists, verify it's called at right times

4. **MEDIUM:** Verify coordinate input flags are applied ✅
   - Method exists, verify it's called in `start_input()`

5. **FUTURE:** Implement edit mode for PythonPart groups 📋
   - Load existing PythonPart data into `saved_paths`/`saved_segments`
   - Allow attribute modification (diameter, system, etc.)
   - Regenerate 3D models with updated attributes
   - **Note:** This is separate from PointInput_SO integration but should be planned

### 6.2 Backward Compatibility

- Ensure existing non-capture workflows are unaffected
- Capture mode is opt-in via `config.enable_capture_mode = True`
- All new features gated by `_capture_enabled()` check

### 6.3 Testing Strategy

1. **Unit Tests:**
   - Test `_capture_split_runs()` with various role sequences
   - Test JSON export structure
   - Test polyline creation logic

2. **Integration Tests:**
   - Full workflow: capture points → Final role → verify polylines created
   - Multiple paths in one session
   - ESC finalizes all paths

3. **Comparison Tests:**
   - Capture same points in `PointInput_SO` and `polyline_base_lib`
   - Compare JSON output structure
   - Compare created polyline geometry

---

## 7. Files to Modify

### 7.1 Primary File
- `2025/Modelat/Instalaciones/Clima/models_lib/py/polyline_base_lib.py`
  - Add `_capture_create_polylines_for_path()` method (with PythonPart group support)
  - Add `_capture_get_common_props_with_color()` helper method
  - Enhance `_capture_finalize_path()` to call polyline creation
  - Add FinishNow support in `modify_element_property()`
  - Verify/complete JSON export function (already done ✅)

### 7.2 Supporting Files (if needed)
- Verify if JSON export function exists in separate utility module (already verified ✅)
- Check if `_commit_elements()` helper exists (not needed - use `AllplanBaseElements.CreateElements()` directly ✅)

### 7.3 Future Files (Edit Mode)
- **Future work:** Add functions to load existing PythonPart group data
- **Future work:** Add edit mode entry point (detect click on PythonPart group)
- **Future work:** Add attribute modification UI/handlers

---

## 8. Questions Resolved ✅

1. **JSON Export Function:** ✅ **RESOLVED**
   - `export_capture_records_to_json()` exists at line 5791
   - **Matches `PointInput_SO` structure exactly:**
     - Uses `{"path_id": N, "iniciales": [], "intermedios": [], "finales": []}`
     - Merges by PathId in single file
     - Writes to Desktop via `ensure_route_groups_json_path()`
     - Marks records as exported after writing

2. **Element Creation:** ✅ **RESOLVED**
   - Uses `AllplanBaseElements.CreateElements()` directly (line 1629)
   - No separate `_commit_elements()` helper needed
   - Pattern: `AllplanBaseElements.CreateElements(doc, matrix, elements, [], None)`

3. **Immediate vs Deferred Creation:** ⚠️ **NEEDS IMPLEMENTATION**
   - **Current behavior:** `_capture_finalize_path()` stores runs to `saved_paths` but does NOT create polylines immediately
   - **PointInput_SO behavior:** Creates Polyline2D and Polyline3D immediately when Final role clicked
   - **Action needed:** Add `_capture_create_polylines_for_path()` method to create polylines immediately

4. **Palette Parameters:** ✅ **MOSTLY RESOLVED**
   - Constants defined: `PALETTE_PROP_PATH_ID`, `PALETTE_PROP_SEGMENT_ID`, `PALETTE_PROP_POINT_ROLE`, `PALETTE_PROP_FINISH_NOW`
   - `_capture_check_finish_now()` method exists (line 1736) but needs to be called from `modify_element_property()`
   - Need to verify these are in the `.pyp` file

---

## 9. PythonPart Groups and Edit Mode Integration

### 9.1 Current Library Support

The `polyline_base_lib.py` already supports PythonPart groups:

- **`CreatePythonPartGroup`** palette parameter (line 915): Controls whether elements are created as editable PythonParts
- **`execute()` method** (line 669): Creates "blueprint" elements (simple lines) that become editable PythonParts
- **Transactional mode**: `on_cancel_function()` returns `CREATE_ELEMENTS`, then Allplan calls `execute()` to create editable PythonParts

### 9.2 Edit Mode Workflow

**Current Pattern:**
1. User creates polyline → `_create_elements_immediately()` creates 3D models
2. User finalizes → `execute()` creates PythonPart blueprint (simple lines)
3. Allplan creates editable PythonPart group
4. User can double-click PythonPart group to edit attributes

**Desired Enhancement:**
- After creating polylines via capture mode, user should be able to:
  - Click on the PythonPart group
  - Enter edit mode
  - Modify attributes (diameter, system, section type, etc.)
  - Modify geometry (move vertices, add/remove points)

### 9.3 Impact on Capture Mode Integration

**Decision Required:** When `PointInput_SO`-style capture creates polylines immediately (on Final role click), should it:

**Option A: Create Simple Polyline2D/3D Elements** (matches `PointInput_SO` exactly)
- ✅ Matches `PointInput_SO` behavior exactly
- ✅ Simple, immediate creation
- ❌ Not editable as PythonPart groups
- ❌ Cannot modify attributes later

**Option B: Create PythonPart Groups** (enables edit mode)
- ✅ Enables edit mode (click to modify)
- ✅ Can modify attributes after creation
- ✅ Consistent with library's PythonPart workflow
- ❌ More complex (requires `execute()` pattern)
- ❌ Different from `PointInput_SO` behavior

**Option C: Hybrid Approach** (recommended)
- Create 3D models immediately via `_create_elements_immediately()`
- Also trigger `execute()` to create PythonPart blueprint
- User gets both: immediate visual feedback + editable PythonPart
- Best of both worlds

### 9.4 Recommended Implementation

**For `_capture_create_polylines_for_path()`:**

1. **Check `CreatePythonPartGroup` parameter:**
   - If `True`: Use transactional pattern (store data, let `execute()` create PythonPart)
   - If `False`: Create simple Polyline2D/3D immediately (matches `PointInput_SO`)

2. **When creating PythonPart groups:**
   - Store finalized runs in `saved_paths` and `saved_segments`
   - Don't create elements immediately in `_capture_create_polylines_for_path()`
   - Instead, trigger `execute()` pattern (return `CREATE_ELEMENTS` from cancel handler)

3. **Edit Mode Support:**
   - Ensure `saved_segments` contain full metadata (diameter, system, etc.)
   - When user clicks PythonPart group, library should:
     - Load existing segments from PythonPart
     - Populate `saved_paths` and `saved_segments`
     - Enter edit mode with existing data
     - Allow attribute modification

### 9.5 Edit Mode Implementation Checklist

**Future Work (not in current scope, but should be planned):**

1. **Load Existing PythonPart Data:**
   - Function to read segments from existing PythonPart group
   - Populate `saved_paths` and `saved_segments` from PythonPart
   - Restore metadata (diameter, system, section_type, etc.)

2. **Edit Mode Entry:**
   - Detect when user clicks on existing PythonPart group
   - Initialize interactor with existing data
   - Show existing polylines in edit mode

3. **Attribute Modification:**
   - Allow changing diameter, system, section_type per segment
   - Update metadata in `saved_segments`
   - Regenerate 3D models with new attributes

4. **Geometry Modification:**
   - Already supported (drag vertices, insert points, delete segments)
   - Ensure it works with loaded PythonPart data

### 9.6 Updated Implementation Priority

Given edit mode requirements:

1. **HIGH:** Implement `_capture_create_polylines_for_path()` with PythonPart group support
2. **HIGH:** Add FinishNow parameter support
3. **MEDIUM:** Verify color synchronization timing
4. **MEDIUM:** Verify coordinate input flags
5. **FUTURE:** Implement edit mode (load from PythonPart, modify attributes)

---

## 10. Next Steps

1. **Review this plan** with the team
2. **Verify existing implementations** (JSON export, element creation helpers)
3. **Implement missing features** in priority order
4. **Test against `PointInput_SO`** to ensure compatibility
5. **Document usage** for installation scripts

---

## Appendix A: Code Snippets Reference

### PointInput_SO Key Methods (for reference)

**`_create_unified_polylines_for_path()`** (lines 281-359):
- Filters captures by path_id
- Splits into runs by roles
- Creates Polyline2D and Polyline3D per run
- Deduplicates points
- Commits to document

**`_export_json_for_path()`** (lines 230-279):
- Groups captures by role (iniciales, intermedios, finales)
- Merges with existing JSON file
- Writes to Desktop

**`_finish_all_paths()`** (lines 220-228):
- Iterates all captured path_ids
- Calls `_export_json_for_path()` and `_create_unified_polylines_for_path()` for each

---

---

## 11. Summary: Key Design Decisions

### 11.1 PythonPart Groups vs Simple Elements

**Decision Point:** When capture mode creates polylines (on Final role click), should it create:
- **Simple Polyline2D/3D** (matches `PointInput_SO` exactly)
- **PythonPart Groups** (enables edit mode)

**Recommendation:** Support both via `CreatePythonPartGroup` parameter:
- `False`: Create simple elements immediately (PointInput_SO behavior)
- `True`: Store data for `execute()` to create editable PythonPart (enables edit mode)

### 11.2 Edit Mode Integration

**Current State:**
- Library supports PythonPart groups via `execute()` method
- User can create polylines and get editable PythonPart groups

**Future Enhancement Needed:**
- Load existing PythonPart group data when user clicks to edit
- Allow attribute modification (diameter, system, section_type)
- Regenerate 3D models with updated attributes

**Impact on Capture Mode:**
- Capture mode should store full metadata in `saved_segments` (already done ✅)
- When creating PythonPart groups, ensure metadata is preserved
- Edit mode can then read and modify this metadata

### 11.3 Implementation Priority

**Immediate (PointInput_SO Integration):**
1. ✅ Add `_capture_create_polylines_for_path()` with PythonPart group support
2. ✅ Add FinishNow parameter handler
3. ✅ Verify color/coordinate flags timing

**Future (Edit Mode Enhancement):**
1. 📋 Load PythonPart group data into library
2. 📋 Attribute modification UI/handlers
3. 📋 Regenerate 3D models with updated attributes

---

**Document Version:** 1.1  
**Date:** 2025  
**Author:** Analysis for CLIMA library integration  
**Updated:** Added PythonPart groups and edit mode considerations
