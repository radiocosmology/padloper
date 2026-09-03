#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Dockerless local setup for padloper.
#
# Prepares a fresh checkout to run the four components by hand (no Docker):
#   1. JanusGraph (+ Cassandra + Elasticsearch)  - graph DB, port 8182
#   2. flask-interface (Flask backend)           - API, port 4300
#   3. oauth-proxy-server (Node)                  - GitHub OAuth helper, 4000
#   4. web-interface (React dev server)           - UI, port 4301
#
# It validates the required environment configuration up front, then handles
# dependency setup for 2-4 (Python venv + packages, npm installs) and writes
# the .env file. JanusGraph is optional and heavy; pass --with-janusgraph to
# download/extract the bundle.
#
# Required configuration (provide via your shell environment OR an existing
# .env file; the script persists them to .env):
#   GITHUB_OAUTH_CLIENT_ID      - GitHub OAuth App client ID
#   GITHUB_OAUTH_CLIENT_SECRET  - GitHub OAuth App client secret
# Auto-handled if absent:
#   SECRET_KEY                  - generated (Flask session secret)
#   PROXY_SERVER_URL            - defaults to http://localhost:4000/
#
# Usage:
#   bash scripts/setup_local.sh                # validate config, then full setup
#   bash scripts/setup_local.sh --check-only   # verify prerequisites + config only
#   bash scripts/setup_local.sh --skip-oauth   # set up deps without OAuth creds
#   bash scripts/setup_local.sh --with-janusgraph
#   bash scripts/setup_local.sh --help
#
# Environment overrides:
#   PYTHON_BIN          python interpreter to use   (default: python3)
#   VENV_DIR            virtualenv location         (default: <repo>/venv)
#   JANUSGRAPH_VERSION  JanusGraph bundle version   (default: 1.1.0)
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$REPO_ROOT/venv}"
JANUSGRAPH_VERSION="${JANUSGRAPH_VERSION:-1.1.0}"
ENV_FILE="$REPO_ROOT/.env"

CHECK_ONLY=0
WITH_JANUSGRAPH=0
SKIP_OAUTH=0

# Variables the user must supply (cannot be auto-generated).
REQUIRED_VARS=(GITHUB_OAUTH_CLIENT_ID GITHUB_OAUTH_CLIENT_SECRET)

# --- logging helpers -------------------------------------------------------
info()  { printf '\033[0;34m[setup]\033[0m %s\n' "$*"; }
ok()    { printf '\033[0;32m[ ok ]\033[0m %s\n' "$*"; }
warn()  { printf '\033[0;33m[warn]\033[0m %s\n' "$*" >&2; }
err()   { printf '\033[0;31m[fail]\033[0m %s\n' "$*" >&2; }
have()  { command -v "$1" >/dev/null 2>&1; }

usage() {
  cat <<'EOF'
Dockerless local setup for padloper.

Prepares a fresh checkout to run the four components by hand (no Docker):
  1. JanusGraph (+ Cassandra + Elasticsearch)  - graph DB, port 8182
  2. flask-interface (Flask backend)           - API, port 4300
  3. oauth-proxy-server (Node)                  - GitHub OAuth helper, 4000
  4. web-interface (React dev server)           - UI, port 4301

Required configuration (via shell environment OR an existing .env file):
  GITHUB_OAUTH_CLIENT_ID      GitHub OAuth App client ID
  GITHUB_OAUTH_CLIENT_SECRET  GitHub OAuth App client secret
Auto-handled if absent:
  SECRET_KEY (generated), PROXY_SERVER_URL (defaults to http://localhost:4000/)

Usage:
  bash scripts/setup_local.sh                # validate config, then full setup
  bash scripts/setup_local.sh --check-only   # verify prerequisites + config only
  bash scripts/setup_local.sh --skip-oauth   # set up deps without OAuth creds
  bash scripts/setup_local.sh --with-janusgraph
  bash scripts/setup_local.sh --help

Environment overrides:
  PYTHON_BIN          python interpreter to use   (default: python3)
  VENV_DIR            virtualenv location         (default: <repo>/venv)
  JANUSGRAPH_VERSION  JanusGraph bundle version   (default: 1.1.0)
EOF
  exit 0
}

# --- arg parsing -----------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --check-only)      CHECK_ONLY=1 ;;
    --skip-oauth)      SKIP_OAUTH=1 ;;
    --with-janusgraph) WITH_JANUSGRAPH=1 ;;
    -h|--help)         usage ;;
    *) err "Unknown argument: $arg (try --help)"; exit 2 ;;
  esac
