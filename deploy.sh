#!/bin/bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-agentlens-489006}"
REGION="${REGION:-us-west1}"
SERVICE="wokly"
REPO="wokly-repo"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE"

echo "Building $IMAGE ..."
docker build -t "$IMAGE" .

echo "Pushing $IMAGE ..."
docker push "$IMAGE"

echo "Deploying to Cloud Run ($REGION) ..."
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --min-instances 0 \
  --max-instances 2 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-secrets "DATABASE_URL=wokly-neon-url:latest" \
  --set-secrets "OPENAI_API_KEY=wokly-openai-key:latest" \
  --set-env-vars "AI_PROVIDER=openai" \
  --allow-unauthenticated

echo "Done. Run ./domain.sh to map menu.agentlens.net."
