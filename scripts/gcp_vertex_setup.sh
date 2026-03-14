#!/usr/bin/env bash

set -e

echo "============================================================"
echo "  Google Cloud Vertex AI Setup for Codomyrmex"
echo "============================================================"
echo ""

if ! command -v gcloud &> /dev/null; then
    echo "[!] Google Cloud CLI (gcloud) is not installed."
    echo "    Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "[✔] gcloud CLI found."

echo "Checking Application Default Credentials..."
if ! gcloud auth application-default print-access-token &> /dev/null; then
    echo "[*] Credentials not found or expired. Prompting for login..."
    gcloud auth application-default login
else
    echo "[✔] Application Default Credentials are valid."
fi

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$PROJECT_ID" ]; then
    echo "[!] No default GCP project is set."
    read -p "Enter your GCP Project ID to use for Vertex AI: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
else
    echo "[✔] Active GCP Project: $PROJECT_ID"
fi

echo "Ensuring Vertex AI API is enabled for project $PROJECT_ID..."
gcloud services enable aiplatform.googleapis.com --project="$PROJECT_ID"

echo ""
echo "============================================================"
echo " Vertex AI setup complete. "
echo " You can now use Gemini Advanced via Vertex AI in Codomyrmex."
echo " In your Codomyrmex config, ensure you set:"
echo "   use_vertex_ai: true"
echo "   vertex_project: \"$PROJECT_ID\""
echo "   vertex_location: \"us-central1\" (or your preferred region)"
echo "============================================================"
