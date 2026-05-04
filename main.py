"""
main.py
-------
FastAPI NL2SQL backend.

Endpoints:
  GET  /health       → system health check
  POST /chat         → natural-language question → SQL + results + optional chart

Run:
  uvicorn main:app --reload
"""

import os
import re
import json
import traceback
import sqlite3
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "clinic.db")

# Lazy-load Vanna (heavy model; skip in tests when DB absent)
_vanna = None

def get_vanna():
    global _vanna
    if _vanna is None:
        from vanna_setup import get_vanna_instance
        _vanna = get_vanna_instance()
    return _vanna


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="NL2SQL Clinic API",
    description="Natural Language to SQL using Vanna 2.0 + Gemini/Groq/Ollama",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ───────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    generate_chart: Optional[bool] = True


class ChatResponse(BaseModel):
    question: str
    sql: Optional[str]
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    chart_json: Optional[str]      # Plotly JSON string or None
    message: str
    error: Optional[str]


class HealthResponse(BaseModel):
    status: str
    database: str
    db_tables: List[str]
    provider: str
    version: str


# ── SQL validation ────────────────────────────────────────────────────────────
FORBIDDEN_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"sqlite_master",
    r"sqlite_sequence",
    r"--",          # SQL comment injection
    r";.*SELECT",   # stacked queries
]

def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Returns (is_valid, reason).
    Only SELECT statements are allowed.
    """
    cleaned = sql.strip().upper()

    if not cleaned.startswith("SELECT") and not cleaned.startswith("WITH"):
        return False, "Only SELECT (or WITH…SELECT) queries are allowed."

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return False, f"Forbidden keyword/pattern detected: {pattern}"

    return True, ""


# ── chart generation ──────────────────────────────────────────────────────────
def should_generate_chart(df: pd.DataFrame) -> bool:
    """Decide if this result set is worth charting."""
    if df.empty or len(df) < 2:
        return False
    num_cols = df.select_dtypes(include="number").columns
    return len(num_cols) >= 1


def generate_chart(df: pd.DataFrame, question: str) -> Optional[str]:
    """
    Auto-select chart type based on data shape and return Plotly JSON.
    Returns None if no suitable chart can be made.
    """
    if not should_generate_chart(df):
        return None

    try:
        num_cols  = list(df.select_dtypes(include="number").columns)
        cat_cols  = list(df.select_dtypes(exclude="number").columns)
        n_rows    = len(df)

        # ── time series ───────────────────────────────────────────────────────
        time_candidates = [c for c in df.columns if any(
            k in c.lower() for k in ("month","year","date","week","day","quarter")
        )]
        if time_candidates and num_cols:
            x_col = time_candidates[0]
            y_col = num_cols[0]
            fig = px.line(
                df, x=x_col, y=y_col,
                title=question[:80],
                markers=True,
                template="plotly_white",
            )
            return fig.to_json()

        # ── category + single numeric → bar ───────────────────────────────────
        if cat_cols and num_cols and n_rows <= 30:
            fig = px.bar(
                df, x=cat_cols[0], y=num_cols[0],
                title=question[:80],
                color=num_cols[0],
                color_continuous_scale="Blues",
                template="plotly_white",
            )
            fig.update_layout(showlegend=False)
            return fig.to_json()

        # ── single category + count → pie (≤ 10 slices) ──────────────────────
        if cat_cols and num_cols and n_rows <= 10:
            fig = px.pie(
                df, names=cat_cols[0], values=num_cols[0],
                title=question[:80],
                template="plotly_white",
            )
            return fig.to_json()

        # ── two numeric columns → scatter ─────────────────────────────────────
        if len(num_cols) >= 2:
            fig = px.scatter(
                df, x=num_cols[0], y=num_cols[1],
                title=question[:80],
                template="plotly_white",
            )
            return fig.to_json()

        # ── fallback horizontal bar ────────────────────────────────────────────
        if cat_cols and num_cols:
            fig = px.bar(
                df.head(20), x=num_cols[0], y=cat_cols[0],
                orientation="h",
                title=question[:80],
                template="plotly_white",
            )
            return fig.to_json()

    except Exception as e:
        print(f"[Chart] Failed to generate chart: {e}")

    return None


# ── run SQL directly ──────────────────────────────────────────────────────────
def run_sql(sql: str) -> List[Dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows


# ── endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
def health():
    """Return system health and database status."""
    tables = []
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cur.fetchall()]
        con.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    return HealthResponse(
        status="ok",
        database=db_status,
        db_tables=tables,
        provider=os.getenv("LLM_PROVIDER", "gemini"),
        version="1.0.0",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Accept a natural-language question.
    Returns: sql, columns, rows, chart_json, message.
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    sql         = None
    columns     = []
    rows        = []
    chart_json  = None
    error_msg   = None
    message     = ""

    try:
        vn = get_vanna()

        # ── 1. Generate SQL ───────────────────────────────────────────────────
        sql = vn.generate_sql(question)

        if not sql:
            return ChatResponse(
                question=question, sql=None, columns=[], rows=[],
                row_count=0, chart_json=None,
                message="Could not generate SQL for this question.",
                error="No SQL generated",
            )

        sql = sql.strip()

        # ── 2. Validate SQL ───────────────────────────────────────────────────
        valid, reason = validate_sql(sql)
        if not valid:
            return ChatResponse(
                question=question, sql=sql, columns=[], rows=[],
                row_count=0, chart_json=None,
                message=f"SQL validation failed: {reason}",
                error=reason,
            )

        # ── 3. Execute SQL ────────────────────────────────────────────────────
        raw_rows = run_sql(sql)

        if not raw_rows:
            return ChatResponse(
                question=question, sql=sql, columns=[], rows=[],
                row_count=0, chart_json=None,
                message="Query executed successfully but returned no results.",
                error=None,
            )

        columns = list(raw_rows[0].keys())
        rows    = raw_rows

        # ── 4. Chart ──────────────────────────────────────────────────────────
        if req.generate_chart:
            df         = pd.DataFrame(rows)
            chart_json = generate_chart(df, question)

        message = f"Query returned {len(rows)} row(s)."

    except sqlite3.Error as e:
        error_msg = f"Database error: {e}"
        message   = "SQL execution failed."
        print(f"[DB Error] {e}\nSQL: {sql}")

    except Exception as e:
        error_msg = str(e)
        message   = "An unexpected error occurred."
        print(f"[Error] {traceback.format_exc()}")

    return ChatResponse(
        question=question,
        sql=sql,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        chart_json=chart_json,
        message=message,
        error=error_msg,
    )


# ── dev entrypoint ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
