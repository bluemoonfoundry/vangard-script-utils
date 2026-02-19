# Testing Strategy for Vangard Script Utils

## Overview

This document outlines a comprehensive testing strategy for the Vangard Script Utils toolkit. The primary challenge is that DAZ Studio cannot be installed or run in CI/CD environments (GitHub Actions), so our testing strategy focuses on:

1. Testing all Python code thoroughly without requiring DAZ Studio
2. Mocking DAZ Studio execution to verify correct command construction
3. Validating the contract between Python and DSA scripts
4. Providing manual test procedures for DAZ Studio integration

## Testing Layers

### Layer 1: Unit Tests (No DAZ Required)

Test individual components in complete isolation.

#### 1.1 Core Framework Tests (`tests/test_framework.py`)

**Test `load_config()`:**
- ✓ Loads valid config.yaml successfully
- ✓ Handles missing config file gracefully
- ✓ Handles malformed YAML with clear error
- ✓ Validates required config structure (app, commands)

**Test `build_parser()`:**
- ✓ Creates ArgumentParser with correct program name and description
- ✓ Registers all commands from config as subparsers
- ✓ Adds all arguments with correct types and flags
- ✓ Sets correct defaults for optional arguments
- ✓ Marks required arguments appropriately
- ✓ Handles boolean flags (store_true) correctly

**Test `load_class()`:**
- ✓ Dynamically imports valid class paths
- ✓ Handles missing modules with clear error
- ✓ Handles missing class names with clear error
- ✓ Handles invalid class paths with clear error

**Test `run_command()`:**
- ✓ Instantiates command class with correct arguments
- ✓ Calls command's process() method
- ✓ Passes parser and config to command constructor
- ✓ Returns command result correctly

#### 1.2 Base Command Tests (`tests/test_base_command.py`)

**Test `BaseCommand.to_dict()`:**
- ✓ Converts Namespace to dict correctly
- ✓ Excludes 'command' and 'class_to_run' by default
- ✓ Excludes additional keys when specified
- ✓ Preserves all argument values correctly
- ✓ Handles None values appropriately

**Test `BaseCommand.exec_remote_script()` (Mocked):**
- ✓ Constructs correct command line string
- ✓ Includes DAZ_ROOT from environment
- ✓ Includes DAZ_ARGS from environment
- ✓ Serializes script_vars to JSON correctly
- ✓ Includes correct script path
- ✓ Uses correct subprocess.Popen arguments
- ✓ Does NOT actually execute subprocess in tests

#### 1.3 Command Class Tests (`tests/test_commands/`)

For each command class (e.g., `test_load_merge_su.py`):

**Test argument processing:**
- ✓ process() receives correct arguments
- ✓ to_dict() produces expected dictionary
- ✓ Required arguments are validated
- ✓ Optional arguments use correct defaults

**Test script invocation (Mocked):**
- ✓ Calls exec_remote_script with correct script name
- ✓ Passes correct script_vars dictionary
- ✓ Constructs expected command line

### Layer 2: Integration Tests (No DAZ Required)

Test components working together, still without DAZ Studio.

#### 2.1 End-to-End CLI Tests (`tests/test_cli_integration.py`)

**Test CLI argument parsing:**
```python
def test_cli_load_scene_basic():
    """Test: python main.py cli load-scene /path/to/scene.duf"""
    with mock.patch('BaseCommand.exec_remote_script') as mock_exec:
        cli.main(['load-scene', '/path/to/scene.duf'])

        # Verify exec_remote_script was called correctly
        mock_exec.assert_called_once()
        script_name, script_vars, cmd_line = mock_exec.call_args[0]

        assert script_name == "LoadMergeSU.dsa"
        assert script_vars['scene_file'] == '/path/to/scene.duf'
        assert script_vars['merge'] == False
```

**Test all commands with various argument combinations:**
- ✓ Required arguments only
- ✓ With optional arguments
- ✓ With flags
- ✓ Error handling for missing required arguments
- ✓ Error handling for invalid argument types

#### 2.2 Interactive Shell Tests (`tests/test_interactive.py`)

**Test interactive mode:**
- ✓ Command parsing from string input
- ✓ Command completion suggestions
- ✓ History functionality
- ✓ Multi-word argument handling with quotes
- ✓ Exit/quit commands

