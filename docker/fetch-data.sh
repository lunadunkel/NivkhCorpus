#!/bin/sh
set -e

REPO="lunadunkel/NivkhCorpus"
TAG="data-v1"
ASSET="data.zip"
URL="https://github.com/$REPO/releases/download/$TAG/$ASSET"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT_DIR"

echo "Downloading corpus data from $URL ..."
mkdir -p "$DATA_DIR"
curl -L -o "$ASSET" "$URL"

echo "Unpacking into $DATA_DIR ..."
if command -v unzip >/dev/null 2>&1; then
  unzip -oj "$ASSET" -d "$DATA_DIR"
else
  python3 -m zipfile -e "$ASSET" "$DATA_DIR"
fi

rm -f "$ASSET"
echo "Done. JSON files are in $DATA_DIR"
