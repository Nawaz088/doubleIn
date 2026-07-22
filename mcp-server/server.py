#!/usr/bin/env python3
"""
DoubleHQ Clone — MCP Server
Exposes the entire codebase (models, endpoints, pages, components, docs)
via MCP tools so AI assistants can explore the project efficiently.
"""

import re
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND = PROJECT_ROOT / "backend"
FRONTEND = PROJECT_ROOT / "frontend"
MODELS_DIR = BACKEND / "app" / "models"
ENDPOINTS_DIR = BACKEND / "app" / "api" / "v1" / "endpoints"
SCHEMAS_DIR = BACKEND / "app" / "schemas"
SERVICES_DIR = BACKEND / "app" / "services"
PAGES_DIR = FRONTEND / "src" / "pages"
COMPONENTS_DIR = FRONTEND / "src" / "components"
TYPES_DIR = FRONTEND / "src" / "types"

mcp = FastMCP(
    "doublehq-mcp",
    instructions="""DoubleHQ Clone MCP Server — provides tools for exploring this accounting SaaS codebase.

Use this server to:
- List all database models (tables + columns)
- List all API endpoints (routes + HTTP methods)
- List all frontend pages (routes + components)
- Search the codebase with grep
- Read any file in the project
- Get architecture overviews
- Read project documentation (AGENTS.md, BUSINESS.md, TODO.md)
- List frontend components by directory
- List TypeScript type definitions

All paths are relative to the project root: /home/nawaz/Documents/Nawaz/doublehq-clone/
""",
)


# ─── Utility ─────────────────────────────────────────────────────────────────


def _safe_read(filepath: Path, offset: int, limit: int) -> str:
    if not filepath.exists():
        return f"File not found: {filepath}"
    try:
        lines = filepath.read_text().splitlines()
    except Exception as e:
        return f"Read error: {e}"
    total = len(lines)
    if offset < 1:
        offset = 1
    if limit < 1:
        limit = 200
    start = offset - 1
    end = start + limit
    snippet = lines[start:end]
    numbered = []
    for i, line in enumerate(snippet, start=start + 1):
        numbered.append(f"{i}: {line}")
    header = f"{filepath.relative_to(PROJECT_ROOT)}  (lines {offset}-{min(end, total)} of {total})\n"
    return header + "\n".join(numbered)


def _parse_model_file(filepath: Path) -> list[dict]:
    """Extract table names and columns from a SQLAlchemy model file."""
    content = filepath.read_text()
    tables = []
    current_table = None
    for line in content.splitlines():
        class_match = re.match(r"class\s+(\w+)\(BaseModel\)", line)
        if class_match:
            current_table = class_match.group(1)
            tables.append({"class": current_table, "table": "", "columns": []})
            continue

        table_match = re.search(r'__tablename__\s*=\s*"([^"]+)"', line)
        if table_match and current_table:
            tables[-1]["table"] = table_match.group(1)
            continue

        col_match = re.match(
            r"\s+(\w+)\s*:\s*Mapped\[(.+?)\]\s*=\s*mapped_column\((.+)\)",
            line,
        )
        if col_match and current_table and tables:
            col_name = col_match.group(1)
            col_type = col_match.group(2).strip()
            col_opts = col_match.group(3).strip()
            fk_match = re.search(r'ForeignKey\("(\w+)\.(\w+)"\)', col_opts)
            tables[-1]["columns"].append(
                {
                    "name": col_name,
                    "type": col_type,
                    "foreign_key": f"{fk_match.group(1)}.{fk_match.group(2)}" if fk_match else None,
                }
            )
    return tables


def _parse_endpoint_file(filepath: Path, prefix: str = "") -> list[dict]:
    """Extract routes and HTTP methods from a FastAPI endpoint file."""
    content = filepath.read_text()
    endpoints = []
    for line in content.splitlines():
        match = re.search(
            r"@router\.(get|post|put|delete|patch)\s*\(\s*\"([^\"]+)\"",
            line,
        )
        if match:
            method = match.group(1).upper()
            path = prefix + match.group(2)
            endpoints.append({"method": method, "path": f"/api/v1{path}"})
    return endpoints


