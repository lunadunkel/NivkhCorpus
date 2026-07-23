#!/bin/sh
set -e

DB="corpus"
IMPORT_DIR="/data/import"

echo "Seeding corpus into $DB.sentences ..."

FOUND=0
for file in "$IMPORT_DIR"/*.json; do
  [ -e "$file" ] || { echo "No JSON files found in $IMPORT_DIR"; break; }
  FOUND=1
  echo "  importing $(basename "$file")..."
  mongoimport \
    --db "$DB" \
    --collection sentences \
    --file "$file" \
    --jsonArray
done

if [ "$FOUND" -eq 0 ]; then
  echo "ERROR: no data to import" >&2
  exit 1
fi

mongosh --quiet "$DB" --eval '
  const n = db.sentences.countDocuments({});
  if (n === 0) { throw new Error("import produced 0 sentences"); }
  db.import_state.replaceOne(
    { _id: "corpus" },
    { _id: "corpus", status: "done", sentences: n, finished_at: new Date() },
    { upsert: true }
  );
  print("Import marker written: " + n + " sentences.");
'

echo "Corpus seeding done."