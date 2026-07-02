from pathlib import Path
import unittest

from application.utils.harvester.config_loader import (
    load_repo_config,
)
from application.utils.harvester.repos_validator import (
    RepositoryValidationError,
    validate_repositories,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class RepositoriesValidatorTests(unittest.TestCase):
    def test_duplicate_repository_ids(self):
        config_path = FIXTURES_DIR / "duplicate_repo_ids.yaml"

        config = load_repo_config(config_path)

        with self.assertRaisesRegex(
            RepositoryValidationError,
            "Duplicate repository id",
        ):
            validate_repositories(config)

    def test_duplicate_repositories(self):
        config_path = FIXTURES_DIR / "duplicate_repositories.yaml"

        config = load_repo_config(config_path)

        with self.assertRaisesRegex(
            RepositoryValidationError,
            "Duplicate repository detected",
        ):
            validate_repositories(config)


if __name__ == "__main__":
    unittest.main()
