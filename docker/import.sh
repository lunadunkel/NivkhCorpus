#!/bin/sh
set -e

IMPORT_DIR="/data/import"
CORPORA=""

for dir in "$IMPORT_DIR"/*/; do
  [ -d "$dir" ] || continue
  DB=$(basename "$dir")
  echo "Seeding corpus into $DB.sentences ..."

  for file in "$dir"*.json; do
    [ -e "$file" ] || continue
    if [ "$(basename "$file")" = "statistics.json" ]; then
      mongoimport --db "$DB" --collection statistics --drop --file "$file" --jsonArray
      continue
    fi
    echo "  importing $(basename "$file")..."
    mongoimport \
      --db "$DB" \
      --collection sentences \
      --file "$file" \
      --jsonArray
  done

  mongo --quiet "$DB" --eval '
    const n = db.sentences.countDocuments({});
    if (n === 0) { throw new Error("import produced 0 sentences"); }
    db.import_state.replaceOne(
      { _id: "corpus" },
      { _id: "corpus", status: "done", sentences: n, finished_at: new Date() },
      { upsert: true }
    );
    print("Import marker written: " + n + " sentences.");
  '
  CORPORA="$CORPORA $DB"
done

if [ -z "$CORPORA" ]; then
  echo "ERROR: no data to import" >&2
  exit 1
fi

mongo --quiet corpus --eval "
  db.import_state.replaceOne(
    { _id: 'corpus' },
    { _id: 'corpus', status: 'done', corpora: '$CORPORA'.trim().split(' '), finished_at: new Date() },
    { upsert: true }
  );
"

echo "Corpus seeding done:$CORPORA"