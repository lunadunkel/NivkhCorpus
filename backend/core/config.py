from enum import Enum
from pathlib import Path

import yaml

from backend.core.corpora import CorpusConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]

CORPORA_DIR = PROJECT_ROOT / "corpora"

COLLECTION_JOB = "jobs_id"
COLLECTION_SENT = "sentences"
COLLECTION_RESULTS = "results"
COLLECTION_DICT = "dictionary"


# FRONTEND DIRECTORIES
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"

# SITE
SITE = {
    "url": "https://corpora.rcc.msu.ru",
    "og_image": "/static/images/og-cover.png",
    "github": "https://github.com/lunadunkel/NivkhCorpus",
    "year": 2026,
}

def load_corpora(directory: Path = CORPORA_DIR) -> dict[str, CorpusConfig]:
    corpora: dict[str, CorpusConfig] = {}

    for path in sorted(directory.glob("*.yaml")):
        if path.name.startswith("_"):   # _labels.yaml и прочие общие файлы
            continue

        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        config = CorpusConfig.model_validate(raw)

        if config.id != path.stem:
            raise ValueError(f"{path.name}: id {config.id!r} не совпадает с именем файла")

        corpora[config.id] = config

    return corpora


CORPORA: dict[str, CorpusConfig] = load_corpora()
ACTIVE_CORPORA: list[str] = [cid for cid, c in CORPORA.items() if c.enabled]