"""
This module contains a sample Plugin class.

This class can be used as a base class for your plugins.
It can be used by the plugin loader to identify plugin modules that can be loaded.

Please note: This is an abstract class so your plugin class can use @abstractmethod to define some must have methods of
the class.
"""

from abc import ABCMeta
import sys
from typing import TextIO

from simple_classproperty import ClasspropertyMeta, classproperty


class SamplePluginMeta(ABCMeta, ClasspropertyMeta):
    pass


class SamplePlugin(metaclass=SamplePluginMeta):
    """
    You can use this class as a base class that can be loaded with the plugin loader.
    """
    def print(self, msg: str, file: TextIO=sys.stdout, **kwargs) -> None:
        """
        Print a message.
        All kwargs of regular 'print' are supported.
        @param msg: The message to print.
        @param file: The destination IO stream where the message is printed on (Default: stdout).
        """
        self.__print(msg, out=file, **kwargs)

    def eprint(self, msg: str, file: TextIO=sys.stderr, **kwargs) -> None:
        """
        Print a message.
        All kwargs of regular 'print' are supported.
        @param msg: The message to print.
        @param file: The destination IO stream where the message is printed on (Default: stderr).
        """
        self.__print(msg, out=file, **kwargs)

    @classproperty
    def plugin_name(cls) -> str:
        """
        Get the name of the plugin.
        By default the class name is used.
        """
        return cls.__name__

    def __print(self, msg: str, out: TextIO=sys.stdout, **kwargs) -> None:
        # insert the plugin name before the message
        print("[%s]: %s" % (self.plugin_name, msg), file=out, **kwargs)
