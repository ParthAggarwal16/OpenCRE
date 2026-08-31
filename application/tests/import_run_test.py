"""Tests for import run metadata (Step 6)."""

import json
import unittest
from datetime import datetime, timezone

from application import create_app, sqla
from application.database import db
from application.utils.harvester.models import (
    IngestChunkRecord,
    Locator,
    SourceInfo,
    SpanInfo,
)


class TestImportRun(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(mode="test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        sqla.create_all()

    def tearDown(self) -> None:
        sqla.session.remove()
        sqla.drop_all()
        self.app_context.pop()

    def test_create_import_run(self) -> None:
        run = db.create_import_run(source="test_source", version="1.0")
        self.assertIsNotNone(run.id)
        self.assertEqual(run.source, "test_source")
        self.assertEqual(run.version, "1.0")
        self.assertIsNotNone(run.created_at)

    def test_get_latest_import_run(self) -> None:
        db.create_import_run(source="test_source", version="1.0")
        run2 = db.create_import_run(source="test_source", version="2.0")
        latest = db.get_latest_import_run("test_source")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.id, run2.id)
        self.assertEqual(latest.version, "2.0")

    def test_create_artifact_ingest_event_and_chunk(self) -> None:
        run = db.create_import_run(source="artifact_ingest", version="1.0")
        observed_at = datetime.now(timezone.utc)

        event = db.create_artifact_ingest_event(
            run_id=run.id,
            artifact_id="artifact-1",
            harvest_mode="backfill",
            event_type="discovered",
            source_json={"uri": "https://example.com/source"},
            locator_json={"path": "/tmp/source"},
            artifact_json={"id": "artifact-1"},
            harvest_json={"status": "ok"},
            observed_at=observed_at,
        )

        self.assertIsNotNone(event.id)
        self.assertEqual(event.run_id, run.id)
        self.assertEqual(event.artifact_id, "artifact-1")
        self.assertEqual(
            json.loads(event.source_json), {"uri": "https://example.com/source"}
        )
        self.assertEqual(json.loads(event.locator_json), {"path": "/tmp/source"})
        self.assertEqual(json.loads(event.artifact_json), {"id": "artifact-1"})
        self.assertEqual(json.loads(event.harvest_json), {"status": "ok"})
        self.assertEqual(
            event.observed_at.replace(tzinfo=None),
            observed_at.astimezone(timezone.utc).replace(tzinfo=None),
        )
        self.assertIsNotNone(event.created_at)

        chunk = db.create_ingest_chunk(
            artifact_event_id=event.id,
            chunk_id="chunk-1",
            text="hello world",
            char_count=11,
            span_json={"start": 0, "end": 11},
            delta_json={"op": "add"},
        )

        self.assertIsNotNone(chunk.id)
        self.assertEqual(chunk.artifact_event_id, event.id)
        self.assertEqual(chunk.chunk_id, "chunk-1")
        self.assertEqual(chunk.text, "hello world")
        self.assertEqual(chunk.char_count, 11)
        self.assertEqual(json.loads(chunk.span_json), {"start": 0, "end": 11})
        self.assertEqual(json.loads(chunk.delta_json), {"op": "add"})
        self.assertIsNotNone(chunk.created_at)

    def test_persist_complete_ingest_chunk_records(self) -> None:
        run = db.create_import_run(source="artifact_ingest", version="1.0")
        source = SourceInfo(
            type="github",
            repository="OWASP/ASVS",
            commit_sha="abc123",
            committed_at=None,
        )
        locator = Locator(
            kind="repo_path",
            id="README.md",
            path="README.md",
        )
        records = [
            IngestChunkRecord(
                schema_version="0.2.0",
                chunk_id="chk:one",
                artifact_id="art:OWASP/ASVS:README.md",
                pipeline_run_id=run.id,
                text="first chunk",
                span=SpanInfo(
                    heading_path=["Introduction"],
                    start_line=1,
                    end_line=1,
                    index=0,
                    total=2,
                    start_char_idx=0,
                    end_char_idx=11,
                ),
                source=source,
                locator=locator,
            ),
            IngestChunkRecord(
                schema_version="0.2.0",
                chunk_id="chk:two",
                artifact_id="art:OWASP/ASVS:README.md",
                pipeline_run_id=run.id,
                text="second chunk",
                span=SpanInfo(
                    heading_path=["Introduction"],
                    start_line=2,
                    end_line=2,
                    index=1,
                    total=2,
                    start_char_idx=12,
                    end_char_idx=25,
                ),
                source=source,
                locator=locator,
            ),
        ]

        event, chunks = db.persist_ingest_chunk_records(
            records=records,
            harvest_mode="backfill",
            event_type="discovered",
            artifact_json={"id": records[0].artifact_id},
            harvest_json={"status": "ok"},
            observed_at=datetime.now(timezone.utc),
        )

        self.assertEqual(event.run_id, run.id)
        self.assertEqual(json.loads(event.source_json)["repository"], "OWASP/ASVS")
        self.assertEqual(json.loads(event.locator_json)["path"], "README.md")
        self.assertEqual(len(chunks), 2)
        self.assertEqual([chunk.chunk_id for chunk in chunks], ["chk:one", "chk:two"])
        self.assertEqual(json.loads(chunks[0].span_json)["index"], 0)
