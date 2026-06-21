# Workflow Documentation

---

## 📚 Project Overview
The **Multi‑Agent Conversational CSV Analytics System** is a Python‑based platform that enables users to ask natural‑language questions about CSV data files.  It orchestrates several agents:

1. **LLM Service** – communicates with a large language model (LLM) to interpret user queries.
2. **EXA Service** – performs vector‑search and retrieval over CSV rows.
3. **History Service** – stores conversation history for context preservation.
4. **Planner / Response Agents** – decide which tool to call and format the final answer.
5. **Context Files** – JSON descriptors for each CSV (e.g., `employees_context.json`).

The system is **container‑agnostic**; you can run it locally, in a virtual environment, or inside Docker.

---

## 🏗️ High‑Level Architecture
```
+-------------------+        +-------------------+        +-------------------+
|   Front‑end UI   | <----> |   llm_service.py | <----> |   LLM (API)       |
+-------------------+        +-------------------+        +-------------------+
                                  |
                                  | calls
                                  v
                          +-------------------+
                          |   planner_agent   |
                          +-------------------+
                                  |
           +-----------+----------+-----------+-----------+-----------+
           |           |                      |           |           |
           v           v                      v           v           v
+----------------+ +----------------+   +----------------+ +----------------+
| exa_service   | | history_service|   | response_agent| | utils (CSV)    |
+----------------+ +----------------+   +----------------+ +----------------+
```

---

## 🚀 Getting Started (Beginner Friendly)
### 1️⃣ Prerequisites
- **Python 3.10+**
- **Git** (already installed for pushing changes)
- An **OpenAI‑compatible API key** (or any LLM endpoint you prefer)
- **Virtual environment** (recommended)

### 2️⃣ Clone the Repo (if not already)
```bash
git clone https://github.com/HARRYSP-DOTCOM/Multi-Agent-Conversational-CSV-Analytics-System-using-LangGraph.git
cd Multi-Agent-Conversational-CSV-Analytics-System-using-LangGraph
```

### 3️⃣ Set Up the Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

### 4️⃣ Configure Secrets
Create a `.env` file at the project root with:
```
LLM_API_KEY=your‑api‑key‑here
```
*(The code loads this file automatically.)*

### 5️⃣ Run the Service
```bash
uvicorn services.llm_service:app --reload
```
The API will be reachable at `http://127.0.0.1:8000`.

---

## 🧭 Typical Question Flow (What the system does)
1. **User sends a natural‑language query** to the FastAPI endpoint `/query`.
2. **LLM Service** forwards the query to the **Planner Agent**.
3. **Planner Agent** decides which tool is needed (e.g., EXA for data lookup).
4. **EXA Service** performs a vector search on the relevant CSV and returns matching rows.
5. **Response Agent** formats those rows into a friendly answer.
6. The answer is sent back to the user, and the **History Service** stores the interaction for future context.

---

## ✅ Test Suite Overview
The repository contains three layers of tests located under the `tests/` folder.
| Layer | Purpose | Example File |
|-------|---------|--------------|
| **Unit** | Test individual functions (CSV parsing, prompt generation) | `tests/unit/test_utils.py` |
| **Integration** | Verify interaction between services (e.g., Planner → EXA) | `tests/integration/test_query_flow.py` |
| **End‑to‑End** | Spin up the FastAPI app and send HTTP requests | `tests/e2e/test_api.py` |

### How to Run All Tests
```bash
pytest -vv
```
*If you only want a specific layer:* `pytest tests/unit`, `pytest tests/integration`, or `pytest tests/e2e`.

### Sample Test Cases (What they cover)
- **CSV Loader** – correct handling of headers, missing values, and datatype conversion.
- **Prompt Builder** – ensures the LLM receives the expected system prompt.
- **Planner Decision Logic** – verifies that a query about "total sales" triggers the EXA service, not the History service.
- **EXA Retrieval** – returns the exact number of rows requested and respects filters.
- **Response Formatting** – checks markdown tables are correctly generated.
- **History Persistence** – a conversation ID is stored and can be retrieved later.
- **Error Paths** – malformed CSV, missing API key, or LLM timeout all produce graceful error messages.

---

## 🔀 Hybrid Question Flow (Data + Reasoning)
Some user queries require **both** a direct data lookup **and** LLM‑driven synthesis.  
Example: *"What was the average salary of employees in the Sales department, and how does it compare to the overall average?"*

The system handles this in two coordinated passes:
1. **Planner Agent** parses the question and detects multiple intents (data retrieval + comparative reasoning).  
2. **First Pass – EXA Service** executes the data‑only part (`SELECT AVG(salary) FROM employees WHERE department='Sales'`).  
3. **Second Pass – LLM Service** receives the raw statistics *plus* the original query, prompting the LLM to generate a natural‑language comparison (e.g., “The Sales average is 12 % higher than the company‑wide average”).  
4. **Response Agent** merges the numeric result with the LLM’s narrative into a single formatted answer.  
5. **History Service** records both sub‑answers for future context.

The flow diagram:
```
User Query → Planner → [EXA → raw metrics] → LLM (with metrics) → Response → User
```

This hybrid approach ensures **accuracy** (exact numbers from the CSV) while providing **insightful explanation** from the LLM.

---

## 🛠️ Extending the Project (For Future Work)
1. **Add a new CSV context** – drop a `.csv` file in `uploads/` and create a matching JSON descriptor in `contexts/`.
2. **Create a new agent** – implement a class in `agents/`, register it in `services/agent_registry.py`.
3. **Write additional tests** – follow the existing structure; place new tests in the appropriate sub‑folder.

---

## 📖 Quick Reference Cheat‑Sheet
| Command | What it Does |
|--------|--------------|
| `git status` | Shows changed files |
| `uvicorn services.llm_service:app --reload` | Starts the API |
| `pytest -k test_exa` | Runs only EXA‑related tests |
| `python -m scripts/generate_context.py uploads/employees.csv` | Generates `employees_context.json` |

---

## 🎉 You’re Ready!
Follow the **Getting Started** steps, explore the **Test Suite**, and experiment by sending queries to the live endpoint.  All code paths are documented in the source files, and the above workflow should give you a clear mental model of how each piece fits together.

---

*If you need a deeper dive into any section (e.g., the exact JSON schema of a context file or the Planner decision tree), just let me know!*
