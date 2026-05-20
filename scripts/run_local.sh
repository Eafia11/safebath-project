#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
uvicorn backend.app.main:app --reload