**Mock prompt_toolkit for automated testing:**
```python
def test_interactive_command_execution():
    """Test interactive shell executes commands correctly"""
    with mock.patch('prompt_toolkit.PromptSession') as mock_session:
        mock_session.return_value.prompt.side_effect = [
            'load-scene /path/to/scene.duf',
            'exit'
        ]

        with mock.patch('BaseCommand.exec_remote_script') as mock_exec:
            interactive.main()

            # Verify command was executed
            assert mock_exec.called
```

#### 2.3 Server API Tests (`tests/test_server.py`)

**Test FastAPI server using TestClient:**
```python
from fastapi.testclient import TestClient
from server import app

def test_health_endpoint():
    """Test GET / returns health status"""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_load_scene_endpoint():
    """Test POST /api/load-scene"""
    client = TestClient(app)

    with mock.patch('BaseCommand.exec_remote_script') as mock_exec:
        response = client.post(
            "/api/load-scene",
            json={"scene_file": "/path/to/scene.duf", "merge": False}
        )

        assert response.status_code == 200
        assert mock_exec.called
```

**Test all endpoints:**
- ✓ All commands have corresponding endpoints
- ✓ Request validation (Pydantic models)
- ✓ Response formatting
- ✓ Error handling and HTTP status codes
- ✓ OpenAPI schema generation

#### 2.4 Config-to-Implementation Tests (`tests/test_config_consistency.py`)

**Verify config.yaml consistency:**
- ✓ All commands in config.yaml have corresponding Python classes
- ✓ All Python command classes have corresponding .dsa scripts
- ✓ All class paths in config.yaml are valid and importable
- ✓ No duplicate command names
- ✓ All argument types are valid (str, int, float)

```python
def test_all_commands_have_classes():
    """Verify every command in config has a valid Python class"""
    config = load_config()

    for cmd in config['commands']:
        class_path = cmd['class']
        # Should not raise exception
        CommandClass = load_class(class_path)
        assert CommandClass is not None

def test_all_commands_have_dsa_scripts():
    """Verify every command has a corresponding .dsa script"""
    config = load_config()

    for cmd in config['commands']:
        class_name = cmd['class'].split('.')[-1]
        script_path = f"vangard/scripts/{class_name}.dsa"
        assert os.path.exists(script_path), f"Missing script: {script_path}"
```

### Layer 3: Contract Tests (DAZ Interface Validation)

Verify the contract between Python and DAZ Studio scripts without executing DAZ.

#### 3.1 Command Line Construction Tests (`tests/test_daz_contract.py`)

**Test command line format:**
```python
def test_daz_command_line_format():
    """Verify DAZ Studio command line is constructed correctly"""
    with mock.patch.dict(os.environ, {
        'DAZ_ROOT': '/path/to/daz',
        'DAZ_ARGS': '--headless'
    }):
        with mock.patch('subprocess.Popen') as mock_popen:
            script_vars = {'scene_file': '/test.duf', 'merge': False}

            BaseCommand.exec_remote_script(
                script_name="LoadMergeSU.dsa",
                script_vars=script_vars,
                daz_command_line=None
            )

            # Verify Popen was called with correct command
            call_args = mock_popen.call_args[0][0]

            assert '/path/to/daz' in call_args
            assert '--headless' in call_args
            assert 'LoadMergeSU.dsa' in call_args
            assert '{"scene_file": "/test.duf", "merge": false}' in call_args
```

#### 3.2 JSON Serialization Tests (`tests/test_json_contract.py`)

**Test argument serialization:**
- ✓ Strings are properly quoted and escaped
- ✓ Integers remain as numbers
- ✓ Booleans serialize to true/false (lowercase)
- ✓ None values serialize to null
- ✓ Special characters are escaped correctly
- ✓ Paths with spaces are handled correctly

```python
def test_json_serialization_of_arguments():
    """Verify arguments are serialized correctly for DSA scripts"""
    test_cases = [
        ({'path': '/path with spaces/file.duf'}, '"path": "/path with spaces/file.duf"'),
        ({'count': 42}, '"count": 42'),
        ({'flag': True}, '"flag": true'),
        ({'optional': None}, '"optional": null'),
        ({'special': 'value"with"quotes'}, r'"special": "value\"with\"quotes"'),
    ]

    for args, expected_json_fragment in test_cases:
        json_output = json.dumps(args)
        assert expected_json_fragment in json_output
```

### Layer 4: Mock-Based Command Tests

Test each command's behavior by mocking DAZ execution and verifying invocations.

#### 4.1 Command Test Template (`tests/test_commands/test_<command>.py`)

For each command, create a test file following this template:

