from state.agent_state import AgentState
from services.dataset_loader import DatasetLoader
from services.embedding_service import EmbeddingService
from services.e2b_execution_service import (
    E2BExecutionService
)

_datasets = None
_embedding_service = None


def get_datasets(force_reload=False):

    global _datasets

    if _datasets is None or force_reload:

        print("Loading datasets...")

        loader = DatasetLoader()

        _datasets = loader.load_datasets()

        print("Datasets Ready.")

    return _datasets


def clear_dataset_cache():

    global _datasets

    _datasets = None


def get_embedding_service():

    global _embedding_service

    if _embedding_service is None:

        print("Loading embedding service...")

        _embedding_service = EmbeddingService()

        _embedding_service.load_index()

        print("Embedding Service Ready.")

    return _embedding_service


def resolve_metric(df, metric):

    if metric is None:

        return None

    for column in df.columns:

        if column.lower() == metric.lower():

            return column

    return None


def analysis_agent(state: AgentState):

    print("\n=== ANALYSIS AGENT ===")

    # ==========================================
    # E2B PATH
    # ==========================================

    generated_code = state.get(
        "generated_code"
    )

    if generated_code:

        print("\nUsing E2B Analysis")

        executor = E2BExecutionService()

        execution_result = executor.execute(
            generated_code
        )

        print("\nExecution Result:")
        print(execution_result)

        state["execution_result"] = (
            execution_result
        )

        state["analysis_result"] = {
            "type": "python_execution"
        }

        return state

    # ==========================================
    # DETERMINISTIC PATH
    # ==========================================

    parsed = state["parsed_query"]

    intent = (
        parsed.get("intent")
        or ""
    ).lower()

    operation = (
        parsed.get("operation")
        or ""
    ).lower()

    metric = parsed.get("metric")

    if intent == "unknown":

        state["analysis_result"] = {
            "type": "unsupported"
        }

        return state

    operation_mapping = {

        "get": "sum",
        "value": "sum",
        "retrieve": "sum",
        "fetch": "sum",
        "show": "sum",
        "sum": "sum",

        "highest": "max",
        "maximum": "max",
        "max": "max",

        "lowest": "min",
        "minimum": "min",
        "min": "min",

        "count": "count",
        "number": "count",

        "compare": "compare",
        "comparison": "compare"
    }

    operation = operation_mapping.get(
        operation,
        operation
    )

    print("Intent:", intent)
    print("Operation:", operation)
    print("Metric:", metric)

    # ==========================================
    # Aggregation
    # ==========================================

    if operation == "sum":

        retrieval = state.get(
            "retrieval_result"
        )

        if retrieval is None:

            state["analysis_result"] = {
                "type": "error",
                "message":
                    "I couldn't confidently identify the entity."
            }

            return state

        datasets = get_datasets()

        dataset_name = retrieval["table"]

        entity_column = retrieval["column"]

        entity_value = retrieval[
            "resolved_entity"
        ]

        df = datasets[
            dataset_name
        ]

        metric_column = resolve_metric(
            df,
            metric
        )

        if metric_column is None:

            state["analysis_result"] = {
                "type": "error",
                "message":
                    f"{metric} column not found.\n"
                    f"Available columns: {df.columns.tolist()}"
            }

            return state

        filtered_df = df[
            df[entity_column]
            ==
            entity_value
        ]

        value = filtered_df[
            metric_column
        ].sum()

        state["analysis_result"] = {
            "type": "aggregation",
            "metric": metric_column,
            "value": float(value)
        }

        return state

    # ==========================================
    # Ranking
    # ==========================================

    if operation in ["max", "min"]:

        datasets = get_datasets()

        df = list(datasets.values())[0] if datasets else None
        
        if df is None:
            return state

        metric_column = resolve_metric(
            df,
            metric
        )

        if metric_column is None:

            state["analysis_result"] = {
                "type": "error",
                "message":
                    f"{metric} column not found.\n"
                    f"Available columns: {df.columns.tolist()}"
            }

            return state

        idx = (
            df[metric_column].idxmax()
            if operation == "max"
            else df[metric_column].idxmin()
        )

        row = df.loc[idx]

        stock_name_column = next(
            (
                col for col in df.columns
                if col.lower() == "stock name"
            ),
            df.columns[0]
        )

        state["analysis_result"] = {
            "type": "ranking",
            "operation": operation,
            "metric": metric_column,
            "entity":
                row[stock_name_column],
            "value":
                float(row[metric_column])
        }

        return state

    # ==========================================
    # Count
    # ==========================================

    if operation == "count":

        datasets = get_datasets()

        first_dataset = list(
            datasets.values()
        )[0]

        state["analysis_result"] = {
            "type": "count",
            "value":
                len(first_dataset)
        }

        return state

    # ==========================================
    # Comparison
    # ==========================================

    if operation == "compare":

        entities = parsed.get(
            "entities",
            []
        )

        comparisons = []

        datasets = get_datasets()

        embedding_service = (
            get_embedding_service()
        )

        for entity in entities:

            entity_value = (
                entity.get("value", "")
                if isinstance(entity, dict)
                else entity
            )

            matches = embedding_service.search(
                entity_value,
                top_k=1
            )

            best_match = matches[0]

            df = datasets[
                best_match["table"]
            ]

            metric_column = resolve_metric(
                df,
                metric
            )

            if metric_column is None:

                continue

            filtered_df = df[
                df[
                    best_match["column"]
                ]
                ==
                best_match["value"]
            ]

            value = filtered_df[
                metric_column
            ].sum()

            comparisons.append({

                "entity":
                    best_match["value"],

                "value":
                    float(value)
            })

        state["analysis_result"] = {
            "type": "comparison",
            "metric": metric,
            "comparisons":
                comparisons
        }

        return state

    # ==========================================
    # Filter
    # ==========================================

    if intent == "filter":

        datasets = get_datasets()

        first_dataset = list(
            datasets.values()
        )[0]

        filters = parsed.get(
            "filters",
            []
        )

        df = first_dataset

        for filter_item in filters:

            column = filter_item.get(
                "column"
            )

            value = filter_item.get(
                "value"
            )

            actual_column = resolve_metric(
                df,
                column
            )

            if actual_column is None:

                continue

            df = df[
                df[actual_column]
                ==
                value
            ]

        state["analysis_result"] = {
            "type": "filter",
            "rows":
                df.to_dict(
                    orient="records"
                )
        }

        return state

    # ==========================================
    # Final Fallback
    # ==========================================

    state["analysis_result"] = {
        "type": "error",
        "message":
            f"Unsupported operation: {operation}"
    }

    return state