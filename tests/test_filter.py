from hive_glob.filter import PartitionFilter


def test_empty_filter_allows_everything():
    pf = PartitionFilter()
    assert pf.filters == {}
    assert pf.allowed("anything") is None
    # match against an empty filter set is always True
    assert pf.match({"region": "us"}) is True
    assert pf.match({}) is True


def test_none_filter_is_empty():
    assert PartitionFilter(None).filters == {}


def test_single_value_normalised_to_str_set():
    pf = PartitionFilter({"year": 2024})
    assert pf.allowed("year") == {"2024"}


def test_iterable_values_normalised_to_str_set():
    assert PartitionFilter({"year": [2024, 2025]}).allowed("year") == {"2024", "2025"}
    assert PartitionFilter({"year": (2024, 2025)}).allowed("year") == {"2024", "2025"}
    assert PartitionFilter({"year": {2024, 2025}}).allowed("year") == {"2024", "2025"}


def test_allowed_unknown_key_is_none():
    assert PartitionFilter({"year": 2024}).allowed("region") is None


def test_match_requires_all_keys_present_and_in_set():
    pf = PartitionFilter({"region": "us", "year": [2024, 2025]})
    assert pf.match({"region": "us", "year": "2024"}) is True
    assert pf.match({"region": "us", "year": "2025"}) is True
    # value not in allowed set
    assert pf.match({"region": "us", "year": "2030"}) is False
    # missing a filtered key
    assert pf.match({"region": "us"}) is False
    # wrong value for a filtered key
    assert pf.match({"region": "eu", "year": "2024"}) is False


def test_match_ignores_extra_partition_keys():
    pf = PartitionFilter({"region": "us"})
    assert pf.match({"region": "us", "year": "2024", "day": "01"}) is True
