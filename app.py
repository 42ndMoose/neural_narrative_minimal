
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ulid import ULID

from models import make_session, Statement, Edge, Container, ContainerStatement

app = FastAPI(title="Neural Narrative (Minimal)")
app.mount("/static", StaticFiles(directory="static_files"), name="static")
templates = Jinja2Templates(directory="tpl")

def session():
    return make_session("sqlite:///kg.db")

# ---------- Pydantic models for API ----------

class StatementOut(BaseModel):
    id: str
    slug: Optional[str] = None
    text: str
    type: str
    scope: Optional[str] = None
    time_as_of: Optional[str] = None
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    actors: List[str] = []
    status: str
    confidence: float
    version: int
    prev_version_id: Optional[str] = None
    tags: List[str] = []

class EdgeOut(BaseModel):
    id: str
    from_id: str
    to_id: str
    relation: str
    note: Optional[str] = None

class ContainerOut(BaseModel):
    slug: str
    title: str
    intro: Optional[str] = None
    root_statement_ids: List[str] = []
    default_path: List[str] = []

class GraphOut(BaseModel):
    container: Optional[str] = None
    statements: List[StatementOut]
    edges: List[EdgeOut]

# ---------- Utilities ----------

def stmt_to_out(stmt: Statement) -> StatementOut:
    actors = json.loads(stmt.actors_json) if stmt.actors_json else []
    tags = json.loads(stmt.tags_json) if stmt.tags_json else []
    return StatementOut(
        id=stmt.id, slug=stmt.slug, text=stmt.text, type=stmt.type,
        scope=stmt.scope, time_as_of=stmt.time_as_of, time_from=stmt.time_from, time_to=stmt.time_to,
        actors=actors, status=stmt.status, confidence=stmt.confidence, version=stmt.version,
        prev_version_id=stmt.prev_version_id, tags=tags
    )

def edge_to_out(edge: Edge) -> EdgeOut:
    return EdgeOut(id=edge.id, from_id=edge.from_id, to_id=edge.to_id, relation=edge.relation, note=edge.note)

# ---------- HTML Routes ----------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = session()
    containers = db.query(Container).all()
    return templates.TemplateResponse("index.html", {"request": request, "containers": containers})

@app.get("/c/{slug}", response_class=HTMLResponse)
def read_container(slug: str, request: Request):
    db = session()
    c = db.query(Container).filter_by(slug=slug).first()
    if not c:
        raise HTTPException(404, "Container not found")
    # Collect statements listed in container_statements for this container
    cs = db.query(ContainerStatement).filter_by(container_id=c.id).all()
    stmt_ids = [x.statement_id for x in cs]

    statements = db.query(Statement).filter(Statement.id.in_(stmt_ids)).all()
    edges = db.query(Edge).all()  # keep simple: expose all edges; front-end will filter

    # Build JSON blob for LLM-friendly export
    kg = {
        "container": c.slug,
        "statements": [stmt_to_out(s).model_dump() for s in statements],
        "edges": [edge_to_out(e).model_dump() for e in edges]
    }

    # Parse path and roots
    default_path = json.loads(c.default_path_json) if c.default_path_json else []
    root_ids = json.loads(c.root_ids_json) if c.root_ids_json else []

    # order statements per default_path if present
    stmt_by_id = {s.id: s for s in statements}
    ordered = [stmt_by_id[sid] for sid in default_path if sid in stmt_by_id] if default_path else statements

    return templates.TemplateResponse(
        "container.html",
        {"request": request, "container": c, "statements": ordered, "all_edges": edges, "kg_json": json.dumps(kg), "root_ids": root_ids}
    )

@app.get("/stmt/{stmt_id}", response_class=HTMLResponse)
def read_statement(stmt_id: str, request: Request):
    db = session()
    s = db.query(Statement).filter_by(id=stmt_id).first()
    if not s:
        raise HTTPException(404, "Statement not found")
    outgoing = db.query(Edge).filter_by(from_id=stmt_id).all()
    incoming = db.query(Edge).filter_by(to_id=stmt_id).all()
    return templates.TemplateResponse(
        "statement.html",
        {"request": request, "s": s, "outgoing": outgoing, "incoming": incoming}
    )

# ---------- API Routes ----------

@app.get("/api/containers", response_model=List[ContainerOut])
def api_list_containers():
    db = session()
    out = []
    for c in db.query(Container).all():
        root_ids = json.loads(c.root_ids_json) if c.root_ids_json else []
        default_path = json.loads(c.default_path_json) if c.default_path_json else []
        out.append(ContainerOut(slug=c.slug, title=c.title, intro=c.intro, root_statement_ids=root_ids, default_path=default_path))
    return out

@app.get("/api/containers/{slug}", response_model=ContainerOut)
def api_get_container(slug: str):
    db = session()
    c = db.query(Container).filter_by(slug=slug).first()
    if not c:
        raise HTTPException(404, "Container not found")
    root_ids = json.loads(c.root_ids_json) if c.root_ids_json else []
    default_path = json.loads(c.default_path_json) if c.default_path_json else []
    return ContainerOut(slug=c.slug, title=c.title, intro=c.intro, root_statement_ids=root_ids, default_path=default_path)

@app.get("/api/graphs", response_model=GraphOut)
def api_graph(container: Optional[str] = None):
    db = session()
    statements = []
    edges = []
    if container:
        c = db.query(Container).filter_by(slug=container).first()
        if not c:
            raise HTTPException(404, "Container not found")
        cs = db.query(ContainerStatement).filter_by(container_id=c.id).all()
        stmt_ids = [x.statement_id for x in cs]
        statements = db.query(Statement).filter(Statement.id.in_(stmt_ids)).all()
    else:
        statements = db.query(Statement).all()
    edges = db.query(Edge).all()
    return GraphOut(
        container=container,
        statements=[stmt_to_out(s) for s in statements],
        edges=[edge_to_out(e) for e in edges]
    )

@app.get("/api/statements/{stmt_id}", response_model=StatementOut)
def api_get_statement(stmt_id: str):
    db = session()
    s = db.query(Statement).filter_by(id=stmt_id).first()
    if not s:
        raise HTTPException(404, "Statement not found")
    return stmt_to_out(s)

# ---------- Simple creation endpoints (optional) ----------
# Keeping creation out to avoid scope creep; use seed.py for initial data.

