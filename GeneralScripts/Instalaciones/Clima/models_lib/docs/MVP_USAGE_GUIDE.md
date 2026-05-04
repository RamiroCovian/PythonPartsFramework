# MVP Example - Complete Usage Guide

## 🚀 Quick Start (5 Minutes to Running)

### Step 1: File Locations

Your MVP example has **2 files** that Allplan needs:

```
2025/Modelat/Instalaciones/Clima/models_lib/
├── examples/
│   └── mvp_example.py          ← Python script
└── pyp/
    └── MvpExample.pyp           ← Palette definition (UI)
```

### Step 2: Install in Allplan

**Option A: Drag & Drop (Fastest)**

1. Open Allplan
2. Open the ActionBar → **PythonParts** palette
3. Find the **"Clima"** folder in the tree
4. Navigate to: `Clima → models_lib → pyp`
5. **Drag `MvpExample.pyp`** directly into your drawing viewport
6. The palette UI will appear immediately

**Option B: Copy to PythonParts Folder**

1. Find your Allplan PythonParts folder, typically:
   ```
   C:\ProgramData\Nemetschek\Allplan\[VERSION]\Etc\PythonPartsScripts\
   ```

2. Copy the files maintaining the structure:
   ```
   PythonPartsScripts/
   └── Clima/
       └── models_lib/
           ├── examples/
           │   └── mvp_example.py
           └── pyp/
               └── MvpExample.pyp
   ```

3. Restart Allplan or refresh the PythonParts palette

### Step 3: Start Drawing

Once the palette appears:

1. **Left-click** in the viewport to add points
2. **Right-click** to finish the polyline (creates the elements)
3. **ESC** to cancel/undo

**That's it!** You should see lines being drawn as you click.

---

## 📋 Understanding the Palette

The MVP example has **4 tabs** in its palette:

### Tab 1: Polyline Drawing (Main Controls)

| Control | Purpose | Default |
|---------|---------|---------|
| **Status** | Shows current operation | "Click to add points..." |
| **Create Mode** | Enable polyline creation | ✓ Checked |
| **Limit Angles** | Snap to 0°/45°/90° | ✓ Checked |

### Tab 2: Capture Settings

**Only relevant if using capture mode** (for advanced PointInput workflows)

| Control | Purpose | Default |
|---------|---------|---------|
| **Path ID** | Current path number | 1 |
| **Segment ID** | Current segment number | 1 |
| **Point Role** | Inicial/Paso/Bifurcacion/Final | Paso |
| **Finish Path Now** | Button to finalize current path | - |
| **Create Point Symbols** | Place symbols at points | ✗ |

### Tab 3: Installation Registry

Shows the active installation configuration:

| Control | Purpose | Value |
|---------|---------|-------|
| **Installation** | Installation name | VENTILACION_MVP |
| **Element Key** | Element type key | segment_demo |
| **Installation Type** | Installation subtype | impulsion |
| **Supported Angles** | Available angles | 0° / 45° / 90° |

### Tab 4: Advanced

Fine-tune interaction behavior:

| Control | Purpose | Default |
|---------|---------|---------|
| **Enable Assist Window** | Show coordinate assist | ✗ |
| **Enable Z Coordinate** | Allow 3D input | ✓ |
| **Enable Undo** | Enable undo steps | ✗ |
| **Set Projection Base** | Use projection base | ✓ |

---

## 🎮 How It Works (Behind the Scenes)

### The Data Flow

```
User clicks
    ↓
Allplan → mvp_example.py → polyline_base_lib.py
                              ↓
                         Captures points
                              ↓
                    Builds segment metadata
                              ↓
                    Calls element_creation_hook
                              ↓
                    _create_demo_elements()
                              ↓
                    Creates Line3D elements
                              ↓
                    Returns to Allplan
                              ↓
                    Elements appear in model
```

### What Each File Does

**`MvpExample.pyp` (Palette Definition)**
- Defines the UI controls Allplan displays
- XML format describing buttons, checkboxes, text fields
- Maps to properties in the Python script via `<Name>` tags

**`mvp_example.py` (Python Script)**
- **Entry point**: `create_script_object()` - Allplan calls this first
- **Configuration**: Sets up `PolylineBaseConfig` with behavior flags
- **Element Creation**: `_create_demo_elements()` converts segments to 3D lines
- **Registration**: Registers a demo installation for the palette

**`polyline_base_lib.py` (The Engine)**
- Handles all mouse/keyboard interaction
- Manages polyline editing (drag points, undo, etc.)
- Captures segment metadata (diameter, system, labels)
- Provides hooks for custom element creation

---

## 🔧 Customizing the MVP

### Change Visual Constants

In `mvp_example.py` lines 70-82:

```python
polyline_lib.HANDLE_SIZE = 110.0          # Size of point handles (mm)
polyline_lib.HIT_TOL_VERTEX = 45.0        # Click tolerance for points (mm)
polyline_lib.DEFAULT_SEGMENT_DIAMETER = 160.0  # Default pipe diameter
polyline_lib.ANGLE_SNAP_VALUES = [0.0, 45.0, 90.0, 135.0, 180.0]
```

