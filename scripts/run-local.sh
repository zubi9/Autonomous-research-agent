#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Usage: ./scripts/run-local.sh [options]

Start the FastAPI app locally and, when available, bring up Redis and Qdrant
for local dependency checks before a Docker build.

Options:
  --no-deps       Skip starting Redis/Qdrant containers.
  --port <port>   Port to expose the API on (default: 8000).
  --dry-run       Print the startup plan without launching anything.
  -h, --help      Show this help message.
EOF
}

SKIP_DEPS=0
PORT=8000
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-deps)
      SKIP_DEPS=1
      ;;
    --port)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --port" >&2
        exit 1
      fi
      PORT="$2"
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ $SKIP_DEPS -eq 0 ]]; then
  if command -v docker >/dev/null 2>&1; then
    echo "Starting Redis and Qdrant dependencies..."
    docker compose -f deploy/docker-compose.yml up -d redis qdrant
  else
    echo "Docker was not found; skipping dependency startup."
  fi
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry run complete. The app would start on http://127.0.0.1:${PORT}"
  exit 0
fi

echo "Starting the API on http://127.0.0.1:${PORT}"

if command -v poetry >/dev/null 2>&1; then
  exec poetry run uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
elif [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  exec "$ROOT_DIR/.venv/bin/python" -m uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
else
  exec python3 -m uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
fi
