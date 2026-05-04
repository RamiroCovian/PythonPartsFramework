# -*- coding: utf-8 -*-
"""MVP Polyline Example - Comprehensive test of polyline_base_lib functionality.

This example demonstrates and tests all major features of the polyline library:
- Basic polyline creation with angle limiting and Z coordinates
- VERTICAL LINES: Full support for 3D vertical segments (drainage stacks, risers)
- Capture mode with point roles (inicial, paso, bifurcacion, final)
- Segment metadata creation and management
- Element creation hooks with custom geometry
- Transactional finalize mode
- Segment utility functions (length, direction, closest point)
- JSON export/import capabilities
- Result extraction

3D Models Created (like saneamiento installations):
- GROUP 1: Cylindrical pipes along segments
- GROUP 2: Junction boxes/manholes at vertices
- GROUP 3: Fittings (tees, elbows) at intermediate points
- GROUP 4: Flow direction arrows
- GROUP 5: Special vertical pipe markers (level indicators)

This demonstrates creating multiple Python parts and element groups
as commonly used in drainage (saneamiento) installations.
"""

from __future__ import annotations
from typing import List, Tuple
import sys
import os
import math

def _add_libreria_py_to_sys_path():
    """Add Instalaciones/Libreria to sys.path (shared library location)."""
    if not __file__:
        return
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.basename(current).lower() == "instalaciones":
            libreria_root = os.path.join(current, "Libreria")
            if os.path.isdir(libreria_root) and libreria_root not in sys.path:
                sys.path.insert(0, libreria_root)
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

def _add_local_models_lib_py():
    """Fallback local path for development (Clima/models_lib/py)."""
    if not __file__:
        return
    script_dir = os.path.dirname(__file__)
    lib_py_dir = os.path.abspath(os.path.join(script_dir, "..", "py"))
    if lib_py_dir not in sys.path:
        sys.path.insert(0, lib_py_dir)

_add_libreria_py_to_sys_path()
_add_local_models_lib_py()

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
    from CreateElementResult import CreateElementResult
    ALLPLAN_AVAILABLE = True
except Exception:
    ALLPLAN_AVAILABLE = False

# Import polyline library with robust path handling
print("[mvp_example] Importing polyline_base_lib...")
try:
    import polyline_base_lib as PBL
    from polyline_base_lib import SegmentMetadata
    print("[mvp_example] ✓ polyline_base_lib imported successfully!")
    
    # Ensure model builders are in path
    if hasattr(PBL, 'ensure_models_in_path'):
        PBL.ensure_models_in_path()
except ImportError as e:
    print(f"[mvp_example] ERROR: Could not import polyline_base_lib: {e}")
    print(f"[mvp_example] Current __file__: {__file__ if '__file__' in globals() else 'N/A'}")
    print(f"[mvp_example] sys.path: {sys.path[:3]}...")  # Show first 3 entries
    raise

# Import real 3D models with validation
MODELS_AVAILABLE = False
TuboPVCConFlecha = None
CodoBasico = None
Manguito = None

model_imports = [
    ("Tub_PVC_TricapaV_005", "TuboPVCConFlecha", "Tube model"),
    ("Colze_basic_001", "CodoBasico", "Elbow model"),
    ("ManguitoBasic_003", "Manguito", "Coupling model"),
]

for module_name, class_name, description in model_imports:
    # Check if module exists first
    exists, path = PBL.validate_model_builder_exists(module_name) if hasattr(PBL, 'validate_model_builder_exists') else (True, None)
    
    if not exists:
        print(f"[mvp_example] ✗ {module_name} not found at expected location")
        continue
    
    try:
        module = __import__(module_name)
        model_class = getattr(module, class_name, None)
        if model_class:
            globals()[class_name] = model_class
            print(f"[mvp_example] ✓ Imported {class_name} ({description})")
            MODELS_AVAILABLE = True
        else:
            print(f"[mvp_example] ✗ {class_name} not found in {module_name}")
    except Exception as e:
        print(f"[mvp_example] ✗ {class_name} import failed: {e}")

if MODELS_AVAILABLE:
    print("[mvp_example] 3D models loaded - will create real geometry!")
else:
    print("[mvp_example] No 3D models available - will use fallback geometry")

# ===== CONFIGURATION =====
# Keep angle limiting OFF - causes visual artifacts with preview
USE_CAPTURE_MODE = False
CONFIG = PBL.PolylineBaseConfig(
    limit_angles=False,  # DISABLE - causes weird preview lines
    # Drawing mode options:
    # - PBL.DRAWING_MODE_2D: 2D plan view (Z forced to 0) - CURRENT MVP SETTING
    # - PBL.DRAWING_MODE_3D_FREE: Full 3D - for vertical polylines (drainage stacks, risers), diagonal segments
    # - PBL.DRAWING_MODE_3D_CONSTRAINED: 3D with Z jump protection (prevents accidental large jumps)
    drawing_mode=PBL.DRAWING_MODE_2D,  # 2D mode for plan view (current MVP)
    enable_z_coordinate=False,  # DEPRECATED: Use drawing_mode instead (kept for backward compatibility)
    allow_insert_point_mode=False,  # Disable insert mode
    enable_capture_mode=False,  # Disable capture mode
    capture_auto_commit_on_final=False,
    capture_auto_export_json=False,
    
    # Enable installation registry
    registry_auto_load=False,  # Manual registration for testing
    sync_palette_with_registry=True,  # Sync InstallationName field
    default_installation="Pluvial_Test",
    installation_name_property="InstallationName",
    
    # System-to-diameter mapping: Maps system values (0=Pluvial, 1=Fecal) to diameter property names
    system_diameter_mapping={
        0: "DiametroAplicarPluvial",  # System 0 (Pluvial) -> DiametroAplicarPluvial property
        1: "DiametroAplicarFecal"     # System 1 (Fecal) -> DiametroAplicarFecal property
    },
)

# TO TEST VERTICAL LINES:
# 1. Enable Z coordinate input (already enabled above)
# 2. When placing points, use different Z values (or use Allplan's Z input)
# 3. The script will automatically detect vertical segments (dx,dy < 10mm, dz > 10mm)
# 4. Special vertical pipe markers will be created for vertical segments

# Global state for demonstrating features
segment_counter = 0
total_length = 0.0
_global_script_object = None  # Store reference for button handlers
_previous_segment = None  # Track previous segment for elbow detection
_finalized_polylines = []  # Store finalized polylines for bifurcation


def check_allplan_version(_build_ele, _version):
    """Required by Allplan framework."""
    return True


