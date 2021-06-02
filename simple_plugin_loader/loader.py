"""
This module can load Python modules by path.
"""

from importlib import import_module
import inspect
import logging
import os
import pkgutil
import sys
from typing import List

from .sample_plugin import SamplePlugin


class _Loader():
    def __init__(self):
        self.__available_plugins = {}

        self.log = logging.getLogger(__name__)

    @property
    def plugins(self):
        """
        Get all already loaded plugins.
        """
        return self.__available_plugins

    def load_plugins(self, path: str,
                     plugin_base_class: type=SamplePlugin,
                     specific_plugins: List[str]=[],
                     recursive: bool=False) -> dict:
        """
        Load all classes in a directory specified by 'path' that match the 'plugin_base_class' class.
        Alternatively if the 'specific_plugins' list contains class names, only those will be loaded.
        They don't need to be subclasses of e.g. 'SamplePlugin'.

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
                              specific_plugins,
                              recursive)

        # reset the modified path again
        if (sys_path_modified and
                os.path.dirname(path) in sys.path):
            sys.path.remove(os.path.dirname(path))

        self.__available_plugins.update(plugins)
        return plugins

    def __load(self, path: str,
               package_name: str,
               plugin_base_class: type=SamplePlugin,
               specific_plugins: List[str]=[],
               recursive: bool=False) -> dict:
        plugins = {}
        # iterate over the modules that are within the path
        for (_, name, ispkg) in pkgutil.iter_modules([path]):
            if ispkg:
                if recursive:
                    plugins.update(self.__load(os.path.join(path, name),
                                               ".".join([package_name, name]),
                                               plugin_base_class,
                                               specific_plugins,
                                               recursive))
                    continue
                else:
                    # do not try to import it, since it's not a module
                    continue

            # import the module
            try:
                imported_module = import_module(".".join([package_name, name]))
            except ModuleNotFoundError as e:
                self.log.error("Can't import module '%s'! (%s) -> Skipping it.",
                               ".".join([package_name, name]), str(e))
                continue

            plugin_found = False
            # try to find a subclass of the plugin class
            for i in dir(imported_module):
                attribute = getattr(imported_module, i)

                # first check if it's a class
                if (inspect.isclass(attribute) and
                        # check if only specific plugins should be loaded
                        ((specific_plugins and
                            # they must match the name case sensitive
                            attribute.__name__ in specific_plugins) or
                         # otherwise check for plugin subclass
                         (not specific_plugins and
                            issubclass(attribute, plugin_base_class) and
                            # but do not match the plugin class itself
                            attribute != plugin_base_class))):
                    # if the plugin is derived from 'SamplePlugin' class,
                    if issubclass(attribute, SamplePlugin):
                        # use the 'plugin_name' property as name
                        pn = attribute.plugin_name
                    else:
                        # otherwise simply use the class name
                        pn = attribute.__name__

                    plugins[pn.casefold()] = attribute
                    plugin_found = True

                    self.log.info("Imported plugin %s as %s", pn, pn.casefold())

            # remove imported module again if no plugin class is found
            if not plugin_found:
                del imported_module

        return plugins
