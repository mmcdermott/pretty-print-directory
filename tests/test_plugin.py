import importlib

import pretty_print_directory.pytest_plugin

importlib.reload(pretty_print_directory.pytest_plugin)


def test_plugin_doctest():
    """This tests the plugin code via a doctest.

    Note that there is no import of `print_directory` here -- it should be automatically added by the plugin.

    Examples:
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     path = Path(tmpdir)
        ...     (path / "file1.txt").touch()
        ...     (path / "foo").mkdir()
        ...     (path / "bar").mkdir()
        ...     (path / "bar" / "baz.csv").touch()
        ...     print_directory(path)
        ├── bar
        │   └── baz.csv
        ├── file1.txt
        └── foo
    """

    pass
