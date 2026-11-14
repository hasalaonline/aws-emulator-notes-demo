import uuid

import boto3
import pytest

from notes import NotesService, create_resources

EMULATOR_ACCOUNT = "000000000000"


@pytest.fixture(scope="session", autouse=True)
def only_the_emulator():
    """Refuse to run if these credentials point at a real AWS account."""
    account = boto3.client("sts").get_caller_identity()["Account"]
    if account != EMULATOR_ACCOUNT:
        pytest.exit(f"Not the emulator (account {account}). Source scripts/emu-env.sh first.")


@pytest.fixture(scope="session")
def resources():
    # A new table starts in CREATING, like on AWS, so create it once per run.
    return create_resources(f"t-{uuid.uuid4().hex[:8]}")


@pytest.fixture
def service(resources):
    bucket, table, _ = resources
    # A fresh queue per test keeps each test's messages to itself.
    queue_url = boto3.client("sqs").create_queue(QueueName=f"q-{uuid.uuid4().hex[:8]}")["QueueUrl"]
    return NotesService(bucket, table, queue_url)
