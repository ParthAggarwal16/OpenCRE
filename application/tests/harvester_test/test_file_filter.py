from application.utils.harvester.file_filter import FileFilter


def test_extension_filtering():
    file_filter = FileFilter()

    result = file_filter.filter_files(
        [
            "README.md",
            "image.png",
            "script.js",
        ]
    )

    assert result == ["README.md"]


def test_regex_filtering():
    file_filter = FileFilter()

    result = file_filter.filter_files(
        [
            ".github/workflows/test.yml",
            "docs/setup.md",
        ]
    )

    assert result == ["docs/setup.md"]


def test_combined_filtering():
    file_filter = FileFilter()

    result = file_filter.filter_files(
        [
            "README.md",
            ".github/workflows/test.yml",
            "node_modules/react/index.js",
            "docs/setup.md",
        ]
    )

    assert result == [
        "README.md",
        "docs/setup.md",
    ]
