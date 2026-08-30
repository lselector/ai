# Python Formatting Rules

This document describes the formatting standards
for all Python files in this project.

## Overview

All Python scripts in this project
must follow these consistent formatting rules
to ensure code readability and maintainability.

## Rule 0

Each python script should start with a multiline doc  
concisely explaining the purpose and function
of this script.

It should show example(s) of usage.

Also when it was created and last updated.


## Rule 1: Short Docstrings

All function and class definitions should have short docstrings.
Preferably to keep them to concise one-liners.

**Good:**
```python
def get_api_key():
    """Get API key from environment."""
    # function body
```

**Bad:**
```python
def get_api_key():
    """
    Get API key from environment variable.

    This function retrieves the API key from the environment
    and validates it before returning.

    Returns:
        str: The API key
    """
    # function body
```

## Rule 2: Function Length Limit

The total length of any function must not exceed **35 lines**.

This includes:
- Function definition line
- Docstring
- All code
- All comments
- All empty lines

**How to comply:**
- Split long functions into smaller helper functions
- Extract complex logic into separate functions
- Keep each function focused on a single responsibility

**Example:**
```python
# Good - function is 20 lines total
def process_data(data):
    """Process input data and return results."""
    cleaned = clean_data(data)
    validated = validate_data(cleaned)
    return transform_data(validated)

def clean_data(data):
    """Remove invalid entries from data."""
    return [x for x in data if x is not None]
```

## Rule 3: Separator Lines Before Functions

Every external function definition must be preceded 
by a horizontal separator line 64 characters long.

**Format:**
```python
# --------------------------------------------------------------
```

Every internal function definition 
(function inside a class or inside another function)
must be preceded by a horizontal separator
started indented same way as the function,
and ending after position 44 on the line
(so it is usually 40 characters long).

**Format:**
```python
    # --------------------------------------
```

**Rules for separator lines:**
- Starts with `#` (pound symbol)
- Followed by one space
- Followed by exactly 62 dash characters (`-`) for external functions,
  or followed by 38 characters for internal functions

**Example:**
```python
# --------------------------------------------------------------
def my_external_function():
    """External Function description."""
    pass

    # --------------------------------------
    def my_internal_function():
        """Internal function description."""
        pass
```


## Rule 4: Separator Before Main Guard

The `if __name__ == "__main__":` statement must also be preceded by a separator line.

**Example:**
```python
# --------------------------------------------------------------
def main():
    """Main function."""
    pass

# --------------------------------------------------------------
if __name__ == "__main__":
    main()
```

## Rule 5: Length of lines should not be longer than 65 characters

## Rule 6: when importing common modules, use common standard ways of naming them

### For example:

```python
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import polars as pl
```

## Rule 7: keep the lengths of individual python scripts and modules no longer than 800 lines. If file grows longer, split it.

## Complete Example

Here's a complete example showing all rules applied:

```python
#!/usr/bin/env python3
"""Module description."""

import os
import sys


# --------------------------------------------------------------
def get_config():
    """Load configuration from environment."""
    return {
        "api_key": os.environ.get("API_KEY"),
        "debug": os.environ.get("DEBUG", "false").lower() == "true"
    }


# --------------------------------------------------------------
def validate_config(config):
    """Validate configuration values."""
    if not config.get("api_key"):
        raise ValueError("API_KEY not set")
    return True


# --------------------------------------------------------------
def process_request(data):
    """Process incoming request data."""
    cleaned = clean_data(data)
    return transform_data(cleaned)


# --------------------------------------------------------------
def clean_data(data):
    """Remove invalid entries."""
    return [x for x in data if x is not None]


# --------------------------------------------------------------
def transform_data(data):
    """Transform data to output format."""
    return [{"value": x, "processed": True} for x in data]


# --------------------------------------------------------------
def main():
    """Main function."""
    config = get_config()
    validate_config(config)
    print("Configuration loaded successfully")


# --------------------------------------------------------------
if __name__ == "__main__":
    main()
```

## Benefits

These formatting rules provide:

1. **Consistency**: All code follows the same visual structure
2. **Readability**: Short functions and docstrings are easier to understand
3. **Maintainability**: Small functions are easier to test and modify
4. **Navigation**: Separator lines make it easy to visually scan the code
5. **Modularity**: Function length limits encourage better code organization

## Enforcement

These rules apply to:
- All new Python files created in the project
- All existing Python files when modified
- All Python files in the project directory and subdirectories

## Tools

These rules can be checked using:
- Manual code review
- Custom linting scripts
- IDE configuration to show line counts per function