done

# ---------------------------------------------------------------------------
# .env helpers (no sed-injection: rewrite the file line-by-line)
# ---------------------------------------------------------------------------
env_file_value() {  # echo the value of VAR from .env, or empty
  local var="$1" line
  [ -f "$ENV_FILE" ] || return 0
  line="$(grep -E "^${var}=" "$ENV_FILE" | tail -1 || true)"
  printf '%s' "${line#"${var}"=}"
}

env_effective() {   # live shell env takes precedence over .env
  local var="$1"
  local live="${!var:-}"
  if [ -n "$live" ]; then printf '%s' "$live"; else env_file_value "$var"; fi
}

env_upsert() {      # set VAR=VAL in .env, replacing or appending
  local var="$1" val="$2" tmp found=0
  tmp="$(mktemp)"
  if [ -f "$ENV_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      if [ "${line%%=*}" = "$var" ]; then
        printf '%s=%s\n' "$var" "$val"; found=1
      else
        printf '%s\n' "$line"
      fi
    done < "$ENV_FILE" > "$tmp"
  fi
  [ "$found" -eq 1 ] || printf '%s=%s\n' "$var" "$val" >> "$tmp"
  mv "$tmp" "$ENV_FILE"
}

mask() {            # redact secrets for display
  local var="$1" val="$2"
  case "$var" in
    *SECRET*|SECRET_KEY) printf 'hidden' ;;
    GITHUB_OAUTH_CLIENT_ID) printf '%s…' "${val:0:6}" ;;
    *) printf '%s' "$val" ;;
  esac
}

# ---------------------------------------------------------------------------
# 1. Prerequisite checks
# ---------------------------------------------------------------------------
check_prereqs() {
  info "Checking prerequisites…"
  local missing=0

  if have "$PYTHON_BIN"; then
    local pyver
    pyver="$("$PYTHON_BIN" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    if "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3,9) else 1)'; then
      ok "python: $pyver ($PYTHON_BIN)"
    else
      err "python $pyver found, but >= 3.9 is required (aiohttp 3.10 / gremlinpython 3.7)"; missing=1
    fi
  else
    err "python interpreter '$PYTHON_BIN' not found (set PYTHON_BIN to override)"; missing=1
  fi

  if have "$PYTHON_BIN" && "$PYTHON_BIN" -c 'import venv' 2>/dev/null; then
    ok "python venv module present"
  else
    err "python 'venv' module missing (Debian/Ubuntu: sudo apt install python3-venv)"; missing=1
  fi

  if have node; then ok "node: $(node -v)"; else err "node not found (need Node 18+)"; missing=1; fi
  if have npm;  then ok "npm:  $(npm -v)";  else err "npm not found"; missing=1; fi

  if have java; then
    local jver; jver="$(java -version 2>&1 | head -1)"
    if java -version 2>&1 | grep -qE '"(11|17|21)\.'; then ok "java: $jver"
    else warn "java present but not 11/17/21: $jver (JanusGraph 1.1.0 supports JDK 8/11; 11 recommended)"; fi
  else
    warn "java not found — only required to run JanusGraph locally (JDK 11 recommended)"
  fi

  if [ "$missing" -ne 0 ]; then
    err "Missing required prerequisites (see above). Install them and re-run."
    exit 1
  fi
  ok "All required prerequisites satisfied."
}

