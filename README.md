# Autonomous Research Agent

An autonomous research system built with LangGraph, FastAPI, Redis, and Qdrant. It breaks down complex queries, fetches web/academic resources (using Tavily and ArXiv APIs), stores context in short-term/long-term memory, and synthesizes reports with complete citations and confidence scores.

## Architecture


![Autonomous Multi-agent research architecture](/assets/img/architecture.png "architecture diagram")

<!-- ```mermaid
graph TD
    User([User Query]) --> API[FastAPI API]
    API --> Graph[LangGraph State Machine]
    
    subgraph Agents [Agent System]
        Graph --> Planner[Planner Agent]
        Planner --> Researcher[Researcher Agent]
        Researcher --> Writer[Writer Agent]
    end

    subgraph Tools [Integration Tools]
        Researcher --> Tavily[Tavily Search API]
        Researcher --> Arxiv[ArXiv PDF Parser]
        Researcher --> Scraper[Web Scraper]
    end

    subgraph Memory [Context & Storage]
        Graph --> Redis[(Redis Short-Term Cache)]
        Researcher --> Qdrant[(Qdrant Vector DB)]
        Writer --> Qdrant
    end

    Writer --> Output[Synthesized Report]
``` -->

## Folder Structure

```
research-agent/
├── agents/            # Core agent reasoning logic (Planner, Researcher, Writer)
├── tools/             # Search, scraping, and document retrieval utilities
├── memory/            # State caching (Redis) and vector search (Qdrant)
├── graph/             # LangGraph state machine definition
├── output/            # Formatting and citation verification
├── api/               # FastAPI endpoints (/research, /status, /report)
├── observability/     # OpenTelemetry, LangSmith, and Prometheus metrics
├── tests/             # Unit and integration test suites
└── deploy/            # Docker and Prometheus configurations
```

## Getting Started

1. Copy `.env.example` to `.env` and fill in API keys:
   ```bash
   cp .env.example .env
   ```

2. Start the app locally before shipping a Docker build:
   ```bash
   chmod +x scripts/run-local.sh
   ./scripts/run-local.sh
   ```

   Optional flags:
   ```bash
   ./scripts/run-local.sh --port 9000
   ./scripts/run-local.sh --no-deps
   ./scripts/run-local.sh --dry-run
   ```

3. Start the services using Docker Compose:
   ```bash
   docker compose -f deploy/docker-compose.yml up --build
   ```

4. Trigger a research task:
   ```bash
   curl -X POST http://localhost:8000/api/v1/research \
     -H "Content-Type: application/json" \
     -d '{"query": "Room temperature superconductivity developments in 2026"}'
   ```

## Walkthrough

The graph-memory workflow can be exercised locally with mocks so you do not need live Redis or Qdrant services for the first pass.

1. Run the focused test suite:
   ```bash
   venv/bin/pytest tests/test_graph_memory.py -q
   ```
2. Run the linter and formatter checks:
   ```bash
   venv/bin/ruff check .
   venv/bin/ruff format --check .
   ```
3. For a manual smoke test, invoke the graph entry point with a simple query:
   ```bash
   venv/bin/python run_graph.py "Latest achievements in warm superconductors"
   ```

The tests cover:
- Redis-backed short-term session persistence.
- Qdrant-backed document storage and vector retrieval.
- End-to-end routing through the planner, researcher, and writer nodes in the LangGraph workflow.

