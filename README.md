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
- **DAZ Studio Integration**: Seamless execution of DAZ Studio scripts from Python
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
┌─────────────────────────────────────────────────────────────┐
│              Subprocess: DAZ Studio Launch                   │
│  DAZ Studio + scriptArg (JSON args) + .dsa script path      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         vangard/scripts/ (DAZ Studio Script Files)           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ LoadMergeSU.dsa                                     │   │
│  │ BatchRenderSU.dsa                                   │   │
│  │ CreateGroupNodeSU.dsa                               │   │
│  │ ... (corresponds to Python command classes)         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **config.yaml**: Central configuration defining all commands, arguments, and class mappings
2. **core/framework.py**: Core engine that loads config, builds parsers, and executes commands
3. **vangard/commands/**: Python command classes that process arguments and launch DAZ scripts
4. **vangard/scripts/**: DAZ Studio script files (.dsa) that perform actual operations in DAZ
5. **Interface Layers**: CLI, Interactive Shell, FastAPI Server, GUI, and Pro web interface

### Command Execution Flow

1. User invokes command through any interface mode
2. Interface layer parses input and passes to core framework
3. Framework loads corresponding command class from config.yaml
4. Command class processes arguments and converts to JSON
5. Command spawns DAZ Studio subprocess with script path and JSON args
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

   **DAZ Script Server mode** (requires the [DAZ Script Server plugin](https://github.com/bluemoonfoundry/vangard-daz-script-server):
   - `DAZ_SCRIPT_SERVER_ENABLED`: Set to `true`, `1`, or `yes` to use the REST API instead of spawning a subprocess. Default: `false`
   - `DAZ_SCRIPT_SERVER_HOST`: Hostname or IP of the DAZ Script Server. Default: `127.0.0.1`
   - `DAZ_SCRIPT_SERVER_PORT`: Port of the DAZ Script Server. Default: `18811`

   When server mode is enabled, commands are sent as a `POST` request to `http://<host>:<port>/execute` with the body:
   ```json
   {
     "scriptFile": "/absolute/path/to/Script.dsa",
     "args": { "arg_name": "value" }
   }
   ```
   `args` is passed as a JSON object (not a string). If no arguments are provided, `args` is an empty object `{}`.

### Alternative: Manual Installation

If you prefer not to install the package:

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

## Usage

After installation, you can use the package in two ways:

### Option 1: Console Scripts (Recommended)

Use the installed console scripts directly:

```bash
vangard-cli [command] [arguments]
# or
vangard cli [command] [arguments]
```

### Option 2: Python Module

Run as a Python module:

```bash
python -m vangard.cli [command] [arguments]
# or
python -m vangard.main cli [command] [arguments]
```

---

### CLI Mode

Execute single commands from the command line:

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

# Or using the multi-mode launcher
vangard cli load-scene /path/to/scene.duf
```

### Interactive Mode

Launch an interactive shell with command history and auto-completion:

```bash
vangard-interactive
# or
vangard interactive
# or
python -m vangard.interactive
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
- Help available for all commands

### Server Mode

Run as a FastAPI REST API server:

```bash
vangard-server
# or
vangard server
# or
python -m vangard.server
```

The server starts at `http://127.0.0.1:8000` with:
- **Interactive API documentation**: http://127.0.0.1:8000/docs
- **OpenAPI schema**: http://127.0.0.1:8000/openapi.json

**API Endpoints**:
- `GET /`: Health check
- `POST /api/{command-name}`: Execute command (one endpoint per command)

**Example API Request**:

```bash
curl -X POST "http://127.0.0.1:8000/api/load-scene" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_file": "/path/to/scene.duf",
    "merge": false
  }'
```

All commands are automatically exposed as REST endpoints based on `config.yaml`.

### GUI Mode

Launch a simple graphical interface:

```bash
vangard-gui
# or
vangard gui
# or
python -m vangard.gui
```

The GUI provides a user-friendly interface for executing commands without using the command line.

### Pro Mode

Launch the professional web interface — a modern, dark-themed browser UI with dynamic forms, real-time feedback, and command discovery:

```bash
vangard-pro
# or
vangard pro
# or
python -m vangard.pro
```

The server starts at **http://127.0.0.1:8000**. Open that URL in any modern browser to access the Pro interface.

**Pro Mode Features**:
- **Visual Command Browser**: Searchable sidebar listing all available commands with icons and descriptions
- **Dynamic Forms**: Forms are auto-generated from `config.yaml` — required fields, type-aware inputs, and help tooltips
- **Real-time Output**: Color-coded results (green = success, red = error) with timestamps
- **Dark Theme**: Professional dark UI with glassmorphism effects, optimized for 3D work environments
- **Theme Toggle**: Switch between dark and light themes
- **API Access**: Swagger UI still available at `/docs`

See [PRO_MODE.md](PRO_MODE.md) for full documentation on Pro mode customization and usage.

**Mode Comparison**:

| Feature | CLI | Interactive | GUI | Server | Pro |
|---------|-----|-------------|-----|--------|-----|
| Visual Interface | ❌ | ❌ | ✅ | ❌ | ✅ |
| No Command Syntax Required | ❌ | ❌ | ✅ | ✅ | ✅ |
| Form-based Input | ❌ | ❌ | ✅ | ✅ | ✅ |
| Modern Design | ❌ | ❌ | ❌ | N/A | ✅ |
| Real-time Feedback | ✅ | ✅ | ✅ | ✅ | ✅ |
| Command Discovery | ❌ | ⚠️ | ⚠️ | ✅ | ✅ |
| API Access | ❌ | ❌ | ❌ | ✅ | ✅ |
| Web-based | ❌ | ❌ | ❌ | ✅ | ✅ |

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

Follow these steps to add a new command to the toolkit:

### 1. Define Command in config.yaml

Add your command definition to `config.yaml`:

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
      - names: ["-o", "--optional-arg"]
        dest: "optional_arg"
        type: "int"
        default: 0
        help: "Description of optional argument"
```

**Argument Types**:
- `str`: String values
- `int`: Integer values
- `float`: Float values
- `action: "store_true"`: Boolean flags

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
/*
 * Copyright (C) 2025 Blue Moon Foundry Software
 * Licensed under GNU Affero General Public License v3
 */

