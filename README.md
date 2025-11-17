
# Neural Narrative (Minimal)

Atomic, typed statements linked by explicit relations—readable as an “article path” or explored as a graph. Built for humans first, LLM-friendly by design.

## What’s inside
- **FastAPI** backend (SQLite via SQLAlchemy)
- **Jinja2** HTML templates with statement data-attributes
- Minimal **CSS/JS** (no frameworks)
- **LLM-friendly JSON** embedded on container pages (`<script id="kg" type="application/json">…</script>`)
- A **seed** that loads a representative slice of your narrative (statements + edges + a default reading path).

## Quickstart

```bash
# 1) Create and activate a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Seed the database
python seed.py

# 4) Run the server
uvicorn app:app --reload
```

Open http://127.0.0.1:8000/

- `/` lists containers
- `/c/trump-elite-compliance` renders the seeded container
- `/stmt/<id>` shows a single statement with incoming/outgoing links
- `/api/containers`, `/api/containers/<slug>`, `/api/graphs?container=<slug>`, `/api/statements/<id>` provide JSON

## Data model (brief)

- **Statement**
  - `id`, `text`, `type`, `scope`, `time_as_of`, `actors[]`, `status`, `tags[]`, etc.
  - HTML includes data attributes: `data-stmt-id`, `data-type`, `data-scope`, `data-time-as_of`, etc.
- **Edge**
  - `from_id`, `to_id`, `relation` ∈ {supports, contradicts, depends_on, derived_from, refines, same_as, illustrates, summarizes}
- **Container**
  - `slug`, `title`, `intro`, `root_ids[]`, `default_path[]`
- **ContainerStatement**
  - Many-to-many membership

## LLM-friendly surfaces

1. **Atomic HTML blocks** per statement with stable IDs and typed relations.
2. **Page JSON export** under `<script id="kg" type="application/json">` containing `statements` and `edges` for the container.
3. **Simple APIs** to fetch containers, statements, and graphs.

This lets a browsing tool fetch only relevant statements instead of a giant wall of text.

## Customize

- Edit `seed.py` to add/modify statements and relations.
- Change the container’s `default_path_json` to control the “article” order.
- Add more containers for other narratives or math proofs.

## Notes

- This is intentionally **small and understandable**. No build steps, no front-end frameworks.
- You can add auth, editors, or graph visualizations later without touching the core model.
