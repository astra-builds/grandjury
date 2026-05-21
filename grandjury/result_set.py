"""
ResultSet — lightweight wrapper around API response data.

Provides .to_pandas(), .to_polars(), .to_parquet(), .to_csv(), .to_json()
without forcing any dependency. Raw data always accessible via .data

Supports auto-pagination: when a `_fetcher` callback is provided, iterating
past the current page transparently fetches the next one. .to_pandas() and
other export methods collect all pages first.

ModelList — lean list of models enrolled in an arena.
"""

from typing import Any, Callable, Dict, List, Optional


class ModelList:
    """
    A list of models enrolled in an arena.

    Usage:
        models = gj.arena("id").models()
        print(models)              # ModelList(14 models)
        print(models[0])           # {'name': 'GPT-5.4', 'slug': 'openai-gpt-5-4', ...}
        for m in models:
            print(m["name"])
        df = models.to_pandas()
    """

    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        names = [m.get("name", "?") for m in self.data[:5]]
        suffix = f", ... +{len(self.data) - 5} more" if len(self.data) > 5 else ""
        return f"ModelList({len(self.data)} models: {names}{suffix})"

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, idx):
        result = self.data[idx]
        if isinstance(idx, slice):
            return ModelList(result)
        return result

    def __bool__(self) -> bool:
        return len(self.data) > 0

    def to_pandas(self):
        """Convert to pandas DataFrame. Requires: pip install pandas"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required: pip install grandjury[pandas]")
        return pd.DataFrame(self.data)

PAGE_SIZE = 1000  # hard cap per API request


class ResultSet:
    """
    A collection of result rows from the GrandJury API.

    Usage:
        results = gj.arena("id").votes()
        print(results)              # ResultSet(1000 rows, paginated)
        print(len(results))         # rows loaded so far

        for row in results:         # auto-paginates — fetches next page when exhausted
            print(row)

        df = results.to_pandas()    # collects ALL pages into one DataFrame
        results.to_parquet("output.parquet")
        results.to_csv("output.csv")
    """

    def __init__(
        self,
        data: List[Dict[str, Any]],
        _fetcher: Optional[Callable[[int], List[Dict[str, Any]]]] = None,
    ):
        """
        Args:
            data: initial page of results
            _fetcher: optional callback(offset) -> list[dict] for auto-pagination.
                      Returns empty list when no more data.
        """
        self.data = data
        self._fetcher = _fetcher
        self._exhausted = _fetcher is None  # lazy: not exhausted until we try

    def fetch(self, n: int = PAGE_SIZE):
        """Fetch up to n rows. Returns self for chaining.

        Args:
            n: number of rows to fetch (default: 1000)
        """
        if self._exhausted:
            return self
        target = len(self.data) + n
        while len(self.data) < target and not self._exhausted:
            page = self._fetcher(len(self.data))
            if not page:
                self._exhausted = True
                break
            self.data.extend(page)
            if len(page) < PAGE_SIZE:
                self._exhausted = True
        return self

    def fetch_all(self):
        """Load all remaining pages into self.data. Returns self for chaining."""
        if self._exhausted:
            return self
        while True:
            page = self._fetcher(len(self.data))
            if not page:
                break
            self.data.extend(page)
            if len(page) < PAGE_SIZE:
                break
        self._exhausted = True
        return self

    def head(self, n: int = 5):
        """Return first n rows as a ResultSet. Fetches if needed."""
        while len(self.data) < n and not self._exhausted:
            self.fetch(PAGE_SIZE)
        return ResultSet(self.data[:n])

    def __len__(self) -> int:
        """Return total row count, forcing a full fetch if not yet exhausted.

        Pythonic: len(result_set) gives the authoritative count, not just what's
        been fetched so far. Triggers fetch_all() which auto-paginates through
        all remaining pages.
        """
        if not self._exhausted:
            self.fetch_all()
        return len(self.data)

    def __repr__(self) -> str:
        if len(self.data) == 0 and not self._exhausted:
            return "ResultSet(not loaded — use .fetch(), .head(), .to_pandas(), or iterate)"
        suffix = ", more available" if not self._exhausted else ""
        return f"ResultSet({len(self.data)} rows{suffix})"

    def __iter__(self):
        """Iterate with auto-pagination — fetches next page when current is exhausted."""
        idx = 0
        while True:
            if idx < len(self.data):
                yield self.data[idx]
                idx += 1
            elif not self._exhausted:
                page = self._fetcher(len(self.data))
                if not page:
                    self._exhausted = True
                    break
                self.data.extend(page)
                if len(page) < PAGE_SIZE:
                    self._exhausted = True
                # continue loop — idx < len(self.data) now
            else:
                break

    def __getitem__(self, idx):
        result = self.data[idx]
        if isinstance(idx, slice):
            return ResultSet(result)
        return result

    def __bool__(self) -> bool:
        return len(self.data) > 0

    def to_pandas(self):
        """Convert to pandas DataFrame. Collects all pages first. Requires: pip install pandas"""
        self.fetch_all()
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required: pip install grandjury[pandas]")
        return pd.DataFrame(self.data)

    def to_polars(self):
        """Convert to polars DataFrame. Collects all pages first. Requires: pip install polars"""
        self.fetch_all()
        try:
            import polars as pl
        except ImportError:
            raise ImportError("polars is required: pip install grandjury[polars]")
        return pl.DataFrame(self.data)

    def to_parquet(self, path: str) -> None:
        """Export to Parquet file. Collects all pages first. Requires: pip install pyarrow or pandas"""
        self.fetch_all()
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
            table = pa.Table.from_pylist(self.data)
            pq.write_table(table, path)
            return
        except ImportError:
            pass
        try:
            self.to_pandas().to_parquet(path, index=False)
            return
        except ImportError:
            raise ImportError("pyarrow or pandas required: pip install grandjury[parquet]")

    def to_csv(self, path: str) -> None:
        """Export to CSV file. Collects all pages first."""
        self.fetch_all()
        try:
            self.to_pandas().to_csv(path, index=False)
            return
        except ImportError:
            pass
        # Fallback: stdlib csv
        import csv
        if not self.data:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)

    def to_json(self, path: Optional[str] = None) -> Optional[str]:
        """Export to JSON. Collects all pages first. If path given, writes file. Otherwise returns string."""
        self.fetch_all()
        import json
        out = json.dumps(self.data, indent=2, default=str)
        if path:
            with open(path, "w") as f:
                f.write(out)
            return None
        return out