# ---------------------------------------------------------------------------
# 2. Environment configuration preflight
#    mode=apply -> writes .env (generate SECRET_KEY, default PROXY, persist
#                  provided values); mode=check -> read-only report.
# ---------------------------------------------------------------------------
preflight_env() {
  local mode="$1"
  info "Validating environment configuration…"

  if [ "$mode" = "apply" ] && [ ! -f "$ENV_FILE" ]; then
    cp "$REPO_ROOT/.env.template" "$ENV_FILE"
    info "Created .env from .env.template"
  fi

  # SECRET_KEY — generate if absent.
  local secret; secret="$(env_effective SECRET_KEY)"
  if [ -n "$secret" ]; then
    [ "$mode" = "apply" ] && env_upsert SECRET_KEY "$secret"
    ok "SECRET_KEY: set (hidden)"
  elif [ "$mode" = "apply" ]; then
    secret="$("$PYTHON_BIN" -c 'import secrets; print(secrets.token_hex(32))')"
    env_upsert SECRET_KEY "$secret"
    ok "SECRET_KEY: generated"
  else
    info "SECRET_KEY: not set (will be generated on a full run)"
  fi

  # PROXY_SERVER_URL — default to localhost.
  local proxy; proxy="$(env_effective PROXY_SERVER_URL)"
  if [ -z "$proxy" ]; then proxy="http://localhost:4000/"; fi
  [ "$mode" = "apply" ] && env_upsert PROXY_SERVER_URL "$proxy"
  ok "PROXY_SERVER_URL: $proxy"

  # Required GitHub OAuth credentials.
  local missing=()
  local var val
  for var in "${REQUIRED_VARS[@]}"; do
    val="$(env_effective "$var")"
    if [ -z "$val" ]; then
      missing+=("$var"); err "$var: MISSING"
    else
      [ "$mode" = "apply" ] && env_upsert "$var" "$val"
      ok "$var: set ($(mask "$var" "$val"))"
    fi
  done

  if [ "${#missing[@]}" -gt 0 ]; then
    {
      echo
      warn "Required configuration is missing (needed for GitHub sign-in):"
      for var in "${missing[@]}"; do printf '         - %s\n' "$var"; done
      cat <<EOF

Provide them, then re-run — either:
  (a) export in your shell:
        export GITHUB_OAUTH_CLIENT_ID=...
        export GITHUB_OAUTH_CLIENT_SECRET=...
  (b) edit the values into ${ENV_FILE}

Create the credentials at:
  GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
EOF
    } >&2
    if [ "$SKIP_OAUTH" -eq 1 ]; then
      warn "--skip-oauth set: continuing without GitHub OAuth credentials."
      warn "Sign-in will not work until you set them in ${ENV_FILE}."
    else
      err "Aborting before install. Re-run with --skip-oauth to set up deps anyway."
      exit 1
    fi
  else
    ok "All required environment variables are set."
  fi
}

# ---------------------------------------------------------------------------
# 3. Python backend (venv + deps + editable padloper)
# ---------------------------------------------------------------------------
setup_python() {
  info "Setting up Python virtualenv at $VENV_DIR"
  if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"; ok "Created venv."
  else
    info "venv already exists — reusing."
  fi
  local pip="$VENV_DIR/bin/pip"
  info "Upgrading pip…";              "$pip" install --upgrade pip >/dev/null
  info "Installing backend requirements (can take a few minutes)…"
  "$pip" install -r "$REPO_ROOT/requirements.txt"
  info "Installing the padloper package (editable)…"
  "$pip" install -e "$REPO_ROOT"
  ok "Python backend ready."
}

# ---------------------------------------------------------------------------
# 4. Node projects
# ---------------------------------------------------------------------------
npm_install_dir() {
  local dir="$1"
  info "Installing npm deps in ${dir#"$REPO_ROOT"/}…"
  if [ -f "$dir/package-lock.json" ]; then ( cd "$dir" && npm ci --no-audit --no-fund )
  else ( cd "$dir" && npm install --no-audit --no-fund ); fi
}

