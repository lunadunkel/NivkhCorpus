[![ru](https://img.shields.io/badge/russian_version-4C7D6E?logo=readme&logoColor=white&labelColor=254038)](https://github.com/lunadunkel/NivkhCorpus/blob/main/readme.md)
# Corpus Platform

A search platform for morphologically annotated corpora of under-resourced and
endangered languages. It currently hosts corpora of **Nivkh** and **Karaim**,
glossed following the Leipzig Glossing Rules and annotated with
Universal Dependencies feature–value pairs.

Everything that varies between languages is declared in a single YAML file per
corpus, so a new corpus can be added without changing Python code.

## Features

- search by word form and lemma, in the corpus language or in the translation;
- search by grammatical features (part of speech, case, tense, mood, person,
  clitics and others), up to ten words in one query;
- a dictionary view with lookup by letter and by lemma;
- a virtual keyboard for the special characters of each language.

## How it is organised

Everything language-specific lives in `corpora/<id>.yaml`: the grammatical
categories and their mapping onto database fields, the layout of the search
form, the keyboard, the alphabetical order of the dictionary, page texts and
styles. Configurations are validated by Pydantic models at startup, so an error
in a YAML file surfaces immediately rather than at the first query.

A query is first translated into a typed intermediate representation
(`backend/core/ir.py`) and then compiled into a MongoDB aggregation pipeline
(`backend/db/compile/`). Each corpus is stored in its own MongoDB database.

**Stack:** Python 3.12, FastAPI, Pydantic, MongoDB (Motor), Jinja2, vanilla JS,
Fuse.js, Docker Compose.

## Quick start (Docker)

Requires Docker with Compose, and `make`.

```bash
cp .env.example .env
make up
```

The site opens at `http://localhost:8000` (the port is set by `APP_PORT`
in `.env`).

On the first run:

1. `data-fetcher` downloads the corpus data archive into `./data` and prepares
   the JSON for import (`docker/preprocess.py`);
2. `mongo` imports the texts into a separate database per corpus
   (`docker/import.sh`);
3. `app` waits for the import to finish, builds the dictionary for each corpus
   and starts the server.

The first run takes a few minutes. Later runs reuse the downloaded data and the
existing database.

### Commands

| Command        | Effect                                               |
| -------------- | ---------------------------------------------------- |
| `make up`      | start all services                                   |
| `make down`    | stop all services                                    |
| `make restart` | restart                                              |
| `make logs`    | follow the logs                                      |
| `make build`   | rebuild the images without cache                     |
| `make clean`   | stop and remove the MongoDB volume                   |
| `make reset`   | remove the MongoDB volume and `./data` (full rebuild)|
| `make help`    | list the commands                                    |

## Local development

To work on the code without rebuilding the container, run the application
directly. This needs a MongoDB instance with the corpora already imported; the
import scripts assume Docker, so the easiest way to get one is `make up`.

```bash
python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Add the database address to `.env`:

```
MONGO_URI=mongodb://localhost:27017
```

If the dictionary has not been built yet:

```bash
python -m backend.db.repositories.dictionary -l nivkh -d
```

Run the server with autoreload:

```bash
uvicorn backend.main:app --reload
```

## Adding a new language

1. Create `corpora/<id>.yaml`. The `id` inside the file must match the file
   name. `corpora/karaim.yaml` is a convenient template.
2. Add the corpus stylesheet at `frontend/static/css/<id>.css` and declare it
   under `assets.styles`.
3. Add an "about" page at `frontend/templates/about/<id>.html`.
4. Put the annotated texts in `data/<id>/`: JSON files of sentences, and
   `corpus_stats.json` with the corpus statistics.
5. Run `make clean && make up`, which reimports every corpus. (`make reset`
   is not suitable here: it also deletes `./data`.)

If anything is missing from the configuration, or values are inconsistent with
one another, the application reports it at startup.

## Data

The texts and their annotation are distributed separately from the code, as a
release archive, and are **not** covered by the licence below. Their terms of
use are set by their authors and collectors.

## Licence

The code is distributed under the MIT licence; see `LICENSE`.
