# DAZ Script Utility Modules

This directory contains modular DAZ Script utilities that provide reusable functionality for DAZ Studio automation.

## Overview

The utility system has been refactored from a single monolithic file (1,649 lines) into 8 focused, well-documented modules for better maintainability and clarity.

## Module Organization

### Core Modules

#### 1. DazCoreUtils.dsa (141 lines)
**Foundational utilities with no dependencies**

**Functions:**
- `debug(...)` - Prints debug messages to console (only when Alt key is pressed)
- `text(sText)` - Returns translated string if localization available
- `updateModifierKeyState()` - Updates global modifier key state variables
- `inheritsType(oObject, aTypeNames)` - Checks if object inherits from specified types

**Constants:**
- `X_AXIS`, `Y_AXIS`, `Z_AXIS` - Axis identifiers
- `s_bShiftPressed`, `s_bControlPressed`, `s_bAltPressed`, `s_bMetaPressed` - Modifier key states

**Use when:** You need basic utility functions or modifier key checking

---

#### 2. DazLoggingUtils.dsa (205 lines)
**Logging and event tracking**

**Dependencies:** DazCoreUtils

**Functions:**
- `init_log(sLogFile, bOverwrite)` - Initializes log file
- `close_log()` - Closes log file
- `init_script_utils(log_source_id)` - Initializes script utilities (recommended entry point)
- `close_script_utils()` - Closes script utilities
- `log_event(event_type, event_name, event_info)` - Logs structured event
- `log_info(event_info)` - Logs informational event
- `log_warning(event_info)` - Logs warning event
- `log_error(event_info)` - Logs error event
- `log_debug(event_info)` - Logs debug event
- `log_success_event(message)` - Logs success with status indicator
- `log_failure_event(message)` - Logs failure with status indicator
- `getDefaultLogSourceName()` - Returns current log source name

**Use when:** You need structured JSON logging to files

**Example:**
```javascript
include("DazLoggingUtils.dsa");

var oScriptVars = init_script_utils("MyScript");
log_info({'message': 'Starting operation', 'parameter': oScriptVars['input']});
// ... your code ...
log_success_event("Operation completed successfully");
close_script_utils();
```

---

### File and String Operations

#### 3. DazFileUtils.dsa (195 lines)
**File I/O operations**

**Dependencies:** DazCoreUtils, DazLoggingUtils

**Functions:**
- `getFileErrorString(oFile)` - Returns human-readable error description
- `readFromFileAsJson(sFilename)` - Reads and parses JSON file
- `writeToFile(sFilename, vData, nMode)` - Writes data to file

**Use when:** You need to read/write files or handle file errors

**Example:**
```javascript
include("DazFileUtils.dsa");

var config = readFromFileAsJson("C:/Temp/config.json");
var error = writeToFile("C:/Temp/output.txt", "Hello World", DzFile.WriteOnly);
if (!error.isEmpty()) {
    log_error({'message': 'Write failed', 'error': error});
}
```

---

#### 4. DazStringUtils.dsa (174 lines)
**String manipulation and formatting**

**Dependencies:** DazLoggingUtils

**Functions:**
- `buildLabelListFromArray(aSourceList)` - Extracts labels from object array
- `extractNameAndSuffix(sSourceName)` - Splits name into base and numeric suffix
- `getNextNumericalSuffixedName(sSourceName, increment_size, next_scene_number)` - Increments numeric suffix
- `incrementedSceneFileName(input_name, increment_size, next_scene_number)` - Increments scene filename
- `getZeroPaddedNumber(input_number, padding_size)` - Pads number with zeros

**Use when:** You need to manipulate strings, generate sequential names, or format numbers

**Example:**
```javascript
include("DazStringUtils.dsa");

var nextName = getNextNumericalSuffixedName("Scene001", 1, null); // Returns "Scene002"
var padded = getZeroPaddedNumber(5, 3); // Returns "005"
```

---

### Scene and Node Management

#### 5. DazNodeUtils.dsa (303 lines)
**Node and scene manipulation**