def create_script_object(build_ele, script_object_data):
    """Create and configure the script object with all library features.
    
    This demonstrates:
    - Initialization with configuration
    - Element creation hooks
    - Transactional finalize mode
    - Reading palette values (diameter, system type)
    - Event handling for palette buttons
    - Automatic elbows at corners
    - Bifurcation support (continue from existing endpoints)
    """
    global _global_script_object, _previous_segment, segment_counter
    
    # Reset tracking for new interaction
    _previous_segment = None
    segment_counter = 0
    
    # Set fusion tolerance from palette if available
    fusion_tol = getattr(build_ele, "FusionTolerance", None)
    if fusion_tol:
        PBL.FUSION_TOLERANCE_MM = float(fusion_tol.value)
        print(f"[mvp] Set fusion tolerance to {PBL.FUSION_TOLERANCE_MM}mm")
    
    # Register test installations (optional - only if test_installations.py exists)
    # This is for development/testing purposes only
    try:
        from test_installations import register_test_installations
        register_test_installations()
    except ImportError:
        pass  # test_installations.py doesn't exist - this is normal, not an error
    except Exception as ex:
        if _debug:
            print(f"[mvp] Error registering test installations: {ex}")
    
    # Initialize with configuration
    script_object = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    
    # Initialize segment indices list (data-driven approach)
    _update_segment_indices_list(build_ele, len(script_object.saved_segments))
    
    # Store global reference for button handlers
    _global_script_object = script_object
    
    # Register our event handler with the library (generic hook system)
    script_object.event_handler_hook = on_control_event
    print("[mvp] Registered event_handler_hook with library")
    
    # Attach element creation hook to test custom geometry creation
    def hook(seg_meta, common_prop):
        # Read palette values for diameter
        system_type = getattr(build_ele, "Saneamiento", None)
        system_value = system_type.value if system_type else 0
        
        # Use "NewDiameter" as the single diameter control (consolidated)
        # Priority: 1) Segment's custom diameter (from Update Segment), 2) NewDiameter palette value, 3) Default
        if seg_meta.diameter and seg_meta.diameter > 0:
            # Segment has a custom diameter - use it (from Update Segment)
            diameter = seg_meta.diameter
            print(f"[mvp] Using segment's custom diameter: {diameter}mm")
        else:
            # Use NewDiameter from palette (single consolidated control)
            new_diam_prop = getattr(build_ele, "NewDiameter", None)
            if new_diam_prop and new_diam_prop.value > 0:
                diameter = float(new_diam_prop.value)
                print(f"[mvp] Using NewDiameter from palette: {diameter}mm")
            else:
                # Fallback to system-specific defaults (for backward compatibility)
                if system_value == 0:  # Pluvial
                    diameter = 110.0
                else:  # Fecal
                    diameter = 40.0
                print(f"[mvp] Using default diameter for system {system_value}: {diameter}mm")
            # Set it in segment metadata for future reference
            seg_meta.diameter = diameter
        
        seg_meta.system = "Pluvial" if system_value == 0 else "Fecal"
        
        return _create_demo_elements(seg_meta, common_prop, build_ele)
    
    script_object.element_creation_hook = hook
    
    # NEW: Set up fitting hooks (after interactor is initialized)
    if script_object.script_object_interactor:
        interactor = script_object.script_object_interactor
        
        # Import fitting implementations
        try:
            import sys
            import os
            # Add current directory to path if not already there
            script_dir = os.path.dirname(__file__) if __file__ else os.getcwd()
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            
            from mvp_example_fittings import (
                create_elbow_fitting,
                create_reducer_fitting
            )
            
            # Wire the hooks
            interactor.elbow_hook = create_elbow_fitting
            interactor.reducer_hook = create_reducer_fitting
            
            print("[mvp] ✓ Fitting hooks installed")
        except ImportError as e:
            print(f"[mvp] ✗ Could not load fittings: {e}")
    
    # Enable transactional finalize for proper element creation
    PBL.enable_transactional_finalize(script_object)
    
    return script_object


def on_control_event(build_ele, event_id: int):
    """Handle palette button events (EventIds).
    
    This is called by Allplan for button clicks.
    EventIds:
    - 2001: Update Segment
    - 2002: Delete Segment
    
    Returns:
        True if event was handled, False/None to let library handle it
    """
    global _global_script_object
    
    print(f"[mvp_example] on_control_event called: event_id={event_id}")
    
    if event_id == 2001:  # Update Segment
        print(f"[mvp_example] Update Segment button clicked (EventId 2001)")
        return _handle_update_segment(build_ele)
    
    elif event_id == 2002:  # Delete Segment
        print(f"[mvp_example] Delete Segment button clicked (EventId 2002)")
        return _handle_delete_segment(build_ele)

    elif event_id == 2050:  # Export to JSON
        print(f"[mvp_example] Export JSON button clicked (EventId 2050)")
        return _handle_export_json(build_ele)

    elif event_id == 2051:  # Import from JSON
        print(f"[mvp_example] Import JSON button clicked (EventId 2051)")
        return _handle_import_json(build_ele)

    elif event_id == 2052:  # Generar Camino Optimo
        print(f"[mvp_example] Generate Optimal button clicked (EventId 2052)")
        return _handle_generate_optimal(build_ele)
    
    # Return False/None for other events to let library handle them (e.g., 1003 Finalize)
    # The library will process these events in its on_control_event method
    return False