```python
import pytest
from unittest import mock
from argparse import Namespace
from vangard.commands.LoadMergeSU import LoadMergeSU

class TestLoadMergeSU:
    """Test suite for LoadMergeSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_basic_load(self, mock_exec):
        """Test loading a scene without merge"""
        args = Namespace(
            scene_file='/path/to/scene.duf',
            merge=False
        )

        cmd = LoadMergeSU(parser=None, config={})
        cmd.process(args)

        # Verify exec_remote_script was called correctly
        mock_exec.assert_called_once()
        script_name, script_vars, cmd_line = mock_exec.call_args[0]

        assert script_name == "LoadMergeSU.dsa"
        assert script_vars['scene_file'] == '/path/to/scene.duf'
        assert script_vars['merge'] == False
        assert 'command' not in script_vars  # Excluded by to_dict
        assert 'class_to_run' not in script_vars  # Excluded by to_dict

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_merge_load(self, mock_exec):
        """Test loading a scene with merge flag"""
        args = Namespace(
            scene_file='/path/to/scene.duf',
            merge=True
        )

        cmd = LoadMergeSU(parser=None, config={})
        cmd.process(args)

        _, script_vars, _ = mock_exec.call_args[0]
        assert script_vars['merge'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_path_with_spaces(self, mock_exec):
        """Test handling of paths with spaces"""
        args = Namespace(
            scene_file='/path with spaces/my scene.duf',
            merge=False
        )

        cmd = LoadMergeSU(parser=None, config={})
        cmd.process(args)

        _, script_vars, _ = mock_exec.call_args[0]
        assert script_vars['scene_file'] == '/path with spaces/my scene.duf'
```

### Layer 5: Functional Tests (With DAZ Studio)

These tests require DAZ Studio to be installed and available.

#### 5.1 Manual Test Procedures (`tests/manual/MANUAL_TESTS.md`)

Document step-by-step manual test procedures:

```markdown
## Manual Test: Load Scene

**Prerequisites:**
- DAZ Studio installed
- .env configured with DAZ_ROOT

**Steps:**
1. Run: `python main.py cli load-scene test/CubeTestScene.duf`
2. Verify: DAZ Studio opens
3. Verify: Scene loads successfully
4. Verify: No errors in console
5. Verify: Scene contains expected objects

**Expected Result:**
- Scene loads without errors
- Console shows "Loaded scene file test/CubeTestScene.duf"
```

#### 5.2 Automated E2E Tests (`tests/e2e/`) - Run Only When DAZ Available

These tests actually execute DAZ Studio and verify results:

```python
import pytest
import os

@pytest.mark.skipif(
    not os.getenv('DAZ_ROOT') or not os.path.exists(os.getenv('DAZ_ROOT', '')),
    reason="DAZ Studio not available"
)
class TestE2EWithDAZ:
    """End-to-end tests that require DAZ Studio"""

    def test_load_scene_produces_no_errors(self):
        """Test that loading a scene completes without errors"""
        result = subprocess.run(
            ['python', 'main.py', 'cli', 'load-scene', 'test/CubeTestScene.duf'],
            capture_output=True,
            text=True,
            timeout=60
        )

        assert result.returncode == 0
        assert 'error' not in result.stderr.lower()
        assert 'Loaded scene file' in result.stdout

    def test_render_produces_output_file(self):
        """Test that rendering creates an image file"""
        output_path = 'test/output/test_render.png'

        # Clean up any existing file
        if os.path.exists(output_path):
            os.remove(output_path)

        result = subprocess.run(
            ['python', 'main.py', 'cli', 'scene-render',
             '-s', 'test/CubeTestScene.duf',
             '-o', output_path],
            timeout=300  # Rendering can take time
        )

        assert result.returncode == 0
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
```

## Test Organization

```
vangard-script-utils/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures and configuration
│   │
│   ├── unit/                          # Layer 1: Unit tests
│   │   ├── test_framework.py
│   │   ├── test_base_command.py
│   │   └── test_utils.py
│   │
│   ├── integration/                   # Layer 2: Integration tests
│   │   ├── test_cli_integration.py
│   │   ├── test_interactive.py
│   │   ├── test_server.py
│   │   └── test_config_consistency.py
│   │
│   ├── contract/                      # Layer 3: Contract tests
│   │   ├── test_daz_contract.py
│   │   └── test_json_contract.py
│   │
│   ├── commands/                      # Layer 4: Command tests
│   │   ├── test_load_merge_su.py
│   │   ├── test_batch_render_su.py
│   │   ├── test_create_group_node_su.py
│   │   └── ...
│   │
│   ├── e2e/                           # Layer 5: E2E tests (require DAZ)
│   │   ├── test_e2e_render.py
│   │   └── test_e2e_scene_operations.py
│   │
│   ├── manual/                        # Manual test procedures
│   │   └── MANUAL_TESTS.md
│   │
│   └── fixtures/                      # Test data
│       ├── sample_config.yaml
│       ├── invalid_config.yaml
│       └── test_scenes/
│
├── pytest.ini                         # Pytest configuration
└── .github/
    └── workflows/
        └── tests.yml                  # GitHub Actions workflow
```

