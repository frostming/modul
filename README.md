# Modul

`/moˈduːl/`

[![Tests](https://github.com/frostming/modul/workflows/Tests/badge.svg)](https://github.com/frostming/modul/actions?query=workflow%3Aci)
[![pypi version](https://img.shields.io/pypi/v/modul.svg)](https://pypi.org/project/modul/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

Control the exported members for your modules

## Requirements

Modul requires Python >=3.7

## Installation

```bash
$ python -m pip install modul
```

Modul is a single-file module with less than 200 lines of code and no dependencies. It can be easily copied into your project.

## Quick start

Write a module exporting limited members:

```python
# mymodule.py
from modul import exports


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

   Besides, the `exports` object supports all APIs of `dict`:

   ```python
   exports.update({"bar": 42})
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

6. Alternatively, you can assign members to the `exports` attribute of the module:

   ```python
   import modul

   modul.exports = {
       "bar": 42,
       "baz": "hello"
   }
   ```

   Note that you can't use `exports = <variable>` in this case, because it will lose the reference to the API.
   And each assignment will overwrite the previous one so there can be only one assignment in your module.
