"""
This module contains a sample Plugin class.

This class can be used as a base class for your plugins.
It can be used by the plugin loader to identify plugin modules that can be loaded.

Please note: This is an abstract class so your plugin class can use @abstractmethod to define some must have methods of the class.
"""

from abc import ABC
import sys


class classproperty(property):
    def __get__(self, _, owner):
        return super(classproperty, self).__get__(owner)


class SamplePlugin(ABC):
    """
    You can use this class as a base class that can be loaded with the plugin loader.
    """
    def print(self, msg: str, **kwargs) -> None:
        """
        Print a string to stdout.

        All kwargs of regular 'print' are supported, except the 'file' argument.
        """
        if "file" in kwargs:
            kwargs.pop("file")
        self.__print(msg, **kwargs)

    def eprint(self, msg: str, **kwargs) -> None:
        """
        Print a string to stderr.

        All kwargs of regular 'print' are supported, except the 'file' argument.
        """
        if "file" in kwargs:
            kwargs.pop("file")
        self.__print(msg, sys.stderr, **kwargs)

    @classproperty
    def plugin_name(self) -> str:
        """
        Get the name of the plugin.
        By default the class name is used.
        """
        return self.__name__

    def __print(self, msg: str, out=sys.stdout, **kwargs) -> None:
        # insert the plugin name before the message
        print("[%s]: %s" % (self.plugin_name, msg), file=out, **kwargs)
