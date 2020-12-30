from io import StringIO
import os
import sys
import unittest

from simple_plugin_loader import Loader
from tests.test_plugins.test_plugin_main import TestPlugin


PLUGIN_PATH = os.path.join(os.path.dirname(__file__), "test_plugins")


class Test(unittest.TestCase):
    def setUp(self):
        self.loader = Loader()

    def tearDown(self):
        del self.loader

    def check_plugin_loaded(self, plugin_list: dict, plugin_name: str):
        # the class with the name 'plugin_name' must be in the imported plugin list
        self.assertIn(plugin_name, plugin_list)

        # create an instance of the plugin
        plugin = plugin_list[plugin_name]()
        # the class must be an instance of 'TestPlugin'
        self.assertIsInstance(plugin, TestPlugin)

    def load_non_recursive(self, verbose):
        plugins = self.loader.load_plugins(PLUGIN_PATH, TestPlugin, recursive=False, verbose=verbose)

        self.check_plugin_loaded(plugins, "plugin1")

        # the 'Plugin2WithErrors' must not be in the imported plugin list, because it contains errors
        self.assertNotIn("plugin2witherrors", plugins)

        # the 'SubPlugin1' must not be in the imported plugin list because the import was done none recursively
        self.assertNotIn("subplugin1", plugins)

    def test_load_non_recursive_without_verbose(self):
        # load plugins without verbosity
        self.load_non_recursive(False)

    def test_load_non_recursive_with_verbose(self):
        # catch output
        stdout = sys.stdout
        stderr = sys.stderr
        sys.stdout = temp_stdout = StringIO()
        sys.stderr = temp_stderr = StringIO()

        # load plugins with verbosity
        self.load_non_recursive(True)

        # check output
        self.assertIn("Imported plugin Plugin1 as plugin1", temp_stdout.getvalue())
        self.assertIn("Can't import module 'test_plugins.plugin2_with_errors'!", temp_stderr.getvalue())

        # restore output
        sys.stdout = stdout
        sys.stderr = stderr

    def test_load_recursive(self):
        plugins = self.loader.load_plugins(PLUGIN_PATH, TestPlugin, recursive=True)

        self.check_plugin_loaded(plugins, "plugin1")
        self.check_plugin_loaded(plugins, "subplugin1")
        self.check_plugin_loaded(plugins, "subplugin2")

    def test_load_specific_plugins(self):
        # normally the class 'Plugin3NoSubclass' should not be loaded
        plugins = self.loader.load_plugins(PLUGIN_PATH, TestPlugin)
        self.assertNotIn("plugin3nosubclass", plugins)

        # now specify the class 'Plugin3NoSubclass' explicitly
        plugins = self.loader.load_plugins(PLUGIN_PATH, specific_plugins=['Plugin3NoSubclass'])
        self.assertIn("plugin3nosubclass", plugins)
        self.assertNotIn("plugin1", plugins)

    def test_load_plugins_from_package_not_in_path(self):
        # this path is not in the current sys.path
        plugin_dir_not_in_path = os.path.join(PLUGIN_PATH, "sub_plugin1")

        plugins = self.loader.load_plugins(plugin_dir_not_in_path, TestPlugin)

        self.check_plugin_loaded(plugins, "subplugin1")


if __name__ == "__main__":
    unittest.main()
