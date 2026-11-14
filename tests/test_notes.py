import json

import boto3
import pytest

from notes import NoteExists


def test_create_and_read_back(service):
    note_id = service.create_note("groceries", "milk, eggs, tea")
    note = service.get_note(note_id)
    assert note == {"id": note_id, "title": "groceries", "body": "milk, eggs, tea"}


def test_duplicate_id_is_rejected(service):
    service.create_note("first", "hello", note_id="same-id")
    with pytest.raises(NoteExists):
        service.create_note("second", "world", note_id="same-id")


def test_create_publishes_an_event(service):
    note_id = service.create_note("todo", "write the article")
    msgs = boto3.client("sqs").receive_message(
        QueueUrl=service.queue_url, WaitTimeSeconds=1
    )["Messages"]
    assert json.loads(msgs[0]["Body"]) == {"event": "note_created", "id": note_id}


def test_missing_note_returns_none(service):
    assert service.get_note("does-not-exist") is None