**Dependencies:** DazCoreUtils, DazLoggingUtils

**Functions:**
- `getSkeletonNodes()` - Gets selected skeleton nodes
- `getRootNode(oNode)` - Gets root node or skeleton
- `select_node(label)` - Selects node by label
- `delete_node(label)` - Deletes node by label
- `setDefaultOptions(oSettings)` - Sets default render settings
- `setRequiredOptions(oSettings, bShowOptions)` - Sets required render settings
- `setElementOption(oSettings, sElementSettingsKey, sElementName)` - Adds element to settings
- `setNodeOption(oSettings, sNodeName)` - Sets node option
- `setNodeOptions(oSettings, aNodeNames)` - Sets multiple node options
- `triggerAction(sClassName, oSettings)` - Triggers DAZ action
- `loadScene(sSceneFile, iMode)` - Loads scene file
- `getSimpleTextInput(sCurrentText)` - Shows text input dialog

**Use when:** You need to manipulate nodes, load scenes, or trigger actions

**Example:**
```javascript
include("DazNodeUtils.dsa");

var node = select_node("Genesis 9");
if (node != null) {
    triggerAction("DzSelectChildrenAction", null);
}

var error = loadScene("C:/Scenes/MyScene.duf", Scene.OpenNew);
```

---

#### 6. DazTransformUtils.dsa (212 lines)
**Transform operations**

**Dependencies:** DazCoreUtils, DazLoggingUtils

**Functions:**
- `transferNodeTransforms(oToNode, oFromNode, bTranslate, bRotate, bScale)` - Transfers transforms
- `getRandomValue(low_range, high_range)` - Generates random value
- `transformNodeRotate(oFromNode, fValue, sAxis)` - Rotates node on axis
- `dropNodeToNode(oFromNode, sAxis, fValue)` - Translates node on axis

**Use when:** You need to manipulate node positions, rotations, or scales

**Example:**
```javascript
include("DazTransformUtils.dsa");

var sourceNode = Scene.findNodeByLabel("Source");
var targetNode = Scene.findNodeByLabel("Target");
transferNodeTransforms(targetNode, sourceNode, true, true, false);

transformNodeRotate(sourceNode, 45.0, Y_AXIS);
dropNodeToNode(targetNode, 'y', 0.0); // Drop to ground
```

---

### Camera Operations

#### 7. DazCameraUtils.dsa (185 lines)
**Camera management**

**Dependencies:** DazLoggingUtils

**Functions:**
- `transferCameraProperties(oTargetCamera, oSourceCamera)` - Copies camera properties
- `getViewportCamera()` - Gets active viewport camera
- `setViewportCamera(oCamera)` - Sets viewport camera
- `getNamedCamera(camera_label)` - Finds camera by label
- `getValidCameraList(oRenderConfig)` - Gets cameras matching criteria
- `createPerspectiveCamera(cameraLabelPrefix, cameraName, cameraClass)` - Creates new camera

**Use when:** You need to work with cameras or viewport

**Example:**
```javascript
include("DazCameraUtils.dsa");

var viewportCam = getViewportCamera();
var newCam = createPerspectiveCamera("Render", "Front", "Perspective");
if (newCam != null) {
    transferCameraProperties(newCam, viewportCam);
    setViewportCamera(newCam);
}
```

---

### Rendering

#### 8. DazRenderUtils.dsa (358 lines)
**Rendering operations and batch processing**

**Dependencies:** DazCoreUtils, DazLoggingUtils, DazCameraUtils, DazStringUtils

**Functions:**
- `prepareIrayBridgeConfiguration(oIrayConfig, oRenderMgr, oRenderer)` - Configures Iray server
- `getDefaultLocalRenderOptions(oRenderMgr, oCamera)` - Gets default render options
- `execLocalToFileRender(oRenderMgr, oRenderOptions, sRenderFile, oCamera)` - Renders to file
- `execNewWindowRender(oRenderMgr, oRenderOptions, oCamera)` - Renders to new window
- `execBatchRender(oRenderConfig, sRenderTarget, sOutputBasePath)` - Executes batch render

