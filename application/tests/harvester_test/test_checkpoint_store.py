from datetime import datetime
from pathlib import Path

from application.utils.harvester.checkpoint_store import CheckpointStore
from application.utils.harvester.models import RepositoryCheckpoint


def test_save_and_load_checkpoint(tmp_path: Path):
    store = CheckpointStore(tmp_path / "checkpoints.json")

    checkpoint = RepositoryCheckpoint(
        repository_id="owasp-asvs",
        last_processed_commit="abc123",
        updated_at=datetime.now(),
    )

    store.save(checkpoint)

    loaded = store.load("owasp-asvs")

    assert loaded is not None
    assert loaded.last_processed_commit == "abc123"
