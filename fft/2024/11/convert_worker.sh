#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

# Input CSV‑XZ file
csv_xz="$1"
parquet="${csv_xz%.csv.xz}.parquet"

echo "[$(date +%H:%M:%S)] Converting $csv_xz → $parquet"

# Stream-decompress into DuckDB and write Parquet
xzcat "$csv_xz" \
  | duckdb --batch -c "
    SET preserve_insertion_order=false;
    COPY (
      SELECT *
          FROM read_csv_auto('/dev/stdin')
    )
    TO '$parquet'
    (FORMAT PARQUET,
     COMPRESSION $PARQUET_COMP,
     ROW_GROUP_SIZE 268435456);
  "

echo "[$(date +%H:%M:%S)] Done: $parquet"

#, auto_type_candidates = ['DECIMAL(5,2)', 'DATE'])