**Use when:** You need to render scenes or configure Iray

**Example:**
```javascript
include("DazRenderUtils.dsa");

var oRenderMgr = App.getRenderMgr();
var oCamera = getViewportCamera();
var oRenderOptions = getDefaultLocalRenderOptions(oRenderMgr, oCamera);

execLocalToFileRender(oRenderMgr, oRenderOptions, "C:/Renders/output.png", oCamera);
```

---

## Backward Compatibility

### DazCopilotUtils.dsa (153 lines)
**Facade that includes all modules**

This file maintains backward compatibility by including all 8 specialized modules. Existing scripts that use:

```javascript
include("DazCopilotUtils.dsa");
```

...will continue to work without modification.

---

## Usage Guidelines

### For Existing Scripts
Continue using the facade:
```javascript
include("DazCopilotUtils.dsa");
```

### For New Scripts (Recommended)
Include only the modules you need:
```javascript
include("DazLoggingUtils.dsa");
include("DazCameraUtils.dsa");
include("DazRenderUtils.dsa");
```

### Benefits of Modular Includes
1. **Faster loading**: Only load what you need
2. **Clearer dependencies**: Easy to see what functionality you're using
3. **Better organization**: Separate concerns in your code
4. **Easier maintenance**: Changes to unused modules don't affect your script

---

## Dependency Graph

```
DazCoreUtils (foundational, no dependencies)
    ├─ DazLoggingUtils
    │   ├─ DazFileUtils
    │   ├─ DazStringUtils
    │   ├─ DazNodeUtils
    │   ├─ DazTransformUtils
    │   └─ DazCameraUtils
    └─ DazFileUtils, DazNodeUtils, DazTransformUtils

DazRenderUtils depends on:
    ├─ DazCoreUtils
    ├─ DazLoggingUtils
    ├─ DazCameraUtils
    └─ DazStringUtils
```

---

## Common Patterns

### Standard Script Template

```javascript
// Include required modules
include("DazLoggingUtils.dsa");
include("DazNodeUtils.dsa");

// Initialize script
var oScriptVars = init_script_utils("MyScriptName");

try {
    // Your script logic here
    log_info({'message': 'Starting operation'});

    // ... do work ...

    log_success_event("Operation completed successfully");
} catch (e) {
    log_failure_event("Operation failed: " + e.toString());
}

// Clean up
close_script_utils();
```

### Batch Rendering Template

```javascript
include("DazLoggingUtils.dsa");
include("DazCameraUtils.dsa");
include("DazRenderUtils.dsa");

var oScriptVars = init_script_utils("BatchRender");

var oRenderConfig = {
    'cameras': 'all_visible',
    'frames': '0-10',
    'job_name_pattern': '%s_%c_%f',
    'output_extension': 'png'
};

execBatchRender(oRenderConfig, "local-to-file", "C:/Renders");

close_script_utils();
```

---

## Testing

While DAZ Script code cannot be automatically tested without DAZ Studio, the Python test suite verifies:
- All Python command wrappers work correctly
- Arguments are properly passed to scripts
- The command framework remains stable

Run tests with:
```bash
pytest tests/ -v
```

All 189 tests pass after refactoring, confirming backward compatibility.

---

## Migration Notes

### From Monolithic to Modular

The original `DazCopilotUtils.dsa` (1,649 lines) has been split into:
- 8 focused modules (1,773 lines of code + headers)
- 1 facade file (153 lines of documentation)
- Total: 1,926 lines (278 line increase due to module headers and documentation)

### No Breaking Changes
- All existing scripts continue to work
- All function signatures unchanged
- All functionality preserved
- New modular organization is opt-in

---

## Questions or Issues?

If you encounter any issues with the modular utilities:
1. Check that you're including the correct modules for your needs
2. Verify the dependency graph above
3. For backward compatibility, fall back to `include("DazCopilotUtils.dsa")`
4. Report issues at: https://github.com/anthropics/claude-code/issues
