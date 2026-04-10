#!/bin/bash
# ─── Heaven Coint — VPS Setup & Deploy Script ─────────────────
# Run on the VPS as root the FIRST time:
#   curl -sSL https://raw.githubusercontent.com/rbegacobas/heavenCoint/main/infrastructure/deploy.sh | bash
# Or copy and run manually.

set -euo pipefail

DOMAIN="heavencoint.rbegacobas.dev"
REPO="https://github.com/rbegacobas/heavenCoint.git"
APP_DIR="/opt/heavencoint"
EMAIL="rbegacobas@gmail.com"   # for Let's Encrypt notifications

echo "════════════════════════════════════════════"
echo "  Heaven Coint — Server Setup & Deploy"
echo "════════════════════════════════════════════"

# ── 1. System update ──────────────────────────────────────────
echo "[1/8] Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

# ── 2. Install Docker ─────────────────────────────────────────
echo "[2/8] Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "  Docker already installed: $(docker --version)"
fi

# ── 3. Install Docker Compose plugin ──────────────────────────
echo "[3/8] Installing Docker Compose..."
if ! docker compose version &>/dev/null; then
    apt-get install -y docker-compose-plugin
fi
echo "  $(docker compose version)"

# ── 4. Create non-root deploy user ────────────────────────────
echo "[4/8] Creating deploy user..."
if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash deploy
    usermod -aG docker deploy
    echo "  User 'deploy' created and added to docker group"
else
    echo "  User 'deploy' already exists"
fi

# ── 5. Clone / update repo ────────────────────────────────────
echo "[5/8] Cloning repository..."
if [ -d "$APP_DIR/.git" ]; then
    echo "  Repo exists, pulling latest..."
    cd "$APP_DIR" && git pull origin main
else
    git clone "$REPO" "$APP_DIR"
fi
chown -R deploy:deploy "$APP_DIR"

# ── 6. Copy .env.production ───────────────────────────────────
echo "[6/8] Setting up environment..."
if [ ! -f "$APP_DIR/.env.production" ]; then
    echo "  ⚠  .env.production not found in $APP_DIR"
    echo "  Copy it manually: scp .env.production root@$DOMAIN:$APP_DIR/.env.production"
    echo "  Then re-run: cd $APP_DIR && docker compose -f docker-compose.prod.yml up -d"
    exit 1
fi

cd "$APP_DIR"

# ── 7. SSL Certificate (Let's Encrypt) ────────────────────────
echo "[7/8] Setting up SSL certificate..."

# Start nginx with HTTP-only config first for ACME challenge
docker compose -f docker-compose.prod.yml --env-file .env.production up -d nginx certbot

sleep 5

# Check if cert already exists
if [ ! -f "/var/lib/docker/volumes/heavencoint_certbot-certs/_data/live/$DOMAIN/fullchain.pem" ]; then
    echo "  Requesting Let's Encrypt certificate..."
    docker compose -f docker-compose.prod.yml --env-file .env.production run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
    echo "  ✅ Certificate obtained!"
else
    echo "  Certificate already exists, skipping..."
fi

# ── 8. Launch all services ────────────────────────────────────
echo "[8/8] Launching all services..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

echo ""
echo "════════════════════════════════════════════"
echo "  ✅ Deploy complete!"
echo "  🌐 https://$DOMAIN"
echo ""
echo "  Useful commands:"
echo "  docker compose -f docker-compose.prod.yml ps"
echo "  docker compose -f docker-compose.prod.yml logs -f backend"
echo "  docker compose -f docker-compose.prod.yml logs -f frontend"
echo "════════════════════════════════════════════"
