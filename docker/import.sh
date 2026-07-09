#!/bin/sh
set -e

DB="corpus"
IMPORT_DIR="/data/import"

echo "Seeding corpus into $DB.sentences ..."

for file in "$IMPORT_DIR"/*.json; do
  [ -e "$file" ] || { echo "No JSON files found in $IMPORT_DIR"; break; }
  echo "  importing $(basename "$file")..."
  mongoimport \
    --db "$DB" \
    --collection sentences \
    --file "$file" \
    --jsonArray
done

echo "Corpus seeding done."
