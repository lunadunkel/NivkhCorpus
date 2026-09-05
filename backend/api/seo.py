from datetime import date
from xml.sax.saxutils import escape

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from backend.core.config import ACTIVE_CORPORA, FRONTEND_DIR, SITE

router = APIRouter(include_in_schema=False)

# Страницы, отдаваемые сервером и пригодные для индексации.
# Шаблон {corpus} подставляется для каждого активного корпуса.
# priority — подсказка для Яндекса; Google его игнорирует, но вреда нет.
INDEXABLE_PATHS = [
    ("/", "weekly", "1.0"),
    ("/{corpus}/", "weekly", "0.9"),
    ("/{corpus}/about", "monthly", "0.7"),
    ("/{corpus}/dictionary", "weekly", "0.8"),
]


def build_sitemap() -> str:
    lastmod = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for path, changefreq, priority in INDEXABLE_PATHS:
        targets = (
            [path]
            if "{corpus}" not in path
            else [path.format(corpus=c) for c in ACTIVE_CORPORA]
        )
        for target in targets:
            lines += [
                "  <url>",
                f"    <loc>{escape(SITE['url'] + target)}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                f"    <changefreq>{changefreq}</changefreq>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            ]

    lines.append("</urlset>")
    return "\n".join(lines)


@router.get("/robots.txt")
async def robots_txt():
    return FileResponse(
        FRONTEND_DIR / "robots.txt",
        media_type="text/plain; charset=utf-8",
    )


@router.get("/sitemap.xml")
async def sitemap_xml():
    return Response(
        content=build_sitemap(),
        media_type="application/xml; charset=utf-8",
    )
