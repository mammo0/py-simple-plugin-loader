import unittest
from simple_plugin_loader.sample_plugin import SamplePlugin
from io import StringIO


class Test(unittest.TestCase):
    def test_plugin_name_property(self):
        self.assertEqual(SamplePlugin.plugin_name, "SamplePlugin")

    def test_print_methods(self):
        message = "Test message."
        additions = "[SamplePlugin]: "

        plugin = SamplePlugin()

        # test print()
        with StringIO() as out:
            plugin.print(message, file=out, end='')

            self.assertEqual(out.getvalue(), additions + message)

        # test eprint()
        with StringIO() as out:
            plugin.eprint(message, file=out, end='')

            self.assertEqual(out.getvalue(), additions + message)


if __name__ == "__main__":
    unittest.main()
