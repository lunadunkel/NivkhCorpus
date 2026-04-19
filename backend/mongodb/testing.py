import asyncio
import pprint

from backend.mongodb.database import get_collection
from backend.mongodb.process_query import QueryBuilder
from backend.mongodb.compile.aggregation_compile import AggregatePipeline


# query = [{'search-type': 'token', 'input_word': '', 'language-select': 'nivkh', 'added-gram-features': '', 'person[]': '1', 'person_obj[]': '3'}]
# query = [{'search-type': 'token', 'input_word': '', 'language-select': 'nivkh', 'added-gram-features': '', 'person[]': '2', 'person_obj[]': '1'}]
# query = [{'search-type': 'token', 'input_word': '', 'language-select': 'nivkh', 'added-gram-features': '', 'verb[]': 'caus'}]

query = [{'search-type': 'token', 'input_word': '', 'language-select': 'nivkh', 'added-gram-features': '', 'number[]': 'Sing'}]
async def main():
    collection = get_collection('sentences')

    qb = QueryBuilder(query)
    aggregate_compiler = AggregatePipeline(qb.queries)

    aggregation = aggregate_compiler.aggregate()
    print(aggregation)
    cursor = collection.aggregate(aggregation)
    result = await cursor.to_list(length=None)
    for res in result:
        pprint.pprint(res)
        break

if __name__ == "__main__":
    asyncio.run(main())