setup_node() {
  npm_install_dir "$REPO_ROOT/oauth-proxy-server"
  npm_install_dir "$REPO_ROOT/web-interface"
  ok "Node projects ready."
}

# ---------------------------------------------------------------------------
# 5. Optional: download + configure JanusGraph bundle
# ---------------------------------------------------------------------------
setup_janusgraph() {
  local ver="$JANUSGRAPH_VERSION"
  local dir="$REPO_ROOT/janusgraph-full-$ver"
  local zip="$REPO_ROOT/janusgraph-full-$ver.zip"
  local url="https://github.com/JanusGraph/janusgraph/releases/download/v${ver}/janusgraph-full-${ver}.zip"

  if [ -d "$dir" ]; then
    info "JanusGraph bundle already present at ${dir#"$REPO_ROOT"/} — skipping download."
  else
    have curl  || { err "curl required to download JanusGraph"; exit 1; }
    have unzip || { err "unzip required to extract JanusGraph"; exit 1; }
    info "Downloading JanusGraph $ver (~400 MB)…"
    curl -fL --progress-bar -o "$zip" "$url"
    info "Extracting…"; unzip -q "$zip" -d "$REPO_ROOT"; rm -f "$zip"
    ok "Extracted to ${dir#"$REPO_ROOT"/}"
  fi

  local props="$dir/conf/janusgraph-cql-es.properties"
  if [ -f "$props" ] && ! grep -q '^schema.default=none' "$props"; then
    printf '\nschema.default=none\n' >> "$props"
    info "Added schema.default=none to the bundle config."
  fi
  for opt in "$dir/conf/jvm-11.options" "$dir/conf/jvm-17.options"; do
    [ -f "$opt" ] && sed -i 's/-Xms[0-9]\+[mg]/-Xms512m/; s/-Xmx[0-9]\+[mg]/-Xmx512m/' "$opt" || true
  done
  ok "JanusGraph configured. Start it with:  ( cd ${dir#"$REPO_ROOT"/} && bin/janusgraph.sh start )"
}

# ---------------------------------------------------------------------------
# Next-steps banner
# ---------------------------------------------------------------------------
print_next_steps() {
  local jg_hint
  if [ "$WITH_JANUSGRAPH" -eq 1 ]; then
    jg_hint="( cd janusgraph-full-$JANUSGRAPH_VERSION && bin/janusgraph.sh start )   # then seed schema: see README"
  else
    jg_hint="Install/start JanusGraph 1.1.x (see README), or re-run with --with-janusgraph"
  fi
  cat <<EOF

$(ok "Setup complete.")

Next steps — start each service in its own terminal:

  0) JanusGraph (graph DB, :8182)
     $jg_hint

  1) Flask backend (:4300) — reads .env automatically
     source venv/bin/activate
     ( cd flask-interface && flask run -p 4300 )

  The Node services below do NOT read .env, so load it into your shell first:
     set -a; . ./.env; set +a

  2) OAuth proxy (:4000)
     ( cd oauth-proxy-server && CLIENT_ID="\$GITHUB_OAUTH_CLIENT_ID" CLIENT_SECRET="\$GITHUB_OAUTH_CLIENT_SECRET" npm start )

  3) React frontend (:4301)
     ( cd web-interface && REACT_APP_GITHUB_CLIENT_ID="\$GITHUB_OAUTH_CLIENT_ID" REACT_APP_BASE_PATH=/padloper npm start )

  Then open  http://localhost:4301/padloper
EOF
}

# ---------------------------------------------------------------------------
main() {
  info "padloper dockerless setup (repo: $REPO_ROOT)"
  check_prereqs
  if [ "$CHECK_ONLY" -eq 1 ]; then
    preflight_env check
    ok "Checks complete (--check-only); nothing installed."
    exit 0
  fi
  preflight_env apply
  setup_python
  setup_node
  [ "$WITH_JANUSGRAPH" -eq 1 ] && setup_janusgraph
  print_next_steps
}

main
