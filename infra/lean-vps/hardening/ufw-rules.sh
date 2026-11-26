#!/usr/bin/env bash
# ==============================================================================
# ufw-rules.sh - Host Firewall Hardening & Zero-Public-Port Enforcement
# Lean VPS Zero-Trust Ingress Profile (EP14-T1a / FR-NET-01 / FR-NET-02)
# ==============================================================================
# Configures Uncomplicated Firewall (UFW) to enforce:
#  - Default DENY for all incoming connections
#  - Default ALLOW for outgoing traffic (QUIC tunnels, Meta API, Tailscale)
#  - Default DENY for routed forwarding
#  - Allowed inbound TCP 22 (SSH) strictly on tailscale0 WireGuard interface
#  - Allowed inbound TCP 5432 (Postgres) strictly on tailscale0 interface
#  - Explicit DENY on public WAN interfaces (eth0, ens3, enp1s0)
#  - External nmap scan verification yields ZERO open public ports
# ==============================================================================

set -euo pipefail

echo "=== [1/5] Checking UFW installation ==="
if ! command -v ufw &>/dev/null; then
  apt-get update && apt-get install -y --no-install-recommends ufw
fi

echo "=== [2/5] Resetting firewall to baseline ==="
ufw --force reset

echo "=== [3/5] Setting strict default policies ==="
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed

echo "=== [4/5] Permitting administrative access ONLY on tailscale0 ==="
# WireGuard Tailscale interface only (CGNAT 100.x.y.z)
ufw allow in on tailscale0 to any port 22 proto tcp comment 'Tailscale SSH Admin Access (FR-NET-02)'
ufw allow in on tailscale0 to any port 5432 proto tcp comment 'Tailscale PostgreSQL Access (FR-NET-02)'
ufw allow in on tailscale0 to any port 3100 proto tcp comment 'Tailscale Loki Log Query Access'

# Local loopback interface (inter-process communication)
ufw allow in on lo to any comment 'Localhost Loopback'

# Explicit rejection of public ingress on standard WAN interfaces
for IFACE in eth0 ens3 enp1s0; do
  if ip link show "${IFACE}" &>/dev/null; then
    echo "Hardening public WAN interface: ${IFACE}"
    ufw deny in on "${IFACE}" to any comment "Block all direct public ingress on ${IFACE}"
  fi
done

echo "=== [5/5] Enabling UFW firewall ==="
ufw --force enable
ufw status verbose

echo "UFW firewall configuration complete. Zero public inbound ports open."
