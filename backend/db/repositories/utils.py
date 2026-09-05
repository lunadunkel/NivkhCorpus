import hashlib
import json
from bson import ObjectId

def clean(obj):
    if isinstance(obj, list):
        return [clean(x) for x in obj]
    if isinstance(obj, dict):
        return {
            k: (str(v) if isinstance(v, ObjectId) else clean(v))
            for k, v in obj.items()
        }
    return obj

def make_hash(query):
    return hashlib.md5(json.dumps(query, sort_keys=True).encode()).hexdigest()