# Quick Test Steps for PointInput Integration

## ✅ What You Already Have

Your `mvp_example.pyp` already has:
- ✅ `PathId` (Integer, default: 1)
- ✅ `SegmentId` (Integer, default: 1)  
- ✅ `PointRole` (IntegerComboBox: 0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final)
- ✅ `CreatePythonPartGroup` (CheckBox)

## ⚠️ What You Need to Add

Add `FinishNow` parameter to your `.pyp` file (optional but recommended):

```xml
<Parameter>
  <Name>FinishNow</Name>
  <Text>Finish Current Path Now</Text>
  <Value>False</Value>
  <ValueType>CheckBox</ValueType>
  <Visible>CaptureExpander</Visible>
</Parameter>
```

Add this inside the `CaptureExpander` section (around line 270).

---

## 🚀 Quick Test (5 Minutes)

### Step 1: Enable Capture Mode

In your Python code (`mvp_example.py`), make sure capture mode is enabled:

```python
config = polyline_base_lib.PolylineBaseConfig(
    enable_capture_mode=True,              # ← Enable this!
    capture_auto_commit_on_final=True,     # Auto-create on Final click
    capture_auto_export_json=True,        # Export JSON
    capture_finish_on_cancel=True,         # Finalize on ESC
)
```

### Step 2: Test in Allplan

1. **Open Allplan** and load your PythonPart
2. **Expand "Capture Mode"** in the palette (it's collapsed by default)
3. **Set these values:**
   - `PathId` = 1
   - `PointRole` = 0 (Inicial)
   - `CreatePythonPartGroup` = False (for simple test)

4. **Click points:**
   - Click point 1 (Inicial)
   - Change `PointRole` = 1 (Paso), click point 2
   - Change `PointRole` = 1 (Paso), click point 3
   - Change `PointRole` = 3 (Final), click point 4
   - **Expected:** Polylines appear immediately!

5. **Check Desktop:**
   - Look for file: `route_groups_XXXXXXXX.json`
   - Open it - should contain your points

---

## 📋 What to Look For

### ✅ Success Signs:
- Console shows: `[CAPTURE] Created X polylines for path Y`
- Polylines appear in drawing when Final is clicked
- JSON file appears on Desktop
- Color changes when you change PathId

### ❌ Problems:
- **No polylines created?** 
  - Check: Is `capture_auto_commit_on_final` = True in config?
  - Check: Is `CreatePythonPartGroup` = False? (for simple test)
  
- **No JSON file?**
  - Check: Is `capture_auto_export_json` = True in config?
  - Check: Desktop folder permissions

- **Nothing happens?**
  - Check: Is `enable_capture_mode` = True in config?
  - Check: Console for error messages

---

## 🎯 Simple Test Workflow

```
1. Load PythonPart in Allplan
2. Expand "Capture Mode" section
3. Set PathId = 1, PointRole = 0 (Inicial)
4. Click first point
5. Set PointRole = 1 (Paso), click 2 more points
6. Set PointRole = 3 (Final), click last point
   → Polylines should appear!
7. Check Desktop for JSON file
```

That's it! If this works, the integration is successful! 🎉

---

## 📝 Notes

- **PointRole values:** 0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final
- **PathId:** Each route gets a different number (1, 2, 3...)
- **Color:** Automatically matches PathId (PathId 1 = Color 1, etc.)
- **JSON:** Saved to Desktop as `route_groups_XXXXXXXX.json`

---

## 🔧 If Something Doesn't Work

1. **Check console output** - look for error messages
2. **Verify config** - make sure `enable_capture_mode=True`
3. **Check palette** - make sure parameters exist
4. **Test simple case first** - one path, 3-4 points, Final role

Good luck! 🚀
