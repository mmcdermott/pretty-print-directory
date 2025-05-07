from typing import Any

import pytest

from .pretty_print_directory import PrintConfig, print_directory


@pytest.fixture(autouse=True)
def ___pretty_print_directory_add_doctest(
    doctest_namespace: dict[str, Any],
) -> None:
    doctest_namespace.update(
        {
            "print_directory": print_directory,
            "PrintConfig": PrintConfig,
        }
    )
