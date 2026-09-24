import json
import os
from pathlib import Path
import sys
from backend.db.repositories.sentences_repo.process_json import Json2MongoProcessing

SRC = Path("/data")
DST = Path("/data/mongo-ready")


def is_raw(path):
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise SystemExit(f"ERROR: {path} — пустой список документов")
    return isinstance(data[0]["tokens"][0]["tagsets"], list)


def main():
    if not os.path.isdir(SRC):
        raise SystemExit(f"ERROR: нет директории с данными: {SRC}")

    os.makedirs(DST, exist_ok=True)
    processor = Json2MongoProcessing(SRC)

    names = sorted(n for n in os.listdir(SRC) if n.endswith(".json"))
    if not names:
        raise SystemExit(f"ERROR: в {SRC} не найдено ни одного json")

    done = 0
    for name in names:
        src_path = os.path.join(SRC, name)

        if not is_raw(src_path):
            print(f"\t{name}: уже обработан")
            continue

        data = processor.process_json(name)
        with open(os.path.join(DST, name), "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

        done += 1
        print(f"  {name}: ok ({len(data)} документов)")

    if done == 0:
        print("Все файлы обработаны.")


    sample = sorted(n for n in os.listdir(DST) if n.endswith(".json"))
    if not sample:
        raise SystemExit(f"ERROR: в {DST} нет файлов")

    with open(os.path.join(DST, sample[0]), encoding="utf8") as f:
        tagsets = json.load(f)[0]["tokens"][0]["tagsets"]

    if not isinstance(tagsets, dict):
        raise SystemExit(
            f"ERROR: tagsets имеет тип {type(tagsets).__name__}, ожидался dict")

    print(f"Готово: {len(sample)} файлов в {DST}, tagsets в форме словаря.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
