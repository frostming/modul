# exports

[![Tests](https://github.com/frostming/exports/workflows/Tests/badge.svg)](https://github.com/frostming/exports/actions?query=workflow%3Aci)
[![pypi version](https://img.shields.io/pypi/v/exports.svg)](https://pypi.org/project/exports/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

Control the exported members for your modules

## Requirements

exports requires Python >=3.7

## Installation

```bash
$ python -m pip install exports
```

## Quick start

Write a module exporting limited members:

```python
# mymodule.py
from exports import exports


@exports
def foo():
    return 42


baz = "unexported"
bar = "hello"

exports.bar = bar
```

In another module or REPL:

```python
>>> import mymodule
>>> mymodule.foo()
42
>>> mymodule.bar
"hello"
>>> mymodule.baz
AttributeError: Module test has no attribute baz
>>> mymodule.__all__
['foo', 'bar']
```

## Usage

1. Export a function with decorator:

   ```python
   @exports
   def foo():
       return 42
   ```

2. Export a variable with attribute set:

   ```python
   exports.bar = 42
   ```

   Note that to use the variable inside the module, you still need to declare a variable for it:

   ```python
   bar = 42
   exports.bar = bar
   ```

3. Export a variable with item set:

   ```python
   exports["bar"] = 42
   ```

4. Export a map of (name, value) pairs:

   ```python
   exports({
       "bar": 42,
       "baz": "hello"
   })
   ```

5. You can even have conditional exports and exports from function call:

   ```python
   flag = True
   if flag:
       exports.foo = 42

   def export_bar():
       exports.bar = 42
   export_bar()
   ```
