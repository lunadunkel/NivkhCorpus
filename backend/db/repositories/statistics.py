import argparse
import asyncio
import json
from pymongo import MongoClient
from datetime import datetime
import re

from backend.core.config import CORPORA
from backend.db.database import get_collection
from backend.db.repositories.utils import drop_collection

def parse_date(date_str):
    """Парсит дату из формата ДД.ММ.ГГГГ в объект Date. Возвращает None, если это 'заглушка' типа 01.01.ГГГГ"""
    if not date_str:
        return None, None
    
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return dt, dt.year
    except ValueError:
        return None, None

def split_by_comma(value):
    """Разбивает строку по запятой и чистит пробелы, возвращает массив"""
    if not value:
        return []
    return [item.strip() for item in value.split(",")]

def extract_url(source_str):
    """Пытается найти URL в строке источника"""
    url_match = re.search(r'(https?://\S+)', source_str)
    if url_match:
        url = url_match.group(0).rstrip('.') # Убираем точку в конце, если она есть
        clean_source = source_str.replace(url, "").strip()
        return clean_source, url
    return source_str, None


async def process_statistics(lang, path, drop=True):
    collection = get_collection(lang, "texts")
    statistics = get_collection(lang, "statistics")

    if drop:
        await drop_collection(collection)
        await drop_collection(statistics)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts_to_insert = []
    for item in data["texts"]:
        date_obj, year = parse_date(item.get("date", ""))
        clean_source, url = extract_url(item.get("source", ""))
        
        text_doc = {
            "file": item["file"],
            "num_sentences": item["num_sentences"],
            "num_tokens": item["num_tokens"],
            "title_n": item.get("title_n", ""),
            "title_r": item.get("title_r", ""),
            "genre": item["genre"],
            "dialect": item["dialect"],
            "author": split_by_comma(item.get("author", "")),
            "interviewer": split_by_comma(item.get("interviewer", "")),
            "date": date_obj,
            "year": year,
            "source": clean_source,
            "source_url": url
        }
        texts_to_insert.append(text_doc)

    if texts_to_insert:
        await collection.insert_many(texts_to_insert)
        print(f"{collection.full_name}: inserted {len(texts_to_insert)} documents.")
        corpus_doc = {
                "total_sentences": data["total_sentences"],
                "total_tokens": data["total_tokens"],
                "total_texts": len(texts_to_insert)
            }
        
        await statistics.insert_one(corpus_doc)