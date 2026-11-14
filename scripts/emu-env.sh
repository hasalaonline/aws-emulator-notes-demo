# Source this file to point the AWS CLI and SDKs at a local AWS Emulator.
#   source scripts/emu-env.sh        (default port 9297)
#   PORT=9300 source scripts/emu-env.sh
PORT="${PORT:-9297}"
export AWS_ENDPOINT_URL="https://127.0.0.1:${PORT}"
export AWS_SHARED_CREDENTIALS_FILE="$HOME/.aws/emulator/${PORT}/emulator_credentials"
export AWS_CONFIG_FILE="$HOME/.aws/emulator/${PORT}/config"
export AWS_CA_BUNDLE="$HOME/.aws/emulator/${PORT}/ca.pem"
export NODE_EXTRA_CA_CERTS="$HOME/.aws/emulator/${PORT}/ca.pem"
export AWS_EC2_METADATA_DISABLED=true
export AWS_DISABLE_HOST_PREFIX_INJECTION=true
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE
