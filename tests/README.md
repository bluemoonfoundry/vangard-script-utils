# Tests

This directory contains the test suite for vangard-script-utils.

## Test Structure

```
tests/
├── conftest.py                      # Shared pytest fixtures
├── unit/                            # Unit tests (fast, isolated)
│   ├── test_framework.py            # Core framework tests
│   └── test_base_command.py         # BaseCommand tests
├── integration/                     # Integration tests
│   └── test_config_consistency.py   # Config validation tests
├── commands/                        # Individual command tests
│   └── test_load_merge_su.py        # LoadMergeSU command tests
├── contract/                        # Contract/interface tests
├── e2e/                             # End-to-end tests (require DAZ)
├── manual/                          # Manual test procedures
└── fixtures/                        # Test data and fixtures
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests (Excluding E2E)

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only (fastest)
pytest tests/unit

# Integration tests
pytest tests/integration

# Command tests
pytest tests/commands

# Run with coverage report
pytest --cov=core --cov=vangard --cov-report=html

# Run specific test file
pytest tests/unit/test_framework.py

# Run specific test
pytest tests/unit/test_framework.py::TestLoadConfig::test_load_valid_config

# Run with verbose output
pytest -v

# Stop at first failure
pytest -x
```

### Run E2E Tests (Requires DAZ Studio)

```bash
pytest -m e2e
```

## Test Markers

Tests are marked with pytest markers to categorize them:

- `@pytest.mark.unit`: Fast unit tests, no external dependencies
- `@pytest.mark.integration`: Integration tests between components
- `@pytest.mark.contract`: Contract/interface validation tests
- `@pytest.mark.command`: Individual command tests
- `@pytest.mark.e2e`: End-to-end tests requiring DAZ Studio
- `@pytest.mark.slow`: Tests that take significant time

## Writing Tests

### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_something(sample_config, mock_daz_execution):
    """Test with config and mocked DAZ execution"""
    # sample_config provides the loaded config.yaml
    # mock_daz_execution prevents actual DAZ Studio execution

    # Your test code here
    assert mock_daz_execution.called
```

### Testing Commands

Template for testing a command:

```python
from unittest import mock
from argparse import Namespace
from vangard.commands.YourCommand import YourCommand

@mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
def test_your_command(mock_exec):
    """Test your command"""
    args = Namespace(
        your_arg='value',
        optional_arg=None
    )

    cmd = YourCommand(parser=None, config={})
    cmd.process(args)

    # Verify script was called correctly
    mock_exec.assert_called_once()
    script_name, script_vars, _ = mock_exec.call_args[0]

    assert script_name == "YourCommand.dsa"
    assert script_vars['your_arg'] == 'value'
```

## Coverage Goals

- **core/framework.py**: 95%+
- **vangard/commands/BaseCommand.py**: 90%+
- **Individual commands**: 80%+
- **Overall project**: 85%+

## Continuous Integration

Tests run automatically on GitHub Actions for:
- All pushes to main and develop branches
- All pull requests
- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Multiple operating systems (Ubuntu, Windows, macOS)

See `.github/workflows/tests.yml` for CI configuration.

## Key Testing Principles

1. **Mock DAZ Studio**: Never execute DAZ Studio in tests (except E2E)
2. **Test Contracts**: Verify command construction, not DAZ execution
3. **Fast Tests**: Unit tests should complete in seconds
4. **Isolated Tests**: Each test is independent
5. **Clear Names**: Test names describe what and why

## More Information

See [TESTING_STRATEGY.md](../TESTING_STRATEGY.md) for comprehensive testing documentation.
