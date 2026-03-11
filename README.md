# Vangard Script Utils

A powerful, configuration-driven command-line utility system that provides standardized automation scripts for DAZ Studio. This toolkit acts as a bridge between Python and DAZ Studio's scripting language (DSA), offering multiple interaction modes including CLI, interactive shell, REST API server, GUI, and a modern web interface (Pro mode).

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [CLI Mode](#cli-mode)
  - [Interactive Mode](#interactive-mode)
  - [Server Mode](#server-mode)
  - [GUI Mode](#gui-mode)
  - [Pro Mode](#pro-mode)
- [DAZ Script Server](#daz-script-server)
- [Available Commands](#available-commands)
- [Adding New Commands](#adding-new-commands)
- [Development](#development)
- [License](#license)

## Features

- **Configuration-Driven**: All commands defined in a central YAML configuration file
- **Multiple Interface Modes**: CLI, interactive shell, REST API, GUI, and Pro web interface
- **Dynamic Command Loading**: Commands are loaded and parsed at runtime
- **Extensible Architecture**: Easy to add new commands without modifying core code
- **Type-Safe Arguments**: Automatic argument validation and type conversion
- **Auto-Generated Documentation**: Command reference documentation generated from config
- **DAZ Studio Integration**: Seamless execution of DAZ Studio scripts via subprocess or a high-performance [Script Server plugin](https://github.com/bluemoonfoundry/vangard-daz-script-server)
- **Smart Autocomplete**: Scene-aware autocomplete in Interactive and Pro modes (requires Script Server)
- **Pro Mode**: Modern, dark-themed web interface with dynamic forms and real-time feedback

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│  (CLI Args / Interactive Shell / HTTP Request / GUI / Pro)   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              vangard/main.py (Entry Point)                   │
│   Routes to: cli.py, interactive.py, server.py,             │
│              gui.py, or pro.py                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              core/framework.py (Core Engine)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ apply_startup_flags() - Processes CLI startup flags │   │
│  │ load_config()    - Loads config.yaml                │   │
│  │ build_parser()   - Creates argparse from config     │   │
│  │ load_class()     - Dynamically imports command class│   │
│  │ run_command()    - Executes command instance        │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          vangard/commands/ (Python Command Classes)          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BaseCommand (Abstract Base)                         │   │
│  │   - process(args)                                   │   │
│  │   - exec_remote_script(script_name, vars)           │   │
│  │   - to_dict(args)                                   │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │ Specific Commands (inherit from BaseCommand)        │   │
│  │ LoadMergeSU, BatchRenderSU, CreateGroupNodeSU, etc. │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Execution Mode (selected by DAZ_SCRIPT_SERVER_ENABLED env var)       │
│                                                                        │
│  Subprocess (default)            │  DAZ Script Server                 │
│  DAZ Studio launched with        │  POST /execute to running server   │
│  -scriptArg (JSON) + .dsa path   │  {"scriptFile": "...", "args": {}} │
└──────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         vangard/scripts/ (DAZ Studio Script Files)           │
│  LoadMergeSU.dsa, BatchRenderSU.dsa, ... (one per command)  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **config.yaml**: Central configuration defining all commands, arguments, and class mappings
2. **core/framework.py**: Core engine that loads config, builds parsers, applies startup flags, and executes commands
3. **vangard/commands/**: Python command classes that process arguments and launch DAZ scripts
4. **vangard/scripts/**: DAZ Studio script files (.dsa) that perform actual operations in DAZ
5. **vangard/scene_cache.py**: Polls DAZ Studio via the Script Server for scene node data, used for smart autocomplete
6. **Interface Layers**: CLI, Interactive Shell, FastAPI Server, GUI, and Pro web interface

### Command Execution Flow

1. User invokes command through any interface mode
2. Interface layer parses input and passes to core framework
3. Framework loads corresponding command class from config.yaml
4. Command class processes arguments and converts to JSON
5. Command executes via DAZ Studio subprocess (default) or sends REST request to Script Server plugin
6. DAZ Studio script executes operation and returns results

## Prerequisites

- **Python**: 3.8 or higher
- **DAZ Studio**: Installed and configured
- **Operating System**: Windows, macOS, or Linux

## Installation

### Quick Install (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bluemoonfoundry/vangard-script-utils.git
   cd vangard-script-utils
   ```

2. **Install the package** (editable mode for development):
   ```bash
   pip install -e .
   ```

   This installs the package and creates console script commands:
   - `vangard` - Multi-mode launcher
   - `vangard-cli` - Direct CLI access
   - `vangard-interactive` - Interactive shell
   - `vangard-server` - FastAPI server
   - `vangard-gui` - GUI interface
   - `vangard-pro` - Pro web interface

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```bash
   # DAZ Studio subprocess mode (default)
   DAZ_ROOT=/path/to/daz/studio/executable
   DAZ_ARGS=--optional-daz-arguments

   # DAZ Script Server plugin mode (optional)
   DAZ_SCRIPT_SERVER_ENABLED=false
   DAZ_SCRIPT_SERVER_HOST=127.0.0.1
   DAZ_SCRIPT_SERVER_PORT=18811
   ```

   **Subprocess mode** (default):
   - `DAZ_ROOT`: Absolute path to your DAZ Studio executable
     - Windows: `C:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe`
     - macOS: `/Applications/DAZ 3D/DAZStudio4 64-bit/DAZStudio.app/Contents/MacOS/DAZStudio`
   - `DAZ_ARGS`: Optional additional arguments to pass to DAZ Studio

   **DAZ Script Server mode** (optional — see [DAZ Script Server](#daz-script-server)):
   - `DAZ_SCRIPT_SERVER_ENABLED`: Set to `true` to enable server mode instead of subprocess. Default: `false`
   - `DAZ_SCRIPT_SERVER_HOST`: Hostname or IP of the DAZ Script Server. Default: `127.0.0.1`
   - `DAZ_SCRIPT_SERVER_PORT`: Port of the DAZ Script Server. Default: `18811`

### Alternative: Manual Installation

```bash
pip install -r requirements.txt
python -m vangard.main [mode] [arguments]
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

## Configuration

All commands are defined in `config.yaml`. The configuration structure:

```yaml
app:
  prog: "vangard-cli"
  description: "A command-line interface for the Vangard toolkit."

commands:
  - name: "command-name"
    class: "vangard.commands.CommandClassName.CommandClassName"
    help: "Description of what the command does"
    arguments:
      - names: ["positional_arg"]
        dest: "positional_arg"
        type: "str"
        required: true
        help: "Description of positional argument"
      - names: ["-o", "--option"]
        dest: "option"
        type: "str"
        default: null
        help: "Description of optional argument"
```

### Argument Types

| `type` value | Python type |
|---|---|
| `str` | `str` |
| `int` | `int` |
| `float` | `float` |
| *(omit type, use `action: "store_true"`)* | `bool` flag |

For list arguments, add `nargs: "*"` or `nargs: "+"`.

### UI Metadata (`ui` field)

Each argument can include a `ui` block that controls how it is rendered in Pro mode and the GUI. This is ignored by the CLI.

```yaml
arguments:
  - names: ["scene_file"]
    dest: "scene_file"
    type: "str"
    ui:
      widget: "file-picker"
      file_type: "file"
      extensions: [".duf", ".dsf"]
      mode: "save"         # "save" or "open" (for file-picker)
```

**Available widgets**:

| `widget` | Description | Extra keys |
|---|---|---|
| `text` | Plain text input | `placeholder` |
| `number` | Numeric input | `min`, `max`, `step` |
| `spinner` | Integer stepper | `min`, `max`, `step` |
| `slider` | Range slider | `min`, `max`, `step`, `show_value` |
| `checkbox` | Boolean toggle | — |
| `radio` | Radio button group | `choices` |
| `select` | Dropdown list | `choices` |
| `textarea` | Multi-line text | `rows`, `placeholder` |
| `file-picker` | File path input with browse button | `file_type`, `extensions`, `mode` |
| `folder-picker` | Folder path input with browse button | — |

**`choices` format** (for `select` and `radio`):
```yaml
choices:
  - value: "direct-file"
    label: "Direct to File (Local)"
  - value: "local-to-window"
    label: "Local to Window"
# or simple string list:
choices: ["png", "jpg", "tif"]
```

### Autocomplete (`autocomplete` field)

Arguments that accept scene node names can be configured for smart autocomplete. This requires the DAZ Script Server to be active (see [DAZ Script Server](#daz-script-server)).

```yaml
arguments:
  - names: ["target_node"]
    dest: "target_node"
    type: "str"
    autocomplete:
      source: "scene-nodes"
      types: ["figure", "prop", "camera"]  # optional — omit to include all types
```

**Node types available for filtering**: `camera`, `light`, `figure`, `prop`, `group`, `conformer`

When `types` is omitted, all non-bone scene nodes are offered as suggestions.

## Usage

After installation, you can use the package in two ways:

### Option 1: Console Scripts (Recommended)

```bash
vangard-cli [command] [arguments]
# or
vangard cli [command] [arguments]
```

### Option 2: Python Module

```bash
python -m vangard.cli [command] [arguments]
# or
python -m vangard.main cli [command] [arguments]
```

---

### Startup Flags

All modes support the following flag:

| Flag | Description |
|---|---|
| `--enable-script-server` | Enable DAZ Script Server mode for this session, overriding the `DAZ_SCRIPT_SERVER_ENABLED` environment variable. Requires DAZ Studio to be running with the Script Server plugin active — the tool will exit with a diagnostic message if the server cannot be reached. |

Examples:
```bash
vangard-interactive --enable-script-server
vangard-pro --enable-script-server
vangard-server --enable-script-server
vangard interactive --enable-script-server
```

---

### CLI Mode

Execute single commands from the command line:

```bash
vangard-cli [command] [arguments]
```

**Examples**:

```bash
# Load a scene file
vangard-cli load-scene /path/to/scene.duf

# Load and merge a scene
vangard-cli load-scene /path/to/scene.duf --merge

# Render current scene
vangard-cli scene-render -o /path/to/output.png

# Batch render multiple scenes
vangard-cli batch-render -s "/path/to/scenes/*.duf" -o /output/dir

# Create a camera
vangard-cli create-cam "MyCamera" "PerspectiveCamera" --focus

# Save scene with incremented filename
vangard-cli inc-scene

# Capture the active viewport to image files
vangard-cli save-viewport -f C:/output/frame

# Get help for a specific command
vangard-cli help batch-render
```

### Interactive Mode

Launch an interactive shell with command history and auto-completion:

```bash
vangard-interactive
vangard-interactive --enable-script-server
```

Once in the shell:

```
vangard-cli> load-scene /path/to/scene.duf
vangard-cli> create-cam "Camera1" "PerspectiveCamera"
vangard-cli> scene-render -o /path/to/output.png
vangard-cli> exit
```

**Interactive Mode Features**:
- Command auto-completion (press Tab)
- Command history (use Up/Down arrows)
- Persistent history across sessions (stored in `.cli_history`)
- **Scene-aware autocomplete**: When started with `--enable-script-server`, argument fields marked with `autocomplete: scene-nodes` in `config.yaml` suggest live node names from the current DAZ Studio scene

**Special Commands** (available when Script Server is enabled):

| Command | Shortcut | Description |
|---|---|---|
| `.refresh` | `.r` | Immediately refresh the scene node cache |
| `.stats` | `.s` | Show scene cache statistics (node counts, staleness, polling status) |
| `.help` | `.h`, `.?` | Show available special commands |

### Server Mode

Run as a FastAPI REST API server:

```bash
vangard-server
vangard-server --enable-script-server
```

The server starts at `http://127.0.0.1:8000` with:
- **Interactive API documentation**: http://127.0.0.1:8000/docs
- **OpenAPI schema**: http://127.0.0.1:8000/openapi.json

**API Endpoints**:
- `GET /`: Health check
- `POST /api/{command-name}`: Execute command (one endpoint per command in config.yaml)

**Example API Request**:

```bash
curl -X POST "http://127.0.0.1:8000/api/load-scene" \
  -H "Content-Type: application/json" \
  -d '{"scene_file": "/path/to/scene.duf", "merge": false}'
```

### GUI Mode

Launch a simple graphical interface:

```bash
vangard-gui
vangard-gui --enable-script-server
```

### Pro Mode

Launch the professional web interface — a modern, dark-themed browser UI with dynamic forms, real-time feedback, and command discovery:

```bash
vangard-pro
vangard-pro --enable-script-server
```

The server starts at **http://127.0.0.1:8000/ui**.

**Pro Mode Features**:
- **Visual Command Browser**: Searchable sidebar listing all available commands with icons and descriptions
- **Dynamic Forms**: Forms are auto-generated from `config.yaml` — respecting widget types, choices, file pickers, sliders, etc.
- **Scene Autocomplete**: When started with `--enable-script-server`, text fields with `autocomplete: scene-nodes` are populated with live node names from the current DAZ Studio scene
- **Real-time Output**: Color-coded results (green = success, red = error) with timestamps
- **Dark/Light Theme**: Toggle via the toolbar
- **API Access**: Swagger UI still available at `/docs`

**Pro Mode Scene API** (additional endpoints available when running Pro mode):

| Endpoint | Method | Description |
|---|---|---|
| `/api/scene/nodes` | GET | Get cached scene nodes, optionally filtered by `node_type` and `name_filter` |
| `/api/scene/labels` | GET | Get node label strings for autocomplete, optionally filtered by `node_type` |
| `/api/scene/refresh` | POST | Force an immediate scene cache refresh |
| `/api/scene/stats` | GET | Get cache statistics (node counts, last update time, polling status) |

See [PRO_MODE.md](PRO_MODE.md) for full documentation on Pro mode customization.

**Mode Comparison**:

| Feature | CLI | Interactive | GUI | Server | Pro |
|---------|-----|-------------|-----|--------|-----|
| Visual Interface | ❌ | ❌ | ✅ | ❌ | ✅ |
| No Command Syntax Required | ❌ | ❌ | ✅ | ✅ | ✅ |
| Form-based Input | ❌ | ❌ | ✅ | ✅ | ✅ |
| Modern Design | ❌ | ❌ | ❌ | N/A | ✅ |
| Real-time Feedback | ✅ | ✅ | ✅ | ✅ | ✅ |
| Scene Autocomplete | ❌ | ✅* | ❌ | ❌ | ✅* |
| API Access | ❌ | ❌ | ❌ | ✅ | ✅ |
| Web-based | ❌ | ❌ | ❌ | ✅ | ✅ |

*Requires `--enable-script-server` or `DAZ_SCRIPT_SERVER_ENABLED=true`

## DAZ Script Server

The DAZ Script Server is an optional DAZ Studio plugin that enables a high-performance REST API interface for script execution. It is available as a separate repository: [vangard-daz-script-server](https://github.com/bluemoonfoundry/vangard-daz-script-server).

### Why Use the Script Server?

- **No subprocess launch overhead**: Scripts execute inside an already-running DAZ Studio instance
- **Scene awareness**: The script server enables the scene cache, which powers smart autocomplete in Interactive and Pro modes
- **Faster iteration**: Commands return results immediately rather than waiting for DAZ Studio to start

### Enabling the Script Server

**Option 1 — Startup flag** (per session, no `.env` change needed):
```bash
vangard-pro --enable-script-server
```
If the server cannot be reached, the tool exits immediately with a diagnostic message listing what to check.

**Option 2 — Environment variable** (persistent via `.env`):
```env
DAZ_SCRIPT_SERVER_ENABLED=true
DAZ_SCRIPT_SERVER_HOST=127.0.0.1
DAZ_SCRIPT_SERVER_PORT=18811
```

### Requirements

1. DAZ Studio must be running
2. The Script Server plugin must be installed and started inside DAZ Studio
3. The server must be listening on the configured host and port

### How Commands Are Sent

When server mode is active, commands are sent as a `POST` request to `http://<host>:<port>/execute`:

```json
{
  "scriptFile": "/absolute/path/to/Script.dsa",
  "args": { "arg_name": "value" }
}
```

The server responds with:
```json
{
  "success": true,
  "result": "<last evaluated expression>",
  "output": ["lines printed by the script"],
  "error": null
}
```

### Scene Cache

When the Script Server is enabled, the scene cache (`vangard/scene_cache.py`) polls DAZ Studio every 30 seconds to retrieve the current scene node hierarchy. This data powers:

- Tab-completion of node names in Interactive mode
- Autocomplete datalists in Pro mode form fields

Nodes returned by the cache are classified into: `camera`, `light`, `figure` (root characters only), `prop`, `group`, and `conformer` (clothing/hair attached to a figure). Bones are excluded from the cache as they add noise without being useful for autocomplete.

## Available Commands

For a complete reference of all commands and their arguments, see [config_reference.md](config_reference.md).

**Common Commands**:

- `load-scene`: Load or merge DAZ Studio scene files
- `batch-render`: Batch render multiple scenes with customizable options
- `scene-render`: Render the current scene
- `create-cam`: Create a new camera in the scene
- `create-group`: Group selected nodes
- `copy-camera`: Copy camera settings between cameras
- `transform-copy`: Copy transforms (translate/rotate/scale) between nodes
- `apply-pose`: Apply pose files to characters
- `rotate-render`: Rotate object and render at intervals
- `inc-scene`: Save scene with incremented filename
- `product-list`: List products used in current scene
- `save-subset`: Save selected items to scene subset file
- `save-viewport`: Capture the active viewport to image files for a range of frames
- `face-render-lora`: Render orbital camera angles around a figure's face for LoRA training image generation

## Adding New Commands

### 1. Define Command in config.yaml

```yaml
commands:
  - name: "my-new-command"
    class: "vangard.commands.MyNewCommandSU.MyNewCommandSU"
    help: "Description of what your command does"
    arguments:
      - names: ["required_arg"]
        dest: "required_arg"
        type: "str"
        required: true
        help: "Description of required argument"
        ui:
          widget: "text"
          placeholder: "Enter value"
      - names: ["-o", "--optional-arg"]
        dest: "optional_arg"
        type: "int"
        default: 0
        help: "Description of optional argument"
        ui:
          widget: "spinner"
          min: 0
          max: 100
          step: 1
```

### 2. Create Python Command Class

Create `vangard/commands/MyNewCommandSU.py`:

```python
from vangard.commands.BaseCommand import BaseCommand

class MyNewCommandSU(BaseCommand):
    # Default implementation calls MyNewCommandSU.dsa script.
    # Override process() only if you need custom Python-side logic.
    pass
```

### 3. Create DAZ Studio Script

Create `vangard/scripts/MyNewCommandSU.dsa`:

```javascript
includeDir_oFILE = DzFile( getScriptFileName() );
util_path = includeDir_oFILE.path() + "/DazCopilotUtils.dsa";
include(util_path);

function MyNewCommandSU() {
    sFunctionName = 'MyNewCommandSU';
    oScriptVars = init_script_utils(sFunctionName);

    var sRequiredArg = oScriptVars['required_arg'];
    var nOptionalArg = oScriptVars['optional_arg'] || 0;

    // Implement your DAZ Studio logic here

    log_success_event('Command executed successfully');
    close_script_utils();
}

MyNewCommandSU();
```

Available utility libraries to include alongside `DazCopilotUtils.dsa`:
`DazCameraUtils.dsa`, `DazCoreUtils.dsa`, `DazFileUtils.dsa`, `DazLoggingUtils.dsa`,
`DazNodeUtils.dsa`, `DazRenderUtils.dsa`, `DazStringUtils.dsa`, `DazTransformUtils.dsa`

### 4. Update Documentation

```bash
python generate_docs.py
```

### 5. Add Tests

Create `tests/commands/test_my_new_command_su.py` following the pattern of existing test files:

```bash
pytest tests/commands/test_my_new_command_su.py -v
pytest tests/integration/  # Verify config consistency
```

## Development

### Project Structure

```
vangard-script-utils/
├── config.yaml             # Command definitions (central registry)
├── config_reference.md     # Auto-generated command reference
├── generate_docs.py        # Regenerates config_reference.md
├── pyproject.toml          # Package configuration
├── requirements.txt        # Python dependencies
├── core/
│   └── framework.py        # Core engine (config loading, arg parsing, startup flags)
├── vangard/
│   ├── main.py             # Multi-mode entry point
│   ├── cli.py              # CLI interface
│   ├── interactive.py      # Interactive shell
│   ├── server.py           # FastAPI server
│   ├── gui.py              # GUI interface
│   ├── pro.py              # Pro web interface
│   ├── scene_cache.py      # Scene node cache for autocomplete
│   ├── interactive_completer.py  # Smart tab-completion for interactive mode
│   ├── static/             # Pro mode frontend assets
│   │   ├── index.html
│   │   ├── css/styles.css
│   │   └── js/app.js
│   ├── commands/           # Python command classes
│   │   ├── BaseCommand.py  # Abstract base class
│   │   └── ...
│   └── scripts/            # DAZ Studio scripts
│       ├── DazCopilotUtils.dsa      # Utility facade (includes all below)
│       ├── DazCoreUtils.dsa
│       ├── DazLoggingUtils.dsa
│       ├── DazFileUtils.dsa
│       ├── DazStringUtils.dsa
│       ├── DazNodeUtils.dsa
│       ├── DazTransformUtils.dsa
│       ├── DazCameraUtils.dsa
│       ├── DazRenderUtils.dsa
│       ├── GetSceneHierarchySU.dsa  # Scene cache query script
│       └── ...                      # One .dsa per command
└── tests/
    ├── conftest.py         # Shared fixtures
    ├── commands/           # Command tests
    ├── unit/               # Unit tests
    └── integration/        # Integration tests
```

### Dependencies

- `PyYAML>=6.0`: YAML configuration parsing
- `fastapi>=0.85.0`: REST API server framework
- `uvicorn[standard]>=0.18.3`: ASGI server for FastAPI
- `prompt-toolkit>=3.0.0`: Interactive shell features
- `python-dotenv`: Environment variable management

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/commands/      # Command tests
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests

# Run with coverage
pytest tests/ --cov=vangard --cov=core --cov-report=html

# Run a single test
pytest tests/unit/test_framework.py::test_load_config -v
```

**Test Markers**:
- `unit` — Fast tests with no external dependencies
- `integration` — Integration tests (no DAZ Studio required)
- `command` — Individual command tests
- `e2e` — End-to-end tests (require DAZ Studio, excluded by default)
- `manual` — Manual tests (excluded by default)

### Code Conventions

- **Command Class Naming**: `CommandNameSU` (suffix "SU" = Script Utility)
- **Script File Naming**: Must match class name: `CommandNameSU.dsa`
- **CLI Command Names**: Use kebab-case (e.g., `load-scene`, `batch-render`)
- **Argument Naming**: Use underscores in Python/config (e.g., `scene_file`)

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

Copyright (C) 2025 Blue Moon Foundry Software

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for the full license text.

---

**Maintained by**: Blue Moon Foundry Software
**Repository**: https://github.com/bluemoonfoundry/vangard-script-utils
