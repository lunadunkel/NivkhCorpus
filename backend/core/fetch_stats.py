import asyncio
from datetime import datetime
from bson import ObjectId
from backend.core.config import CORPORA
from backend.db.database import get_collection


async def fetch_per_corpus():
    data = {}
    for corpus in CORPORA.keys():
        collection = get_collection(corpus, "statistics")
        result = await collection.find_one({}, {"_id": 0})
        data[corpus] = result

    print(data)
    return data

if __name__ == "__main__":
    asyncio.run(fetch_per_corpus())