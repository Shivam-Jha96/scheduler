#!/usr/bin/env bash
# ==============================================================================
# setup-tunnel.sh - Cloudflare Dual Redundant Zero-Trust Tunnel Setup
# Lean VPS Zero-Trust Ingress Profile (EP14-T1a / R-EP14-01 / FR-NET-01)
# ==============================================================================
# Idempotent provisioning script for installing cloudflared, configuring
# dual tunnel replicas (cloudflared-1 and cloudflared-2), and verifying
# health readiness on localhost. Zero public inbound ports opened.
# ==============================================================================

set -euo pipefail

CLOUDFLARED_VERSION="2024.11.0"
CONFIG_DIR="/etc/cloudflared"
SYSTEMD_DIR="/etc/systemd/system"
USER="cloudflared"
GROUP="cloudflared"

echo "=== [1/6] Installing cloudflared daemon ==="
if ! command -v cloudflared &>/dev/null; then
  echo "Downloading cloudflared binary (v${CLOUDFLARED_VERSION})..."
  ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
  case "${ARCH}" in
    amd64|x86_64) BIN_ARCH="amd64" ;;
    arm64|aarch64) BIN_ARCH="arm64" ;;
    *) echo "Unsupported architecture: ${ARCH}"; exit 1 ;;
  esac

  curl -fsSL "https://github.com/cloudflare/cloudflared/releases/download/${CLOUDFLARED_VERSION}/cloudflared-linux-${BIN_ARCH}" \
    -o /usr/local/bin/cloudflared
  chmod +x /usr/local/bin/cloudflared
  echo "cloudflared installed successfully: $(cloudflared --version)"
else
  echo "cloudflared already installed: $(cloudflared --version)"
fi

echo "=== [2/6] Ensuring unprivileged user and group ==="
if ! id "${USER}" &>/dev/null; then
  groupadd -r "${GROUP}" || true
  useradd -r -g "${GROUP}" -s /usr/sbin/nologin -d "${CONFIG_DIR}" -c "Cloudflare Tunnel Service" "${USER}"
  echo "Created system user: ${USER}"
fi

mkdir -p "${CONFIG_DIR}"
chmod 750 "${CONFIG_DIR}"
chown -R "${USER}:${GROUP}" "${CONFIG_DIR}"

echo "=== [3/6] Generating tunnel configuration from template ==="
TEMPLATE_FILE="$(dirname "$0")/config.yml.template"

if [[ ! -f "${CONFIG_DIR}/config.yml" ]]; then
  if [[ -f "${TEMPLATE_FILE}" ]]; then
    TUNNEL_ID="${TUNNEL_ID:-schedulerbot-vps-tunnel}"
    TUNNEL_HOSTNAME="${TUNNEL_HOSTNAME:-api.schedulerbot.internal}"

    sed -e "s/\${TUNNEL_ID}/${TUNNEL_ID}/g" \
        -e "s/\${TUNNEL_HOSTNAME}/${TUNNEL_HOSTNAME}/g" \
        "${TEMPLATE_FILE}" > "${CONFIG_DIR}/config.yml"
    
    # Generate replica configuration with distinct metrics port (2001) for cloudflared-2
    sed -e "s/\${TUNNEL_ID}/${TUNNEL_ID}/g" \
        -e "s/\${TUNNEL_HOSTNAME}/${TUNNEL_HOSTNAME}/g" \
        -e "s/metrics: 127.0.0.1:2000/metrics: 127.0.0.1:2001/g" \
        "${TEMPLATE_FILE}" > "${CONFIG_DIR}/config-replica.yml"

    chown "${USER}:${GROUP}" "${CONFIG_DIR}/config.yml" "${CONFIG_DIR}/config-replica.yml"
    chmod 640 "${CONFIG_DIR}/config.yml" "${CONFIG_DIR}/config-replica.yml"
    echo "Configuration written to ${CONFIG_DIR}/config.yml and config-replica.yml"
  else
    echo "Warning: config.yml.template not found at ${TEMPLATE_FILE}"
  fi
else
  echo "Existing tunnel configuration found at ${CONFIG_DIR}/config.yml"
fi

echo "=== [4/6] Installing systemd units for dual redundancy ==="
SERVICE_FILE="$(dirname "$0")/cloudflared.service"

# Primary Tunnel Instance
cp "${SERVICE_FILE}" "${SYSTEMD_DIR}/cloudflared.service"

# Secondary Redundant Tunnel Instance
sed -e 's/config.yml/config-replica.yml/g' \
    -e 's/Zero-Trust Ingress Daemon/Zero-Trust Ingress Daemon (Replica 2)/g' \
    "${SERVICE_FILE}" > "${SYSTEMD_DIR}/cloudflared-replica.service"

systemctl daemon-reload
echo "Systemd service definitions deployed: cloudflared.service & cloudflared-replica.service"

echo "=== [5/6] Enabling and starting cloudflared services ==="
systemctl enable cloudflared.service || true
systemctl enable cloudflared-replica.service || true

if [[ -f "${CONFIG_DIR}/credentials.json" ]] || [[ -f "${CONFIG_DIR}/${TUNNEL_ID:-default}.json" ]]; then
  systemctl restart cloudflared.service
  systemctl restart cloudflared-replica.service
  echo "Services started."
else
  echo "NOTICE: Cloudflare credentials not present in ${CONFIG_DIR}."
  echo "Place credentials json in ${CONFIG_DIR}/<TUNNEL_ID>.json and run:"
  echo "  systemctl restart cloudflared cloudflared-replica"
fi

echo "=== [6/6] Verifying Local Metrics Readiness Probe ==="
# Attempt health query against localhost:2000
if curl -sf http://127.0.0.1:2000/ready >/dev/null 2>&1; then
  echo "PASS: Primary tunnel metrics probe (127.0.0.1:2000/ready) is responding."
else
  echo "INFO: Primary tunnel metrics probe (127.0.0.1:2000/ready) waiting for credentials/connect."
fi

echo "Cloudflare Tunnel Setup Completed Successfully."