includeDir_oFILE = DzFile( getScriptFileName());
util_path = includeDir_oFILE.path() + "/DazCopilotUtils.dsa";
include (util_path);

function MyNewCommandSU() {
    sFunctionName = 'MyNewCommandSU';

    // Initialize and parse incoming JSON arguments
    oScriptVars = init_script_utils(sFunctionName);

    // Access arguments by name
    var sRequiredArg = getScriptArgValue('required_arg', null);
    var nOptionalArg = getScriptArgValue('optional_arg', 0);

    // Implement your DAZ Studio logic here

    log_success_event('Command executed successfully');
    close_script_utils();
}

MyNewCommandSU();
```

### 4. Update Documentation

Regenerate the command reference:

```bash
python generate_docs.py
```

### 5. Add Tests

Create `tests/commands/test_my_new_command_su.py` following the pattern of existing test files. Then run:

```bash
pytest tests/commands/test_my_new_command_su.py -v
pytest tests/integration/  # Verify config consistency
```

## Development

### Project Structure

```
vangard-script-utils/
├── setup.py                # Package setup configuration
├── pyproject.toml          # Modern packaging configuration
├── MANIFEST.in             # Distribution manifest
├── config.yaml             # Command definitions
├── config_reference.md     # Auto-generated command reference
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
├── generate_docs.py        # Regenerates config_reference.md
├── core/
│   ├── __init__.py
│   └── framework.py        # Core framework engine
├── vangard/                # Main package
│   ├── __init__.py         # Package version and exports
│   ├── main.py             # Multi-mode entry point
│   ├── cli.py              # CLI interface
│   ├── interactive.py      # Interactive shell
│   ├── server.py           # FastAPI server
│   ├── gui.py              # GUI interface
│   ├── pro.py              # Pro web interface (FastAPI + static files)
│   ├── static/             # Pro mode frontend assets
│   │   ├── index.html
│   │   ├── css/styles.css
│   │   └── js/app.js
│   ├── commands/           # Python command classes
│   │   ├── BaseCommand.py  # Abstract base class
│   │   ├── LoadMergeSU.py
│   │   ├── BatchRenderSU.py
│   │   ├── SaveViewportSU.py
│   │   ├── FaceRenderLoraSU.py
│   │   └── ...
│   └── scripts/            # DAZ Studio scripts
│       ├── DazCopilotUtils.dsa  # Utility functions
│       ├── LoadMergeSU.dsa
│       ├── BatchRenderSU.dsa
│       ├── SaveViewportSU.dsa
│       ├── FaceRenderLoraSU.dsa
│       └── ...
├── tests/                  # Test suite (179 tests)
│   ├── conftest.py         # Test fixtures
│   ├── commands/           # Command tests (137 tests)
│   ├── unit/               # Unit tests (39 tests)
│   └── integration/        # Integration tests (8 tests)
└── .github/
    └── workflows/
        └── tests.yml       # CI/CD workflow
```

### Dependencies

- `PyYAML>=6.0`: YAML configuration parsing
- `fastapi>=0.85.0`: REST API server framework
- `uvicorn[standard]>=0.18.3`: ASGI server for FastAPI
- `prompt-toolkit>=3.0.0`: Interactive shell features
- `python-dotenv`: Environment variable management

### Running Tests

The project includes a comprehensive test suite with 179 tests:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test categories
pytest tests/commands/      # Command tests
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests

# Run with coverage
pytest tests/ --cov=vangard --cov=core --cov-report=html
```

**Test Markers**:
- `unit` - Fast tests with no external dependencies
- `integration` - Integration tests (no DAZ Studio required)
- `command` - Individual command tests
- `e2e` - End-to-end tests (require DAZ Studio, excluded by default)
- `manual` - Manual tests (excluded by default)

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
