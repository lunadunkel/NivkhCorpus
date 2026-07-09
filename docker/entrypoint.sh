#!/bin/sh
set -e
 
MONGO_URI="${MONGO_URI:-mongodb://mongo:27017/corpus}"
 
# 1. Ждём, пока корпус (sentences) будет налит init-скриптом Mongo.
#    Healthcheck гарантирует, что Mongo отвечает, но import.sh
#    может ещё доливать большой корпус — поэтому ждём непустую коллекцию.
echo "Importing corpus data..."
python3 - <<'PY'
import os, sys, time
from pymongo import MongoClient
 
uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus")
db = MongoClient(uri).get_default_database()
 
for attempt in range(1, 31):
    try:
        if db.sentences.count_documents({}) > 0:
            print(f"Corpus ready ({db.sentences.count_documents({})} sentences).")
            sys.exit(0)
    except Exception as e:
        print(f"  Mongo not ready yet: {e}")
    print(f"  waiting... ({attempt}/30)")
    time.sleep(2)
 
print("ERROR: corpus is still empty after waiting — did the import run?")
sys.exit(1)
PY
 
# 2. Строим словарь только если он ещё пуст.
DICT_COUNT=$(python3 - <<'PY'
import os
from pymongo import MongoClient
uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/corpus")
db = MongoClient(uri).get_default_database()
print(db.dictionary.count_documents({}))
PY
)
 
if [ "$DICT_COUNT" -eq "0" ]; then
  echo "Building dictionary from corpus..."
  python3 -m backend.mongodb.repositories.dictionary_repo.create_dictionary -d True
  echo "Dictionary built."
else
  echo "Dictionary already has $DICT_COUNT entries — skipping build."
fi
 
# 3. Запускаем API. exec — чтобы uvicorn стал главным процессом
#    контейнера и корректно получал сигналы остановки.
echo "Starting API..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000