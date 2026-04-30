#!/bin/bash
set -euo pipefail

DOMAIN="${WOKLY_DOMAIN:-menu.agentlens.net}"
REGION="${REGION:-us-west1}"
SERVICE="wokly"

echo "Mapping $DOMAIN → Cloud Run service '$SERVICE' ..."
gcloud beta run domain-mappings create \
  --service "$SERVICE" \
  --domain "$DOMAIN" \
  --region "$REGION"

echo ""
echo "Cloud Run has printed the DNS record above."
echo "Add a CNAME at your DNS provider:"
echo "  $DOMAIN  CNAME  <target shown above>"
echo "TLS is provisioned automatically once DNS propagates."
