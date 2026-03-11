# UI Hints Implementation Summary

This document summarizes the implementation of UI hints support in Pro Mode.

## Overview

UI hints allow `config.yaml` to specify visual metaphors for command arguments, providing better user experience in the Pro web interface. Instead of generic text fields, users now get appropriate controls like sliders, dropdowns, file pickers, etc.

## Changes Made

### 1. Backend: `vangard/server.py`

**Added:**
- Import `Field` from pydantic
- Extract `ui` metadata from config.yaml arguments
- Pass UI metadata through OpenAPI schema via `json_schema_extra`

**Key Changes:**
```python
# Import Field
from pydantic import create_model, BaseModel, Field

# Extract and pass UI metadata
ui_metadata = arg.get("ui", {})
field_kwargs = {
    "description": description,
}
if ui_metadata:
    field_kwargs["json_schema_extra"] = {"ui": ui_metadata}

# Use Field() for all pydantic fields
pydantic_fields[field_name] = (field_type, Field(..., **field_kwargs))
```

### 2. Frontend: `vangard/static/js/app.js`

**Modified Functions:**
- `extractParameters()` - Now reads `ui` metadata from OpenAPI schema
- `generateFormField()` - Completely rewritten to support all widget types

**New Functions:**
- `inferWidget()` - Infers widget type from parameter properties
- `generateTextInput()` - Text input with placeholder
- `generateNumberInput()` - Number input with min/max/step
- `generateSpinnerInput()` - Number spinner
- `generateSliderInput()` - Range slider with value display
- `generateSelectInput()` - Dropdown with choices
- `generateCheckboxInput()` - Checkbox for booleans
- `generateRadioInput()` - Radio buttons for exclusive choices
- `generateFilePickerInput()` - File/folder picker
- `generateTextareaInput()` - Multi-line text input
- `updateSliderValue()` - Updates slider value display in real-time

### 3. Styling: `vangard/static/css/styles.css`

**Added Styles:**
- `.slider-container` - Flex container for slider + value
- `.form-slider` - Custom slider styling (webkit and moz)
- `.slider-value` - Value display next to slider
- `.radio-group` - Radio button container
- `.form-radio-wrapper` - Radio button + label wrapper
- `.form-radio` - Radio button styling
- `textarea.form-input` - Textarea enhancements
- `select.form-input` - Enhanced dropdown with custom arrow

## Supported Widget Types

### 1. **text** (default)
```yaml
ui:
  widget: "text"
  placeholder: "Enter value"
```

### 2. **number** / **spinner**
```yaml
ui:
  widget: "spinner"
  min: 0
  max: 100
  step: 1
```

### 3. **slider**
```yaml
ui:
  widget: "slider"
  min: 0
  max: 360
  step: 15
  show_value: true
```

### 4. **select** (dropdown)
```yaml
ui:
  widget: "select"
  choices:
    - value: "option1"
      label: "Option 1"
    - value: "option2"
      label: "Option 2"
```
Or simplified:
```yaml
ui:
  widget: "select"
  choices: ["option1", "option2", "option3"]
```

### 5. **checkbox**
```yaml
ui:
  widget: "checkbox"
```

### 6. **radio**
```yaml
ui:
  widget: "radio"
  choices:
    - value: "choice1"
      label: "Choice 1"
    - value: "choice2"
      label: "Choice 2"
```

### 7. **file-picker**
```yaml
ui:
  widget: "file-picker"
  file_type: "file"
  extensions: [".duf", ".dsx"]
  mode: "save"  # or omit for open
```

### 8. **folder-picker**
```yaml
ui:
  widget: "folder-picker"
```

### 9. **textarea**
```yaml
ui:
  widget: "textarea"
  rows: 4
  placeholder: "Enter text"
```

## Widget Type Inference

If no `widget` is specified, the system infers it from parameter type:
- `type: "boolean"` → `checkbox`
- `type: "integer"` or `type: "number"` → `number`
- `type: "array"` → `text` (comma-separated)
- Default → `text`

## Example: rotate-render Command

```yaml
- name: "rotate-render"
  arguments:
    - names: ["object_name"]
      dest: "object_name"
      type: "str"
      required: true
      help: "Label of the object to rotate"
      ui:
        widget: "text"
        placeholder: "e.g., Genesis9, Camera, Chair"

    - names: ["lower"]
      dest: "lower"
      type: "int"
      default: 0
      help: "Starting rotation (in degrees)"
      ui:
        widget: "slider"
        min: 0
        max: 360
        step: 15
        show_value: true

    - names: ["slices"]
      dest: "slices"
      type: "int"
      help: "How many rotations"
      ui:
        widget: "spinner"
        min: 0
        max: 72
        step: 1

    - names: ["-o", "--output-file"]
      dest: "output_file"
      type: "str"
      help: "Output directory"
      ui:
        widget: "folder-picker"
```

## Benefits

1. **Better UX** - Visual controls are more intuitive than text fields
2. **Client-side Validation** - Min/max/choices provide immediate feedback
3. **Self-documenting** - UI controls show valid ranges/options visually
4. **Backward Compatible** - CLI and other modes ignore `ui` metadata
5. **Extensible** - Easy to add new widget types in the future

## Testing

To test the implementation:

1. Start Pro Mode:
   ```bash
   vangard-pro
   ```

2. Open browser to `http://127.0.0.1:8000/ui`

3. Select a command with UI hints (e.g., `rotate-render`)

4. Verify:
   - Sliders display with value indicators
   - Spinners have up/down arrows
   - Dropdowns show choices
   - File pickers have browse buttons
   - All default values are populated correctly

## Future Enhancements

Potential improvements:
- Color picker widget
- Date/time picker
- Tag input widget
- Multi-select widget
- Native file picker dialogs (via browser API)
- Range slider (two thumbs for min/max)
- Conditional field visibility based on other fields

## Files Modified

1. `vangard/server.py` - Backend API schema generation
2. `vangard/static/js/app.js` - Frontend form generation
3. `vangard/static/css/styles.css` - Widget styling
4. `config.yaml` - Added UI hints to all 22 commands (70 total widgets)
