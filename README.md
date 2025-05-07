# `pretty_print_directory`: A Simple Utility to Pretty-Print Directory Contents

[![PyPI - Version](https://img.shields.io/pypi/v/pretty-print-directory)](https://pypi.org/project/pretty-print-directory/)
![python](https://img.shields.io/badge/-Python_%3E3.10-blue?logo=python&logoColor=white)
[![codecov](https://codecov.io/gh/mmcdermott/pretty-print-directory/graph/badge.svg?token=5RORKQOZF9)](https://codecov.io/gh/mmcdermott/pretty-print-directory)
[![tests](https://github.com/mmcdermott/pretty-print-directory/actions/workflows/tests.yaml/badge.svg)](https://github.com/mmcdermott/pretty-print-directory/actions/workflows/tests.yml)
[![code-quality](https://github.com/mmcdermott/pretty-print-directory/actions/workflows/code-quality-main.yaml/badge.svg)](https://github.com/mmcdermott/pretty-print-directory/actions/workflows/code-quality-main.yaml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/mmcdermott/pretty-print-directory#license)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/mmcdermott/pretty-print-directory/pulls)
[![contributors](https://img.shields.io/github/contributors/mmcdermott/pretty-print-directory.svg)](https://github.com/mmcdermott/pretty-print-directory/graphs/contributors)

## 1. Install

```bash
pip install pretty-print-directory
```

## 2. Usage

### Basic usage

This package is largely used through the `print_directory` function, which takes a path and prints the
contents of that directory in a tree-like format. It will print the contents of the directory and all
subdirectories.

```python
>>> from pretty_print_directory import print_directory
>>> from pathlib import Path
>>> import tempfile
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

```

You can change the print characters by passing a different `config` object to the `print_directory` function.
This object is a `PrintConfig` dataclass:

```python
>>> from pretty_print_directory import PrintConfig
>>> import inspect
>>> print(inspect.getsource(PrintConfig)) # doctest: +NORMALIZE_WHITESPACE
@dataclass
class PrintConfig:
    ...
    space: str = SPACE
    branch: str = BRANCH
    tee: str = TEE
    last: str = LAST
    file_extension: list[str] | None = None
    ...

```

#### Controlling what files are shown:

You can control what files are shown via the `file_extension` parameter of the `PrintConfig` object.

````python
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     path = Path(tmpdir)
...     (path / "file1.txt").touch()
...     (path / "foo").mkdir()
...     (path / "bar").mkdir()
...     (path / "bar" / "baz.csv").touch()
...     print_directory(path, config=PrintConfig(file_extension=".csv"))
└── bar
    └── baz.csv
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     path = Path(tmpdir)
...     (path / "file1.txt").touch()
...     (path / "foo").mkdir()
...     (path / "bar").mkdir()
...     (path / "bar" / "baz.csv").touch()
...     print_directory(path, config=PrintConfig(file_extension=[".csv", ".txt"]))
├── bar
│   └── baz.csv
└── file1.txt

#### Customizing the print style:

You can customize the print style with the `space`, `branch`, `tee`, and `last` parameters of the
`PrintConfig` object.

```python
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     path = Path(tmpdir)
...     (path / "file1.txt").touch()
...     (path / "foo").mkdir()
...     (path / "bar").mkdir()
...     (path / "bar" / "baz.csv").touch()
...     print_directory(path, config=PrintConfig(tee="+-- "))
+-- bar
│   └── baz.csv
+-- file1.txt
└── foo

````

#### Customizing the print function:

You can also pass more keyword arguments to this function which will be passed to the underlying print call.

```python
>>> from io import StringIO
>>> string_io = StringIO()
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     path = Path(tmpdir)
...     (path / "file1.txt").touch()
...     (path / "foo").mkdir()
...     (path / "bar").mkdir()
...     (path / "bar" / "baz.csv").touch()
...     print_directory(path, file=string_io)
>>> print(string_io.getvalue())
├── bar
│   └── baz.csv
├── file1.txt
└── foo
<BLANKLINE>

```

### As a pytest plugin

This package exports a pytest plugin that adds the `print_directory` function to the doctest namespace, so you
can use it in doctests easily without importing it manually. It has no other special pytest functionality at
this time.

## 3. Other notes

This repository may or may not be generally useful. There are a few other alternatives you should consider,
including:

1. https://github.com/chrizzFTD/printree
2. https://github.com/itsbrex/print-pretty-tree
3. https://github.com/AharonSambol/PrettyPrintTree
4. https://github.com/Textualize/rich

Please feel free to file issues or submit PRs for features you want to add. I make no guarantees about long
term maintenance, however.

## 4. Development

If you want to contribute, please fork the repo and make a PR. I will try to review it as soon as I can.
Install the package locally with dev and test dependencies via:

```bash
pip install -e .[dev,test]
```

Then run the tests with:

```bash
pytest
```

Note that the code blocks in the README are tested via doctests. All tests in this repository are doctests.
