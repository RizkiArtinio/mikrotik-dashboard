#!/bin/bash
# One-time bootstrap for the first Let's Encrypt certificate.
# nginx's config requires a certificate to exist before it can even start the
# HTTPS server block, but certbot needs nginx running (for the HTTP-01
# webroot challenge) to issue one. This script breaks that chicken-and-egg
# problem by creating a temporary self-signed cert, starting nginx, then
# swapping in the real certificate.
#
# Run once from the docker/ directory: ./init-letsencrypt.sh
set -e

cd "$(dirname "$0")"
ENV_FILE="../.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE — copy .env.example to .env and fill it in first."
  exit 1
fi

# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a

if [ -z "$DOMAIN" ] || [ -z "$CERTBOT_EMAIL" ]; then
  echo "DOMAIN and CERTBOT_EMAIL must be set in .env"
  exit 1
fi

echo "==> Creating temporary self-signed certificate for $DOMAIN"
docker compose run --rm --entrypoint "\
  mkdir -p /etc/letsencrypt/live/$DOMAIN && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj '/CN=localhost'" certbot

echo "==> Starting nginx"
docker compose up -d nginx

echo "==> Requesting real certificate from Let's Encrypt"
docker compose run --rm --entrypoint "\
  rm -rf /etc/letsencrypt/live/$DOMAIN /etc/letsencrypt/archive/$DOMAIN /etc/letsencrypt/renewal/$DOMAIN.conf && \
  certbot certonly --webroot -w /var/www/certbot \
    -d $DOMAIN --email $CERTBOT_EMAIL --agree-tos --no-eff-email" certbot

echo "==> Reloading nginx with the real certificate"
docker compose exec nginx nginx -s reload

echo "Done. $DOMAIN is now served over HTTPS with a valid Let's Encrypt certificate."
