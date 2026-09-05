"""Настройка Jinja."""

from __future__ import annotations
from fastapi.templating import Jinja2Templates
from jinja2 import StrictUndefined, Environment, FileSystemLoader, select_autoescape
from backend.core.config import FRONTEND_DIR, SITE

def build_env():
    env = Environment(
        loader=FileSystemLoader(FRONTEND_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["site"] = SITE
    return env

TEMPLATES = Jinja2Templates(env=build_env())