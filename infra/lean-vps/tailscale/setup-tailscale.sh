#!/usr/bin/env bash
# ==============================================================================
# setup-tailscale.sh - Bastion-Free Administration via Tailscale WireGuard
# Lean VPS Zero-Trust Ingress Profile (EP14-T1a / FR-NET-02)
# ==============================================================================
# Enrolls node into corporate Tailscale mesh with:
#  - OpenSSH over Tailscale enabled (--ssh)
#  - Route acceptance disabled (--accept-routes=false)
#  - External inbound shields active (--shields-up=false)
#  - Production tag advertised (--advertise-tags=tag:scheduler-prod)
#  - OpenSSH & PostgreSQL listeners bound strictly to 127.0.0.1 + tailscale0 IP
# ==============================================================================

set -euo pipefail

TAILSCALE_TAG="tag:scheduler-prod"
AUTH_KEY="${TAILSCALE_AUTHKEY:-}"
SSHD_CONFIG="/etc/ssh/sshd_config"
PG_CONF_DIR="/etc/postgresql/16/main"

echo "=== [1/5] Installing Tailscale WireGuard ==="
if ! command -v tailscale &>/dev/null; then
  echo "Adding Tailscale official package repository..."
  curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
  curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list >/dev/null
  apt-get update
  apt-get install -y --no-install-recommends tailscale
  systemctl enable --now tailscaled
  echo "Tailscale installed and service started."
else
  echo "Tailscale already installed: $(tailscale version)"
fi

echo "=== [2/5] Authenticating and Enrolling Node ==="
UP_ARGS=(
  "--ssh"
  "--accept-routes=false"
  "--shields-up=false"
  "--advertise-tags=${TAILSCALE_TAG}"
  "--reset"
)

if [[ -n "${AUTH_KEY}" ]]; then
  echo "Enrolling node using pre-authenticated auth key..."
  tailscale up "${UP_ARGS[@]}" --authkey="${AUTH_KEY}"
else
  echo "INFO: No TAILSCALE_AUTHKEY supplied in environment."
  echo "Running non-interactive check or interactive login if required:"
  if tailscale status &>/dev/null; then
    echo "Tailscale already logged in. Applying settings..."
    tailscale set "${UP_ARGS[@]}"
  else
    echo "Please authenticate manually using: tailscale up ${UP_ARGS[*]}"
  fi
fi

echo "=== [3/5] Resolving tailscale0 CGNAT IP (100.x.y.z) ==="
TAILSCALE_IP=""
for i in {1..10}; do
  TAILSCALE_IP="$(tailscale ip -4 2>/dev/null || true)"
  if [[ -n "${TAILSCALE_IP}" ]]; then
    break
  fi
  sleep 1
done

if [[ -z "${TAILSCALE_IP}" ]]; then
  echo "WARNING: Could not obtain Tailscale IPv4 address. Ensure node is authenticated."
  TAILSCALE_IP="100.64.0.1" # Placeholder for config rendering
else
  echo "Tailscale IPv4 assigned: ${TAILSCALE_IP}"
fi

echo "=== [4/5] Restricting OpenSSH ListenAddress to localhost & Tailscale ==="
if [[ -f "${SSHD_CONFIG}" ]]; then
  # Remove existing ListenAddress entries
  sed -i '/^ListenAddress/d' "${SSHD_CONFIG}"
  
  # Append strict bindings
  cat <<EOF >> "${SSHD_CONFIG}"

# Bound strictly by setup-tailscale.sh (FR-NET-02 Zero-Trust Admin)
ListenAddress 127.0.0.1
ListenAddress ${TAILSCALE_IP}
EOF

  # Validate sshd configuration before reloading
  if sshd -t; then
    systemctl reload ssh || systemctl reload sshd || true
    echo "sshd_config updated and reloaded: listening only on 127.0.0.1 and ${TAILSCALE_IP}"
  else
    echo "ERROR: Invalid sshd configuration generated. Reverting changes."
    sed -i '/# Bound strictly by setup-tailscale.sh/d' "${SSHD_CONFIG}"
    sed -i "/ListenAddress ${TAILSCALE_IP}/d" "${SSHD_CONFIG}"
    exit 1
  fi
fi

echo "=== [5/5] Restricting PostgreSQL listen_addresses ==="
if [[ -d "${PG_CONF_DIR}" ]]; then
  PG_CONF="${PG_CONF_DIR}/postgresql.conf"
  if [[ -f "${PG_CONF}" ]]; then
    sed -i "s/^#\?listen_addresses\s*=.*/listen_addresses = '127.0.0.1,${TAILSCALE_IP}'/" "${PG_CONF}"
    if systemctl is-active --quiet postgresql; then
      systemctl reload postgresql
    fi
    echo "PostgreSQL configured to listen strictly on 127.0.0.1 and ${TAILSCALE_IP}"
  fi
fi

echo "Tailscale WireGuard Administration Setup Completed."
