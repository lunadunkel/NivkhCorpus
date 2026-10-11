"""Настройка Jinja."""

from __future__ import annotations
from fastapi.templating import Jinja2Templates
from jinja2 import StrictUndefined, Environment, FileSystemLoader, select_autoescape
from backend.core.config import FRONTEND_DIR, SITE
from backend.models.derived import columns, glossary, public_dict, reference_page

def plural(n: int, forms: tuple[str, str, str]) -> str:
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return forms[0]
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return forms[1]
    return forms[2]

def thousands(n: int) -> str:
    return f"{n:,}".replace(",", " ")

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
    env.globals["glossary"] = glossary
    env.globals["reference_page"] = reference_page
    env.filters["plural"] = plural
    env.filters["thousands"] = thousands
    return env


TEMPLATES = Jinja2Templates(env=build_env())