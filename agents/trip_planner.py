from state import State
from memory import shared_memory
from agents.llm_call import call_llm,call_llm_without_tools
from langchain_core.messages import ToolMessage, AIMessage
import json

def clean_json_string(json_str: str) -> str:
    """Clean JSON string by removing Markdown code block markers"""
    cleaned_str = json_str.strip()
    if cleaned_str.startswith('```json'):
        cleaned_str = cleaned_str[7:]
    if cleaned_str.endswith('```'):
        cleaned_str = cleaned_str[:-3]
    return cleaned_str.strip()


def trip_planner(state: State) -> State:
    print("-" * 80)
    print("state messages:")
    for i in state.get("messages", []):
        print(i)
    print(state.get("messages", []))
    print("state user_query:", state.get("user_query", ""))
    print("-" * 80)
    """Trip Planner node to create travel itinerary"""
    user_query = state["user_query"]
    user_preferences = state.get("user_preferences", {})
    assessment_result = state.get("assessment_result", {})
    messages = state.get("messages", [])

    # Get assessment suggestions
    assessment_suggestions = assessment_result.get("suggestion", "")

    # Search shared memory for relevant information
    memory_results = shared_memory.search_memory(
        "Plan trip based on assessment suggestions, memory info, and user input")
    # Format memory results for prompt
    memory_info = "\n".join(
        [f"- {item}" for item in memory_results]) if memory_results else "No relevant information found in memory"

    # Check if last message is a tool message
    is_tool_message = False
    tool_result = None
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'tool_call_id') and last_message.tool_call_id:
            is_tool_message = True
            tool_result = last_message.content

    updated_messages = messages.copy()
    trip_plan = {}

    if not is_tool_message:
        # First, use LLM to determine locations and which tool to use
        system_prompt = """###You are a professional trip planner. 
####Based on the assessment suggestions, shared memory information,user input and Existing tool search results(Supplementary information obtained from past use of tools), determine the main locations for the trip and if need tool to use to gather information.
###Determine whether it is necessary to use the tool(For example, no existing tool search results, or additional tool information is needed.), and if not,format your response as a JSON object with keys: route (array of destinations), and description.
like:
{
  "route": ["Destination 1", "Destination 2", "Destination 3"],
  "description": "A detailed description of the trip route, including the highlights of each destination and the overall travel experience."
}
###The plan should include a sequence of destinations and brief descriptions of each destination. 
###Focus on the route itself, not on daily schedules or specific activities. 
###Only consider which locations are suitable to include in the travel route, without taking time factors into account.
###If there are assessment suggestions, please consider them together with the existing tool search results.
"""

        user_prompt = f"""# Assessment Suggestions:
{assessment_suggestions}

# Shared Memory Information:
{memory_info}

# User Input
User query: {user_query}

User preferences: {user_preferences}

#Existing tool search results
search results:{state.get("search_activities_results", "")}
"""

        result = call_llm(system_prompt, user_prompt)

        # Extract content from the result
        if result and result.get("messages"):
            ai_message = result["messages"][0]
            if hasattr(ai_message, "tool_calls") and ai_message.tool_calls:
                print("有 tool call")
            else:
                content = getattr(ai_message, "content", "")
                trip_plan_json = clean_json_string(content)
                try:
                    trip_plan = json.loads(trip_plan_json)
                    # Save to shared memory
                    shared_memory.write_memory("Trip Planner",
                                               f"Plan trip based on tool results and user input",
                                               str(trip_plan))
                except json.JSONDecodeError:
                    print("trip_plan_json 无法解析:", trip_plan_json)
            updated_messages.append(ai_message)
        else:
            print("trip_planner failed result result:", result)


    else:
        # Process tool result and generate trip plan
        system_prompt = """###You are a professional trip planner. 
####Based on the tool results, create a detailed trip route plan. 
###The plan should include a sequence of destinations and brief descriptions of each destination. 
###Focus on the route itself, not on daily schedules or specific activities. 
###Only consider which locations are suitable to include in the travel route, without taking time factors into account.
###Format your response as a JSON object with keys: route (array of destinations), and description.
like:
{
  "route": ["Destination 1", "Destination 2", "Destination 3"],
  "description": "A detailed description of the trip route, including the highlights of each destination and the overall travel experience."
}
###Please respond only in JSON format, do not reply with other statements.
###Do not use tools anymore, please return the result directly."""

        user_prompt = f"""# Tool Results:
{tool_result}

# User Input
User query: {user_query}

User preferences: {user_preferences}"""

        result = call_llm_without_tools(system_prompt, user_prompt)

        # Extract content from the result
        if result and result.get("messages"):
            ai_message = result["messages"][0]
            content = getattr(ai_message, "content", "")
            updated_messages.append(ai_message)
        else:
            content = ""

        # Parse the trip plan
        try:
            trip_plan = json.loads(content)
        except json.JSONDecodeError:
            # Fallback to default plan if JSON parsing fails
            print("can not parse content:", content)

        # Save to shared memory
        shared_memory.write_memory("Trip Planner",
                                   f"Plan trip based on tool results and user input",
                                   str(trip_plan))

    print("trip_plan : ", trip_plan)
    return {
        "messages": updated_messages,
        "trip_plan": trip_plan
    }