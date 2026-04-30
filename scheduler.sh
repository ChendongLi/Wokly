#!/bin/bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-agentlens-489006}"
REGION="${REGION:-us-west1}"
SERVICE_URL="https://menu.agentlens.net"

echo "Creating Cloud Scheduler job 'wokly-weekly-gen' ..."
gcloud scheduler jobs create http wokly-weekly-gen \
  --project "$PROJECT_ID" \
  --location "$REGION" \
  --schedule "0 19 * * 5" \
  --uri "$SERVICE_URL/api/generate" \
  --http-method POST \
  --time-zone "America/Los_Angeles" \
  --attempt-deadline 300s \
  --max-retry-attempts 3 \
  --message-body '{"source": "scheduler"}'

echo ""
echo "Scheduler job created. Fires every Friday at 11:00 AM PST (19:00 UTC)."
echo "To trigger manually: gcloud scheduler jobs run wokly-weekly-gen --location $REGION"