# ─── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def list_models(model_file: str = "") -> str:
    """List all SQLAlchemy database models with their table names and columns.
    
    Args:
        model_file: Optional specific model filename (e.g. 'accounting.py', 'tax.py').
                    If empty, lists all models.
    """
    results = []
    files = (
        [MODELS_DIR / model_file]
        if model_file
        else sorted(MODELS_DIR.glob("*.py"))
    )
    for fp in files:
        if fp.name.startswith("_") or fp.name == "base.py":
            continue
        tables = _parse_model_file(fp)
        if not tables:
            continue
        results.append(f"=== {fp.name} ===")
        for t in tables:
            results.append(f"\n  class {t['class']} → table: {t['table']}")
            for col in t["columns"]:
                fk = f" (FK → {col['foreign_key']})" if col["foreign_key"] else ""
                results.append(f"    • {col['name']}: {col['type']}{fk}")
        results.append("")
    return "\n".join(results) if results else "No models found."


@mcp.tool()
def list_endpoints(endpoint_file: str = "") -> str:
    """List all FastAPI API endpoints with HTTP methods and full paths.
    
    Args:
        endpoint_file: Optional specific endpoint filename (e.g. 'clients.py', 'tax.py').
                       If empty, lists all endpoints grouped by prefix.
    """
    with open(ENDPOINTS_DIR.parent / "__init__.py") as f:
        router_init = f.read()

    prefix_map = {}
    for line in router_init.splitlines():
        match = re.search(
            r'include_router\((\w+)\.router,\s*prefix="([^"]+)"',
            line,
        )
        if match:
            module_name = match.group(1)
            prefix_map[module_name] = match.group(2)

    module_to_file = {
        "auth": "auth.py",
        "scorecards": "scorecards.py",
        "clients": "clients.py",
        "tasks": "tasks.py",
        "task_lists": "task_lists.py",
        "bank": "bank.py",
        "journal": "journal.py",
        "reports": "reports.py",
        "file_review": "file_review.py",
        "portal": "portal.py",
        "tax": "tax.py",
        "receipts": "receipts.py",
        "accruals": "accruals.py",
        "inbox": "inbox.py",
        "integrations": "integrations.py",
        "org": "org.py",
        "users": "users.py",
        "files": "files.py",
        "webhooks": "webhooks.py",
    }

    results = []
    files_to_scan = (
        [ENDPOINTS_DIR / endpoint_file]
        if endpoint_file
        else None
    )

    if endpoint_file:
        # Find prefix for this file
        file_module = None
        for mod, fname in module_to_file.items():
            if fname == endpoint_file:
                file_module = mod
                break
        prefix = prefix_map.get(file_module or endpoint_file.replace(".py", ""), "")
        eps = _parse_endpoint_file(ENDPOINTS_DIR / endpoint_file, prefix)
        results.append(f"=== {endpoint_file} ===")
        for ep in eps:
            results.append(f"  {ep['method']:7s} {ep['path']}")
    else:
        for module, fname in module_to_file.items():
            fp = ENDPOINTS_DIR / fname
            if not fp.exists():
                continue
            prefix = prefix_map.get(module, "")
            eps = _parse_endpoint_file(fp, prefix)
            if eps:
                results.append(f"=== {module} ({fname}) ===")
                for ep in eps:
                    results.append(f"  {ep['method']:7s} {ep['path']}")
                results.append("")
    return "\n".join(results) if results else "No endpoints found."


@mcp.tool()
def list_pages() -> str:
    """List all frontend React pages with their routes (from App.tsx router)."""
    app_tsx = FRONTEND / "src" / "App.tsx"
    content = app_tsx.read_text()
    lines = []
    for line in content.splitlines():
        match = re.search(r'<Route\s+path="([^"]+)"\s+element=\{<(\w+)\s*/>\}', line)
        if match:
            lines.append(f"  {match.group(1):35s} → {match.group(2)}")
    return "=== Frontend Routes (App.tsx) ===\n\n" + "\n".join(sorted(lines))