## Pytest Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for different test types
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (still no DAZ required)
    contract: Contract/interface tests
    command: Individual command tests
    e2e: End-to-end tests (require DAZ Studio)
    manual: Manual tests (documentation only)
    slow: Tests that take significant time

# Don't run e2e tests by default
addopts = -v --tb=short -m "not e2e and not manual"
```

## Running Tests

```bash
# Run all tests except E2E and manual
pytest

# Run only unit tests (fastest)
pytest -m unit

# Run integration tests
pytest -m integration

# Run contract tests
pytest -m contract

# Run all command tests
pytest -m command

# Run specific command test
pytest tests/commands/test_load_merge_su.py

# Run E2E tests (requires DAZ)
pytest -m e2e

# Run all tests including E2E
pytest -m ""

# Run with coverage
pytest --cov=core --cov=vangard --cov-report=html

# Run with verbose output
pytest -vv

# Run and stop at first failure
pytest -x
```

## GitHub Actions Workflow (`.github/workflows/tests.yml`)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-mock

      - name: Run unit tests
        run: pytest -m unit --cov=core --cov=vangard

      - name: Run integration tests
        run: pytest -m integration

      - name: Run contract tests
        run: pytest -m contract

      - name: Run command tests
        run: pytest -m command

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
```

## Coverage Goals

Target coverage levels:
- **core/framework.py**: 95%+ (critical infrastructure)
- **vangard/commands/BaseCommand.py**: 90%+ (base functionality)
- **Individual commands**: 80%+ (command-specific logic)
- **Interface layers (cli.py, server.py, etc.)**: 85%+
- **Overall project**: 85%+

## Key Testing Principles

1. **Mock External Dependencies**: Never actually call DAZ Studio in CI/CD
2. **Test Contracts, Not Implementations**: Verify command construction, not DAZ execution
3. **Fast Tests**: Unit and integration tests should run in seconds
4. **Isolated Tests**: Each test is independent and can run in any order
5. **Clear Test Names**: Test names describe what is being tested and expected outcome
6. **Fixtures for Common Setup**: Use pytest fixtures to avoid repetition
7. **Parametrize Where Appropriate**: Test multiple scenarios with parameterization

## Common Fixtures (`tests/conftest.py`)

```python
import pytest
from unittest import mock
from core.framework import load_config

@pytest.fixture
def sample_config():
    """Returns a sample configuration for testing"""
    return load_config('config.yaml')

@pytest.fixture
def mock_daz_execution():
    """Mocks BaseCommand.exec_remote_script to prevent DAZ execution"""
    with mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script') as mock_exec:
        yield mock_exec

@pytest.fixture
def mock_subprocess():
    """Mocks subprocess.Popen to prevent any subprocess execution"""
    with mock.patch('subprocess.Popen') as mock_popen:
        yield mock_popen

@pytest.fixture
def temp_env():
    """Provides temporary environment variables for testing"""
    with mock.patch.dict(os.environ, {
        'DAZ_ROOT': '/mock/daz/studio',
        'DAZ_ARGS': '--headless --test'
    }):
        yield
```

## Next Steps

1. Create `tests/` directory structure
2. Implement `conftest.py` with common fixtures
3. Write core framework unit tests first (highest priority)
4. Write BaseCommand unit tests
5. Create command test template and implement for 2-3 commands
6. Write integration tests for CLI and server
7. Document manual test procedures
8. Set up GitHub Actions workflow
9. Establish coverage reporting
10. Gradually achieve 85%+ coverage

## Benefits of This Strategy

- ✅ Tests run in CI/CD without DAZ Studio
- ✅ Fast test execution (unit + integration in seconds)
- ✅ High confidence in command construction
- ✅ Catches regressions early
- ✅ Documents expected behavior
- ✅ Enables safe refactoring
- ✅ Validates contract between Python and DSA scripts
- ✅ Provides manual test procedures for full E2E validation
