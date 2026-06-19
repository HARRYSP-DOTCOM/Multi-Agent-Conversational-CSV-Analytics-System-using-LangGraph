import csv
import os
import re
from services.dataset_loader import DatasetLoader

from services.context_service import ContextService
from services.llm_service import LLMService


_context_service = None
_llm_service = None


def get_context_service():
    global _context_service
    if _context_service is None:
        _context_service = ContextService()
    return _context_service


def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def _normalize(text):
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(text).lower()
    ).strip()


def _tokens(text):
    tokens = set(
        token
        for token in _normalize(text).split()
        if len(token) > 1
    )

    singular_tokens = {
        token[:-1]
        for token in tokens
        if token.endswith("s")
        and len(token) > 3
    }

    return tokens | singular_tokens


def _add_term(terms, value):
    normalized_value = _normalize(value)

    if normalized_value:
        terms.add(normalized_value)
        terms.update(_tokens(value))


def _load_dataset_terms():
    terms = set()
    datasets = []

    try:
        contexts = get_context_service().load_contexts()
    except Exception:
        contexts = {}

    for dataset_name, context in contexts.items():
        datasets.append(dataset_name)

        _add_term(
            terms,
            dataset_name
        )

        for column in context.get("columns", []):
            column_name = column.get("name", "")
            _add_term(
                terms,
                column_name
            )

            for value in column.get("top_values", []):
                _add_term(
                    terms,
                    value
                )

    _load_upload_terms(
        terms,
        datasets
    )

    return terms, datasets


def _load_upload_terms(terms, datasets, upload_directory="uploads"):
    if not os.path.isdir(upload_directory):
        return

    for file_name in os.listdir(upload_directory):
        if not file_name.lower().endswith(".csv"):
            continue

        dataset_name = os.path.splitext(file_name)[0]

        if dataset_name not in datasets:
            datasets.append(dataset_name)

        _add_term(
            terms,
            dataset_name
        )

        path = os.path.join(
            upload_directory,
            file_name
        )

        try:
            with open(
                path,
                newline="",
                encoding="utf-8-sig"
            ) as file:
                reader = csv.reader(file)
                headers = next(reader, [])

                for header in headers:
                    _add_term(
                        terms,
                        header
                    )

                for row_index, row in enumerate(reader):
                    if row_index >= 100:
                        break

                    for value in row:
                        _add_term(
                            terms,
                            value
                        )

        except Exception:
            continue


def _has_column_in_datasets(metric):
    normalized_metric = _normalize(metric)
    contexts = get_context_service().load_contexts()
    for context in contexts.values():
        for column in context.get("columns", []):
            if _normalize(column.get("name", "")) == normalized_metric:
                return True
    return False


def planner_agent(state):
    """Planner agent that decides whether to use CSV, Web, or Hybrid.

    It analyses the user's question, scores CSV vs Web relevance, and checks if the
    required column exists in any uploaded dataset. The function returns an updated
    state dictionary expected by downstream agents.
    """
    question = state.get("question")
    if not question:
        state["route"] = "web"
        return state

    # Load terms for CSV scoring
    dataset_terms, _ = _load_dataset_terms()
    csv_score, csv_matches, _ = _score_csv(question, dataset_terms)
    web_score, web_matches = _score_web(question)

    # Determine routing: prefer CSV when its score is higher (and >0) and the
    # column appears in any uploaded dataset. Otherwise fall back to web.
    route = "web"
    if csv_score >= web_score and csv_score > 0:
        if _has_column_in_datasets(question):
            route = "csv"
        else:
            # If column not found but CSV still seems relevant, still use CSV
            route = "csv"
    elif web_score > 0:
        route = "web"

    csv_q, web_q = _build_subquestions(question, route)

    return {
        "route": route,
        "csv_question": csv_q,
        "web_question": web_q,
        "matches": {
            "csv": csv_matches,
            "web": web_matches
        }
    }


