# Installation Guide

## Quick Install

### Development Installation (Editable)

For development, install the package in editable mode so changes are immediately reflected:

```bash
pip install -e .
```

This installs the package and creates console scripts that you can run from anywhere.

### Production Installation

To install the package normally:

```bash
pip install .
```

### Install from Git

Once published to a Git repository:

```bash
pip install git+https://github.com/yourusername/vangard-script-utils.git
```

## Installing Dependencies Only

To install just the runtime dependencies:

```bash
pip install -r requirements.txt
```

To install development dependencies:

```bash
pip install -e ".[dev]"
```

## Console Scripts

After installation, the following console scripts are available:

### `vangard` - Multi-mode launcher

Main entry point with multiple interface modes:

```bash
# Standard CLI mode
vangard cli load-scene /path/to/scene.duf

# Interactive shell mode
vangard interactive

# Web server mode
vangard server

# GUI mode
vangard gui
```

### `vangard-cli` - Direct CLI access

Direct command-line interface (bypasses mode selection):

```bash
vangard-cli load-scene /path/to/scene.duf --merge
vangard-cli scene-render --output-file /renders/output.png
vangard-cli help
vangard-cli help load-scene
```

### `vangard-interactive` - Interactive shell

Launches directly into interactive prompt mode:

```bash
vangard-interactive
```

Then use commands interactively:
```
vangard-cli> load-scene /path/to/scene.duf
vangard-cli> scene-render --output-file output.png
vangard-cli> exit
```

### `vangard-server` - Web API server

Starts the FastAPI web server:

```bash
vangard-server
```

Server runs at `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/`

### `vangard-gui` - GUI interface

Launches the graphical user interface:

```bash
vangard-gui
```

## PATH Configuration

If you see a warning about scripts not being on PATH:

```
WARNING: The scripts vangard, vangard-cli... are installed in '/Users/username/Library/Python/3.12/bin' which is not on PATH.
```

Add the directory to your PATH:

### macOS/Linux (bash/zsh)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/Library/Python/3.12/bin:$PATH"
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Verify Installation

Check that the package is installed:

```bash
pip show vangard-script-utils
```

Test the console scripts:

```bash
vangard-cli --help
vangard --help
```

## Uninstallation

To uninstall the package:

```bash
pip uninstall vangard-script-utils
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're in the correct directory and have activated any virtual environment:

```bash
# Check installation
pip show vangard-script-utils

# Reinstall in editable mode
pip install -e . --force-reinstall
```

### Console Scripts Not Found

If commands aren't found after installation:

1. Check if scripts directory is in PATH (see PATH Configuration above)
2. Use full path to scripts:
   ```bash
   /Users/username/Library/Python/3.12/bin/vangard-cli --help
   ```
3. Or use Python module execution:
   ```bash
   python -m vangard.cli --help
   ```

### Tests Not Running

If tests fail, install development dependencies:

```bash
pip install -e ".[dev]"
python -m pytest tests/
```

## Development Workflow

1. **Clone the repository**
2. **Install in editable mode**: `pip install -e ".[dev]"`
3. **Make changes** to code
4. **Run tests**: `python -m pytest tests/`
5. **Use console scripts** immediately (changes auto-reflected)
6. **Commit and push** changes

## Package Information

Check package version:

```python
import vangard
print(vangard.__version__)  # 0.1.0
```

List installed console scripts:

```bash
pip show -f vangard-script-utils | grep bin/
```
