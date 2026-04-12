from langgraph.graph import StateGraph, START, END
from state import State
from agents.user_assistant import user_assistant
from agents.privacy_guardian import privacy_guardian
from agents.trip_planner import trip_planner
from agents.recommendation_agent import recommendation_agent
from agents.meeting_scheduler import meeting_scheduler
from agents.assessment_agent import assessment_agent
from agents.report_generator import report_generator
from langgraph.prebuilt import ToolNode
from tools.search_activities_restaurants_hotels import search_activities_restaurants_hotels
from tools.search_tourist_attractions import search_tourist_attractions

#judge if tool
def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "meeting_scheduler"

def should_continue_recommendation_agent(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "recommendation_agent"

#judge next node based on tool used
def tool_to_node(state: State):
    messages = state["messages"]
    # Find the last tool call and its result
    msg=messages[-1]
    if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
        # Get the tool name from the last tool call
        tool_name = msg.name
        if tool_name == 'search_activities_restaurants_hotels':
            return "recommendation_agent"
        elif tool_name == 'search_tourist_attractions':
            return "trip_planner"
    return "meeting_scheduler"


# Build workflow
workflow = StateGraph(State)
# Create tool node with our tools
tool_node = ToolNode([search_activities_restaurants_hotels, search_tourist_attractions])
# Add nodes
workflow.add_node("tools", tool_node)
workflow.add_node("user_assistant", user_assistant)
workflow.add_node("privacy_guardian", privacy_guardian)
workflow.add_node("trip_planner", trip_planner)
workflow.add_node("recommendation_agent", recommendation_agent)
workflow.add_node("meeting_scheduler", meeting_scheduler)
workflow.add_node("assessment_agent", assessment_agent)
workflow.add_node("report_generator", report_generator)

# Add edges to connect nodes
workflow.add_edge(START, "user_assistant")
# Add conditional edge from user_assistant based on is_travel_query
workflow.add_conditional_edges(
    "user_assistant",
    lambda state: "travel" if state.get("is_travel_query", False) else "non_travel",
    {
        "travel": "privacy_guardian",  # If travel-related, go to privacy_guardian
        "non_travel": "user_assistant"  # If not travel-related, loop back to user_assistant
    }
)

# Parallel edges from privacy_guardian to trip_planner and recommendation_agent
workflow.add_edge("privacy_guardian", "trip_planner")
# Add conditional edges from trip_planner and recommendation_agent
workflow.add_conditional_edges("trip_planner", should_continue_recommendation_agent, ["tools", "recommendation_agent"])
workflow.add_conditional_edges("recommendation_agent", should_continue, ["tools", "meeting_scheduler"])
# Add conditional edge from tool_node based on tool used
workflow.add_conditional_edges("tools", tool_to_node, ["recommendation_agent", "trip_planner", "meeting_scheduler"])
# Add edge from meeting_scheduler to assessment_agent
workflow.add_edge("meeting_scheduler", "assessment_agent")


# Add conditional edge from assessment_agent
workflow.add_conditional_edges(
    "assessment_agent",
    lambda state: "conflict" if state.get("assessment_result", {}).get("has_conflict", False) else "no_conflict",
    {
        "conflict": "trip_planner",  # Loop back to planning if conflict
        "no_conflict": "report_generator"
    }
)

# Add remaining edges
workflow.add_edge("report_generator", END)

# Compile
chain = workflow.compile()


if __name__ == "__main__":
    # Example usage
    initial_state = {
        "user_query": "I want to plan a trip to China for 3 days",
        "conversation_history": [],
        "shared_memory": []
    }
    
    result = chain.invoke(initial_state)
    print("Final reply:")
    print(result.get("reply", "No reply generated"))