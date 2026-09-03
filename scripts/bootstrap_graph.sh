#!/usr/bin/env bash
set -euo pipefail

# Bootstrap helper for JanusGraph schema seeding and admin mapping.
#
# Usage:
#   bash scripts/bootstrap_graph.sh <github_login>
#     - Default: applies schema (if missing) and maps <github_login> to admin.
#   bash scripts/bootstrap_graph.sh init <github_login>
#     - Same as default.
#   bash scripts/bootstrap_graph.sh schema
#     - Applies schema only.
#   bash scripts/bootstrap_graph.sh map-admin <github_login>
#     - Maps <github_login> to the admin group (ensuring user/group exist).

# Allow override via environment; default to 'janusgraph'
JANUS_CONTAINER="${JANUS_CONTAINER:-janusgraph}"
FLASK_CONTAINER="${FLASK_CONTAINER:-flask-interface}"

# Resolve repo root so the script can be run from any directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

wait_for_schema() {
  # Simple settle delay to allow schema commits to propagate.
  local delay="${1:-5}"
  echo "[bootstrap] Allowing schema to settle for ${delay}s …"
  sleep "$delay"
}

# Probe whether the basic schema and seed data exist (master user).
schema_probe() {
  require_container
  # Ensure gremlin is up to avoid false negatives
  wait_for_gremlin >/dev/null 2>&1 || return 1
  if docker exec -i "$JANUS_CONTAINER" sh -lc "printf ':remote connect tinkerpop.server conf/remote.yaml session\n:> g.V().has(\"category\",\"user\").has(\"name\",\"master\").limit(1).count()\n:> :remote close\n:exit\n' | bin/gremlin.sh 2>/dev/null | tr -d '\r' | grep -q '==>1'"; then
    echo "EXISTS"
  else
    echo "MISSING"
  fi
}

# Wait until gremlin server in janusgraph container accepts connections
wait_for_gremlin() {
  local tries=${1:-60}
  local delay=${2:-2}
  echo "[bootstrap] Waiting for JanusGraph Gremlin server …"
  for i in $(seq 1 "$tries"); do
    if docker exec -i "$JANUS_CONTAINER" sh -lc "printf ':remote connect tinkerpop.server conf/remote.yaml session\n:> 1+1\n:> :remote close\n:exit\n' | bin/gremlin.sh >/dev/null 2>&1"; then
      echo "[bootstrap] Gremlin server is ready."
      return 0
    fi
    sleep "$delay"
  done
  echo "Error: Timed out waiting for Gremlin server to become ready." >&2
  return 1
}

require_container() {
  if ! docker ps --format '{{.Names}}' | grep -qx "$JANUS_CONTAINER"; then
    echo "Error: Container '$JANUS_CONTAINER' is not running. Run 'docker compose up -d' first." >&2
    exit 1
  fi
}

require_backend() {
  if ! docker ps --format '{{.Names}}' | grep -qx "$FLASK_CONTAINER"; then
    echo "Error: Container '$FLASK_CONTAINER' is not running. Run 'docker compose up -d' first." >&2
    exit 1
  fi
}

cmd_schema() {
  require_container
  # Ensure Gremlin server is up before attempting schema
  wait_for_gremlin
  # Skip schema apply if it already appears present
  if [ "$(schema_probe)" = "EXISTS" ]; then
    echo "[bootstrap] Schema appears to exist; skipping apply."
    wait_for_schema 2
    return 0
  fi
  if [ ! -f "$REPO_ROOT/index_setup.txt" ]; then
    echo "Error: index_setup.txt not found at repo root." >&2
    exit 1
  fi
  echo "[bootstrap] Applying schema and seeding admin via index_setup.txt …"
  # Filter out comment lines starting with '#' which Groovy won't accept.
  if ! sed -E '/^[[:space:]]*#/d' "$REPO_ROOT/index_setup.txt" | docker exec -i "$JANUS_CONTAINER" bin/gremlin.sh >/dev/null; then
    echo "Error: Failed to apply schema via Gremlin console." >&2
    exit 1
  fi
  echo "[bootstrap] Schema applied."
  # Wait until the schema is visible on the server before proceeding.
  wait_for_schema 5
}

cmd_map_admin() {
  require_container
  local login="${1:-}"
  if [ -z "$login" ]; then
    echo "Usage: bash scripts/bootstrap_graph.sh map-admin <github_login>" >&2
    exit 1
  fi
  # Guard: ensure schema exists when running map-admin directly (skip if called from init)
  if [ "${BOOTSTRAP_INIT:-0}" != "1" ]; then
    probe=$(schema_probe)
    if [ "$probe" != "EXISTS" ]; then
      echo "Error: Schema does not appear to be applied. Run 'bootstrap_graph.sh init $login' or 'bootstrap_graph.sh schema' first." >&2
      exit 1
    fi
  fi
  echo "[bootstrap] Mapping user '$login' to admin group (creating user/group if missing) …"
  require_backend
  # Ensure Gremlin server is up before Python tries to connect
  wait_for_gremlin
  # Sync latest padloper code into the running backend container to pick up fixes
  # without requiring a full image rebuild.
  if [ -d "$REPO_ROOT/padloper" ]; then
    docker cp "$REPO_ROOT/padloper/." "$FLASK_CONTAINER:/padloper" >/dev/null
  fi
  docker exec -i "$FLASK_CONTAINER" sh -lc "export PYTHONPATH=\$PYTHONPATH:/; python3 -m padloper.scripts.init_user-groups --ensure-admin '$login' --actor master"
  echo "[bootstrap] Admin mapping complete for '$login'."
}

main() {
  local subcmd="${1:-}"
  case "$subcmd" in
    init)
      shift
      local login="${1:-}"
      if [ -z "$login" ]; then
        echo "Usage: bash scripts/bootstrap_graph.sh init <github_login>" >&2
        exit 1
      fi
      echo "[bootstrap] Initializing schema and admin mapping for '$login' …"
      BOOTSTRAP_INIT=1
      cmd_schema
      cmd_map_admin "$login"
      ;;
    schema)
      cmd_schema
      ;;
    map-admin)
      shift
      cmd_map_admin "${1:-}"
      ;;
    "")
      cat >&2 <<USAGE
Usage:
  bash scripts/bootstrap_graph.sh <github_login>
  bash scripts/bootstrap_graph.sh init <github_login>
  bash scripts/bootstrap_graph.sh schema
  bash scripts/bootstrap_graph.sh map-admin <github_login>
USAGE
      exit 1
      ;;
    *)
      # Default: treat the first argument as the GitHub login and run init
      local login="$subcmd"
      echo "[bootstrap] Initializing schema and admin mapping for '$login' …"
      BOOTSTRAP_INIT=1
      cmd_schema
      cmd_map_admin "$login"
      ;;
  esac
}

main "$@"
