# 📊 Multi-Agent Conversational CSV Analytics System

> **Academic Submission & Production Architecture Edition**  
> Features an enterprise-grade LangGraph multi-agent architecture implementing **every major Python concept** (OOP, Dunder methods, Metaprogramming Decorators, Context Managers, Generators, Concurrency, Custom Exceptions, and Typing).  
> **Evaluation Documentation:** [PYTHON_CONCEPTS_MANUAL.md](PYTHON_CONCEPTS_MANUAL.md) | [PROJECT_REPORT.md](PROJECT_REPORT.md)  
> **Automated Test Suite:** 41 Unit Tests (100% Passing)

---

## What It Does

- **Multi-Agent Orchestration:** Uses LangGraph to coordinate Query, Retrieval, Analysis, Planning, History, and Response agents.
- **Natural Language to Code:** Generates dynamic Pandas code from natural language using Ollama (`qwen2.5:1.5b`).
- **Safe Sandboxed Execution:** Executes generated code safely in an isolated E2B Code Interpreter sandbox with automated retry correction.
- **Semantic Entity Memory:** Uses SentenceTransformers and FAISS vector indices for semantic fuzzy matching on categorical values.
- **Academic Python Concepts Showcase:** Implements Abstract Base Classes, Dunder protocols, Metaprogramming decorators, Context managers, Streaming generators, ThreadPool concurrency, and Custom Exception hierarchies.

## Quick Start for Evaluation

```powershell
# 1. Run the Live Interactive Python Concepts Demonstration (Recommended for Viva/Professor review)
python run_concepts_demo.py

# 2. Run the Full Automated Test Suite (41 Tests)
python -m unittest discover -s tests -p "test_*.py" -v

# 3. Launch the Streamlit Web Application
streamlit run app.py

# 4. Run CLI Interactive Agent Session
python run_day2.py
```

## Project Layout

