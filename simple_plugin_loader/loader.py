"""
This module can load Python modules by path.
"""

from importlib import import_module
import inspect
import os
import pkgutil
import sys

from simple_plugin_loader.sample_plugin import SamplePlugin


class _Loader():
    def __init__(self):
        self.__available_plugins = {}

    @property
    def plugins(self):
        """
        Get all already loaded plugins.
        """
        return self.__available_plugins

    def load_plugins(self, path: str, plugin_base_class: type=SamplePlugin, recursive: bool=False) -> dict:
        """
        Load all classes in a directory specified by 'path' that match the 'plugin_base_class' class.

        All other classes or methods are ignored.
        """
        # normalize the path
        path = os.path.abspath(os.path.normpath(path))

        # add the parent path to the system PATH if it doesn't already exists
        # this is needed for the import later
        sys_path_modified = False
        if os.path.dirname(path) not in sys.path:
            # insert the parent path at index zero, because the loader should look at this location first
            sys.path.insert(0, os.path.dirname(path))
            sys_path_modified = True

        # do the actual import
        plugins = self.__load(path,
                              os.path.basename(path),  # the module main package is the last directory of the path
                              plugin_base_class,
                              recursive)

        # reset the modified path again
        if (sys_path_modified and
                os.path.dirname(path) in sys.path):
            sys.path.remove(os.path.dirname(path))

        self.__available_plugins.update(plugins)
        return plugins

    def __load(self, path: str, package_name: str, plugin_base_class: type=SamplePlugin, recursive: bool=False) -> dict:
        plugins = {}
        # iterate over the modules that are within the path
        for (_, name, ispkg) in pkgutil.iter_modules([path]):
            if ispkg:
                if recursive:
                    plugins.update(self.__load(os.path.join(path, name),
                                               ".".join([package_name, name]),
                                               plugin_base_class,
                                               recursive))
                    continue
                else:
                    # do not try to import it, since it's not a module
                    continue

            # import the module
            imported_module = import_module(".".join([package_name, name]))

            plugin_found = False
            # try to find a subclass of the plugin class
            for i in dir(imported_module):
                attribute = getattr(imported_module, i)

                if (inspect.isclass(attribute) and
                        # check for plugin subclass
                        issubclass(attribute, plugin_base_class) and
                        # but do not match the plugin class itself
                        attribute != plugin_base_class):
                    # if the plugin is derived from 'SamplePlugin' class,
                    if issubclass(attribute, SamplePlugin):
                        # use the 'plugin_name' property as name
                        pn = attribute.plugin_name
                    else:
                        # otherwise simply use the class name
                        pn = attribute.__name__

                    plugins[pn.casefold()] = attribute
                    plugin_found = True

            # remove imported module again if no plugin class is found
            if not plugin_found:
                del imported_module

        return plugins
