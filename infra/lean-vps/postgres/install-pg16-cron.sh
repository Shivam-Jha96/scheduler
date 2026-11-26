#!/usr/bin/env bash
# ==============================================================================
# install-pg16-cron.sh - PostgreSQL 16 + pg_cron >= 1.5 + pgBackRest Provisioner
# Lean VPS Zero-Trust Ingress Profile (EP14-T1a / EP14-T2 / BO-05)
# ==============================================================================
# Automates:
#  1. Official PostgreSQL Apt Repository setup (PG 16 + pg_cron >= 1.5)
#  2. Installation of postgresql-16, postgresql-16-cron, pgbackrest
#  3. Extension enablement: uuid-ossp, pgcrypto, pg_cron in scheduler_db
#  4. Verification of sub-minute (10-second) cron capability
#  5. Managed Postgres Contingency: Flag & doc for pg_try_advisory_lock
# ==============================================================================

set -euo pipefail

DB_NAME="scheduler_db"
DB_USER="scheduler_app"
PG_CONF="/etc/postgresql/16/main/postgresql.conf"
PGBACKREST_CONF="/etc/pgbackrest/pgbackrest.conf"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== [1/6] Adding PostgreSQL Official APT Repository ==="
apt-get update
apt-get install -y --no-install-recommends curl ca-certificates gnupg lsb-release

if [[ ! -f /etc/apt/trusted.gpg.d/postgresql.gpg ]]; then
  curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
fi

CODENAME="$(lsb_release -cs)"
echo "deb http://apt.postgresql.org/pub/repos/apt ${CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list
apt-get update

echo "=== [2/6] Installing PostgreSQL 16, pg_cron & pgBackRest ==="
apt-get install -y --no-install-recommends \
  postgresql-16 \
  postgresql-client-16 \
  postgresql-16-cron \
  pgbackrest \
  zstd

echo "=== [3/6] Configuring postgresql.conf for pg_cron ==="
if [[ -f "${SRC_DIR}/postgresql.conf" ]]; then
  cp "${SRC_DIR}/postgresql.conf" "${PG_CONF}"
  chown postgres:postgres "${PG_CONF}"
  chmod 644 "${PG_CONF}"
else
  # Fallback inline append
  if ! grep -q "shared_preload_libraries.*pg_cron" "${PG_CONF}"; then
    echo "shared_preload_libraries = 'pg_cron'" >> "${PG_CONF}"
    echo "cron.database_name = '${DB_NAME}'" >> "${PG_CONF}"
    echo "cron.use_background_workers = on" >> "${PG_CONF}"
    echo "cron.timezone = 'UTC'" >> "${PG_CONF}"
  fi
fi

systemctl restart postgresql
systemctl enable postgresql

echo "=== [4/6] Initializing Database & Core Extensions ==="
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'\" | grep -q 1" || \
  su - postgres -c "psql -c \"CREATE DATABASE ${DB_NAME};\""

su - postgres -c "psql -d ${DB_NAME} -c \"
  CREATE EXTENSION IF NOT EXISTS \\\"uuid-ossp\\\";
  CREATE EXTENSION IF NOT EXISTS \\\"pgcrypto\\\";
  CREATE EXTENSION IF NOT EXISTS \\\"pg_cron\\\";
\""

echo "=== [5/6] Verifying pg_cron >= 1.5 Sub-Minute (10-second) Scheduling ==="
CRON_VERSION="$(su - postgres -c "psql -d ${DB_NAME} -t -c \"SELECT extversion FROM pg_extension WHERE extname = 'pg_cron';\"" | xargs)"
echo "Detected pg_cron version: ${CRON_VERSION}"

# Test 10-second interval scheduling syntax supported in pg_cron >= 1.5
su - postgres -c "psql -d ${DB_NAME} -c \"
  DO \\\$\$
  BEGIN
    -- Verify 10-second syntax capability
    PERFORM cron.schedule('sub_minute_smoke_check', '10 seconds', 'SELECT 1');
    -- Clean up test entry immediately
    PERFORM cron.unschedule('sub_minute_smoke_check');
  END
  \\\$\$;
\""
echo "PASS: Sub-minute (10-second) scheduling verified in pg_cron ${CRON_VERSION}."

echo "=== [6/6] Managed DB Contingency Flag: pg_try_advisory_lock ==="
# DigitalOcean Managed PostgreSQL and certain restricted cloud DBs disallow
# sub-minute cron resolution (< 1m) or disable background workers.
# In such environments, set:
#   ENABLE_ADVISORY_LOCK_WORKER_FALLBACK=true
# The worker daemon executes 'SELECT pg_try_advisory_lock(hashtext('scheduler_reaper_lock'))'
# to safely coordinate recurring polling at 10-second intervals without pg_cron.
export ENABLE_ADVISORY_LOCK_WORKER_FALLBACK="${ENABLE_ADVISORY_LOCK_WORKER_FALLBACK:-false}"
echo "Advisory lock contingency status: ENABLE_ADVISORY_LOCK_WORKER_FALLBACK=${ENABLE_ADVISORY_LOCK_WORKER_FALLBACK}"

echo "=== [Setup pgBackRest Local Stanza] ==="
mkdir -p /var/lib/pgbackrest /etc/pgbackrest
chown -R postgres:postgres /var/lib/pgbackrest /etc/pgbackrest
chmod 750 /var/lib/pgbackrest
if [[ -f "${SRC_DIR}/pgbackrest.conf" ]]; then
  cp "${SRC_DIR}/pgbackrest.conf" "${PGBACKREST_CONF}"
  chown postgres:postgres "${PGBACKREST_CONF}"
  chmod 640 "${PGBACKREST_CONF}"
fi

su - postgres -c "pgbackrest --stanza=${DB_NAME} stanza-create" || true
su - postgres -c "pgbackrest --stanza=${DB_NAME} check" || true

echo "PostgreSQL 16 + pg_cron + pgBackRest Provisioning Completed."
