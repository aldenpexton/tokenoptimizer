# TokenOptimizer Workspace Setup

This document provides guidance on setting up your development environment for the TokenOptimizer project.

## VS Code Setup

If you're using VS Code (recommended), follow these steps to ensure a smooth development experience:

1. Install the recommended extensions:
   - MS Python Extension
   - Pylance (for type checking)
   - Black Formatter (for code formatting)

2. Use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"  # Install the package in development mode with dev dependencies
   ```

3. Configure Python Interpreter:
   - Press `Cmd+Shift+P` (or `Ctrl+Shift+P` on Windows)
   - Select "Python: Select Interpreter" 
   - Choose the interpreter from your virtual environment

## Type Checking

We use Pylance for type checking. If you encounter many errors, they might be related to type checking configuration.

If you encounter excessive type checking errors, you can:

1. Check if your workspace is properly set up with the right Python interpreter
2. Try reloading VS Code window
3. Make sure the project dependencies are installed correctly

### Dealing with Type Checking Errors

The project has type checking disabled by default in `pyrightconfig.json` to prevent overwhelming users with errors. This is because:

1. Some external libraries don't have proper type stubs 
2. Dynamic Python code often causes false positives in type checkers
3. The project prioritizes runtime correctness over static type checking

If you want to enable stricter type checking:

1. Open `.vscode/settings.json` and change `"python.analysis.typeCheckingMode": "off"` to `"basic"` or `"strict"`
2. Open `pyrightconfig.json` and make the same change
3. Restart VS Code

Remember that type checking errors don't affect runtime behavior - they're just warnings from the IDE.

## Running Tests

To run the tests:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest sdk/tests/test_adapters.py

# Run specific test class
python -m pytest sdk/tests/test_adapters.py::TestGeminiAdapter
```

## Common Issues

1. **Import errors**: Make sure you have installed the package in development mode
2. **Type checking errors**: These are usually due to missing type stubs or configuration issues; they don't affect runtime
3. **Test failures**: If tests are failing, check that you have the correct dependencies installed 