```text
.
|-- app.py                         # Streamlit interactive chat UI
|-- run_concepts_demo.py           # Live interactive Python concepts demo for viva
|-- run_day1.py                    # Semantic-memory initialization script
|-- run_day2.py                    # CLI chat runner for LangGraph workflow
|-- requirements.txt               # Python dependencies
|-- PYTHON_CONCEPTS_MANUAL.md      # Professor evaluation guide & syllabus mapping
|-- PROJECT_REPORT.md              # Formal academic project report
|-- core/                          # Foundational Python Architecture
|   |-- base_agent.py              # BaseAgent(abc.ABC) & Template Method pattern
|   |-- base_service.py            # BaseService(abc.ABC) abstract service contract
|   |-- context_managers.py        # BenchmarkTimer & temporary_directory_scope
|   |-- decorators.py              # @retry, @timing_profiler, @memoize, @validate_non_empty
|   |-- enums.py                   # QueryIntent, AgentRoute, ExecutionStatus, DataType
|   |-- exceptions.py              # CSVAnalyticsError domain exception hierarchy
|   |-- logger.py                  # Standard library logging configuration
|   `-- models.py                  # DatasetContainer (dunder methods), @dataclass, namedtuple
|-- agents/                        # Autonomous Agents (Polymorphic BaseAgent subclasses)
|   |-- agent_factory.py           # Factory and Registry Design Patterns
|   |-- query_agent.py             # Generates analytical code with timing profiler
|   |-- analysis_agent.py          # E2B Sandbox executor & retry management
|   |-- planner_agent.py           # Autonomous router (CSV, Web, Hybrid)
|   |-- response_agent.py          # Response formatting & summarization
|   |-- retrieval_agent.py         # FAISS vector store entity resolution
|   |-- history_agent.py           # Conversational memory & DB cache lookup
|   `-- web_search_agent.py        # Real-time web retrieval via Exa API
|-- graphs/
|   `-- analytics_graph.py         # LangGraph StateGraph workflow definition
|-- services/
|   |-- dataset_loader.py          # Concurrent ThreadPool loading & yield streaming
|   |-- context_generator.py       # Parallel column profiling & dataclass manifests
|   |-- upload_service.py          # Upload lifecycle & SHA-256 fingerprinting
|   |-- context_service.py         # Context deserialization & dictionary comprehensions
|   |-- rebuild_service.py         # End-to-end pipeline orchestration
|   |-- llm_service.py             # Ollama LLM prompt engineering
|   `-- e2b_execution_service.py   # E2B sandbox code execution
|-- utils/
|   |-- functional_tools.py        # map, filter, reduce, partial, comprehensions
|   `-- tree_utils.py              # Directory tree formatting utility
|-- tests/                         # Comprehensive Automated Unit Test Suite (41 Tests)
|   |-- test_oop_agents.py         # ABCs, inheritance, polymorphism, __call__, factory
|   |-- test_data_structures.py    # Dataclasses, namedtuples, dunder methods, collections
|   |-- test_decorators.py         # @retry, @timing_profiler, @memoize, @validate_non_empty
|   |-- test_context_managers.py   # Class-based and generator-based context managers
|   |-- test_custom_exceptions.py  # Exception hierarchy, attributes, and chaining
|   |-- test_generators_and_iterators.py # yield streaming, iterator protocol, lazy eval
|   |-- test_concurrency.py        # ThreadPoolExecutor, thread locks, race safety
|   |-- test_functional_tools.py   # map, filter, reduce, partial, comprehensions
|   `-- test_services.py           # DatasetLoader, ContextGenerator, SHA-256 hashing
|-- state/
|   `-- agent_state.py             # Shared TypedDict graph state schema
|-- uploads/                       # Active uploaded CSV files
|-- contexts/                      # Generated dataset context JSON files
|-- vector_store/                  # FAISS index and metadata
`-- sample_data/                   # Example CSV files
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

The code imports the `ollama` Python package in `services/llm_service.py`. If it is not already installed in your environment, install it too:

```powershell
pip install ollama
```

Install and run Ollama locally, then pull the model used by the app:

```powershell
ollama pull qwen2.5:1.5b
```

Create a `.env` file with your E2B key:

```text
E2B_API_KEY=your_e2b_api_key_here
```

## Running The App

Start Streamlit:

```powershell
streamlit run app.py
```

Then open the local Streamlit URL in your browser, upload CSV files, and ask questions in the chat box.

For a command-line flow, run:

```powershell
python run_day2.py
```

## Upload And Rebuild Workflow

When files are uploaded in `app.py`, the following happens:

1. `UploadService.save_files()` deletes old CSV files from `uploads/`.
2. The new CSV files are saved into `uploads/`.
3. `RebuildService.rebuild()` clears old generated memory from `contexts/` and `vector_store/`.
4. `DatasetLoader` loads every CSV in `uploads/` as a pandas DataFrame.
5. `ContextGenerator` profiles each dataset and writes one JSON file per dataset into `contexts/`.
6. `EmbeddingPreparation` selects string columns that look useful for semantic lookup.
7. `EmbeddingService` embeds selected unique values with `sentence-transformers/all-MiniLM-L6-v2`.
8. A FAISS index is written to `vector_store/faiss.index`.
9. Matching metadata is written to `vector_store/metadata.json`.
10. Streamlit clears the cached graph, clears cached datasets, and resets chat history.

**Performance Optimization:** The upload processing block tracks file states (`st.session_state["last_uploaded_files"]`). It only executes the expensive FAISS rebuild and dataset profiling operations when completely new files are uploaded, preventing unnecessary re-computations during normal chat interactions or page reruns.

This means every upload replaces the active working dataset set. The app is designed around the current uploaded CSVs, not a growing historical collection.

## Question Workflow

Every chat question starts in `app.py` with an `AgentState` dictionary:

```python
{
    "question": question,
    "parsed_query": None,
    "retrieval_result": None,
    "analysis_result": None,
    "final_response": None,
    "generated_code": None,
    "execution_result": None
}
```

The graph in `graphs/analytics_graph.py` runs these nodes:

```text
query -> retrieval -> analysis -> response -> END
```

There is also a conditional edge after `analysis`. If generated code fails and the retry count is below 3, the graph loops back to `query` with the error message and previous code so the LLM can repair its code.

## Agent Responsibilities

### Query Agent

`agents/query_agent.py` loads the dataset contexts from `contexts/` and calls `LLMService.generate_python()`.

The generated code must:

- Use the `datasets` dictionary.
- Use exact dataset keys from the context.
- Use exact column names from the schema.
- Store the final answer in a variable named `result`.
- Use pandas operations only.

The current implementation routes all normal questions through this dynamic E2B path.

### Retrieval Agent

`agents/retrieval_agent.py` can resolve fuzzy entity names through the FAISS semantic index. It loads the persisted index and metadata from `vector_store/`.

In the current main workflow, this step is skipped when generated Python code already exists. The deterministic retrieval path remains in the codebase for older aggregation/comparison logic or future hybrid behavior.

### Analysis Agent

`agents/analysis_agent.py` sees generated code and sends it to `E2BExecutionService`.

If the E2B result is an error, the agent stores:

- `error_message`
- `previous_code`
- `retry_count`

LangGraph then routes the state back to the query agent, up to 3 retries.

### Response Agent

`agents/response_agent.py` takes the raw execution result and asks the LLM to produce a concise natural-language summary. The response object keeps both the displayable data and the summary.

## Execution Model

`services/e2b_execution_service.py` creates an E2B sandbox and uploads the current CSV files into it. Before running generated code, it builds a helper prelude that:

- Imports pandas.
- Loads every uploaded CSV into a `datasets` dictionary.
- Exposes the first dataset as `df` for convenience.
- Makes DataFrame column access more forgiving when casing differs.
- Makes common string comparisons case-insensitive.
- Converts simple currency/comma-formatted numeric strings where possible.
- Falls back to the first dataset if generated code requests an unknown dataset key.

After generated code runs, the executor reads the required `result` variable and serializes it into one of these response types:

- `dataframe`
- `series`
- `number`
- `text`
- `error`

Streamlit then renders the response type appropriately.

## Memory Management

The project has several kinds of memory:

### Dataset Files

`uploads/` contains the active CSV files. Uploading new files deletes the previous CSVs. This keeps the app focused on one active dataset collection at a time.

### Dataset Context Memory

`contexts/*.json` files store generated profiles for each CSV. A context includes:

- Dataset name.
- Row and column counts.
- Column names.
- Simplified data types.
- Missing-value counts.
- Numeric min, max, and mean.
- String unique counts and top values.
- Detected date ranges for date-like strings.

These context files are what the LLM sees when generating pandas code.

### Semantic Memory

`vector_store/faiss.index` and `vector_store/metadata.json` store embedded values from useful string columns.

`EmbeddingPreparation` classifies string columns as:

- `identifier` when the unique-value ratio is greater than `0.7`.
- `categorical` when the unique-value ratio is less than or equal to `0.7`.

Unique values from those columns are embedded and saved with metadata:

```json
{
    "value": "John Smith",
    "table": "employees",
    "column": "Employee Name",
    "column_type": "identifier"
}
```

This semantic memory can support fuzzy matching such as resolving a user phrase to an actual CSV value.

### Runtime Cache

Some objects are cached in memory while the app is running:

- `app.py` caches the compiled LangGraph with `@st.cache_resource`.
- `agents.query_agent` caches `LLMService` and `ContextService` module-level instances.
- `agents.analysis_agent` caches loaded datasets in `_datasets`.
- Streamlit stores chat messages in `st.session_state.messages`.

When uploads change, `app.py` clears the graph cache, clears the dataset cache, and resets chat history.

### Conversation Memory (Linear)

Chat history is stored only in Streamlit session state. It is used for display, not as long‑term reasoning memory for the LLM prompts. Each question is answered from the current uploaded data, generated contexts, generated code, and the current graph state.

### Conversation Branching

The app supports branching conversation threads. Every message is stored with a unique `id` and a `parent_id` (the message it branches from). Users can spawn independent, isolated chat threads from any historical AI message.

The UI relies on two numeric toggle buttons (`[1]` and `[2]`):
- **Global View (`[1]`)**: Displays the main chronological conversation. Here, each AI message displays a `[2]` button.
- **Branch View (`[2]`)**: Clicking `[2]` creates an isolated view showing only that specific message and any new follow-up messages you send underneath it. You can return to the main conversation by clicking the `[1]` button at the top of the branch.

The backend stores messages in `st.session_state.messages` as an adjacency-list dictionary keyed by message IDs. Helper functions in `utils/tree_utils.py` support:
- Adding new messages with proper parent links (`add_message`).
- Retrieving the active branch path for the current view (`get_branch_path`).
- Traversing downward to find the most recent leaf node of an active branch (`get_leaf_node`).

This allows the UI to render a dynamic conversation tree seamlessly while keeping the LangGraph execution flow completely linear.


## Error Handling And Retries

The retry loop is managed by `graphs/analytics_graph.py`:

```text
analysis error + retry_count < 3 -> query
otherwise -> response
```

On retry, `LLMService.generate_python()` receives:

- The original question.
- The dataset contexts.
- The previous error message.
- The previous generated code.

This gives the LLM a chance to fix column names, dataset keys, syntax issues, or pandas mistakes.

`LLMService.generate_python()` also applies a few deterministic cleanup rules, including:

- Extracting code from markdown fences.
- Ensuring `result` exists.
- Fixing some year-filtering expressions.
- Fixing some malformed `.sum()` / `.count()` bracket patterns.
- Converting text search to `startswith` or `endswith` when the question asks for that.

## Generated Files

These files and folders are generated or runtime-specific:

- `uploads/*.csv`
- `contexts/*.json`
- `vector_store/faiss.index`
- `vector_store/metadata.json`
- `debug_e2b_code.py`, if generated during E2B execution

The FAISS binary index is ignored by git through `.gitignore`.

## Notes For Development

- The app currently depends on Ollama being available locally.
- The configured LLM model is hardcoded as `qwen2.5:1.5b` in `services/llm_service.py`.
- The E2B API key is loaded from `.env`.
- The main Streamlit path rebuilds memory automatically after upload.
- `run_day1.py` can manually initialize semantic memory from the CSVs already present in `uploads/`.
- `run_day2.py` can be used to test the graph from the terminal.
- The deterministic parsing and retrieval code still exists, but the active query path now generates pandas code for E2B execution.

## Typical End-To-End Flow

```text
User uploads CSVs
  -> old uploads are deleted
  -> new uploads are saved
  -> contexts are regenerated
  -> embeddable values are extracted
  -> FAISS semantic memory is rebuilt
  -> chat state is reset

User asks a question
  -> graph starts with AgentState
  -> query agent generates pandas code from schema context
  -> retrieval is skipped for the dynamic path
  -> analysis agent executes code in E2B
  -> failed code loops back for repair, up to 3 retries
  -> response agent summarizes result
  -> Streamlit renders text, metric, dataframe, series, or error
```
