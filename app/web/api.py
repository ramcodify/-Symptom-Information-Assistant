import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.graph.workflow import run_medicine_assistant
from app.mcp.tools.drug_info import get_drug_info
from app.mcp.tools.check_interaction import check_drug_interaction
from app.mcp.tools.find_generic import find_generic_equivalent
from app.mcp.tools.web_search import search_health_advisories
from app.mcp.server import mcp_server
from evaluation.eval_runner import run_evaluation_suite

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Safe, informational assistant explaining medicines, checking interactions, and recognizing emergencies."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template & Static directories
WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
INDEX_HTML_PATH = TEMPLATES_DIR / "index.html"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Request Models
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class DrugInfoRequest(BaseModel):
    drug_name: str

class InteractionRequest(BaseModel):
    drugs: List[str]

class GenericRequest(BaseModel):
    medicine_name: str

class AdvisoryRequest(BaseModel):
    query: str
    max_results: int = 3


# Endpoints
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    if INDEX_HTML_PATH.exists():
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>MediSafe AI Dashboard</h1><p>index.html not found</p>", status_code=404)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    state = run_medicine_assistant(req.query, req.history)
    return {
        "query": req.query,
        "intent": state.get("intent"),
        "escalation_triggered": state.get("escalation_triggered", False),
        "interrupted": state.get("interrupted", False),
        "guardrail_result": state.get("guardrail_result", {}),
        "extracted_drugs": state.get("extracted_drugs", []),
        "response_text": state.get("response_text", ""),
        "sources": state.get("sources", []),
        "disclaimer_included": state.get("disclaimer_included", True),
        "status": state.get("status")
    }

@app.post("/api/drug-info")
async def drug_info_endpoint(req: DrugInfoRequest):
    return get_drug_info(req.drug_name)

@app.post("/api/check-interactions")
async def check_interactions_endpoint(req: InteractionRequest):
    return check_drug_interaction(req.drugs)

@app.post("/api/generic-finder")
async def generic_finder_endpoint(req: GenericRequest):
    return find_generic_equivalent(req.medicine_name)

@app.post("/api/search-advisories")
async def advisories_endpoint(req: AdvisoryRequest):
    return search_health_advisories(req.query, req.max_results)

@app.get("/api/evaluate")
async def run_evaluation_endpoint():
    """Runs the 28-query automated evaluation benchmark and returns accuracy metrics."""
    return run_evaluation_suite()

@app.post("/mcp")
async def mcp_jsonrpc_endpoint(request: Request):
    """Standard Model Context Protocol (MCP) JSON-RPC 2.0 endpoint."""
    body = await request.body()
    resp_str = mcp_server.handle_json_rpc(body.decode("utf-8"))
    return JSONResponse(content=json.loads(resp_str))
