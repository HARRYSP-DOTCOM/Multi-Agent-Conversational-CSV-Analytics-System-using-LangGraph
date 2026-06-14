from state.agent_state import AgentState
from services.dataset_loader import DatasetLoader
loader = DatasetLoader()
datasets = loader.load_datasets()
def analysis_agent(state: AgentState):
    print("\n=== ANALYSIS AGENT ===")
    metric = (
        state["parsed_query"]["metric"]
    )

    retrieval = (
        state["retrieval_result"]
    )

    dataset_name = retrieval["table"]

    entity_column = retrieval["column"]

    entity_value = (
        retrieval["resolved_entity"]
    )
    print("Dataset:", dataset_name)
    print("Metric:", metric)
    print("Entity:", entity_value)

    df = datasets[dataset_name] 
    filtered_df = df[
        df[entity_column] == entity_value
    ]
    value = filtered_df[
        metric
    ].sum()

    print("Computed Value:")
    print(value)

    state["analysis_result"] = {
        "metric": metric,
        "value": float(value),
        "dataset": dataset_name
    }
    return state    

