from state.agent_state import AgentState
from services.dataset_loader import DatasetLoader
from services.embedding_service import EmbeddingService

loader = DatasetLoader()
datasets = loader.load_datasets()

embedding_service = EmbeddingService()
embedding_service.load_index()


def analysis_agent(state: AgentState):

    print("\n=== ANALYSIS AGENT ===")

    parsed = state["parsed_query"]

    # ==========================================
    # Extract raw values
    # ==========================================
    intent = parsed.get(
        "intent",
        ""
    ).lower()

    operation = parsed.get(
        "operation",
        ""
    ).lower()

    metric = parsed.get(
        "metric"
    )

    if metric:
        metric = metric.title()

    # ==========================================
    # Normalize intent
    # ==========================================
    intent_mapping = {

        "aggregation": "aggregation",
        "profit": "aggregation",
        "get profit": "aggregation",
        "retrieve profit": "aggregation",

        "ranking": "ranking",

        "comparison": "comparison",

        "count": "count",

        "filter": "filter"
    }

    intent = intent_mapping.get(
        intent,
        intent
    )

    # ==========================================
    # Normalize operation
    # ==========================================
    operation_mapping = {

        # Aggregation
        "get": "sum",
        "value": "sum",
        "retrieve": "sum",
        "fetch": "sum",
        "show": "sum",
        "sum": "sum",

        # Ranking
        "highest": "max",
        "maximum": "max",
        "max": "max",

        "lowest": "min",
        "minimum": "min",
        "min": "min",

        # Count
        "count": "count",
        "number": "count",

        # Comparison
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
                    "No retrieval result found."
            }

            return state

        dataset_name = retrieval["table"]

        entity_column = retrieval["column"]

        entity_value = retrieval[
            "resolved_entity"
        ]

        print("Dataset:", dataset_name)
        print("Entity:", entity_value)

        df = datasets[dataset_name]

        filtered_df = df[
            df[entity_column]
            ==
            entity_value
        ]

        if metric not in df.columns:

            state["analysis_result"] = {

                "type": "error",

                "message":
                    f"{metric} column not found."
            }

            return state

        value = filtered_df[
            metric
        ].sum()

        print("Computed Value:")
        print(value)

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

        df = datasets["employees"]

        state["analysis_result"] = {

            "type": "count",

            "value": len(df)
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

        df = datasets["employees"]

        for filter_item in filters:

            column = filter_item.get(
                "column"
            )

            value = filter_item.get(
                "value"
            )

            if (
                column
                not in df.columns
            ):

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
            f"Unsupported operation: "
            f"{operation}"
    }

    return state