# Deployment Fix Guide

## Issues Identified

1. **MultilineText Error** - Cached `.pyp` file still has old value type
2. **Module Import Error** - `ManguitoBasic_003` import failing on reload
3. **Weird Coordinates** - Extremely large negative values causing broken polyline display

## Solutions

### Fix 1: Clean Deployment

**Step 1:** Close Allplan completely

**Step 2:** Delete OLD files from BOTH locations:

**ProgramData Location:**
```
C:\ProgramData\Nemetschek\Allplan\2025\Etc\PythonPartsFramework\GeneralScripts\Instalaciones\Clima\models_lib\
```

**User Documents Location:**
```
C:\Users\NW\Documents\Nemetschek\Allplan\2025\Usr\Local\PythonPartsScripts\Instalaciones\Clima\models_lib\
```

**Step 3:** Copy ENTIRE `models_lib` folder fresh to BOTH locations from:
```
c:\Users\NW\OneDrive\Escritorio\work\ON PROGRESS\CLIMA\2025\Modelat\Instalaciones\Clima\models_lib\
```

### Fix 2: Test with Simple Version First

Before testing the full advanced features version, test with the simplified version:

1. Use `mvp_example_simple.pyp` (just created) - it has NO Page 3, only core features
2. This will verify:
   - Core library works
   - 3D models load correctly
   - Coordinates are reasonable
   - No import errors

3. Once simple version works, switch back to full `mvp_example.pyp`

### Fix 3: Coordinate Issue Investigation

The coordinates show extremely large negative values:
```
Point added! Total points: 1 - (-1428527863.9, 1158006062.4, 0.0)
```

This suggests:
- Origin is being set but to a strange location
- OR there's a coordinate system issue in Allplan

**Quick Fix:**
1. When you start drawing, FIRST click "Set Current as Origin" button
2. Then start drawing your polyline
3. This will ensure coordinates are relative to a reasonable origin

## Deployment Checklist

- [ ] Close Allplan
- [ ] Delete old `models_lib` folder from ProgramData location
- [ ] Delete old `models_lib` folder from User Documents location  
- [ ] Copy NEW `models_lib` folder to ProgramData location
- [ ] Copy NEW `models_lib` folder to User Documents location
- [ ] Restart Allplan
- [ ] Test with `mvp_example_simple` first
- [ ] If simple works, test full `mvp_example` with Page 3

## Files Updated

### Core Files (Required):
- `mvp_example.py` - Main script with all event handlers
- `mvp_example.pyp` - Full palette with Page 3 (advanced features)
- `mvp_example_simple.pyp` - Simplified palette (test first)
- `polyline_base_lib.py` - Library (if modified)

### New Files (For Advanced Features):
- `mvp_example_fittings.py` - Fitting hooks (elbow, reducer)
- `test_installations.py` - Installation registry test data

## Testing Sequence

### Phase 1: Simple Test (Use mvp_example_simple.pyp)
1. Open Allplan
2. Double-click `mvp_example_simple`
3. Draw a simple polyline (3-4 points)
4. Click "Finalize & Create"
5. Verify 3D tubes appear

### Phase 2: Full Test (Use mvp_example.pyp)
1. Double-click `mvp_example`
2. Page 1: Draw polyline
3. Page 2: Read info
4. Page 3: Test advanced features one by one

## If Still Having Issues

### Clear Python Cache:
Delete all `.pyc` files and `__pycache__` folders from:
```
C:\ProgramData\Nemetschek\Allplan\2025\Etc\PythonPartsFramework\
C:\Users\NW\Documents\Nemetschek\Allplan\2025\Usr\Local\PythonPartsScripts\
```

### Check Console Output:
Look for these success messages:
```
[mvp_example] ✓ polyline_base_lib imported successfully!
[mvp_example] ✓ Imported TuboPVCConFlecha (Tube model)
[mvp_example] ✓ Imported CodoBasico (Elbow model)
[mvp_example] ✓ Imported Manguito (Coupling model)
[mvp_example] 3D models loaded - will create real geometry!
```

If you see import errors for the models, check that model files exist in the `py` folder.