def _score_csv(question, dataset_terms):
    normalized_question = _normalize(question)
    question_tokens = _tokens(question)

    explicit_csv_terms = {
        "csv",
        "dataset",
        "datasets",
        "uploaded",
        "upload",
        "file",
        "files",
        "table",
        "column",
        "columns",
        "rows",
    }

    score = 0
    matches = []

    for term in explicit_csv_terms:
        if term in question_tokens:
            score += 3
            matches.append(term)

    for term in dataset_terms:
        if not term:
            continue

        if " " in term and term in normalized_question:
            score += 4
            matches.append(term)
        elif term in question_tokens:
            score += 2
            matches.append(term)

    explicit_matches = sorted(
        set(matches) & explicit_csv_terms
    )

    return score, sorted(set(matches)), explicit_matches


def _score_web(question):
    normalized_question = _normalize(question)
    question_tokens = _tokens(question)

    strong_web_terms = {
        "latest",
        "current",
        "today",
        "now",
        "news",
        "recent",
        "realtime",
        "live",
        "weather",
    }

    comparison_terms = {
        "compare",
        "versus",
        "vs",
        "against",
        "relative",
    }

    external_terms = {
        "trend",
        "trends",
        "inflation",
        "interest",
        "rate",
        "rates",
        "market",
        "industry",
        "benchmark",
        "competition",
        "competitor",
        "competitors",
        "competitiors",
        "competetitor",
        "competetitors",
        "economy",
        "economic",
        "forecast",
        "outlook",
    }

    knowledge_phrases = {
        "full form",
        "stands for",
        "stand for",
        "meaning of",
        "definition of",
        "when did",
        "where is",
    }

    score = 0
    matches = []

    for term in strong_web_terms:
        if term in question_tokens:
            score += 4
            matches.append(term)

    for term in external_terms:
        if term in question_tokens:
            score += 1
            matches.append(term)

    for phrase in knowledge_phrases:
        if phrase in normalized_question:
            score += 4
            matches.append(phrase)

    if any(term in question_tokens for term in comparison_terms):
        if any(term in question_tokens for term in external_terms):
            score += 2
            matches.append("external comparison")

    if {"trend", "trends", "forecast", "outlook", "news"} & question_tokens:
        if any(term in question_tokens for term in external_terms):
            score += 2
            matches.append("external context")

    competitor_pattern = (
        r"\b(top|main|major|biggest|largest|leading)\s+"
        r"compet\w+\b"
    )

    if re.search(competitor_pattern, normalized_question):
        score += 4
        matches.append("competitor research")

    if (
        "competitor" in question_tokens
        or "competitors" in question_tokens
        or "competitiors" in question_tokens
        or "competition" in question_tokens
    ):
        score += 2
        matches.append("competitors")

    if re.search(r"\b20\d{2}\b", normalized_question):
        score += 1
        matches.append("year")

    return score, sorted(set(matches))


def _build_subquestions(question, route):
    if route == "csv":
        return question, None

    if route == "web":
        return None, question

    csv_question = (
        "Using only the uploaded CSV files, calculate or return the "
        "uploaded-data facts needed for this question. Do not answer, "
        "fetch, estimate, or compare any current/external/web facts. "
        "If the question also asks for a full form, meaning, definition, "
        "current trend, or general knowledge, ignore that part. "
        f"Original question: {question}"
    )

    web_question = (
        "Find only the current/external/web context needed for this "
        "question, such as full forms, meanings, definitions, or current "
        f"facts. Do not use uploaded CSV data. Original question: {question}"
    )

    return csv_question, web_question



# Helper to check if a given column exists in any uploaded dataset
def _has_column_in_datasets(column_name: str) -> bool:
    if not column_name:
        return False
    try:
        loader = DatasetLoader()
        datasets = loader.load_datasets()
        for df in datasets.values():
            if column_name.lower() in (c.lower() for c in df.columns):
                return True
    except Exception:
        pass
    return False
