# My-Workflow-Engine
# Minimal Agent Workflow Engine (LangGraph-Style)

This project implements a **small workflow/graph engine** similar to a simplified version of LangGraph.  
The engine allows you to define:

- Nodes (Python functions called “tools”)
- Edges (routing between nodes)
- Shared state passed across steps
- Conditional branching
- Loops
- FastAPI endpoints to create and run workflows

A sample workflow (**Summarization + Refinement**) is included to demonstrate how the engine works.

---

# 📁 Project Structure

my-workflow-engine/
│
├── app/
│ ├── init.py
│ ├── main.py # FastAPI app + routes
│ ├── engine.py # Graph engine (nodes, edges, state, runs)
│ ├── models.py # Pydantic request/response models
│ ├── tools.py # Tool registry + tool implementations
│ └── workflows.py # Example workflow creation
│
├── requirements.txt
└── README.md

---

# ⚙️ Features of the Workflow Engine

### ✅ 1. Graph Execution Engine
- Each node maps to a Python tool function  
- Each tool receives and updates the shared state  
- A graph is a set of nodes + edges  
- Supports:
  - Linear transitions (`A → B`)
  - Conditional transitions (`if state[key] > X → go to node C`)
  - Loops (`refine → evaluate → refine`)  
- Execution produces an **execution log**

### ✅ 2. Tool Registry
Tools are simple Python functions:

```python
def tool(state: dict, config: dict) -> dict:
    return {"new_key": "new_value"}

registry.register("tool_name", tool_function)


3.FastAPI Endpoints
| Endpoint                      | Description                       |
| ----------------------------- | --------------------------------- |
| **POST /graph/create**        | Create a workflow graph from JSON |
| **POST /graph/run**           | Run a graph end-to-end            |
| **GET /graph/state/{run_id}** | Fetch previous run state + logs   |



Installation Guide (macOS / Windows / VS Code) — Very Clear Steps

Follow these steps exactly to run the project.

1️⃣ Install Python 3

Check your Python version:

python3 --version


If missing, install from:

https://www.python.org/downloads/

2️⃣ Clone or Create the Project Folder

Example:

my-workflow-engine/
    app/
    requirements.txt


Move into the project folder:

cd ~/my-workflow-engine


Replace the path if your folder is elsewhere.

3️⃣ Create a Virtual Environment (Optional but Recommended)
python3 -m venv venv
source venv/bin/activate


Windows:

venv\Scripts\activate

4️⃣ Install Dependencies
If you're using macOS / zsh:

zsh treats uvicorn[standard] as a pattern.
So install using quotes:

python3 -m pip install "uvicorn[standard]" fastapi pydantic


Or install everything at once:

python3 -m pip install -r requirements.txt

5️⃣ Verify Uvicorn Installation
python3 -m uvicorn --help


If help text appears → Uvicorn installed correctly.

6️⃣ Run the FastAPI Server

Run from your project root (not inside /app):

python3 -m uvicorn app.main:app --reload

