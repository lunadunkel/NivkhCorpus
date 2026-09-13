"""Настройка Jinja."""

from __future__ import annotations
from fastapi.templating import Jinja2Templates
from jinja2 import StrictUndefined, Environment, FileSystemLoader, select_autoescape
from backend.core.config import FRONTEND_DIR, SITE
from backend.models.derived import columns, public_dict

def build_env():
    env = Environment(
        loader=FileSystemLoader(FRONTEND_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["site"] = SITE
    env.globals["columns"] = columns
    env.globals["public_dict"] = public_dict
    return env

TEMPLATES = Jinja2Templates(env=build_env())