### Change Behavior

In `mvp_example.py` lines 88-100:

```python
USE_CAPTURE_MODE = True  # Set to False for simple polyline mode
CONFIG = PolylineBaseConfig(
    limit_angles=True,              # Enable angle snapping
    enable_z_coordinate=True,       # Allow 3D coordinates
    allow_insert_point_mode=False,  # Allow inserting points mid-segment
    enable_capture_mode=True,       # Enable advanced capture workflow
    capture_auto_commit_on_final=True,  # Auto-save on "Final" role
    capture_auto_export_json=True,  # Export to Desktop JSON
)
```

### Change What Gets Created

The hook in `mvp_example.py` lines 174-203 creates simple lines. Replace it to create custom elements:

```python
def _create_demo_elements(
    segment_meta: SegmentMetadata, 
    common_prop: "AllplanBaseElements.CommonProperties"
) -> List["AllplanBasisElements.ModelElement3D"]:
    """Your custom element creation logic here."""
    elements = []
    
    # Example: Create a cylinder instead of a line
    start = _as_point3d(segment_meta.points[0])
    end = _as_point3d(segment_meta.points[1])
    diameter = segment_meta.diameter
    
    # Create cylinder geometry here...
    
    return elements
```

---

## 🐛 Troubleshooting

### Problem: Palette doesn't appear when I drag the .pyp file

**Solution:**
- Check the file path in the .pyp matches your actual folder structure
- Line 4 of `MvpExample.pyp`: `<Name>Clima\models_lib\examples\mvp_example.py</Name>`
- The path must be relative to your PythonParts root folder

### Problem: "Module not found" error

**Solution:**
- Ensure `polyline_base_lib.py` is in: `Clima/models_lib/py/polyline_base_lib.py`
- Ensure `installation_registry.py` is in: `Clima/models_lib/py/installation_registry.py`
- Ensure `__init__.py` files exist in all folders

### Problem: Nothing happens when I click

**Solution:**
- Check "Create Mode" is checked in the palette
- Check the Allplan console for Python errors (View → Output Window)
- Verify the library was installed correctly (import test below)

### Problem: Lines are created but wrong diameter/properties

**Solution:**
- Modify the constants in `mvp_example.py` lines 70-82
- Or modify `_create_demo_elements()` to read palette values

---

## ✅ Testing the Installation

### Quick Import Test

1. Open Allplan's Python console (if available)
2. Or create a test script:

```python
# test_import.py
try:
    from Clima.models_lib.py import polyline_base_lib
    print("✓ polyline_base_lib imported successfully")
    print(f"  Version: {polyline_base_lib.__version__}")
    
    from Clima.models_lib.py import installation_registry
    print("✓ installation_registry imported successfully")
    
    from Clima.models_lib.examples import mvp_example
    print("✓ mvp_example imported successfully")
    
    print("\n✓✓✓ All imports successful! Ready to use.")
except Exception as e:
    print(f"✗ Import failed: {e}")
```

---

## 📁 Complete File Structure

Your working installation should look like this:

```
2025/Modelat/Instalaciones/Clima/
├── __init__.py
└── models_lib/
    ├── py/
    │   ├── __init__.py
    │   ├── polyline_base_lib.py       ← The engine (2853 lines)
    │   ├── installation_registry.py   ← Installation management
    │   └── pythonpart.py
    ├── pyp/
    │   ├── MvpExample.pyp             ← Palette UI definition ★
    │   ├── MvpExample_eng.xml
    │   └── PolylineBaseLib.pyp
    ├── examples/
    │   └── mvp_example.py             ← Your entry point script ★
    └── docs/
        ├── MVP_USAGE_GUIDE.md         ← This file
        ├── INSTALLATION_USAGE.md
        └── README.md
```

The two files marked with ★ are the essential ones for running the example.

---

## 🎯 Next Steps

### For Production Use:

1. **Copy the MVP example** to your own installation folder
2. **Rename** to match your installation (e.g., `ventilacion.py`, `Ventilacion.pyp`)
3. **Customize** the element creation hook to create your actual elements
4. **Register** your installation with real element definitions
5. **Test** with real use cases

### Advanced Features to Explore:

- **JSON Bootstrap**: Load polylines from PointInput_SO JSON files
- **Capture Mode**: Advanced workflow with role-based point capture
- **Automatic Fusion**: Polylines automatically connect when endpoints are near
- **Angle Limiting**: Snap to specific angles based on installation
- **Element Hooks**: Create complex fittings, elbows, reducers, bifurcations
- **Undo/Redo**: Built-in state management

### Documentation:

- See `INSTALLATION_USAGE.md` for advanced installation configuration
- See `README.md` for library architecture overview

---

## 🆘 Getting Help

If you encounter issues:

1. Check the console output in Allplan (View → Output Window)
2. Enable debug mode in `polyline_base_lib.py`:
   ```python
   script_object.set_debug(True)
   ```
3. Check the generated JSON files on your Desktop (if using capture mode)
4. Verify file paths and imports are correct

---

**Last Updated**: 2025-01-10
**Library Version**: 0.3.0
**Compatibility**: Allplan 2023+

