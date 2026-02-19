# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based command-line utility system that provides standardized scripts for DAZ Studio (3D rendering software). It acts as a bridge between Python CLI interfaces and DAZ Studio's scripting language (DSA - DAZ Script).

## Common Development Commands

### Package Installation
```bash
# Install in editable/development mode (recommended)
pip install -e .

# Install with dev dependencies (includes pytest, coverage, etc.)
pip install -e ".[dev]"
```

This creates console scripts: `vangard`, `vangard-cli`, `vangard-interactive`, `vangard-server`, `vangard-gui`

### Running Tests
```bash
# Run all tests (excludes e2e and manual by default)
pytest tests/

# Run specific test categories using markers
pytest tests/ -m unit           # Fast unit tests only
pytest tests/ -m integration    # Integration tests
pytest tests/ -m command        # Individual command tests
pytest tests/ -m "not slow"     # Exclude slow tests

# Run tests in a specific directory
pytest tests/commands/          # All command tests (122 tests)
pytest tests/unit/              # Unit tests (39 tests)
pytest tests/integration/       # Integration tests (8 tests)

# Run a single test file
pytest tests/unit/test_framework.py

# Run a specific test function
pytest tests/unit/test_framework.py::test_load_config

# Run with verbose output and coverage
pytest tests/ -v --cov=vangard --cov=core --cov-report=html
```

**Test Markers**: The project uses pytest markers for test organization:
- `unit`: Fast tests with no external dependencies
- `integration`: Integration tests (no DAZ required)
- `command`: Individual command tests
- `contract`: Contract/interface tests
- `e2e`: End-to-end tests (require DAZ Studio - not run by default)
- `manual`: Manual tests (documentation only - not run by default)
- `slow`: Time-consuming tests

### Generating Documentation
```bash
# Regenerate config_reference.md from config.yaml
python generate_docs.py
```

Note: The script generates `config_reference.md`, not `ARGS.md`. Both files may exist but `config_reference.md` is the auto-generated one.

## Architecture

### Core Components

1. **Configuration-Driven System** (`config.yaml`)
   - Central YAML file defines all available commands, their arguments, and which Python classes handle them
   - Commands are dynamically loaded and parsed at runtime
   - Each command specifies: name, Python class path, help text, and argument definitions

2. **Core Framework** (`core/framework.py`)
   - `load_config()`: Loads config.yaml
   - `build_parser()`: Dynamically builds argparse parser from config
   - `load_class()`: Dynamically imports command classes using string paths
   - `run_command()`: Instantiates command class and executes it

3. **Command System**
   - **Python Commands** (`vangard/commands/`): Python classes that inherit from `BaseCommand`
   - **DSA Scripts** (`vangard/scripts/`): Corresponding DAZ Studio scripts (`.dsa` files)
   - Flow: User invokes Python command → Command class processes args → Launches DAZ Studio with .dsa script

4. **Multiple Interface Modes** (selected via `main.py`)
   - **CLI** (`cli.py`): Standard command-line execution
   - **Interactive** (`interactive.py`): Shell with prompt-toolkit, command completion, and history
   - **Server** (`server.py`): FastAPI web server with dynamically generated REST endpoints
   - **GUI** (`gui.py`): Simple graphical interface

### Command Execution Flow

1. User runs command via any interface: `vangard-cli [command] [args]` or `python -m vangard.cli [command] [args]`
2. Interface layer (`cli.py`, `interactive.py`, `server.py`, or `gui.py`) loads config and builds parser
3. Parser identifies command and its associated Python class from `config.yaml`
4. Command class instantiated, `process()` method called
5. `BaseCommand.exec_remote_script()` spawns DAZ Studio subprocess
6. Python args converted to JSON, passed to .dsa script via `-scriptArg`
7. DAZ Studio executes the .dsa script with provided arguments

### Test Organization

```
tests/
├── commands/         # 122 tests - One test file per command class
├── unit/            # 39 tests - Core framework and utility tests
├── integration/     # 8 tests - Cross-component integration tests
├── contract/        # Contract/interface tests
├── e2e/            # End-to-end tests (require DAZ Studio)
├── manual/         # Manual test documentation
├── fixtures/       # Shared test fixtures
└── conftest.py     # Pytest configuration and shared fixtures
```

The test suite totals 164 automated tests. E2E and manual tests are excluded from default runs.

### Key Base Classes

**BaseCommand** (`vangard/commands/BaseCommand.py`)
- All command classes inherit from this abstract base class
- `__init__(parser, config)`: Initializes with optional parser and config references
- `process(args)`: Main execution method that subclasses can override for custom behavior. Default implementation calls `exec_default_script()`
- `exec_default_script(args)`: Executes .dsa script with the same name as the command class
- `exec_remote_script(script_name, script_vars, daz_command_line)`: Static method that spawns DAZ Studio subprocess with specified script and JSON arguments
- `to_dict(args, exclude)`: Static method that converts argparse.Namespace to dict, automatically excluding framework keys ('command', 'class_to_run')

**Important**: When creating a new command, you typically only need to create the class and the .dsa script. The default `process()` implementation handles everything unless you need custom Python-side logic.

## Environment Setup

Required environment variables (typically in `.env` file):
- `DAZ_ROOT`: Absolute path to DAZ Studio executable
- `DAZ_ARGS`: Optional additional arguments for DAZ Studio

## Running the Application

After installing with `pip install -e .`, use the console scripts:

```bash
# CLI mode (two equivalent ways)
vangard-cli [command] [args]
vangard cli [command] [args]

# Interactive shell
vangard-interactive
vangard interactive

# FastAPI server (runs on http://127.0.0.1:8000)
vangard-server
vangard server

# GUI mode
vangard-gui
vangard gui
```

Alternative (without installation):
```bash
python -m vangard.cli [command] [args]
python -m vangard.interactive
python -m vangard.server
python -m vangard.gui
# or
python -m vangard.main cli [command] [args]
```

## Development Workflow

### Adding a New Command

1. Add command definition to `config.yaml`:
   ```yaml
   - name: "my-command"
     class: "vangard.commands.MyCommandSU.MyCommandSU"
     help: "Description of what the command does"
     arguments:
       - names: ["required_arg"]
         dest: "required_arg"
         type: "str"
         required: true
         help: "Description of argument"
   ```

2. Create Python command class in `vangard/commands/MyCommandSU.py`:
   ```python
   from vangard.commands.BaseCommand import BaseCommand

   class MyCommandSU(BaseCommand):
       # Default behavior: calls MyCommandSU.dsa script
       # Override process() if custom behavior needed
       pass
   ```

3. Create corresponding DAZ Studio script in `vangard/scripts/MyCommandSU.dsa`
   - Include `DazCopilotUtils.dsa` at the top of your script for utility functions
   - Use `init_script_utils(sFunctionName)` to parse incoming JSON args
   - Access args via `oScriptVars['arg_name']`
   - Use `log_success_event()` and `log_failure_event()` for consistent logging
   - Call `close_script_utils()` at the end to clean up

4. Regenerate documentation:
   ```bash
   python generate_docs.py
   ```
   This updates `config_reference.md` with the new command information.

## Command Name Conventions

- Python command classes: `CommandNameSU` (suffix "SU" for Script Utility)
- DSA script files: `CommandNameSU.dsa` (matches class name)
- CLI command names: Use kebab-case (e.g., `load-scene`, `batch-render`)

## Testing Notes

Test assets located in `test/` directory include:
- `CubeTestScene.duf`: Test scene file
- `CubeTestScene_Camera*.png`: Expected render outputs

See the "Common Development Commands" section above for test execution commands.
