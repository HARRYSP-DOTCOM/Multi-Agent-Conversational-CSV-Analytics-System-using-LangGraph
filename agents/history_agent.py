from state.agent_state import AgentState
from services.history_service import HistoryService
from services.llm_service import LLMService
import os

# Initialize history service globally to reuse the DB connection and embedding model
# Disable connection locally if NO_MONGO is set (for testing without db)
history_service = HistoryService() if not os.environ.get("NO_MONGO") else None

def history_agent(state: AgentState):
    """
    Checks conversational memory and MongoDB for a previously answered similar question.
    """
    question = state["question"]
    chat_history = state.get("chat_history", [])
    
    # 1. Check conversational memory first
    print("--- CHECKING CONVERSATIONAL MEMORY ---")
    try:
        llm = LLMService()
        memory_answer = llm.check_conversational_memory(question, chat_history)
        if memory_answer:
            print("--- MATCH FOUND IN CONVERSATIONAL MEMORY ---")
            return {
                "final_response": {"type": "text", "data": memory_answer},
                "route": "cached",
                "route_reason": {"reason": "Answered using conversation history."}
            }
    except Exception as e:
        print(f"Error checking conversational memory: {e}")
    
    # 2. Check MongoDB cache
    if history_service:
        print("--- CHECKING DB HISTORY CACHE ---")
        cached_response = history_service.find_similar_interaction(question)
        
        if cached_response:
            print("--- MATCH FOUND IN DB HISTORY ---")
            return {
                "final_response": cached_response,
                "route": "cached",
                "route_reason": {"reason": "Found semantically similar question in database cache."}
            }
    
    print("--- NO MATCH IN HISTORY, PROCEEDING TO PLANNER ---")
    return {
        "route": "planner"
    }
