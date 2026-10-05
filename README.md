# Blog Writer - Refactored Architecture

The original monolithic script has been split by responsibility while keeping
the same LangGraph execution flow.

## Architecture

```text
                         ┌─────────────┐
                         │    START    │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │    Router   │
                         └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              needs research?              │
                    │                       │
              ┌─────▼─────┐                 │
              │  Research │                 │
              └─────┬─────┘                 │
                    │                       │
                    └───────────┬───────────┘
                                │
                         ┌──────▼──────┐
                         │Orchestrator │
                         │  (Plan)     │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │   Fan-out   │
                         └──────┬──────┘
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
              Worker 1      Worker 2      Worker N
                  └─────────────┼─────────────┘
                                │
                    ┌───────────▼───────────┐
                    │    Reducer Subgraph  │
                    │                       │
                    │ merge_content         │
                    │       ↓               │
                    │ decide_images         │
                    │       ↓               │
                    │ generate_and_place... │
                    └───────────┬───────────┘
                                │
                         ┌──────▼──────┐
                         │     END     │
                         └─────────────┘
```

## Folder structure

```text
blog_writer_refactored/
│
├── main.py
├── README.md
│
└── app/
    ├── __init__.py
    ├── config.py
    ├── schemas.py
    ├── state.py
    ├── graph.py
    │
    ├── nodes/
    │   ├── __init__.py
    │   ├── router.py
    │   ├── research.py
    │   ├── orchestrator.py
    │   └── worker.py
    │
    └── reducer/
        ├── __init__.py
        ├── graph.py
        ├── nodes.py
        └── image_generation.py
```

## What belongs where?

| File | Responsibility |
|---|---|
| `schemas.py` | Pydantic models: Task, Plan, Evidence, ImageSpec |
| `state.py` | Shared LangGraph `State` |
| `config.py` | Environment loading and shared LLM |
| `nodes/router.py` | Research decision and routing |
| `nodes/research.py` | Tavily search + evidence cleanup |
| `nodes/orchestrator.py` | Blog plan + worker fan-out |
| `nodes/worker.py` | Writes individual blog sections |
| `reducer/nodes.py` | Merge sections + image planning + image placement |
| `reducer/image_generation.py` | Gemini image API + filename utility |
| `reducer/graph.py` | Reducer subgraph wiring |
| `graph.py` | Main graph wiring |
| `main.py` | Simple application entry point |

## Important import

The compiled graph is now:

```python
from main import app
```

or:

```python
from app.graph import app
```

## Environment variables

The code expects:

```env
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

`TAVILY_API_KEY` is optional for closed-book topics.

`GOOGLE_API_KEY` is only required when the image generation stage actually
needs to create an image.

## Why this structure is easier to maintain

- Change routing logic -> `app/nodes/router.py`
- Change Tavily/research logic -> `app/nodes/research.py`
- Change blog planning -> `app/nodes/orchestrator.py`
- Change section-writing behavior -> `app/nodes/worker.py`
- Change image decisions -> `app/reducer/nodes.py`
- Change Gemini implementation -> `app/reducer/image_generation.py`
- Change graph connections -> `app/graph.py`
- Change shared state -> `app/state.py`
- Change schemas -> `app/schemas.py`

The reducer remains a real LangGraph subgraph, so its three-node flow is
preserved instead of flattening it into the main graph.


