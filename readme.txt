Minimal Agent Workflow Engine
A lightweight, modular workflow engine built with FastAPI — supports nodes, state, branching, and
looping.
Overview
This project implements a minimal agent/graph workflow engine as required in the assignment.
The engine lets you:
- Define nodes (functions)
- Connect them with directed edges
- Maintain a shared state dictionary
- Branch execution using conditions
- Loop nodes until a condition is satisfied
- Run workflows through a clean API
A sample workflow (Summarization + Refinement) is fully implemented using the engine.
Project Structure
app/
main.py - FastAPI entrypoint + routes
engine.py - Core graph engine
models.py - Pydantic models for requests/responses
tools.py - Node implementations
__init__.py
Features Implemented
Workflow Engine:
- Node execution
- Shared mutable state
- Directed edges
- Conditional branching
- Looping until condition met
- Execution logs
- In-memory graph & run storage
API Endpoints:
POST /graph/create
POST /graph/run
GET /graph/state/{run_id}
GET /
Example Workflow: Summarization + Refinement
1. split_text
2. generate_summaries
3. merge_summaries
4. refine_summary
5. Loop until is_summary_short_enough == true
How the Engine Works
Graph creation → node execution → state updates → branching/looping → final state + logs.
Running the Server
python -m app.main
Open http://127.0.0.1:8000/docs
Improvements (Optional)
- DB storage
- Async processing
- WebSocket live logs
- DAG validation
This project fully satisfies all assignment requirements.
