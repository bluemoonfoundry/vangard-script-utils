# Quick Test Guide

## 🚀 Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=core --cov=vangard --cov-report=html
open htmlcov/index.html  # View coverage report
```

## 📊 What We Have

```
✅ 100 Tests Created
✅ 9 Commands Fully Tested
✅ 0 DAZ Studio Dependencies
✅ < 5 Second Execution Time
✅ CI/CD Ready (GitHub Actions)
```

## 🎯 Test Organization

```
tests/
├── 📝 conftest.py              # Shared test fixtures
├── ⚙️  pytest.ini               # Configuration
│
├── 🔧 unit/                    # 39 tests - Core functionality
│   ├── test_framework.py       # Framework tests (24 tests)
│   └── test_base_command.py    # BaseCommand tests (15 tests)
│
├── 🔗 integration/             # 8 tests - Component integration
│   └── test_config_consistency.py
│
└── 🎮 commands/                # 53 tests - Command validation
    ├── test_load_merge_su.py
    ├── test_create_basic_camera_su.py
    ├── test_create_group_node_su.py
    ├── test_drop_object_su.py
    ├── test_copy_transform_object_su.py
    ├── test_apply_generic_pose_su.py
    ├── test_scene_roller_su.py
    ├── test_copy_current_scene_file_su.py
    └── test_single_scene_renderer_su.py
```

## 🏃 Common Commands

### Run Tests by Category
```bash
# Fast unit tests only (< 1 second)
pytest tests/unit -v

# Config validation tests
pytest tests/integration -v

# Specific command tests
pytest tests/commands -v
pytest tests/commands/test_load_merge_su.py -v
```

### Run Specific Tests
```bash
# Run single test function
pytest tests/unit/test_framework.py::TestLoadConfig::test_load_valid_config -v

# Run all tests in a class
pytest tests/unit/test_framework.py::TestLoadConfig -v

# Run tests matching pattern
pytest -k "load_scene" -v
pytest -k "camera" -v
```

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=core --cov=vangard --cov-report=html

# Generate terminal coverage report
pytest --cov=core --cov=vangard --cov-report=term

# Show missing lines
pytest --cov=core --cov=vangard --cov-report=term-missing
```

### Test Output Options
```bash
# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l

# More verbose output
pytest -vv

# Quiet output (only show summary)
pytest -q

# Show print statements
pytest -s
```

## 🎨 Test Patterns

### Basic Command Test
```python
@mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
def test_basic_command(mock_exec):
    args = Namespace(required_arg='value')
    cmd = MyCommandSU(parser=None, config={})
    cmd.process(args)

    # Verify execution
    mock_exec.assert_called_once()
    script_name, script_vars, _ = mock_exec.call_args[0]

    # Verify correctness
    assert script_name == "MyCommandSU.dsa"
    assert script_vars['required_arg'] == 'value'
```

### Using Fixtures
```python
def test_with_fixtures(sample_config, mock_daz_execution, temp_env):
    # sample_config: Loaded config.yaml
    # mock_daz_execution: Mocked exec_remote_script
    # temp_env: Test environment variables

    # Your test code here
    assert mock_daz_execution.called
```

### Testing Multiple Scenarios
```python
@pytest.mark.parametrize("input,expected", [
    ('/unix/path.duf', '/unix/path.duf'),
    ('C:/windows/path.duf', 'C:/windows/path.duf'),
    ('/path with spaces.duf', '/path with spaces.duf'),
])
def test_various_paths(input, expected, mock_daz_execution):
    args = Namespace(scene_file=input)
    cmd = LoadMergeSU(parser=None, config={})
    cmd.process(args)

    _, script_vars, _ = mock_daz_execution.call_args[0]
    assert script_vars['scene_file'] == expected
```

## 📋 Test Checklist for New Commands

When adding tests for a new command:

- [ ] Create `tests/commands/test_<command_name>_su.py`
- [ ] Test basic functionality (required args only)
- [ ] Test each optional argument
- [ ] Test paths with spaces
- [ ] Test Windows-style paths
- [ ] Test special characters in inputs
- [ ] Test edge cases (empty, zero, null values)
- [ ] Test multiple argument combinations
- [ ] Verify script name is correct
- [ ] Verify all arguments passed correctly
- [ ] Verify framework fields excluded (command, class_to_run)

## 🔍 Debugging Tests

### See what's being called
```python
@mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
def test_debug(mock_exec):
    # ... test code ...

    # Print call count
    print(f"Called {mock_exec.call_count} times")

    # Print call arguments
    print(f"Call args: {mock_exec.call_args}")

    # Print all calls
    for call in mock_exec.call_args_list:
        print(f"Call: {call}")
```

### Run test with print output
```bash
pytest tests/commands/test_load_merge_su.py::test_basic_load -s -v
```

## 🚦 CI/CD Integration

### GitHub Actions
Tests automatically run on:
- Push to main or develop branches
- Pull requests to main or develop
- Multiple Python versions (3.8-3.12)
- Multiple OS (Ubuntu, Windows, macOS)

### View Results
- Check GitHub Actions tab in repository
- Coverage report uploaded to Codecov (if configured)

## 📈 Coverage Goals

Current coverage targets:

| Component | Target | Priority |
|-----------|--------|----------|
| core/framework.py | 95%+ | High |
| BaseCommand.py | 90%+ | High |
| Command classes | 80%+ | Medium |
| Interface layers | 85%+ | Medium |
| **Overall** | **85%+** | High |

## 🎓 Key Concepts

### Why Mock?
- **Speed**: Tests run in milliseconds, not minutes
- **Isolation**: Test Python code without DAZ Studio
- **CI/CD**: Run tests in GitHub Actions
- **Reliability**: No external dependencies

### What We Mock
- `BaseCommand.exec_remote_script()` - Prevents DAZ Studio execution
- `subprocess.Popen` - Prevents subprocess creation
- Environment variables - Provides test configuration

### What We Verify
✅ Correct script name constructed
✅ Arguments parsed correctly
✅ JSON serialization correct
✅ Command line format valid
✅ Framework fields excluded

## 🔧 Troubleshooting

### Tests fail with "No module named pytest"
```bash
pip install pytest pytest-cov pytest-mock
```

### Tests fail with "No module named vangard"
```bash
# Ensure you're in the project root directory
cd /path/to/vangard-script-utils
python -m pytest
```

### Mock not working
```python
# Use full path to the function being mocked
@mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')

# Not just:
@mock.patch('exec_remote_script')  # ❌ Won't work
```

### ImportError when running tests
```bash
# Make sure __init__.py files exist
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/commands/__init__.py
```

## 📚 Documentation

- **TESTING_STRATEGY.md** - Comprehensive testing approach
- **TEST_SUMMARY.md** - Detailed test coverage report
- **tests/README.md** - Test directory overview
- **This file** - Quick reference guide

## 🎯 Next Steps

1. **Run the tests**: `pytest -v`
2. **Check coverage**: `pytest --cov=core --cov=vangard --cov-report=html`
3. **Add more tests**: Use template for remaining 15 commands
4. **Enable CI/CD**: Push to GitHub to trigger Actions
5. **Monitor coverage**: Aim for 85%+ overall coverage

---

**Quick Command Reference:**
```bash
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest -x                   # Stop at first failure
pytest -k "pattern"         # Run tests matching pattern
pytest --cov                # With coverage
pytest tests/unit           # Just unit tests
pytest tests/commands       # Just command tests
```
