from tests.test_plugins.test_plugin_main import TestPlugin


class Plugin2WithErrors(TestPlugin):
    import this_module_does_not_exist
