"""Настройка корпусных конфигов при запуске"""
from typing import Annotated
from fastapi import Depends, HTTPException, Path
from backend.core.config import CORPORA
from backend.models.corpus import CorpusConfig

def get_corpus(corpus_name: Annotated[str, Path()]) -> CorpusConfig:
    corpus = CORPORA.get(corpus_name)
    if corpus is None:
        raise HTTPException(404, f"Unknown corpus: {corpus_name}")
    return corpus


CorpusDep = Annotated[CorpusConfig, Depends(get_corpus)]