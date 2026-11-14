# aws-emulator-notes-demo

A tiny notes service (S3 + DynamoDB + SQS) and a pytest suite that runs against
[AWS Emulator](https://github.com/aws/aws-emulator) on your machine and in GitHub Actions.
No AWS account needed.

## Run it (Linux)

```bash
# 1. Install and start the emulator (leave it running)
curl -fsSLo aws-emulator.deb https://downloads.aws.com/aws-emulator/packages/aws-emulator/LTS/latest/aws-emulator_amd64.deb
sudo apt-get install -y ./aws-emulator.deb
aws-emulator

# 2. In a second terminal
pip install -r requirements.txt
source scripts/emu-env.sh
pytest -v
```

On macOS or Windows, run the emulator in Docker:
see the [Docker guide](https://docs.aws.amazon.com/emulator/latest/userguide/getting-started-docker.html).

The test suite refuses to run unless `sts get-caller-identity` returns the emulator's
account `000000000000`, so it can't touch a real AWS account by accident.

## Files

- `notes.py` - the service and a `create_resources()` helper
- `tests/` - pytest suite; each test gets its own bucket, table and queue
- `scripts/emu-env.sh` - environment variables that point the CLI and SDKs at the emulator
- `.github/workflows/test.yml` - the same tests in CI
