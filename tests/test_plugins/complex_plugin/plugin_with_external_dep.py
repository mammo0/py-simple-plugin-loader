from package.dependency import Dependency
from tests.test_plugins.test_plugin_main import TestPlugin


class PluginWithExternalDep(TestPlugin):
    test = Dependency()
