import os

import pytest

from hive_glob import HiveDataset, LocalFileSystem

# data/region=us/year=2024/data.parquet
# data/region=us/year=2025/data.parquet
# data/region=eu/year=2024/data.parquet
# data/region=eu/year=2024/_meta.txt
LEAVES = [
    ("region=us", "year=2024", "data.parquet"),
    ("region=us", "year=2025", "data.parquet"),
    ("region=eu", "year=2024", "data.parquet"),
    ("region=eu", "year=2024", "_meta.txt"),
]


@pytest.fixture
def root(tmp_path):
    for region, year, fname in LEAVES:
        leaf = tmp_path / region / year
        leaf.mkdir(parents=True, exist_ok=True)
        (leaf / fname).write_text("x")
    return tmp_path


@pytest.fixture
def ds(root):
    return HiveDataset(root=str(root), fs=LocalFileSystem())


def _as_set(dicts):
    return {frozenset(d.items()) for d in dicts}


def _expected_files(root, predicate=lambda r, y, f: True):
    return sorted(os.path.join(str(root), r, y, f) for r, y, f in LEAVES if predicate(r, y, f))


# ------------------------ partition discovery ------------------------
def test_partition_keys(ds):
    assert ds.partition_keys == ["region", "year"]


def test_partitions_all(ds):
    assert _as_set(ds.partitions()) == {
        frozenset({("region", "us"), ("year", "2024")}),
        frozenset({("region", "us"), ("year", "2025")}),
        frozenset({("region", "eu"), ("year", "2024")}),
    }


def test_partitions_filtered_by_single_value(ds):
    assert _as_set(ds.partitions({"region": "us"})) == {
        frozenset({("region", "us"), ("year", "2024")}),
        frozenset({("region", "us"), ("year", "2025")}),
    }


def test_partitions_filtered_by_list(ds):
    assert _as_set(ds.partitions({"year": [2025]})) == {
        frozenset({("region", "us"), ("year", "2025")}),
    }


def test_partitions_no_match_is_empty(ds):
    assert ds.partitions({"region": "apac"}) == []


# ------------------------ values ------------------------
def test_values(ds):
    assert ds.values("region") == ["eu", "us"]
    assert ds.values("year") == ["2024", "2025"]


def test_values_with_filter(ds):
    assert ds.values("year", {"region": "us"}) == ["2024", "2025"]
    assert ds.values("year", {"region": "eu"}) == ["2024"]


def test_values_unknown_key_is_empty(ds):
    assert ds.values("nope") == []


# ------------------------ files ------------------------
def test_files_all(ds, root):
    assert sorted(ds.files()) == _expected_files(root)


def test_files_with_pattern(ds, root):
    assert sorted(ds.files(pattern="*.parquet")) == _expected_files(root, lambda r, y, f: f.endswith(".parquet"))


def test_files_filtered(ds, root):
    assert sorted(ds.files({"region": "us"})) == _expected_files(root, lambda r, y, f: r == "region=us")


def test_glob_convenience(ds, root):
    assert sorted(ds.glob(region="us")) == _expected_files(root, lambda r, y, f: r == "region=us")


# ------------------------ _parse_partition ------------------------
def test_parse_partition():
    assert HiveDataset._parse_partition("region=us") == ("region", "us")
    # only the first '=' splits
    assert HiveDataset._parse_partition("k=a=b") == ("k", "a=b")
    # not a partition directory
    assert HiveDataset._parse_partition("plain") is None
