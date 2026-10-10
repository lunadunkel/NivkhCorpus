import csv, io
from typing import Any, Literal
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.core.config import COLLECTION_RESULTS, COLLECTION_JOB, COLLECTION_SENT
from backend.core.deps import CorpusDep
from backend.core.search_service import run_search_db, save_results
from backend.db.compile.process_query import queries_from_doc
from backend.db.database import get_collection

router = APIRouter(prefix="/{corpus_name}/export")

FILTER_FIELDS = {"genre", "dialect"}
SORT = {'default': {"idx": 1}, "old": {"result.date": 1}, "new": {"result.date": -1}}
COLUMNS = {"result.text": "Текст", "result.translation_text": "Перевод", 
           "result.genre": "Жанр", "result.dialect": "Диалект",
           "result.author": "Автор", "result.title": "Название"} 

def attachment(filename: str) -> dict:
    return {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"}

@router.get("")
async def export(request: Request, corpus: CorpusDep, job_id: str, format: Literal["csv", "txt"]):
    lang = corpus.id
    job = await get_collection(lang, COLLECTION_JOB).find_one({"_id": job_id})
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "done":
        raise HTTPException(409, "Search is not finished yet")

    collection = get_collection(lang, COLLECTION_RESULTS)
    if not await collection.find_one({"job_id": job_id}, {"_id": 1}):
        queries = queries_from_doc(job["ir"])
        result = await run_search_db(corpus, get_collection(lang, COLLECTION_SENT), queries)
        await save_results(lang, job_id, result)

    query: dict[str, Any] = {"job_id": job_id}
    for field in FILTER_FIELDS:
        mapping = {y: x for x, y in corpus.meta[field].items()}
        values = request.query_params.getlist(field)
        if values:
            print([mapping[x] for x in values])
            query[f'result.{field}'] = {"$in": [mapping[x] for x in values]}

    sorting = request.query_params.get('sort')
    if sorting is None:
        sorting = "default"
    cursor = collection.find(query, {c: 1 for c in COLUMNS.keys()} | {"_id": 0}, sort=SORT[sorting])

    filename = f"results.{format}"

    if format == "csv":
        async def stream_csv():
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(COLUMNS.values())
            yield "\ufeff" + buf.getvalue()          # BOM + заголовок уходят сразу
            buf.seek(0); buf.truncate(0)
            async for doc in cursor:
                row = [doc['result'].get(c.removeprefix("result."), "") for c in COLUMNS.keys()]
                w.writerow(row)
                yield buf.getvalue()
                buf.seek(0); buf.truncate(0)
        return StreamingResponse(stream_csv(), media_type="text/csv; charset=utf-8",
                                 headers=attachment(filename))

    async def stream_txt():
        active = {k: v for k, v in query.items() if k != "job_id"}
        flt = ", ".join(f"{k}={','.join(v['$in'])}" for k, v in active.items()) or "нет"
        yield f"Фильтры: {flt}\n\n"
        n = 0
        async for doc in cursor:
            n += 1
            yield f"[{n}] {doc['result'].get('text', '')}\n"
            if doc['result'].get("translation_text"):
                yield f"    {doc['result']['translation_text']}\n"
            if doc['result'].get('author'):
                if doc['result'].get('title'):
                    yield f"[{doc['result']['author']}. {doc['result']['title']}]\n"
                else:
                    yield f"Автор: {doc['result']['author']}\n"
            yield "\n"
    return StreamingResponse(stream_txt(), media_type="text/plain; charset=utf-8",
                             headers=attachment(filename))