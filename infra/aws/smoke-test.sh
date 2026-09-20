#!/usr/bin/env bash
set -euo pipefail
url="${1:?Usage: smoke-test.sh APPLICATION_URL}"
url="${url%/}"
ready=$(mktemp)
api=$(mktemp)
trap 'rm -f "$ready" "$api"' EXIT
test "$(curl --fail --silent --show-error --max-time 30 --output "$ready" --write-out '%{http_code}' "$url/ready")" = 200
jq -e '.status == "ready"' "$ready" >/dev/null
test "$(curl --fail --silent --show-error --max-time 30 --output "$api" --write-out '%{http_code}' "$url/api/v1/exercises")" = 200
jq -e 'type == "array" and length > 0' "$api" >/dev/null
echo "CloudFront readiness and proxied exercises API passed. Authenticated admin verification is still required."
