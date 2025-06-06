#!/usr/bin/env bash
set -euo pipefail

# ─── CONFIG ────────────────────────────────────────────────────────────────────
# Number of parallel jobs; override by exporting PARALLEL before running
PARALLEL="${PARALLEL:-4}"

# Parquet compression settings
PARQUET_COMP="brotli"
PARQUET_LEVEL=9

# ─── REQUIREMENTS ─────────────────────────────────────────────────────────────
#  • duckdb CLI
#  • GNU parallel
#  • xz-utils
# ──────────────────────────────────────────────────────────────────────────────

export LC_ALL=C

shopt -s nullglob
files=( *.csv.xz )
count=${#files[@]}

if (( count == 0 )); then
  echo "❌  No .csv.xz files found in $(pwd)"
  exit 1
fi

echo "🔄  Converting $count file(s) with up to $PARALLEL parallel jobs…"

# Export shared settings for worker
export PARQUET_COMP PARQUET_LEVEL

# Call the worker script in parallel
parallel -j "$PARALLEL" --bar ./convert_worker.sh ::: "${files[@]}"

echo "🎉  All done! Converted $count file(s)."
