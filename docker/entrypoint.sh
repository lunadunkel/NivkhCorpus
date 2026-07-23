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
            print(f"Corpus ready ({state['sentences']} sentences).")
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
uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus")
db = MongoClient(uri).get_default_database()

state = db.import_state.find_one({"_id": "corpus"}) or {}
corpus_n = state.get("sentences", 0)
dict_state = db.import_state.find_one({"_id": "dictionary"}) or {}

if db.dictionary.count_documents({}) == 0:
    print("1")
elif dict_state.get("built_for_sentences") != corpus_n:
    print("1")
else:
    print("0")
PY
)

if [ "$NEED_DICT" -eq "1" ]; then
  echo "Building dictionary from corpus..."
  python3 -m backend.mongodb.repositories.dictionary_repo.create_dictionary -d True
  python3 - <<'PY'
import os
from pymongo import MongoClient
uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus")
db = MongoClient(uri).get_default_database()
state = db.import_state.find_one({"_id": "corpus"}) or {}
db.import_state.replace_one(
    {"_id": "dictionary"},
    {"_id": "dictionary", "built_for_sentences": state.get("sentences", 0)},
    upsert=True,
)
print("Dictionary marker written.")
PY
  echo "Dictionary built."
else
  echo "Dictionary is up to date — skipping build."
fi

echo "Starting API..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000