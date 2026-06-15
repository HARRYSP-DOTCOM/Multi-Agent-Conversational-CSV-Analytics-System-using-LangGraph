from state.agent_state import AgentState
from services.dataset_loader import DatasetLoader
from services.embedding_service import EmbeddingService

# ==========================================
# Cached Resources
# ==========================================

_datasets = None
_embedding_service = None


def get_datasets():

    global _datasets

    if _datasets is None:

        print("Loading datasets...")

        loader = DatasetLoader()

        _datasets = loader.load_datasets()

        print("Datasets Ready.")

    return _datasets


def get_embedding_service():

    global _embedding_service

    if _embedding_service is None:

        print("Loading embedding service...")

        _embedding_service = EmbeddingService()

        _embedding_service.load_index()

        print("Embedding Service Ready.")

    return _embedding_service


# ==========================================
# Analysis Agent
# ==========================================

def analysis_agent(state: AgentState):

    print("\n=== ANALYSIS AGENT ===")

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

    if metric:
        metric = metric.title()

    # ==========================================
    # Unsupported
    # ==========================================

    if intent == "unknown":

        state["analysis_result"] = {
            "type": "unsupported"
        }

        return state

    # ==========================================
    # Normalize operations
    # ==========================================

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

        if metric not in df.columns:

            state["analysis_result"] = {
                "type": "error",
                "message":
                    f"{metric} column not found."
            }

            return state

        filtered_df = df[
            df[entity_column]
            ==
            entity_value
        ]

        value = filtered_df[
            metric
        ].sum()

        state["analysis_result"] = {
            "type": "aggregation",
            "metric": metric,
            "value": float(value)
        }

        return state

    # ==========================================
    # Ranking
    # ==========================================

    if operation in ["max", "min"]:

        datasets = get_datasets()

        df = datasets["stocks"]

        if metric not in df.columns:

            state["analysis_result"] = {
                "type": "error",
                "message":
                    f"{metric} column not found."
            }

            return state

        if operation == "max":

            idx = df[
                metric
            ].idxmax()

        else:

            idx = df[
                metric
            ].idxmin()

        row = df.loc[idx]

        state["analysis_result"] = {
            "type": "ranking",
            "operation": operation,
            "metric": metric,
            "entity":
                row["Stock Name"],
            "value":
                float(row[metric])
        }

        return state

    # ==========================================
    # Count
    # ==========================================

    if operation == "count":

        datasets = get_datasets()

        df = datasets[
            "employees"
        ]

        state["analysis_result"] = {
            "type": "count",
            "value":
                len(df)
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

            if isinstance(
                entity,
                dict
            ):

                entity_value = entity.get(
                    "value",
                    ""
                )

            else:

                entity_value = entity

            matches = embedding_service.search(
                entity_value,
                top_k=1
            )

            best_match = matches[0]

            df = datasets[
                best_match["table"]
            ]

            filtered_df = df[
                df[
                    best_match["column"]
                ]
                ==
                best_match["value"]
            ]

            value = filtered_df[
                metric
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

        filters = parsed.get(
            "filters",
            []
        )

        datasets = get_datasets()

        df = datasets[
            "employees"
        ]

        for filter_item in filters:

            column = filter_item.get(
                "column"
            )

            value = filter_item.get(
                "value"
            )

            if column not in df.columns:
                continue

            df = df[
                df[column]
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
    # Fallback
    # ==========================================

    state["analysis_result"] = {
        "type": "error",
        "message":
            f"Unsupported operation: {operation}"
    }

    return state