def modify_element_property(build_ele, name, value):
    """Handle palette events (button clicks, property changes).
    
    This is called by Allplan when palette buttons are clicked.
    EventIds from .pyp file:
    - 1002: Save Polyline (manual save via button)
    - 1003: Finalize & Create (triggers execute via transactional mode)
    """
    global _global_script_object
    
    print(f"\n[mvp_example] modify_element_property called: name={name}, value={value}")
    
    if name == "generarpolilinea":  # EventId 1002 - Save button
        print("[mvp_example] Save Polyline button clicked")
        print("  → Manually saving current polyline...")
        if _global_script_object is not None:
            interactor = getattr(_global_script_object, "script_object_interactor", None)
            if interactor is not None and hasattr(interactor, "save_current_polyline"):
                interactor.save_current_polyline()
                # Update segment indices list after saving (segments were created)
                if _global_script_object and hasattr(_global_script_object, 'saved_segments'):
                    _update_segment_indices_list(build_ele, len(_global_script_object.saved_segments))
                print("  → Polyline saved successfully")
            else:
                print("  → ERROR: Interactor not found or doesn't have save_current_polyline")
        else:
            print("  → ERROR: Script object not available")
        return True
    
    elif name == "finalizarCreacion":  # EventId 1003 - Finalize button  
        print("[mvp_example] Finalize & Create button clicked")
        print("  → Calling _finalize_and_create_now() to trigger execute()...")
        if _global_script_object is not None:
            finalize_method = getattr(_global_script_object, "_finalize_and_create_now", None)
            if finalize_method is not None and callable(finalize_method):
                finalize_method()
                print("  → Finalize method called successfully")
            else:
                print("  → ERROR: _finalize_and_create_now method not found")
        else:
            print("  → ERROR: Script object not available")
        return True
    
    # NEW: Advanced Features Event Handlers
    elif name == "UpdateSegmentBtn":  # EventId 2001 - Update Segment
        print(f"[mvp_example] UpdateSegmentBtn clicked - calling _handle_update_segment")
        result = _handle_update_segment(build_ele)
        print(f"[mvp_example] _handle_update_segment returned: {result}")
        return result
    
    elif name == "DeleteSegmentBtn":  # EventId 2002 - Delete Segment
        return _handle_delete_segment(build_ele)
    
    elif name == "InsertAtMidpointBtn":  # EventId 2020 - Insert at Midpoint
        return _handle_insert_at_midpoint(build_ele)
    
    elif name == "RefreshInstallationsBtn":  # EventId 2030 - Refresh Registry
        return _handle_refresh_registry(build_ele)
    
    elif name == "ViewMetadataBtn":  # EventId 2040 - View Metadata
        return _handle_view_metadata(build_ele)
    
    elif name == "ExportJSONBtn":  # EventId 2050 - Export to JSON
        return _handle_export_json(build_ele)
    
    elif name == "ImportJSONBtn":  # EventId 2051 - Import from JSON
        return _handle_import_json(build_ele)
    
    elif name == "GenerateOptimalBtn":  # EventId 2052 - Generar Camino Optimo
        return _handle_generate_optimal(build_ele)
    
    return True  # Always return True to allow property change


