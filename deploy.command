#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.command — One-click SSH Deployment to CloudPanel Server
# Double-click this file in Finder or run `./deploy.command` in Terminal.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

cd "$(dirname "$0")"

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

SERVER_IP="${SERVER_IP:-46.225.123.125}"
SITE_USER="${SITE_USER:-roland-digital-time}"
SITE_PASSWORD="${SITE_PASSWORD:-7CvecmzsRvildcNW3J74}"
SITE_DOMAIN="${SITE_DOMAIN:-time-series.roland-digital.de}"
SITE_PORT="${SITE_PORT:-8091}"
SSH_PORT="${SSH_PORT:-22}"

REMOTE_PATH="/home/$SITE_USER/htdocs/$SITE_DOMAIN"

echo "================================================================="
echo "🚀 Deploying Lake Time-Series Forecasting to CloudPanel Server"
echo "   Server IP:   $SERVER_IP"
echo "   SSH Port:    $SSH_PORT"
echo "   Site User:   $SITE_USER"
echo "   Domain:      $SITE_DOMAIN"
echo "   App Port:    $SITE_PORT"
echo "================================================================="

command -v sshpass >/dev/null || { echo "❌ Error: sshpass is required."; exit 1; }
command -v rsync >/dev/null || { echo "❌ Error: rsync is required."; exit 1; }

echo "📡 Step 1: Connecting to server over SSH..."
sshpass -p "$SITE_PASSWORD" ssh \
  -p "$SSH_PORT" \
  -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -o ConnectTimeout=10 \
  "$SITE_USER@$SERVER_IP" \
  "mkdir -p '$REMOTE_PATH'"

echo "📦 Step 2: Uploading project files via rsync..."
sshpass -p "$SITE_PASSWORD" rsync -az --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.DS_Store' \
  --exclude='logs/*.json' \
  --exclude='.env' \
  -e "ssh -p $SSH_PORT -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no" \
  ./ "$SITE_USER@$SERVER_IP:$REMOTE_PATH/"

echo "⚙️ Step 3: Setting up Python environment & installing dependencies..."
sshpass -p "$SITE_PASSWORD" ssh \
  -p "$SSH_PORT" \
  -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  "$SITE_USER@$SERVER_IP" "
    set -e
    cd '$REMOTE_PATH'

    # Ensure pip and virtualenv exist
    if [ ! -f ~/.local/bin/virtualenv ]; then
      rm -f /tmp/get-pip_$SITE_USER.py
      curl -sSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip_$SITE_USER.py
      python3 /tmp/get-pip_$SITE_USER.py --user --break-system-packages
      ~/.local/bin/pip install --user virtualenv --break-system-packages
    fi

    # Clean incomplete venv if missing pip
    if [ ! -f venv/bin/pip ]; then
      rm -rf venv
      ~/.local/bin/virtualenv venv
    fi

    # Install / update requirements
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt

    # Stop previous instance owned by this user
    pkill -u $(whoami) -f 'streamlit run app.py' 2>/dev/null || true
    sleep 1

    # Launch Streamlit in background with reverse proxy compatibility
    echo "⚡ Starting Streamlit server on port $SITE_PORT..."
    nohup venv/bin/streamlit run app.py \
      --server.port=$SITE_PORT \
      --server.address=0.0.0.0 \
      --server.headless=true \
      --server.enableCORS=false \
      --server.enableXsrfProtection=false </dev/null > app.log 2>&1 & disown
    sleep 3

    # Check health
    if curl -s http://127.0.0.1:$SITE_PORT > /dev/null; then
      echo '✅ Streamlit application is live and listening on port $SITE_PORT!'
    else
      echo '⚠️ Streamlit process launched; checking log tail:'
      tail -n 10 app.log
    fi
  "

echo ""
echo "================================================================="
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "🌐 URL: https://$SITE_DOMAIN"
echo "================================================================="
