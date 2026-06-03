# Hive Glob

Simple Python Library for aiding Hive Partitioned Dataset Handling.

Supports Local and S3 Based FileSystems.

## Example

```python
from hive_glob import HiveDataset, FileSystem

ds = HiveDataset(root="s3://bucket/dataset_root/", fs=S3FileSystem())

ds.partition_keys  # ["key1", "key2"]
```
