# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based command-line utility system that provides standardized scripts for DAZ Studio (3D rendering software). It acts as a bridge between Python CLI interfaces and DAZ Studio's scripting language (DSA - DAZ Script).

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

1. User runs: `python main.py cli [command] [args]`
2. `cli.py` loads config and builds parser
3. Parser identifies command and its associated Python class
4. Command class instantiated, `process()` method called
5. `BaseCommand.exec_remote_script()` spawns DAZ Studio subprocess
6. Python args converted to JSON, passed to .dsa script via `-scriptArg`
7. DAZ Studio executes the .dsa script with provided arguments

### Key Base Classes

**BaseCommand** (`vangard/commands/BaseCommand.py`)
- All command classes inherit from this
- `process(args)`: Main execution method (can be overridden)
- `exec_default_script(args)`: Executes corresponding .dsa script with same name as class
- `exec_remote_script(script_name, script_vars, daz_command_line)`: Spawns DAZ Studio with script
- `to_dict(args, exclude)`: Converts argparse.Namespace to dict, excluding framework keys

## Environment Setup

Required environment variables (typically in `.env` file):
- `DAZ_ROOT`: Absolute path to DAZ Studio executable
- `DAZ_ARGS`: Optional additional arguments for DAZ Studio

## Running the Application

```bash
# CLI mode
python main.py cli [command] [args]

# Interactive shell
python main.py interactive

# FastAPI server (runs on http://127.0.0.1:8000)
python main.py server

# GUI mode
python main.py gui
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
   - Use `init_script_utils()` to parse incoming JSON args
   - Access args via `oScriptVars['arg_name']`

4. Regenerate documentation:
   ```bash
   python generate_docs.py
   ```

### Documentation Generation

Run `python generate_docs.py` to regenerate `ARGS.md` (or `config_reference.md`) from `config.yaml`. This creates a formatted markdown table with all commands and their arguments.

## Command Name Conventions

- Python command classes: `CommandNameSU` (suffix "SU" for Script Utility)
- DSA script files: `CommandNameSU.dsa` (matches class name)
- CLI command names: Use kebab-case (e.g., `load-scene`, `batch-render`)

## Testing

Test files located in `test/` directory. Test assets include:
- `CubeTestScene.duf`: Test scene file
- `CubeTestScene_Camera*.png`: Expected render outputs
