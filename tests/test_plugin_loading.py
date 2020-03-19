import os
import unittest

from plugin_loader.loader import Loader
from tests.test_plugins.test_plugin_main import TestPlugin


PLUGIN_PATH = "test_plugins"


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

    def test_load_non_recursive(self):
        plugins = self.loader.load_plugins(PLUGIN_PATH, TestPlugin, False)

        self.check_plugin_loaded(plugins, "plugin1")

        # the 'SubPlugin1' must not be in the imported plugin list because the import was done none recursively
        self.assertNotIn("subplugin1", plugins)

    def test_load_recursive(self):
        plugins = self.loader.load_plugins(PLUGIN_PATH, TestPlugin, True)

        self.check_plugin_loaded(plugins, "plugin1")
        self.check_plugin_loaded(plugins, "sub_plugin1")

    def test_load_plugins_from_package_not_in_path(self):
        # this path is not in the current sys.path
        plugin_dir_not_in_path = os.path.join(PLUGIN_PATH, "sub_plugin1")

        plugins = self.loader.load_plugins(plugin_dir_not_in_path, TestPlugin)

        self.check_plugin_loaded(plugins, "sub_plugin1")


if __name__ == "__main__":
    unittest.main()
