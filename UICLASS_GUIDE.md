# UIClass Field Guide - Special UI Widgets for Pro Mode

The `uiclass` field in `config.yaml` allows you to specify special UI widgets for parameters in Vangard Pro mode.

## Overview

When you add a `uiclass` field to a command argument in `config.yaml`, the Pro interface will render a specialized UI widget instead of a plain text input.

## Supported UIClass Values

### `pick-folder`
Renders a text input with a "Browse Folder" button for selecting directories.

**Use case:** When the parameter expects a folder/directory path.

**Example:**
```yaml
arguments:
  - names: ["output_dir"]
    dest: "output_dir"
    type: "str"
    required: true
    help: "Output directory for rendered images"
    uiclass: "pick-folder"
```

**Renders as:**
```
Output Dir *  ⓘ
┌────────────────────────────────┬──────────────────┐
│ /path/to/output/directory      │ 📁 Browse Folder │
└────────────────────────────────┴──────────────────┘
```

---

### `pick-file`
Renders a text input with a "Browse File" button for selecting files.

**Use case:** When the parameter expects a file path.

**Example:**
```yaml
arguments:
  - names: ["scene_file"]
    dest: "scene_file"
    type: "str"
    required: true
    help: "Path to the DAZ Studio scene file (.duf)"
    uiclass: "pick-file"
```

**Renders as:**
```
Scene File *  ⓘ
┌────────────────────────────────┬────────────────┐
│ /path/to/scene.duf             │ 📄 Browse File │
└────────────────────────────────┴────────────────┘
```

---

## How It Works

### In config.yaml

Add the `uiclass` field to any argument:

```yaml
commands:
  - name: "my-command"
    class: "vangard.commands.MyCommand.MyCommand"
    help: "Example command with special UI widgets"
    arguments:
      # Regular text input
      - names: ["name"]
        dest: "name"
        type: "str"
        required: true
        help: "Name of the item"

      # File picker widget
      - names: ["input_file"]
        dest: "input_file"
        type: "str"
        required: true
        help: "Input file path"
        uiclass: "pick-file"

      # Folder picker widget
      - names: ["-o", "--output"]
        dest: "output"
        type: "str"
        default: null
        help: "Output directory"
        uiclass: "pick-folder"
```

### In the Pro Interface

When a user selects this command:

1. **Regular parameters** render as standard text inputs
2. **Parameters with `uiclass: "pick-file"`** render with a file browser button
3. **Parameters with `uiclass: "pick-folder"`** render with a folder browser button

The user can either:
- Type the path directly in the text field
- Click the browse button to select via GUI (coming soon)

### Technical Details

The `uiclass` value is passed to the frontend via OpenAPI schema using the `x-uiclass` extension field. The JavaScript form generator recognizes these values and creates the appropriate UI widgets.

## Current Implementation Status

### ✅ Implemented
- Backend support for reading `uiclass` from config.yaml
- OpenAPI schema includes `x-uiclass` extension
- Frontend recognizes and renders file/folder picker widgets
- Styled buttons and layout for pickers

### 🚧 Coming Soon
- Native file/folder browser dialogs (using HTML5 File API)
- Drag-and-drop support for file inputs
- Path validation and autocomplete
- Recently used paths history

### 💡 Future UIClass Types (Planned)

#### `pick-color`
Color picker widget for color parameters
```yaml
uiclass: "pick-color"
```

#### `slider`
Slider widget for numeric ranges
```yaml
uiclass: "slider"
# Optional: Add min, max, step
```

#### `dropdown`
Dropdown menu for enum/choice parameters
```yaml
uiclass: "dropdown"
# Optional: Add choices list
```

#### `multiline`
Textarea for long text input
```yaml
uiclass: "multiline"
```

#### `date-picker`
Date selection widget
```yaml
uiclass: "date-picker"
```

## Example: Complete Command with UIClass

Here's a complete example of a command using multiple uiclass values:

```yaml
commands:
  - name: "batch-process"
    class: "vangard.commands.BatchProcess.BatchProcess"
    help: "Batch process multiple scene files"
    arguments:
      # Folder picker for input directory
      - names: ["input_dir"]
        dest: "input_dir"
        type: "str"
        required: true
        help: "Directory containing scene files to process"
        uiclass: "pick-folder"

      # Folder picker for output directory
      - names: ["-o", "--output"]
        dest: "output"
        type: "str"
        required: true
        help: "Output directory for processed files"
        uiclass: "pick-folder"

      # Regular text input for pattern
      - names: ["-p", "--pattern"]
        dest: "pattern"
        type: "str"
        default: "*.duf"
        help: "File pattern to match (e.g., *.duf)"

      # Boolean checkbox
      - names: ["--recursive"]
        dest: "recursive"
        action: "store_true"
        help: "Process subdirectories recursively"
```

## Benefits

1. **Better UX**: Users can browse for files/folders instead of typing paths
2. **Less Errors**: Reduces typos and invalid paths
3. **Discoverability**: Makes it obvious which parameters expect paths
4. **Platform Native**: Can use native file dialogs (when implemented)
5. **Backwards Compatible**: CLI/server modes ignore uiclass, only Pro mode uses it

## Notes

- The `uiclass` field is **optional** and only affects the Pro web interface
- Other modes (CLI, Interactive, Server) ignore this field
- If `uiclass` is not specified, the parameter uses the default UI for its type
- The text input is always available, so users can type paths if they prefer

---

**Ready to use!** Just add `uiclass` fields to your command arguments in `config.yaml` and they'll automatically render as special widgets in Pro mode.
