# Simple Python Plugin Loader

![PyPI package](https://github.com/mammo0/py-simple-plugin-loader/workflows/PyPI%20package/badge.svg)
[![PyPI version](https://badge.fury.io/py/simple-plugin-loader.svg)](https://badge.fury.io/py/simple-plugin-loader)

This module provides a simple way to dynamically load other Python modules as Plugins to your current project.


### Install

You can install this python module via **pip**:
```shell
pip install simple-plugin-loader
```

Otherwise the module can be downloaded from PyPI: https://pypi.org/project/simple-plugin-loader/


### Usage

1. Import the module:
    ```python
    from plugin_loader.loader import Loader
    ```
2. Load your plugins/modules:
    ```python
    # initialize the loader
    loader = Loader()

    # load your plugins
    plugins = self.loader.load_plugins(<plugin_path>, <plugin_base_class, <recursive>)
    ```
3. **(Optional)** The already loaded plugins/modules can be accessed via the `plugins` property of the loader instance:
   ```python
   plugins = loader.plugins
   ```

### `load_plugins(...)` Method

##### Arguments

- `<plugin_path>`: _str_</br>
  This string represents the path (relative or absolute) to the directory from where the plugins/modules should be loaded.
- `<plugin_base_class>`: _class_ (Default: `SamplePlugin`)</br>
  The Loader does not load all found modules that are in the above directory. It only loads classes that are **sub-classes** of the here specified class.</br>
  The default value of this argument is the `SamplePlugin` class. You can use this class as the base class for your plugins:
  ```python
  from plugin_loader.sample_plugin import SamplePlugin

  class YourPlugin(SamplePlugin):
      pass
  ```
- `<recursive>`: _bool_ (Default: `False`)</br>
  Set this flag to `True` if you wish to load plugins/modules recursively to the above directory.

##### Return value

The method returns a dictionary that has the following structure:

- **Key**: The name of the plugin/module. This name is the module name of the module that contains the plugin class.
- **Value**: The plugin class. Not an instance!
