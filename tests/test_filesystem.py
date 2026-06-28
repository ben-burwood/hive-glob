import os

import pytest

from hive_glob import LocalFileSystem


@pytest.fixture
def tree(tmp_path):
    # tmp_path/
    #   region=us/      (dir)
    #   readme.txt      (file)
    #   data.parquet    (file)
    (tmp_path / "region=us").mkdir()
    (tmp_path / "readme.txt").write_text("hi")
    (tmp_path / "data.parquet").write_text("x")
    return tmp_path


def test_ls_returns_full_child_paths(tree):
    fs = LocalFileSystem()
    listed = set(fs.ls(str(tree)))
    expected = {
        str(tree / "region=us"),
        str(tree / "readme.txt"),
        str(tree / "data.parquet"),
    }
    assert listed == expected


def test_is_dir(tree):
    fs = LocalFileSystem()
    assert fs.is_dir(str(tree / "region=us")) is True
    assert fs.is_dir(str(tree / "readme.txt")) is False


def test_glob(tree):
    fs = LocalFileSystem()
    matched = fs.glob(os.path.join(str(tree), "*.parquet"))
    assert matched == [str(tree / "data.parquet")]


def test_join(tree):
    fs = LocalFileSystem()
    assert fs.join("a", "b", "c") == os.path.join("a", "b", "c")
