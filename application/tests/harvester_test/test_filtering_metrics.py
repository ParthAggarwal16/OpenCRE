from application.utils.harvester.filtering_metrics import (
    FilteringMetricsCollector,
)


def test_filtering_metrics_collection():
    collector = FilteringMetricsCollector()

    collector.record_retained()
    collector.record_retained()
    collector.record_filtered()

    metrics = collector.build()

    assert metrics.total_files == 3
    assert metrics.retained_files == 2
    assert metrics.filtered_files == 1
