# Vangard Script Utils

A powerful, configuration-driven command-line utility system that provides standardized automation scripts for DAZ Studio. This toolkit acts as a bridge between Python and DAZ Studio's scripting language (DSA), offering multiple interaction modes including CLI, interactive shell, REST API server, and GUI.

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
- [Available Commands](#available-commands)
- [Adding New Commands](#adding-new-commands)
- [Development](#development)
- [License](#license)

## Features

- **Configuration-Driven**: All commands defined in a central YAML configuration file
- **Multiple Interface Modes**: CLI, interactive shell, REST API, and GUI
- **Dynamic Command Loading**: Commands are loaded and parsed at runtime
- **Extensible Architecture**: Easy to add new commands without modifying core code
- **Type-Safe Arguments**: Automatic argument validation and type conversion
- **Auto-Generated Documentation**: Command reference documentation generated from config
- **DAZ Studio Integration**: Seamless execution of DAZ Studio scripts from Python

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│  (CLI Args / Interactive Shell / HTTP Request / GUI)         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              vangard/main.py (Entry Point)                   │
│       Routes to: vangard/cli.py, vangard/interactive.py,     │
│                vangard/server.py, or vangard/gui.py          │
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
│  │   - exec_remote_script(script_name, vars)          │   │
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
5. **Interface Layers**: CLI, Interactive Shell, FastAPI Server, and GUI implementations

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

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```bash
   DAZ_ROOT=/path/to/daz/studio/executable
   DAZ_ARGS=--optional-daz-arguments
   ```

   - `DAZ_ROOT`: Absolute path to your DAZ Studio executable
     - Windows: `C:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe`
     - macOS: `/Applications/DAZ 3D/DAZStudio4 64-bit/DAZStudio.app/Contents/MacOS/DAZStudio`
   - `DAZ_ARGS`: Optional additional arguments to pass to DAZ Studio

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

## Available Commands

For a complete list of available commands and their arguments, see [ARGS.md](ARGS.md).

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
    """
    Command to do something specific.
    """
    # Default implementation calls MyNewCommandSU.dsa script
    # Override process() if you need custom Python logic:

    def process(self, args):
        """
        Custom processing logic (optional).
        """
        args_dict = self.to_dict(args)

        # Do any Python-side processing here
        print(f"Processing command with args: {args_dict}")

        # Execute the DAZ Studio script
        self.exec_default_script(args_dict)

        # Or call a specific script:
        # self.exec_remote_script(
        #     script_name="MyNewCommandSU.dsa",
        #     script_vars=args_dict,
        #     daz_command_line=None
        # )
```

### 3. Create DAZ Studio Script

Create `vangard/scripts/MyNewCommandSU.dsa`:

```javascript
/*
 * Copyright (C) 2025 Blue Moon Foundry Software
 * Licensed under GNU Affero General Public License v3
 */

// Include utility functions
includeDir_oFILE = DzFile( getScriptFileName() );
util_path = includeDir_oFILE.path() + "/DazCopilotUtils.dsa";
include (util_path);

function MyNewCommandSU() {
    sFunctionName = 'MyNewCommandSU';

    // Initialize and parse incoming JSON arguments
    oScriptVars = init_script_utils(sFunctionName);

    // Access arguments by name
    sRequiredArg = oScriptVars['required_arg'];
    nOptionalArg = oScriptVars['optional_arg'];

    print('MyNewCommandSU: required_arg=' + sRequiredArg +
          ', optional_arg=' + nOptionalArg);

    // Implement your DAZ Studio logic here
    // Example: Get current scene, modify objects, render, etc.

    var scene = Scene.getScene();
    if (scene) {
        // Do something with the scene
        log_success_event('Command executed successfully');
    } else {
        log_failure_event('Failed to get scene');
    }

    // Clean up
    close_script_utils();
}

// Execute the function
MyNewCommandSU();
```

### 4. Update Documentation

Regenerate the command reference documentation:

```bash
python generate_docs.py
```

This updates `ARGS.md` with your new command's information.

### 5. Test Your Command

Test your new command in all modes:

```bash
# CLI mode
python main.py cli my-new-command "test value" --optional-arg 42

# Interactive mode
python main.py interactive
> my-new-command "test value" --optional-arg 42

# Server mode (in another terminal)
python main.py server
# Then use curl or visit http://127.0.0.1:8000/docs
```

## Development

### Project Structure

```
vangard-script-utils/
├── setup.py                # Package setup configuration
├── pyproject.toml          # Modern packaging configuration
├── MANIFEST.in             # Distribution manifest
├── config.yaml             # Command definitions
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
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
│   ├── commands/           # Python command classes
│   │   ├── BaseCommand.py  # Abstract base class
│   │   ├── LoadMergeSU.py
│   │   ├── BatchRenderSU.py
│   │   └── ...
│   └── scripts/            # DAZ Studio scripts
│       ├── DazCopilotUtils.dsa  # Utility functions
│       ├── LoadMergeSU.dsa
│       ├── BatchRenderSU.dsa
│       └── ...
├── tests/                  # Test suite (164 tests)
│   ├── conftest.py         # Test fixtures
│   ├── commands/           # Command tests (122 tests)
│   ├── unit/               # Unit tests (39 tests)
│   └── integration/        # Integration tests (8 tests)
├── .github/
│   └── workflows/
│       └── tests.yml       # CI/CD workflow
├── ARGS.md                 # Auto-generated command reference
├── CLAUDE.md               # AI assistant guidance
├── INSTALLATION.md         # Installation guide
├── TESTING_STRATEGY.md     # Testing documentation
└── README.md               # This file
```

### Dependencies

- `PyYAML>=6.0`: YAML configuration parsing
- `fastapi>=0.85.0`: REST API server framework
- `uvicorn[standard]>=0.18.3`: ASGI server for FastAPI
- `prompt-toolkit>=3.0.0`: Interactive shell features
- `python-dotenv`: Environment variable management

### Running Tests

The project includes a comprehensive test suite with 164 tests. Run tests using pytest:

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/commands/      # Command tests
python -m pytest tests/unit/          # Unit tests
python -m pytest tests/integration/   # Integration tests

# Run with coverage
python -m pytest tests/ --cov=vangard --cov=core --cov-report=html
```

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
