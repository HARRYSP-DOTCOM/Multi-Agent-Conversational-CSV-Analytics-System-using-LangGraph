from state.agent_state import AgentState
from services.history_service import HistoryService
import os

# Initialize history service globally to reuse the DB connection and embedding model
# Disable connection locally if NO_MONGO is set (for testing without db)
history_service = HistoryService() if not os.environ.get("NO_MONGO") else None

def history_agent(state: AgentState):
    """
    Checks MongoDB for a previously answered similar question.
    """
    question = state["question"]
    
    # Check if history checking is enabled
    if history_service:
        print("--- CHECKING HISTORY ---")
        cached_response = history_service.find_similar_interaction(question)
        
        if cached_response:
            print("--- MATCH FOUND IN HISTORY ---")
            return {
                "final_response": cached_response,
                "route": "cached",
                "route_reason": {"reason": "Found semantically similar question in chat history."}
            }
    
    print("--- NO MATCH IN HISTORY, PROCEEDING TO PLANNER ---")
    return {
        "route": "planner"
    }
