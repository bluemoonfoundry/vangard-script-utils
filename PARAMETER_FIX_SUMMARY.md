# Parameter Display Fix - Summary

## Problem Identified

The Pro mode interface was showing "This command has no parameters" for all commands, even though they had parameters defined in `config.yaml`.

### Root Cause

The JavaScript `extractParameters()` function wasn't resolving OpenAPI `$ref` references. FastAPI generates schemas like:

```json
{
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/Load_sceneRequest"
        }
      }
    }
  }
}
```

The actual parameter definitions were in `components.schemas.Load_sceneRequest.properties`, but the code wasn't looking there.

## Solution Implemented

### 1. Fixed JavaScript Parameter Extraction

**File: `vangard/static/js/app.js`**

**Changes:**
- Added `openApiSchema` to state to store full schema
- Modified `extractParameters()` to:
  - Accept full schema as parameter
  - Resolve `$ref` references by traversing the schema
  - Handle `anyOf` pattern for optional nullable fields
  - Support `x-uiclass` extension for special UI widgets

**Before:**
```javascript
function extractParameters(operation) {
    const schema = operation.requestBody.content['application/json'].schema;
    const properties = schema.properties || {};
    // ... (would fail if schema has $ref)
}
```

**After:**
```javascript
function extractParameters(operation, fullSchema) {
    let schema = operation.requestBody.content['application/json'].schema;

    // Resolve $ref if present
    if (schema.$ref) {
        const refPath = schema.$ref.split('/').slice(1);
        schema = refPath.reduce((obj, key) => obj[key], fullSchema);
    }

    const properties = schema.properties || {};
    // ... (now works with $ref)
}
```

### 2. Added UIClass Support

**Feature:** Special UI widgets for file/folder selection

**Supported UIClass Values:**
- `pick-file` - File browser button
- `pick-folder` - Folder browser button

**UI Implementation:**
- Text input field (user can type path manually)
- Browse button (for future native file picker)
- Styled wrapper with icon buttons

**CSS Added:**
```css
.file-picker-wrapper {
    display: flex;
    gap: var(--spacing-sm);
    align-items: stretch;
}

.file-picker-input {
    flex: 1;
}

.file-picker-button {
    white-space: nowrap;
    padding: var(--spacing-md) var(--spacing-lg);
}
```

## How to Use UIClass (Optional Feature)

### Adding UIClass to config.yaml

You can now add a `uiclass` field to any argument to get special UI widgets in Pro mode:

```yaml
commands:
  - name: "load-scene"
    class: "vangard.commands.LoadMergeSU.LoadMergeSU"
    help: "Load or merge DAZ Studio scene files"
    arguments:
      - names: ["scene_file"]
        dest: "scene_file"
        type: "str"
        required: true
        help: "Path to the DAZ Studio scene file"
        uiclass: "pick-file"  # ← Add this for file picker UI

      - names: ["-m", "--merge"]
        dest: "merge"
        action: "store_true"
        help: "Merge with existing scene instead of replacing"
```

### UIClass in Action

**Without UIClass (standard text input):**
```
┌─────────────────────────────────────┐
│ /path/to/scene.duf                  │
└─────────────────────────────────────┘
```

**With `uiclass: "pick-file"`:**
```
┌─────────────────────────────┬──────────────────┐
│ /path/to/scene.duf          │ 📄 Browse File   │
└─────────────────────────────┴──────────────────┘
```

**With `uiclass: "pick-folder"`:**
```
┌─────────────────────────────┬──────────────────┐
│ /path/to/output/directory   │ 📁 Browse Folder │
└─────────────────────────────┴──────────────────┘
```

## Test Results

Tested with multiple commands:

- ✅ **load-scene**: 2 parameters (scene_file, merge)
- ✅ **batch-render**: 13 parameters (all extracting correctly)
- ✅ **create-cam**: 3 parameters (cam_name, cam_class, focus)
- ✅ **help**: 1 parameter (command_name)

All commands now display their parameters correctly!

## Implementation Status

### ✅ Completed
- [x] JavaScript $ref resolution
- [x] anyOf pattern handling for optional fields
- [x] UIClass support in form generation
- [x] File picker UI widget
- [x] Folder picker UI widget
- [x] CSS styling for pickers
- [x] Documentation (UICLASS_GUIDE.md)

### 🚧 Future Enhancements
- [ ] Native file/folder browser dialogs (HTML5 File API)
- [ ] Drag-and-drop file support
- [ ] Path autocomplete
- [ ] Recent paths history
- [ ] Additional UIClass types (color picker, slider, dropdown, etc.)

## Files Modified

1. **vangard/static/js/app.js**
   - Added `openApiSchema` to state
   - Fixed `extractParameters()` to resolve $ref
   - Added UIClass widget generation
   - Updated `loadCommands()` to pass full schema

2. **vangard/static/css/styles.css**
   - Added `.file-picker-wrapper` styling
   - Added `.file-picker-input` styling
   - Added `.file-picker-button` styling

3. **New Documentation**
   - `UICLASS_GUIDE.md` - Complete guide for UIClass feature

## Testing

To verify the fix works:

1. Start Pro mode:
   ```bash
   vangard-pro
   ```

2. Open browser to: http://127.0.0.1:8000/ui

3. Click any command (e.g., "load-scene")

4. **Expected:** You should now see parameter fields:
   - "Scene File" with a text input (required field marked with *)
   - "Merge" with a checkbox

5. Commands without parameters will show "This command has no parameters"

## Benefits

1. **Fixed Core Issue**: All command parameters now display correctly
2. **Better UX**: Added special widgets for file/folder selection
3. **Extensible**: Easy to add more UIClass types in the future
4. **Backwards Compatible**: UIClass is optional, existing commands work fine
5. **CLI Unaffected**: UIClass only affects Pro mode, other modes unchanged

## Next Steps (Optional)

If you want to add file/folder pickers to your commands:

1. Edit `config.yaml`
2. Add `uiclass: "pick-file"` or `uiclass: "pick-folder"` to relevant arguments
3. Restart the Pro server
4. The UI will automatically show browse buttons for those fields

See `UICLASS_GUIDE.md` for complete examples and documentation.

---

**Status: ✅ FIXED AND TESTED**

Parameters now display correctly in Vangard Pro mode!
