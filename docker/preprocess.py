import json
import os
from pathlib import Path
import sys

import yaml
from backend.db.repositories.process_json import Json2MongoProcessing

SRC = Path("/data")
DST = Path("/data/mongo-ready")
CORPORA_DIR = Path("/src/corpora")
STATS_FILE = "corpus_stats.json"


def is_raw(path):
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise SystemExit(f"ERROR: {path} — empty document list")
    return isinstance(data[0]["tokens"][0]["tagsets"], list)


def write_statistics(src_dir, dst_dir):
    """corpus_stats.json -> statistics.json: один документ для главной страницы."""
    with open(src_dir / STATS_FILE, encoding="utf8") as f:
        data = json.load(f)
    total_texts = data.get("texts")
    if total_texts is None:
        total_texts = data['total_texts']
    else:
        total_texts = len(total_texts)
    doc = {
        "total_sentences": data["total_sentences"],
        "total_tokens": data["total_tokens"],
        "total_texts": total_texts,
    }
    with open(dst_dir / "statistics.json", "w", encoding="utf8") as f:
        json.dump([doc], f, ensure_ascii=False)

def process_corpus(config):
    corpus = config["id"]
    src_dir = SRC / corpus
    dst_dir = DST / corpus

    if not src_dir.is_dir():
        print(f"{corpus}: no folder {src_dir} — skipping")
        return
    if (dst_dir / ".done").exists():
        print(f"{corpus}: already processed")
        return

    os.makedirs(dst_dir, exist_ok=True)
    search = config["search"]
    meta = {search["translation_field"], search["sentence_text_field"]}
    processor = Json2MongoProcessing(src_dir, config["ingest"], corpus, meta)

    names = sorted(n for n in os.listdir(src_dir) if n.endswith(".json") and n != STATS_FILE)
    if not names:
        raise SystemExit(f"ERROR: {src_dir} no json found")

    for name in names:
        src_path = os.path.join(src_dir, name)

        if not is_raw(src_path):
            print(f"\t{corpus}/{name}: уже обработан")
            continue

        data = processor.process_json(name)
        with open(os.path.join(dst_dir, name), "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"  {corpus}/{name}: ok ({len(data)} documents)")

    if (src_dir / STATS_FILE).exists():
        write_statistics(src_dir, dst_dir)
    else:
        print(f"{corpus}: no {STATS_FILE} — no statistics presented in corpora")

    sample = sorted(n for n in os.listdir(dst_dir) if n.endswith(".json") and n != "statistics.json")
    with open(os.path.join(dst_dir, sample[0]), encoding="utf8") as f:
        tagsets = json.load(f)[0]["tokens"][0]["tagsets"]
    if not isinstance(tagsets, dict):
        raise SystemExit(
            f"ERROR: {corpus}: tagsets is of type {type(tagsets).__name__}, expected dict")

    (dst_dir / ".done").touch()
    print(f"{corpus}: ready, {len(sample)} files in {dst_dir}")



def main():
    if not os.path.isdir(SRC):
        raise SystemExit(f"ERROR: no directory with data: {SRC}")

    for path in sorted(CORPORA_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        process_corpus(yaml.safe_load(path.read_text(encoding="utf-8")))
    return 0

if __name__ == "__main__":
    sys.exit(main())
