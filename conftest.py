import importlib
import tempfile
from pathlib import Path
from typing import Any

import pytest

import pretty_print_directory
import pretty_print_directory.pretty_print_directory

importlib.reload(pretty_print_directory)
importlib.reload(pretty_print_directory.pretty_print_directory)


@pytest.fixture(autouse=True)
def _setup(doctest_namespace: dict[str, Any]):
    doctest_namespace.update({"tempfile": tempfile, "Path": Path})
