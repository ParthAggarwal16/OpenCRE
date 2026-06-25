from dataclasses import dataclass

from .file_filter import FileFilter
from .filtering_metrics import FilteringMetrics


@dataclass
class FilteringBenchmarkResult:
    total_files: int
    retained_files: int
    filtered_files: int
    retention_rate: float
    filtering_rate: float


class FilteringBenchmark:
    def __init__(
        self,
        file_filter: FileFilter,
        metrics: FilteringMetrics,
    ):
        self.file_filter = file_filter
        self.metrics = metrics

    def run(self, file_paths: list[str]) -> FilteringBenchmarkResult:
        retained = self.file_filter.filter_files(file_paths)

        total = len(file_paths)

        return FilteringBenchmarkResult(
            total_files=total,
            retained_files=self.metrics.retained_files,
            filtered_files=self.metrics.filtered_files,
            retention_rate=(self.metrics.retained_files / total if total else 0.0),
            filtering_rate=(self.metrics.filtered_files / total if total else 0.0),
        )
