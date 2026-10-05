#!/bin/sh
set -e

export MONGO_URI="${MONGO_URI:-mongodb://mongo:27017/corpus}"
export WAIT_ATTEMPTS="${WAIT_ATTEMPTS:-150}"
export WAIT_INTERVAL="${WAIT_INTERVAL:-4}"

# MONGO_URI="${MONGO_URI:-mongodb://mongo:27017/corpus}"
# WAIT_ATTEMPTS="${WAIT_ATTEMPTS:-150}"
# WAIT_INTERVAL="${WAIT_INTERVAL:-4}"

echo "Waiting for corpus import to complete..."
python3 - <<'PY'
import os, sys, time
from pymongo import MongoClient

uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus")
attempts = int(os.getenv("WAIT_ATTEMPTS", "150"))
interval = float(os.getenv("WAIT_INTERVAL", "4"))
db = MongoClient(uri, serverSelectionTimeoutMS=5000).get_default_database()

for attempt in range(1, attempts + 1):
    try:
        state = db.import_state.find_one({"_id": "corpus"})
        if state and state.get("status") == "done":
            print(f"Corpora ready: {', '.join(state['corpora'])}.")
            sys.exit(0)
    except Exception as e:
        print(f"  Mongo not ready yet: {e}")
    print(f"  waiting for import marker... ({attempt}/{attempts})")
    time.sleep(interval)

print("ERROR: import marker never appeared — check mongo init logs.", file=sys.stderr)
sys.exit(1)
PY

NEED_DICT=$(python3 - <<'PY'
import os
from pymongo import MongoClient
client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus"))
done = client.get_default_database().import_state.find_one({"_id": "corpus"}) or {}

for corpus in done.get("corpora", []):
    db = client[corpus]
    state = db.import_state.find_one({"_id": "corpus"}) or {}
    dict_state = db.import_state.find_one({"_id": "dictionary"}) or {}
    if db.dictionary.count_documents({}) == 0 or dict_state.get("built_for_sentences") != state.get("sentences", 0):
        print(corpus)
PY
)

for CORPUS in $NEED_DICT; do
  echo "Building dictionary for $CORPUS..."
  python3 -m backend.db.repositories.dictionary -l "$CORPUS" -d
  CORPUS="$CORPUS" python3 - <<'PY'
import os
from pymongo import MongoClient
db = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus"))[os.environ["CORPUS"]]
state = db.import_state.find_one({"_id": "corpus"}) or {}
db.import_state.replace_one(
    {"_id": "dictionary"},
    {"_id": "dictionary", "built_for_sentences": state.get("sentences", 0)},
    upsert=True,
)
print("Dictionary marker written.")
PY
done

exec uvicorn backend.main:app --host 0.0.0.0 --port 8000