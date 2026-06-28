# Hive Glob

Simple Python Library for aiding Hive Partitioned Dataset Handling.

Supports Local FileSystems and S3-Based Objects Stores.

## Installation

Install from Github or PyPi:

```bash
pip install hive-glob

# With S3FS Addition

```bash
pip install hive-glob[s3]
```

## Example

```python
from hive_glob import HiveDataset, FileSystem

ds = HiveDataset(root="s3://bucket/dataset_root/", fs=S3FileSystem())

ds.partition_keys  # ["key1", "key2"]
```