def _handle_update_segment(build_ele):
    """Update segment properties using library API.
    
    Uses selected segment from edit mode if available, otherwise uses SegmentIndex from palette.
    """
    print(f"[mvp] _handle_update_segment CALLED")
    try:
        global _global_script_object
        so = _global_script_object
        if not so or not so.script_object_interactor:
            print("[mvp] ✗ No active script object")
            return False
        
        interactor = so.script_object_interactor
        new_diameter = build_ele.NewDiameter.value
        print(f"[mvp] New diameter value from palette: {new_diameter}")
        
        # Find the actual segment index in saved_segments
        actual_seg_idx = None
        
        if hasattr(interactor, 'selected_seg') and interactor.selected_seg:
            path_idx, seg_idx = interactor.selected_seg
            print(f"[mvp] Using selected segment from edit mode: path {path_idx}, segment {seg_idx}")
            
            # Find the actual segment index in saved_segments by matching path_idx and seg_idx
            for saved_idx, saved_seg in enumerate(so.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(saved_seg)
                if seg_meta.custom.get("path_idx") == path_idx and seg_meta.custom.get("seg_idx") == seg_idx:
                    actual_seg_idx = saved_idx
                    break
            
            if actual_seg_idx is None:
                print(f"[mvp] ✗ Could not find segment in saved_segments: path {path_idx}, segment {seg_idx}")
                return False
        else:
            # Use segment index from palette (this is already the saved_segments index)
            actual_seg_idx = build_ele.SegmentIndex.value
            print(f"[mvp] Using segment index from palette: {actual_seg_idx}")
        
        # Check segment exists
        if actual_seg_idx is not None and 0 <= actual_seg_idx < len(so.saved_segments):
            seg_meta = SegmentMetadata.from_legacy(so.saved_segments[actual_seg_idx])
            if seg_meta.custom.get("deleted"):
                print(f"[mvp] ✗ Segment {actual_seg_idx} is deleted (soft-delete).")
                return False
            
            # Get path_idx and seg_idx from segment metadata (for persistent identification)
            path_idx = seg_meta.custom.get("path_idx")
            seg_idx_local = seg_meta.custom.get("seg_idx")
            
            # Update diameter in the segment metadata
            seg_meta.diameter = new_diameter
            seg_meta.section_type = f"{new_diameter}mm"
            
            # Also store diameter in custom dict for persistence across rebuilds
            if "custom_diameters" not in seg_meta.custom:
                seg_meta.custom["custom_diameters"] = {}
            if path_idx is not None and seg_idx_local is not None:
                if "path_diameters" not in seg_meta.custom:
                    seg_meta.custom["path_diameters"] = {}
                seg_meta.custom["path_diameters"][f"{path_idx}_{seg_idx_local}"] = new_diameter
            
            # Update the saved segment (convert back to legacy format if needed)
            so.saved_segments[actual_seg_idx] = seg_meta
            
            # Update NewDiameter palette control to match (single consolidated control)
            try:
                new_diam_prop = getattr(build_ele, "NewDiameter", None)
                if new_diam_prop:
                    new_diam_prop.value = int(round(float(new_diameter)))
                    print(f"[mvp] Updated NewDiameter palette control to {new_diameter}mm")
            except:
                pass  # Ignore errors updating palette diameter
            
            print(f"[mvp] ✓ Updated segment {actual_seg_idx} diameter to {new_diameter}mm")
            
            # Keep segment indices list in sync (data-driven approach)
            _update_segment_indices_list(build_ele, len(so.saved_segments))
            
            # Trigger re-render if needed
            if interactor.current_point:
                interactor._draw_preview(interactor.current_point)
            # Update section info
            interactor._update_section_info()
            return True
        else:
            print(f"[mvp] ✗ Segment index {actual_seg_idx} out of range (0-{len(so.saved_segments)-1})")
            return False
            
    except Exception as ex:
        print(f"[mvp] Error updating segment: {ex}")
        import traceback
        traceback.print_exc()
        return False


def _update_segment_indices_list(build_ele, num_segments: int):
    """Update the segment indices list using pure data-driven approach.
    
    DATA-DRIVEN APPROACH:
    1. We ONLY update SegmentIndicesList (our data source - a simple Integer property)
    2. SegmentIndex.ValueList is defined in .pyp as: [str(i) for i in range(0, SegmentIndicesList + 1)]
    3. The combobox automatically reads from its ValueList, which references SegmentIndicesList
    4. We NEVER touch SegmentIndex.value or SegmentIndex.ValueList directly
    
    This prevents "bad lexical cast" errors because:
    - We only update a simple Integer property (SegmentIndicesList)
    - The combobox's ValueList is derived from that property automatically
    - Allplan handles the value validation when reading from the derived list
    """
    try:
        # Calculate max valid index
        # Always ensure at least 0, even if num_segments is 0
        max_index = max(0, num_segments - 1) if num_segments > 0 else 0
        
        # Get the data source property (our single source of truth)
        indices_list_prop = getattr(build_ele, "SegmentIndicesList", None)
        if indices_list_prop is None:
            print(f"[mvp] ERROR: SegmentIndicesList property not found on build_ele")
            return False
        
        # CRITICAL: Update ONLY the data source - never touch the combobox value directly
        indices_list_prop.value = max_index
        
        print(f"[mvp] Updated SegmentIndicesList (data source): {max_index} (num_segments={num_segments})")
        return True
    except Exception as ex:
        print(f"[mvp] Error updating segment indices list: {ex}")
        import traceback
        traceback.print_exc()
    return False


def _handle_delete_segment(build_ele):
    """Delete a segment using library API."""
    global _global_script_object
    try:
        so = _global_script_object
        if not so or not so.script_object_interactor:
            return False
        
        # Get segment index - prefer selected segment from edit mode
        interactor = so.script_object_interactor
        actual_seg_idx = None
        
        if hasattr(interactor, 'selected_seg') and interactor.selected_seg:
            path_idx, seg_idx = interactor.selected_seg
            print(f"[mvp] Using selected segment from edit mode: path {path_idx}, segment {seg_idx}")
            
            # Find the actual segment index in saved_segments by matching path_idx and seg_idx
            for saved_idx, saved_seg in enumerate(so.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(saved_seg)
                if seg_meta.custom.get("path_idx") == path_idx and seg_meta.custom.get("seg_idx") == seg_idx:
                    actual_seg_idx = saved_idx
                    break
            
            if actual_seg_idx is None:
                print(f"[mvp] ✗ Could not find segment in saved_segments: path {path_idx}, segment {seg_idx}")
                return False
        else:
            actual_seg_idx = build_ele.SegmentIndex.value
            print(f"[mvp] Using segment index from palette: {actual_seg_idx}")
        
        # Validate segment index
        if actual_seg_idx is None or not (0 <= actual_seg_idx < len(so.saved_segments)):
            print(f"[mvp] Invalid segment index: {actual_seg_idx} (valid range: 0-{len(so.saved_segments)-1})")
            return False
        
        # Get current segment count before deletion (for soft-delete padding)
        num_segments_before = len(so.saved_segments)
        
        # Delete the segment
        success = interactor.delete_segment(actual_seg_idx, delete_geometry=True)
        
        if success:
            print(f"[mvp] Deleted segment {actual_seg_idx}")
            
            num_segments = len(so.saved_segments)
            print(f"[mvp] Segments remaining after deletion: {num_segments}")
            
            # SOFT-DELETE BEHAVIOR (MVP ONLY):
            # Keep saved_segments length stable to avoid palette crashes.
            # Pad with placeholder segments marked as deleted.
            if num_segments < num_segments_before:
                missing = num_segments_before - num_segments
                for _ in range(missing):
                    placeholder = SegmentMetadata(
                        points=[],
                        diameter=0.0,
                        section_type="",
                        system="",
                        label="",
                        custom={"deleted": True}
                    )
                    so.saved_segments.append(placeholder)
                num_segments = len(so.saved_segments)
                print(f"[mvp] Soft-delete padding applied. saved_segments now: {num_segments}")
            
            # CRITICAL: Update the indices list IMMEDIATELY after deletion
            # This must happen before Allplan calls update_palette
            # Pure data-driven approach: only update ValueList, never touch .value
            # If this fails, log error but continue - deletion succeeded
            update_success = _update_segment_indices_list(build_ele, num_segments)
            if not update_success:
                print(f"[mvp] ERROR: Failed to update segment indices list")
                # Log but don't fail - the deletion itself succeeded
            
            # Clear selection
            if hasattr(interactor, 'selected_seg'):
                interactor.selected_seg = None
            
            # Update display
            interactor._update_section_info()
            if interactor.current_point:
                interactor._draw_preview(interactor.current_point)
            
            print(f"[mvp] Deletion complete, returning True")
            return True
        else:
            print(f"[mvp] Failed to delete segment {actual_seg_idx}")
        
        return success
        
    except Exception as ex:
        print(f"[mvp] Error deleting segment: {ex}")
        import traceback
        traceback.print_exc()
        return False


def _handle_insert_at_midpoint(build_ele):
    """Programmatically insert point at segment midpoint."""
    try:
        global _global_script_object
        so = _global_script_object
        if not so:
            return False
        
        seg_idx = build_ele.InsertTestSegmentIndex.value
        
        if 0 <= seg_idx < len(so.saved_segments):
            seg_meta = so.saved_segments[seg_idx]
            
            # Calculate midpoint
            p1, p2 = seg_meta.points[0], seg_meta.points[1]
            mid_x = (p1.X + p2.X) / 2
            mid_y = (p1.Y + p2.Y) / 2
            mid_z = (p1.Z + p2.Z) / 2
            
            midpoint = AllplanGeo.Point3D(mid_x, mid_y, mid_z)
            
            # Use library's insert point logic
            interactor = so.script_object_interactor
            
            # Enable insert mode temporarily
            old_insert = interactor.insert_mode
            interactor.insert_mode = True
            
            # Simulate finding insert target
            target = interactor._find_insert_target(midpoint)
            
            if target:
                print(f"[mvp] ✓ Found insert target at segment {target[0]}")
                print(f"[mvp] Insert point detection test passed")
            else:
                print(f"[mvp] Insert point detection test completed (no target found)")
            
            interactor.insert_mode = old_insert
            return True
        
        return False
        
    except Exception as ex:
        print(f"[mvp] Error testing insert: {ex}")
        import traceback
        traceback.print_exc()
        return False


def _handle_refresh_registry(build_ele):
    """Refresh the installation registry."""
    try:
        # Re-register test installations (optional - only if test_installations.py exists)
        try:
            from test_installations import register_test_installations
            register_test_installations()
        except ImportError:
            pass  # test_installations.py doesn't exist - this is normal
        
        # Get current installation from palette
        inst_name = getattr(build_ele, "InstallationName", None)
        current_inst = inst_name.value if inst_name else "Pluvial_Test"
        
        # Apply installation angles if registry sync is enabled
        global _global_script_object
        so = _global_script_object
        if so and so.script_object_interactor:
            interactor = so.script_object_interactor
            interactor._apply_installation_angles()
            print(f"[mvp] ✓ Registry refreshed, current installation: {current_inst}")
        
        return True
        
    except Exception as ex:
        print(f"[mvp] Error refreshing registry: {ex}")
        import traceback
        traceback.print_exc()
        return False


def _handle_view_metadata(build_ele):
    """View custom metadata for a specific segment."""
    try:
        global _global_script_object
        so = _global_script_object
        if not so:
            return False
        
        seg_idx = build_ele.ViewMetadataSegmentIndex.value
        
        if 0 <= seg_idx < len(so.saved_segments):
            seg_meta = so.saved_segments[seg_idx]
            
            # Build metadata display string
            metadata_lines = [
                f"Segment {seg_idx} Metadata:",
                f"",
                f"Basic Properties:",
                f"  Diameter: {seg_meta.diameter}mm",
                f"  System: {seg_meta.system}",
                f"  Section Type: {seg_meta.section_type}",
                f"  Label: {seg_meta.label}",
                f"",
                f"Custom Fields:",
            ]
            
            # Add custom fields
            if seg_meta.custom:
                for key, value in seg_meta.custom.items():
                    metadata_lines.append(f"  {key}: {value}")
            else:
                metadata_lines.append("  (No custom fields)")
            
            # Update palette display field
            metadata_text = "\n".join(metadata_lines)
            metadata_field = getattr(build_ele, "MetadataDisplay", None)
            if metadata_field:
                metadata_field.value = metadata_text
            
            print(f"[mvp] ✓ Displayed metadata for segment {seg_idx}")
            print(metadata_text)
            return True
        else:
            print(f"[mvp] ✗ Segment index {seg_idx} out of range")
            return False
            
    except Exception as ex:
        print(f"[mvp] Error viewing metadata: {ex}")
        import traceback
        traceback.print_exc()
        return False


def _handle_export_json(build_ele):
    """Export saved polylines to JSON file."""
    try:
        global _global_script_object
        so = _global_script_object
        if not so:
            print("[mvp] No active script object")
            return False
        
        path_id = build_ele.JSONPathID.value
        
        # Export saved_paths and saved_segments
        if not so.saved_paths and not so.saved_segments:
            print("[mvp] ✗ No saved polylines to export")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ No saved polylines"
            return False
        
        # Create capture records from saved paths
        capture_records = []
        segment_counter = 0
        
        for path_idx, path_points in enumerate(so.saved_paths):
            if len(path_points) < 2:
                continue
            
            # Create capture records for this path
            for pt_idx, pt in enumerate(path_points):
                # Determine role: first=0 (Inicial), last=3 (Final), others=1 (Paso)
                if pt_idx == 0:
                    role = 0  # Inicial
                elif pt_idx == len(path_points) - 1:
                    role = 3  # Final
                else:
                    role = 1  # Paso
                
                # Get segment_id from saved_segments if available
                segment_id = 1
                if so.saved_segments:
                    # Find which segment this point belongs to
                    for seg_idx, seg_meta in enumerate(so.saved_segments):
                        if seg_meta.points and len(seg_meta.points) >= 2:
                            if pt in seg_meta.points or any(
                                abs(pt.X - p.X) < 0.1 and abs(pt.Y - p.Y) < 0.1 and abs(pt.Z - p.Z) < 0.1
                                for p in seg_meta.points
                            ):
                                segment_id = seg_idx + 1
                                break
                
                capture_point = PBL.CapturePoint(
                    point=pt,
                    path_id=path_id if path_id > 0 else path_idx + 1,
                    segment_id=segment_id,
                    role=role,
                    color_id=1,
                    order_index=pt_idx,
                    exported=False
                )
                capture_records.append(capture_point)
        
        if not capture_records:
            print("[mvp] ✗ No valid points to export")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ No valid points"
            return False
        
        # Export to JSON using library function
        export_path_id = path_id if path_id > 0 else 1
        json_path = PBL.export_capture_records_to_json(capture_records, export_path_id)
        
        if json_path:
            print(f"[mvp] ✓ Exported {len(capture_records)} points from {len(so.saved_paths)} paths to JSON: {json_path}")
            print(f"[mvp] JSON export path={json_path} records={len(capture_records)}")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = f"✓ Exported {len(capture_records)} points to {os.path.basename(json_path)}"
            return True
        else:
            print(f"[mvp] ✗ Export failed")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ Export failed"
            return False
            
    except Exception as ex:
        print(f"[mvp] Error exporting JSON: {ex}")
        import traceback
        traceback.print_exc()
        json_status = getattr(build_ele, "JSONStatus", None)
        if json_status:
            json_status.value = f"✗ Error: {str(ex)[:50]}"
        return False


def _handle_import_json(build_ele):
    """Import polyline from JSON file and recreate it."""
    try:
        global _global_script_object
        so = _global_script_object
        if not so or not so.script_object_interactor:
            print("[mvp] No active script object")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ No active script object"
            return False
        
        path_id = build_ele.JSONPathID.value
        import_path_id = path_id if path_id > 0 else None
        
        # Find latest JSON file
        json_path = PBL.find_latest_route_groups_json()
        
        if not json_path:
            print(f"[mvp] ✗ No JSON file found on Desktop")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ No JSON file found"
            return False
        
        print(f"[mvp] Loading from JSON: {json_path}")
        
        # Load points from JSON
        points = PBL.load_points_from_json(json_path, path_id=import_path_id)
        
        if not points or len(points) < 2:
            print(f"[mvp] ✗ No points found for path_id {import_path_id or 'latest'}")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = f"✗ No points found for path {import_path_id or 'latest'}"
            return False
        
        print(f"[mvp] ✓ Loaded {len(points)} points from path_id {import_path_id or 'latest'}")
        
        # Convert points from world to relative coordinates if needed
        interactor = so.script_object_interactor
        origin_x = getattr(build_ele, "StartX", None)
        origin_y = getattr(build_ele, "StartY", None)
        origin_z = getattr(build_ele, "StartZ", None)
        
        offset_x = float(origin_x.value) if origin_x else 0.0
        offset_y = float(origin_y.value) if origin_y else 0.0
        offset_z = float(origin_z.value) if origin_z else 0.0
        
        # Convert to relative coordinates (support Point3D or tuple/list)
        relative_points = []
        for pt in points:
            try:
                x, y, z = pt.X, pt.Y, pt.Z
            except Exception:
                # Tuple/list fallback
                if isinstance(pt, (tuple, list)) and len(pt) >= 3:
                    x, y, z = pt[0], pt[1], pt[2]
                else:
                    continue
            rel_pt = AllplanGeo.Point3D(
                float(x) - offset_x,
                float(y) - offset_y,
                float(z) - offset_z
            )
            relative_points.append(rel_pt)
        
        # Add points to interactor and save as new path
        interactor.points = relative_points.copy()
        interactor.save_current_polyline()
        
        print(f"[mvp] ✓ Recreated polyline with {len(relative_points)} points")
        print(f"[mvp] JSON import path={json_path} records={len(relative_points)}")
        
        # Update status
        json_status = getattr(build_ele, "JSONStatus", None)
        if json_status:
            json_status.value = f"✓ Imported {len(relative_points)} points, saved as path"
        
        return True
            
    except Exception as ex:
        print(f"[mvp] Error importing JSON: {ex}")
        import traceback
        traceback.print_exc()
        json_status = getattr(build_ele, "JSONStatus", None)
        if json_status:
            json_status.value = f"✗ Error: {str(ex)[:50]}"
        return False


def _handle_generate_optimal(build_ele):
    """Run the full optimization pipeline via the library."""
    try:
        global _global_script_object
        so = _global_script_object
        if not so or not so.script_object_interactor:
            print("[mvp] No active script object for optimizer")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ No active script object"
            return False

        interactor = so.script_object_interactor
        if not hasattr(interactor, "generar_camino_optimo"):
            print("[mvp] generar_camino_optimo not available")
            json_status = getattr(build_ele, "JSONStatus", None)
            if json_status:
                json_status.value = "✗ Optimizer not available in library"
            return False

        tipo = ""
        tipo_attr = getattr(build_ele, "InstallationType", None)
        if tipo_attr:
            tipo = str(getattr(tipo_attr, "value", ""))

        success = interactor.generar_camino_optimo(tipo_instalacion=tipo)

        json_status = getattr(build_ele, "JSONStatus", None)
        if json_status:
            json_status.value = "✓ Camino óptimo generado" if success else "✗ Optimización fallida"
        return success

    except Exception as ex:
        print(f"[mvp] Error in generate optimal: {ex}")
        import traceback
        traceback.print_exc()
        json_status = getattr(build_ele, "JSONStatus", None)
        if json_status:
            json_status.value = f"✗ Error: {str(ex)[:50]}"
        return False


def create_preview(_build_ele, _doc):
    """Create a preview polyline to show initial state.
    
    DISABLED for now - causing visual artifacts.
    """
    # Return empty to avoid preview geometry issues
    return CreateElementResult([])


def _try_create_elbow_at_junction(prev_seg, curr_seg, build_ele, common_prop):
    """Detect if an elbow is needed at junction between two segments.
    
    Args:
        prev_seg: Previous SegmentMetadata (or None if first segment)
        curr_seg: Current SegmentMetadata
        build_ele: Build element for accessing palette settings
        common_prop: Common properties for element creation
    
    Returns:
        List of elbow elements (empty if no elbow needed)
    """
    if prev_seg is None or curr_seg is None:
        return []
    
    # Check if auto-elbows enabled in palette
    auto_elbows = getattr(build_ele, "TestElbowsCheckbox", None)
    if auto_elbows and not auto_elbows.value:
        return []
    
    if not ALLPLAN_AVAILABLE or not MODELS_AVAILABLE or CodoBasico is None:
        return []
    
    try:
        # Get direction vectors
        prev_dir = PBL.get_segment_direction_vector(prev_seg)
        curr_dir = PBL.get_segment_direction_vector(curr_seg)
        
        # Calculate angle between segments (in degrees)
        import math
        dot_product = prev_dir[0]*curr_dir[0] + prev_dir[1]*curr_dir[1] + prev_dir[2]*curr_dir[2]
        # Clamp to [-1, 1] to avoid math domain error
        dot_product = max(-1.0, min(1.0, dot_product))
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)
        
        print(f"[mvp_example] Junction angle: {angle_deg:.1f}°")
        
        # Only create elbow if angle is significant (> 15 degrees)
        MIN_ELBOW_ANGLE = 15.0
        if angle_deg < MIN_ELBOW_ANGLE:
            print(f"[mvp_example] Angle too small for elbow ({angle_deg:.1f}° < {MIN_ELBOW_ANGLE}°)")
            return []
        
        # Get junction point (end of prev segment = start of curr segment)
        junction_pt = prev_seg.points[-1]
        
        # Determine elbow type based on angle
        # 90° elbows for angles 75-105°
        # 45° elbows for angles 30-60°
        # etc.
        if 75 <= angle_deg <= 105:
            elbow_type = 90
        elif 30 <= angle_deg <= 60:
            elbow_type = 45
        else:
            # Use closest standard angle
            standard_angles = [22.5, 30, 45, 67.5, 90]
            elbow_type = min(standard_angles, key=lambda x: abs(x - angle_deg))
        
        print(f"[mvp_example] Creating {elbow_type}° elbow at junction")
        
        # Create elbow using CodoBasico
        diameter = curr_seg.diameter if curr_seg.diameter > 0 else 110.0
        
        # Use simplified elbow creation
        elbow_builder = CodoBasico(build_ele)
        
        # Create a simple cube marker at junction (placeholder for elbow)
        try:
            marker_size = 200.0  # mm - visible marker
            center = AllplanGeo.Point3D(junction_pt.X, junction_pt.Y, junction_pt.Z)
            
            # Create cube at junction
            cube = AllplanGeo.Polyhedron3D.CreateCuboid(
                AllplanGeo.Point3D(center.X - marker_size/2, center.Y - marker_size/2, center.Z - marker_size/2),
                AllplanGeo.Point3D(center.X + marker_size/2, center.Y + marker_size/2, center.Z + marker_size/2)
            )
            
            # Create marker with distinct color
            marker_prop = AllplanBaseElements.CommonProperties()
            marker_prop.Color = 4  # Yellow for elbow markers
            
            marker_elem = AllplanBasisElements.ModelElement3D(marker_prop, cube)
            
            print(f"[mvp_example] ✓ Created {elbow_type}° elbow marker at junction")
            return [marker_elem]
        except Exception as ex:
            print(f"[mvp_example] Error creating elbow marker: {ex}")
            return []
        
    except Exception as ex:
        print(f"[mvp_example] Error creating elbow: {ex}")
        import traceback
        traceback.print_exc()
        return []


def _create_demo_elements(segment_meta, common_prop, build_ele):
    """Element creation hook - creates 3D tube models for each segment.
    
    NEW: Also creates elbows at corners automatically!
    """
    global segment_counter, total_length, _previous_segment
    
    print("\n" + "="*60)
    print("[mvp_example] _create_demo_elements CALLED!")
    print("="*60)
    
    if not ALLPLAN_AVAILABLE:
        print("[mvp_example] Allplan not available!")
        return []
    
    # Add custom metadata to test the feature
    segment_meta.custom["flow_direction"] = "downstream"
    segment_meta.custom["material"] = "PVC"
    segment_meta.custom["installation_date"] = "2025-12-18"
    segment_meta.custom["inspector_notes"] = f"Segment at {segment_meta.points[0].X:.0f},{segment_meta.points[0].Y:.0f}"
    segment_meta.custom["segment_number"] = segment_counter + 1
    print(f"[mvp_example] Added custom metadata: {segment_meta.custom}")
    
    elements = []
    pts = list(segment_meta.points)
    
    if len(pts) < 2:
        print("[mvp_example] Not enough points")
        return elements
    
    segment_counter += 1
    
    # AUTOMATIC ELBOW DETECTION: Check if we need an elbow between previous and current segment
    elbow_elements = _try_create_elbow_at_junction(_previous_segment, segment_meta, build_ele, common_prop)
    if elbow_elements:
        elements.extend(elbow_elements)
        print(f"[mvp_example] ✓ Added {len(elbow_elements)} elbow elements!")
    
    # Store this segment for next iteration
    _previous_segment = segment_meta
    
    try:
        # Get start/end points
        start = _as_point3d(pts[0])
        end = _as_point3d(pts[-1])
        
        # Calculate segment properties
        length = PBL.get_segment_length(segment_meta)
        total_length += length
        direction = PBL.get_segment_direction_vector(segment_meta)
        
        # Detect orientation
        dx = abs(end.X - start.X)
        dy = abs(end.Y - start.Y)
        dz = abs(end.Z - start.Z)
        is_vertical = (dx < 10.0 and dy < 10.0 and dz > 10.0)
        
        print(f"[mvp_example] Segment #{segment_counter}: Length={length:.0f}mm, Vertical={is_vertical}")
        print(f"[mvp_example] Diameter={segment_meta.diameter}mm, System={segment_meta.system}")
        
        # Get pipe diameter from metadata
        diameter = segment_meta.diameter if segment_meta.diameter > 0 else 110.0
        
        # Try to create REAL 3D tube model
        if MODELS_AVAILABLE and TuboPVCConFlecha is not None:
            print(f"[mvp_example] Creating REAL 3D tube (TuboPVCConFlecha)")
            pipe_elements = _create_real_tube(start, end, length, diameter, direction, is_vertical, build_ele)
            if pipe_elements:
                elements.extend(pipe_elements)
                print(f"[mvp_example] ✓ Created {len(pipe_elements)} 3D model elements!")
            else:
                print(f"[mvp_example] Model creation returned empty, using fallback")
                elements.extend(_create_fallback_pipe(start, end, diameter / 2.0))
        else:
            # Fallback to simple geometry
            print(f"[mvp_example] Models not available, creating fallback cylinder")
            elements.extend(_create_fallback_pipe(start, end, diameter / 2.0))
        
        print(f"[mvp_example] Total: {len(elements)} elements")
        
    except Exception as e:
        print(f"[mvp_example] ERROR: {e}")
        import traceback
        traceback.print_exc()
        # Return fallback on error
        try:
            start = _as_point3d(pts[0])
            end = _as_point3d(pts[-1])
            elements = _create_fallback_pipe(start, end, 55.0)
        except:
            pass
    
    return elements


def _create_real_tube(start, end, length, diameter, direction, is_vertical, build_ele):
    """Create a REAL tube using Saneamiento's TuboPVCConFlecha model.
    
    This demonstrates importing and using actual PythonPart models in the library.
    """
    if not ALLPLAN_AVAILABLE or not MODELS_AVAILABLE:
        return _create_fallback_pipe(start, end, diameter / 2.0)
    
    elements = []
    
    try:
        # Use the real Saneamiento model
        builder = TuboPVCConFlecha(build_ele)
        
        # Choose config based on diameter
        config = builder.CONFIG.get(diameter, builder.CONFIG[110.0])
        
        # Build the tube geometry
        brep = builder._build_tube(length, diameter, config)
        flecha_poly = builder._build_arrow(length, diameter, config)
        
        # Apply the model's standard 180° rotation
        z_flecha = diameter * config["altura_flecha"] + builder.FLECHA_OFFSET_Z
        brep, flecha_poly = builder._apply_180_transform(brep, flecha_poly, z_flecha)
        
        # Create comprehensive transformation to position tube along segment
        matrix = AllplanGeo.Matrix3D()
        
        # Calculate rotation to align tube with segment direction
        # After 180° rotation, tube is along +X axis
        if is_vertical:
            # For vertical segments, rotate from X to Z axis
            # Rotate 90° around Y axis to point tube upward
            matrix.SetRotation(
                AllplanGeo.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeo.Angle(math.radians(90.0))
            )
        else:
            # For horizontal/inclined segments
            # Calculate angle in XY plane
            angle_z = math.atan2(direction[1], direction[0])
            
            # If there's a Z component (inclined), add Y rotation
            if abs(direction[2]) > 0.01:
                # Calculate inclination angle
                horizontal_dist = math.sqrt(direction[0]**2 + direction[1]**2)
                angle_y = math.atan2(direction[2], horizontal_dist)
                
                # Apply Y rotation first (inclination)
                rot_y = AllplanGeo.Matrix3D()
                rot_y.SetRotation(
                    AllplanGeo.Line3D(0, 0, 0, 0, 1, 0),
                    AllplanGeo.Angle(angle_y)
                )
                matrix = rot_y
            
            # Apply Z rotation (direction in XY plane)
            rot_z = AllplanGeo.Matrix3D()
            rot_z.SetRotation(
                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                AllplanGeo.Angle(angle_z)
            )
            
            # Combine rotations
            if abs(direction[2]) > 0.01:
                matrix = AllplanGeo.Matrix3D(matrix) * rot_z
            else:
                matrix = rot_z
        
        # Translate to start position
        trans = AllplanGeo.Matrix3D()
        trans.SetTranslation(AllplanGeo.Vector3D(start))
        matrix = matrix * trans
        
        # Apply transformation
        brep = AllplanGeo.Transform(brep, matrix)
        flecha_poly = AllplanGeo.Transform(flecha_poly, matrix)
        
        # Create elements with proper properties
        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.Color = builder.COLORES["general"]
        props.Layer = 3700
        
        flecha_props = AllplanBaseElements.CommonProperties()
        flecha_props.GetGlobalProperties()
        flecha_props.Color = builder.COLORES["flecha"]
        
        elements.append(AllplanBasisElements.ModelElement3D(props, brep))
        elements.append(AllplanBasisElements.ModelElement3D(flecha_props, flecha_poly))
        
        print(f"    Created REAL TuboPVCConFlecha model!")
        
    except Exception as e:
        print(f"[mvp_example] Error creating real tube: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to simple geometry
        elements = _create_fallback_pipe(start, end, diameter / 2.0)
    
    return elements


def _create_fallback_pipe(start, end, radius):
    """Fallback to simple geometry if real models unavailable."""
    if not ALLPLAN_AVAILABLE:
        return []
    
    elements = []
    
    try:
        # Create JUST a simple line - nothing fancy
        line = AllplanGeo.Line3D(start, end)
        
        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.Color = 3  # Green
        props.Pen = 5  # Medium pen
        props.Stroke = 1
        props.Layer = -1  # Active layer
        
        elem = AllplanBasisElements.ModelElement3D(props, line)
        elements.append(elem)
        
        print(f"    Created simple line from ({start.X:.1f},{start.Y:.1f}) to ({end.X:.1f},{end.Y:.1f})")
        
    except Exception as e:
        print(f"[mvp_example] Error creating line: {e}")
        import traceback
        traceback.print_exc()
    
    return elements


def _create_real_coupling(point, direction, is_start=True):
    """Create a REAL coupling using Saneamiento's Manguito model.
    
    This demonstrates using actual connection fittings from the library.
    """
    if not ALLPLAN_AVAILABLE or not MODELS_AVAILABLE:
        return []
    
    elements = []
    
    try:
        # Calculate rotation to align coupling with pipe direction
        angle_z = math.atan2(direction[1], direction[0])
        rot_z_deg = math.degrees(angle_z)
        
        # Use the real Manguito model with rotation
        builder = Manguito(rot_x=0.0, rot_y=180.0, rot_z=rot_z_deg)
        result = builder.create_result()
        
        # Position the coupling elements at the point
        matrix = AllplanGeo.Matrix3D()
        matrix.SetTranslation(AllplanGeo.Vector3D(point))
        
        for elem in result.elements:
            # Get the geometry from the element
            geo = elem.GetGeometry()
            # Transform it
            err, geo_transformed = AllplanGeo.Transform(geo, matrix)
            
            if err != AllplanGeo.eGeometryErrorCode.eOK:
                print(f"[mvp_example] Warning: Coupling transformation error")
                continue
            
            # Create new element with transformed geometry
            props = AllplanBaseElements.CommonProperties()
            props.GetGlobalProperties()
            props.Color = 65 if is_start else 5  # Different colors for start/end
            props.Layer = 3701
            
            elements.append(AllplanBasisElements.ModelElement3D(props, geo_transformed))
        
        print(f"    Created REAL Manguito coupling!")
        
    except Exception as e:
        print(f"[mvp_example] Error creating real coupling: {e}")
        import traceback
        traceback.print_exc()
    
    return elements


def _create_real_elbow(point, build_ele):
    """Create a REAL elbow fitting using Saneamiento's CodoBasico model.
    
    This demonstrates using actual elbow fittings (45° or 90°) from the library.
    """
    if not ALLPLAN_AVAILABLE or not MODELS_AVAILABLE:
        return []
    
    elements = []
    
    try:
        # Use the real CodoBasico model
        # Default to 45° elbow (tipo=0)
        builder = CodoBasico(build_ele, rot_x=0.0, rot_y=0.0, rot_z=0.0)
        result = builder.create_result()
        
        # Position the elbow at the point
        matrix = AllplanGeo.Matrix3D()
        matrix.SetTranslation(AllplanGeo.Vector3D(point))
        
        for elem in result.elements:
            # Get the geometry from the element
            geo = elem.GetGeometry()
            # Transform it
            err, geo_transformed = AllplanGeo.Transform(geo, matrix)
            
            if err != AllplanGeo.eGeometryErrorCode.eOK:
                print(f"[mvp_example] Warning: Elbow transformation error")
                continue
            
            # Create new element with transformed geometry
            props = AllplanBaseElements.CommonProperties()
            props.GetGlobalProperties()
            props.Color = 24  # CodoBasico color
            props.Layer = 3702
            
            elements.append(AllplanBasisElements.ModelElement3D(props, geo_transformed))
        
        print(f"    Created REAL CodoBasico elbow!")
        
    except Exception as e:
        print(f"[mvp_example] Error creating real elbow: {e}")
        import traceback
        traceback.print_exc()
    
    return elements


def _as_point3d(point):
    """Convert various point representations to AllplanGeo.Point3D.
    
    Tests point conversion utilities.
    """
    if ALLPLAN_AVAILABLE and isinstance(point, AllplanGeo.Point3D):
        return point
    
    if hasattr(point, "X"):
        return AllplanGeo.Point3D(float(point.X), float(point.Y), float(point.Z))
    
    if isinstance(point, (tuple, list)) and len(point) >= 3:
        return AllplanGeo.Point3D(float(point[0]), float(point[1]), float(point[2]))
    
    return AllplanGeo.Point3D(0, 0, 0)


# ===== OPTIONAL: DEMONSTRATING RESULT EXTRACTION =====
def _demo_result_extraction(script_object):
    """Demonstrate how to extract results from the script object.
    
    This is typically called after user completes the interaction.
    Note: This is for demonstration - normally Allplan drives the lifecycle.
    """
    try:
        # Method 1: Extract result using library function
        result = PBL.extract_result_from_script_object(script_object)
        print(f"\n[mvp_example] === Result Extraction Demo ===")
        print(f"  Extracted {len(result.points)} points")
        print(f"  Is closed: {result.is_closed}")
        
        if result.points:
            print(f"  First point: {result.points[0]}")
            print(f"  Last point: {result.points[-1]}")
        
        # Method 2: Save and get result
        result2 = PBL.save_and_get_result(script_object, clear_state=False)
        print(f"  save_and_get_result returned {len(result2.points)} points")
        
    except Exception as e:
        print(f"[mvp_example] Result extraction demo error: {e}")


# ===== OPTIONAL: DEMONSTRATING JSON LOADING =====
def _demo_json_loading():
    """Demonstrate JSON loading capabilities.
    
    This shows how to load points from previously captured JSON files.
    Note: This is for demonstration purposes.
    """
    try:
        print("\n[mvp_example] === JSON Loading Demo ===")
        
        # Try to find the latest JSON file
        json_path = PBL.find_latest_route_groups_json()
        if json_path:
            print(f"  Found JSON: {json_path}")
            
            # Load points
            points = PBL.load_points_from_json(json_path)
            print(f"  Loaded {len(points)} points from JSON")
            
            # Load path IDs
            path_ids = PBL.load_json_path_ids(json_path)
            print(f"  Available path IDs: {path_ids}")
            
            # Load by segments
            segments = PBL.load_points_from_json_by_segments(json_path)
            print(f"  Loaded {len(segments)} segments from JSON")
        else:
            print("  No JSON file found (this is normal for first run)")
            
    except Exception as e:
        print(f"[mvp_example] JSON loading demo error: {e}")


# Uncomment to run demos (for testing purposes)
# Note: These would typically be called from a separate test harness
# if __name__ == "__main__":
#     _demo_json_loading()


