"""A tiny notes service: body in S3, metadata in DynamoDB, an event on SQS."""
import json
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


class NoteExists(Exception):
    pass


class NotesService:
    def __init__(self, bucket, table, queue_url):
        self.bucket = bucket
        self.table = table
        self.queue_url = queue_url
        self.s3 = boto3.client("s3")
        self.ddb = boto3.client("dynamodb")
        self.sqs = boto3.client("sqs")

    def create_note(self, title, body, note_id=None):
        note_id = note_id or str(uuid.uuid4())
        key = f"notes/{note_id}.txt"
        try:
            self.ddb.put_item(
                TableName=self.table,
                Item={
                    "id": {"S": note_id},
                    "title": {"S": title},
                    "s3_key": {"S": key},
                    "created_at": {"S": datetime.now(timezone.utc).isoformat()},
                },
                ConditionExpression="attribute_not_exists(id)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise NoteExists(note_id) from e
            raise
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=body.encode())
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps({"event": "note_created", "id": note_id}),
        )
        return note_id

    def get_note(self, note_id):
        item = self.ddb.get_item(TableName=self.table, Key={"id": {"S": note_id}}).get("Item")
        if not item:
            return None
        obj = self.s3.get_object(Bucket=self.bucket, Key=item["s3_key"]["S"])
        return {"id": note_id, "title": item["title"]["S"], "body": obj["Body"].read().decode()}


def create_resources(prefix):
    """Create the bucket, table and queue the service needs. Returns their names."""
    s3, ddb, sqs = boto3.client("s3"), boto3.client("dynamodb"), boto3.client("sqs")
    bucket, table = f"{prefix}-notes", f"{prefix}-notes"
    s3.create_bucket(Bucket=bucket)
    ddb.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )
    ddb.get_waiter("table_exists").wait(TableName=table)
    queue_url = sqs.create_queue(QueueName=f"{prefix}-note-events")["QueueUrl"]
    return bucket, table, queue_url
