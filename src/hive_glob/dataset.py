from dataclasses import dataclass
from typing import Iterator

from hive_glob.domain import PartitionKey, PartitionValue
from hive_glob.filesystem import FileSystem
from hive_glob.filter import FilterValue, PartitionFilter


@dataclass(frozen=True)
class HiveDataset:
    """Configuration of a Hive Dataset"""

    root: str  # Root Path of the Hive Dataset (e.g., "s3://bucket/dataset/")
    fs: FileSystem

    # ------------------------
    # Partition Discovery
    # ------------------------
    @staticmethod
    def _parse_partition(name: str) -> tuple[PartitionKey, PartitionValue] | None:
        if "=" not in name:
            return None
        k, v = name.split("=", 1)
        return k, v

    def _walk_partitions(self, base_path: str, filter_obj: PartitionFilter, collected: dict[str, str]) -> Iterator[tuple[str, dict[str, str]]]:
        """Depth-first Traversal with Pruning
        :return (path, partition_dict)
        """
        partition_dirs = []
        files_present = False

        for p in self.fs.ls(base_path):
            if self.fs.is_dir(p):
                name = p.rstrip("/").split("/")[-1]
                parsed = self._parse_partition(name)

                if parsed:
                    key, value = parsed

                    allowed = filter_obj.allowed(key)
                    if allowed and value not in allowed:
                        continue  # prune

                    partition_dirs.append((p, key, value))
            else:
                files_present = True

        # Leaf partition
        if not partition_dirs and files_present:
            if filter_obj.match(collected):
                yield base_path, dict(collected)
            return

        # Continue traversal
        for p, key, value in partition_dirs:
            collected[key] = value
            yield from self._walk_partitions(p, filter_obj, collected)
            collected.pop(key)

    # ------------------------
    # Public API
    # ------------------------
    @property
    def partition_keys(self) -> list[PartitionKey]:
        """Discover All Partition Keys in the Dataset"""
        keys = set()
        for path, parts in self._walk_partitions(self.root, PartitionFilter(None), {}):
            keys.update(parts.keys())
        return sorted(keys)

    def partitions(self, filters: FilterValue | None = None) -> list[dict[PartitionKey, PartitionValue]]:
        """Discover Partitions Matching the Given Filters - All Partitions if No Filters Provided"""
        pf = PartitionFilter(filters)
        results = []
        for path, parts in self._walk_partitions(self.root, pf, {}):
            results.append(parts)
        return results

    def files(self, filters: FilterValue | None = None, pattern: str = "*") -> list[str]:
        """Discover Files Matching the Given Filters - All Files if No Filters Provided"""
        pf = PartitionFilter(filters)
        results = []

        for path, _ in self._walk_partitions(self.root, pf, {}):
            glob_path = self.fs.join(path, pattern)
            results.extend(self.fs.glob(glob_path))

        return results

    def values(self, key: str, filters: FilterValue | None = None) -> list[str]:
        """Discover Unique Values for a Given Partition Key"""
        vals = set()
        for p in self.partitions(filters):
            if key in p:
                vals.add(p[key])
        return sorted(vals)

    # ------------------------
    # Convenience Methods
    # ------------------------
    def glob(self, **filters):
        return self.files(filters=filters)
