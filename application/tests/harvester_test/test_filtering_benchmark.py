from application.utils.harvester.file_filter import FileFilter
from application.utils.harvester.models import FilteringMetrics


def test_filtering_benchmark():
    files = [
        "README.md",
        ".github/workflows/ci.yml",
        "docs/guide.md",
        "image.png",
        "notes.txt",
        "package-lock.json",
    ]

    file_filter = FileFilter()

    retained_files = file_filter.filter_files(files)

    metrics = FilteringMetrics(
        total_files=len(files),
        retained_files=len(retained_files),
        filtered_files=len(files) - len(retained_files),
    )

    assert metrics.total_files == 6
    assert metrics.retained_files == 3
    assert metrics.filtered_files == 3
