"""
This module can load Python modules by path.
"""

from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
import inspect
from logging import Logger
import logging
import os
import sys
from types import ModuleType
from typing import List, Dict, Tuple, Optional

from .sample_plugin import SamplePlugin


class _Loader():
    def __init__(self) -> None:
        self.__available_plugins: Dict[str, type] = {}

        self.log: Logger = logging.getLogger(__name__)

        # dictionary to save the index where the PYTHONPATH was modified with the corresponding path
        self.__sys_path_modified_at_index: Dict[str, int] = {}

    @property
    def plugins(self) -> Dict[str, type]:
        """
        @return: All already loaded plugins.
        """
        return self.__available_plugins

    def load_plugins(self, path: str,
                     plugin_base_class: type=SamplePlugin,
                     specific_plugins: List[str]=[],
                     recursive: bool=False) -> Dict[str, type]:
        """
        Load all classes in a directory specified by 'path' that match the 'plugin_base_class' class.
        Alternatively if the 'specific_plugins' list contains class names, only those will be loaded.
        They don't need to be subclasses of e.g. 'SamplePlugin'.

        All other classes or methods are ignored.

        @param path: The path to the plugins.
        @param plugin_base_class: The plugins must be subclasses of this class to get loaded.
        @param specific_plugins: A list with class names that should be loaded. If this argument is set the
                                 plugin_base_class argument will be ignored.
        @param recursive: Set this to True if sub-directories of path should also be searched. (Default: False)
        @return: A dictionary that contains the class name as the key and the loaded class itself as value.
        """
        # normalize the path
        path = os.path.abspath(os.path.normpath(path))

        # add the parent path to the system PATH if it doesn't already exists
        # this is needed for the import later
        self.__add_to_pythonpath(path)

        # do the actual import
        plugins: Dict[str, type] = self.__load(path,
                                               plugin_base_class,
                                               specific_plugins,
                                               recursive)

        # reset the modified path again
        self.__remove_from_pythonpath(path)

        self.__available_plugins.update(plugins)
        return plugins

    def __load(self, path: str,
               plugin_base_class: type=SamplePlugin,
               specific_plugins: List[str]=[],
               recursive: bool=False) -> Dict[str, type]:
        """
        This method does the actual plugin loading.
        The arguments are the same as the of the load_plugins method.
        """
        plugins: Dict[str, type] = {}

        # use the FileFinder from pkgutil to find the modules

        # indicator if in the current path are only directories (will be checked later)
        only_packages: bool = True

        found_modules: List[Tuple[str, bool]] = []
        try:
            dircontents: List[str] = os.listdir(path)
        except OSError:
            # ignore unreadable directories like import does
            dircontents = []
        for item in dircontents:
            item = os.path.join(path, item)
            if os.path.isdir(item):
                found_modules.append((item, True))
            elif os.path.isfile(os.path.join(path, item)):
                module_name: Optional[str] = inspect.getmodulename(item)
                if module_name and module_name != "__init__":
                    found_modules.append((item, False))
                    # now there are not only directories to import
                    only_packages = False

        # iterate over the modules that are within the path
        for module_path, is_dir in found_modules:
            if is_dir:
                # search in the package if recursive search is requested
                # or if only packages are found in the path -> try to find plugin modules one level down
                if recursive or only_packages:
                    plugins.update(self.load_plugins(module_path,
                                                     plugin_base_class,
                                                     specific_plugins,
                                                     recursive))
                    continue
                else:
                    # do not try to import it, since it's not a module
                    continue

            # import the module
            name: Optional[str] = inspect.getmodulename(module_path)
            if not name:
                # this can not happen, because the module name is already checked above
                # basically the spec_from_file_location method works also with an empty string
                name = ""

            try:
                spec: Optional[ModuleSpec] = spec_from_file_location(name, module_path)
                if spec:
                    imported_module: ModuleType = module_from_spec(spec)
                    if spec.loader:
                        spec.loader.exec_module(imported_module)
                    else:
                        raise ModuleNotFoundError(f"No loader found for module '{name}'")
                else:
                    raise ModuleNotFoundError(f"No spec found for module '{name}'")
            except ModuleNotFoundError as e:
                self.log.error(f"Can't import module '{name}'! ({e}) -> Skipping it.")

                continue

            plugin_found: bool = False
            # try to find a subclass of the plugin class
            for i in dir(imported_module):
                attribute: type = getattr(imported_module, i)

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
                    pn: str
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

    def __add_to_pythonpath(self, path: str) -> None:
        """
        Helper method to add a path to the PYTHONPATH.
        @param path: The path to add.
        """
        # only add if it doesn't already exist
        if path not in sys.path:
            # append the parent path to the PYTHONPATH to find relative imports of the imported module
            # save the index on which the path is inserted
            self.__sys_path_modified_at_index[path] = len(sys.path)
            # add the path
            sys.path.insert(self.__sys_path_modified_at_index[path], path)

    def __remove_from_pythonpath(self, path: str) -> None:
        """
        Helper method to remove a path from the PYTHONPATH.
        @param path: The path to remove.
        """
        if path in self.__sys_path_modified_at_index:
            # the PYTHONPATH could be modified by an imported module, so check if the saved index is still valid
            if sys.path[self.__sys_path_modified_at_index[path]] == path:
                sys.path.pop(self.__sys_path_modified_at_index[path])
            else:
                # otherwise remove the last occurence of the path
                for i in range(len(sys.path) - 1, 0, -1):
                    if sys.path[i] == path:
                        sys.path.pop(i)
