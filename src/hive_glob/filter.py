from typing import Iterable, Optional

from hive_glob.domain import PartitionKey, PartitionValue

# Filter Value as a Key,[Value] Pair
## Key - Partition Key (e.g., "month_id")
## Value - A single value or a list of values to match against the Partition Value
type FilterValue = dict[PartitionKey, PartitionValue | Iterable[PartitionValue]]


class PartitionFilter:
    """Represents Filters on a Hive Partition DataSet"""

    def __init__(self, filters: FilterValue | None = None):
        self.filters: dict[PartitionKey, Optional[set[PartitionValue]]] = {}

        if filters:
            for k, v in filters.items():
                if isinstance(v, (list, tuple, set)):
                    self.filters[k] = {str(x) for x in v}
                else:
                    self.filters[k] = {str(v)}

    def allowed(self, key: str) -> Optional[set[str]]:
        return self.filters.get(key)

    def match(self, partitions: dict[str, str]) -> bool:
        for k, allowed in self.filters.items():
            if k not in partitions:
                return False
            if partitions[k] not in allowed:
                return False
        return True