@mcp.tool()
def search_codebase(query: str) -> str:
    """Search the entire codebase for a regex pattern or string.
    
    Args:
        query: Regex pattern or plain string to search for.
               Examples: 'class.*BaseModel', 'router\\.get', 'Mapped\\[', 'useState'
    """
    import subprocess
    try:
        result = subprocess.run(
            ["grep", "-rn",
             "--exclude-dir=.venv", "--exclude-dir=node_modules",
             "--exclude-dir=dist", "--exclude-dir=__pycache__",
             "--exclude-dir=.git",
             "--include=*.py", "--include=*.tsx", "--include=*.ts",
             "--include=*.md", "--include=*.yml", "--include=*.json",
             query,
             str(PROJECT_ROOT / "backend"),
             str(PROJECT_ROOT / "frontend" / "src"),
             str(PROJECT_ROOT)],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()
        if not output:
            return f"No matches found for: {query}"
        lines = output.split("\n")
        if len(lines) > 100:
            return "\n".join(lines[:100]) + f"\n\n... and {len(lines) - 100} more matches."
        return output
    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def read_file(path: str, offset: int = 1, limit: int = 200) -> str:
    """Read a file from the project with optional offset and line limit.

    Args:
        path: File path relative to project root.
              Examples: 'backend/app/models/tax.py', 'frontend/src/pages/TaxPage.tsx'
        offset: Line number to start from (1-indexed). Default: 1
        limit: Maximum number of lines to return. Default: 200
    """
    return _safe_read(PROJECT_ROOT / path, offset, limit)


@mcp.tool()
def get_module(module_name: str) -> str:
    """Get comprehensive details about a specific module/feature area.

    Args:
        module_name: One of: auth, clients, tasks, bank-feeds, journal-entries,
                     file-review, reports, receipts, accruals, portal, inbox,
                     tax, integrations, scorecards, settings, org, users
    """
    with open(PROJECT_ROOT / "AGENTS.md") as f:
        agents = f.read()

    sections = {
        "auth": ["Week 1", "Auth:", "Users & Organizations", "JWT"],
        "clients": ["Week 2", "Clients", "CRM"],
        "tasks": ["Weeks 3-4", "Task Management", "TaskList", "Close Page"],
        "bank-feeds": ["Bank Feed", "BankConnection", "Week 8"],
        "journal-entries": ["Journal Entries", "Week 9"],
        "file-review": ["File Review", "Week 10"],
        "reports": ["Week 11", "ReportPackage", "ReportSection"],
        "receipts": ["Week 13", "Receipts", "Tesseract OCR"],
        "accruals": ["Week 14", "AccrualSchedule", "AccrualEntry"],
        "portal": ["Week 12", "PortalMessage", "Client Portal"],
        "inbox": ["Week 16", "Email Inbox", "EmailMessage"],
        "tax": ["Week 15", "Tax Suite", "TaxReturn", "TaxOrganizer"],
        "integrations": ["QBO", "Xero", "Integration", "OAuth"],
        "scorecards": ["scorecard"],
        "settings": ["OrganizationSettings", "SettingsPage"],
        "org": ["OrgMembership", "Organization"],
        "users": ["users", "User"],
    }

    keywords = sections.get(module_name.lower(), [module_name])

    # Find the API prefix
    with open(ENDPOINTS_DIR.parent / "__init__.py") as f:
        router_init = f.read()

    prefix_line = ""
    for line in router_init.splitlines():
        if module_name.lower().replace("-", "_") in line.lower() and 'include_router' in line:
            prefix_line = line.strip()
            break

    # Find relevant models
    model_files = []
    endpoint_files = []
    page_files = []

    prefix_map = {
        "auth": "auth", "clients": "clients", "tasks": "tasks",
        "bank-feeds": "bank", "journal-entries": "journal",
        "file-review": "file_review", "reports": "reports",
        "receipts": "receipts", "accruals": "accruals",
        "portal": "portal", "inbox": "inbox", "tax": "tax",
        "integrations": "integrations", "scorecards": "scorecards",
        "org": "org", "users": "users",
    }

    ep_file = prefix_map.get(module_name.lower(), module_name.lower().replace("-", "_"))

    # Find model files
    for mp in MODELS_DIR.glob("*.py"):
        if mp.name.startswith("_"):
            continue
        content = mp.read_text()
        for kw in keywords:
            if kw.lower() in content.lower():
                model_files.append(mp.name)
                break

    # Find endpoint
    ep_path = ENDPOINTS_DIR / f"{ep_file}.py"
    if ep_path.exists():
        endpoint_files.append(ep_path)

    # Find pages  
    for pp in PAGES_DIR.glob("*.tsx"):
        pname = pp.stem.lower()
        if any(kw.lower() in pname for kw in keywords):
            page_files.append(pp.name)

    output = [f"=== Module: {module_name} ===\n"]
    
    if prefix_line:
        output.append(f"API Prefix: {prefix_line}\n")

    output.append("--- Models ---")
    if model_files:
        for mf in model_files:
            output.append(f"  backend/app/models/{mf}")
            tables = _parse_model_file(MODELS_DIR / mf)
            for t in tables:
                output.append(f"    class {t['class']} → table: {t['table']}")
                for col in t["columns"]:
                    fk = f" → FK({col['foreign_key']})" if col["foreign_key"] else ""
                    output.append(f"      {col['name']}: {col['type']}{fk}")
    else:
        output.append("  (no specific models — see accounting.py for Client/Task)")

    output.append("\n--- API Endpoints ---")
    if endpoint_files:
        for ef in endpoint_files:
            eps = _parse_endpoint_file(ef, f"/{ep_file}")
            for ep in eps:
                output.append(f"  {ep['method']:7s} {ep['path']}")
    else:
        output.append(f"  (no endpoint file at endpoints/{ep_file}.py)")

    output.append("\n--- Frontend Pages ---")
    if page_files:
        for pf in page_files:
            output.append(f"  frontend/src/pages/{pf}")
    else:
        output.append("  (no dedicated page found)")

    return "\n".join(output)


@mcp.tool()
def get_architecture() -> str:
    """Get the project architecture overview: tech stack, directory structure, 
    infrastructure layout, and module relationships."""
    return """=== DoubleHQ Clone — Architecture Overview ===

TECH STACK:
  Frontend: Vite + React 19 + TypeScript + Tailwind CSS v4 + Radix UI + shadcn/ui
  Backend:  Python 3.12+ / FastAPI + SQLAlchemy 2.0 (async) + Alembic
  Database: PostgreSQL 16
  Cache:    Redis + Celery
  Auth:     JWT (access + refresh tokens)
  Storage:  S3-compatible (MinIO dev / AWS S3 prod)
  OCR:      Tesseract (self-hosted)
  PDF:      WeasyPrint
  Real-time: WebSocket via FastAPI
  Email:    SendGrid / Resend

DIRECTORY STRUCTURE:
  backend/
    app/
      api/v1/endpoints/   — 19 endpoint files (auth, clients, tasks, bank, ...)
      models/             — 9 model files (~32 DB tables)
      schemas/            — Pydantic request/response schemas
      services/           — Business logic (QBO, Xero, OCR, PDF, email, storage)
      core/               — Config, security, database, middleware, rate limiting
      seeders/            — Prebuilt KPI definitions
    docker-compose.yml
    requirements.txt
  frontend/
    src/
      pages/              — 25 page components
      components/ui/      — shadcn components (button, card, input, badge)
      components/layout/  — AppLayout with sidebar
      context/            — AuthContext, ThemeContext
      api/                — apiFetch client with auto-refresh
      types/              — TypeScript interfaces
      hooks/              — Custom hooks
  mcp-server/             — This MCP server
  infra/                  — Nginx config, backup script
  docs/                   — (empty)

INFRASTRUCTURE (Single Hetzner VPS):
  ┌─ FastAPI (4 uvicorn workers)
  ├─ Nginx reverse proxy
  ├─ PostgreSQL 16
  ├─ Redis
  ├─ Celery worker
  └─ MinIO (object storage)

API ROUTE TREE:
  /api/v1/auth/          — Login, register, refresh, magic-link
  /api/v1/scorecards/    — Scorecards, KPIs, templates, entries
  /api/v1/clients/       — Client CRUD, dashboard
  /api/v1/task-lists/    — Task list CRUD, reorder
  /api/v1/tasks/         — Task CRUD, comments, attachments
  /api/v1/bank-feeds/    — Bank connections, transactions, rules
  /api/v1/journal-entries/ — JE CRUD, post to ledger
  /api/v1/reports/       — Report packages, sections, PDF export
  /api/v1/file-review/   — Review reports, findings
  /api/v1/portal/        — Messages, documents, branding
  /api/v1/tax/           — Tax returns, organizers, signatures
  /api/v1/receipts/      — Receipt upload, OCR, post
  /api/v1/accruals/      — Accrual schedules, entries
  /api/v1/inbox/         — Email messages
  /api/v1/integrations/  — QBO/Xero OAuth, sync
  /api/v1/org/           — Org settings, members
  /api/v1/users/         — User profile, preferences
  /api/v1/files/         — File upload, presigned URLs
  /api/v1/webhooks/      — QBO/Xero/SendGrid receivers

KEY MODULES:
  CRM          — Client management with custom properties (JSONB)
  Task Mgmt    — Close page, task lists, subtasks, comments, attachments
  Bank Feeds   — Transaction import, classification rules, bulk actions
  Journal      — JE creation, line items, posting to QBO/Xero
  Reports      — Report package builder, section config, PDF via WeasyPrint
  File Review  — Rule-based review reports with findings
  Scorecards   — KPI tracking, templates, attendees, action items
  Receipts     — Tesseract OCR, drag-drop upload, coding
  Accruals     — Straight-line amortization, schedule management
  Tax          — Tax returns, organizers, e-signatures
  Client Portal — White-label portal, messaging, document sharing
  Email Inbox  — Team inbox, convert-to-task
  Integrations — QBO/Xero OAuth 2.0, sync engine, webhooks
"""


@mcp.tool()
def read_doc(doc_name: str = "") -> str:
    """Read project documentation files.
    
    Args:
        doc_name: One of 'AGENTS.md', 'BUSINESS.md', 'TODO.md'.
                  If empty, lists available docs.
    """
    docs = {
        "AGENTS.md": PROJECT_ROOT / "AGENTS.md",
        "BUSINESS.md": PROJECT_ROOT / "BUSINESS.md",
        "TODO.md": PROJECT_ROOT / "TODO.md",
    }
    if not doc_name:
        return "Available docs: " + ", ".join(f"'{k}'" for k in docs)
    if doc_name not in docs:
        return f"Doc not found. Available: {list(docs.keys())}"
    return _safe_read(docs[doc_name], 1, 500)


@mcp.tool()
def list_components(directory: str = "") -> str:
    """List all frontend React components organized by directory.
    
    Args:
        directory: Optional subdirectory under components/ (e.g. 'ui', 'layout').
                   If empty, lists all.
    """
    base = COMPONENTS_DIR
    if directory:
        base = base / directory

    results = []
    for root, dirs, files in os.walk(base):
        for f in sorted(f for f in files if f.endswith((".tsx", ".ts"))):
            rel = os.path.relpath(os.path.join(root, f), COMPONENTS_DIR)
            results.append(f"  {rel}")

    if not results:
        return f"No components found in components/{directory or ''}"

    header = f"=== Frontend Components" + (f" / {directory}" if directory else "") + " ===\n\n"
    return header + "\n".join(results)


@mcp.tool()
def list_types() -> str:
    """List all frontend TypeScript type definitions from types/index.ts."""
    return _safe_read(TYPES_DIR / "index.ts", 1, 500)


if __name__ == "__main__":
    mcp.run(transport="stdio")
