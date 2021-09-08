from io import StringIO
import unittest

from simple_plugin_loader.sample_plugin import SamplePlugin


class Test(unittest.TestCase):
    def test_plugin_name_property(self) -> None:
        self.assertEqual(SamplePlugin.plugin_name, "SamplePlugin")

    def test_print_methods(self) -> None:
        message: str = "Test message."
        additions: str = "[SamplePlugin]: "

        plugin: SamplePlugin = SamplePlugin()

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
