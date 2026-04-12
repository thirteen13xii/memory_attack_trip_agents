from state import State
from memory import shared_memory
from agents.llm_call import call_llm
import ast


def clean_json_string(json_str: str) -> str:
    """Clean JSON string by removing Markdown code block markers"""
    cleaned_str = json_str.strip()
    if cleaned_str.startswith('```json'):
        cleaned_str = cleaned_str[7:]
    if cleaned_str.endswith('```'):
        cleaned_str = cleaned_str[:-3]
    return cleaned_str.strip()


def execute_tool(tool_name: str, tool_args: dict) -> any:
    """Execute a tool with given arguments"""
    if tool_name in TOOLS:
        tool = TOOLS[tool_name]
        return tool["function"](**tool_args)
    return None


def trip_planner(state: State) -> State:
    print("-" * 80)
    print("state messages:", state.get("messages", []))
    print("state user_query:", state.get("user_query", ""))
    print("-" * 80)
    """Trip Planner node to create travel itinerary"""
    user_query = state["user_query"]
    user_preferences = state.get("user_preferences", {})
    assessment_result = state.get("assessment_result", {})

    # Get assessment suggestions
    assessment_suggestions = assessment_result.get("suggestion", "")

    # Search shared memory for relevant information
    memory_results = shared_memory.search_memory(
        "Plan trip based on assessment suggestions, memory info, and user input")
    # Format memory results for prompt
    memory_info = "\n".join(
        [f"- {item}" for item in memory_results]) if memory_results else "No relevant information found in memory"

    # First, use LLM to determine locations and which tool to use
    system_prompt = """###You are a professional trip planner. 
####Based on the assessment suggestions, shared memory information, and user input, determine the main locations for the trip and which tool to use to gather information.

Available tools:
1. search_tourist_attractions: Search for tourist attractions in a specific location
2. search_activities_restaurants_hotels: Search for activities, restaurants, and hotels in a specific location

Format your response as JSON with keys: locations (array of strings), tool_to_use (string), tool_args (object with location parameter)"""

    user_prompt = f"""# Assessment Suggestions:
{assessment_suggestions}

# Shared Memory Information:
{memory_info}

# User Input
User query: {user_query}

User preferences: {user_preferences}"""

    tool_decision_json = call_llm(system_prompt, user_prompt)

    tool_decision_json = clean_json_string(tool_decision_json)

    import json
    locations = []
    tool_results = {}

    try:
        tool_decision = json.loads(tool_decision_json)
        locations = tool_decision.get("locations", [])
        tool_to_use = tool_decision.get("tool_to_use")
        tool_args = tool_decision.get("tool_args", {})

        # Execute the chosen tool for each location
        for location in locations:
            tool_args["location"] = location
            result = execute_tool(tool_to_use, tool_args)
            tool_results[location] = result
    except json.JSONDecodeError as e:
        print(f"Error parsing tool decision: {e}")
        # Fallback to default locations
        locations = ["Tokyo", "Kyoto", "Osaka"]
        # Use default tool results
        for location in locations:
            tool_results[location] = {
                "attractions": [f"Attraction 1 in {location}", f"Attraction 2 in {location}"],
                "activities": [f"Activity 1 in {location}", f"Activity 2 in {location}"],
                "restaurants": [f"Restaurant 1 in {location}", f"Restaurant 2 in {location}"],
                "hotels": [f"Hotel 1 in {location}", f"Hotel 2 in {location}"]
            }

    # Now use LLM to generate trip plan based on tool results
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
}"""

    user_prompt = f"""# Tool Results:
{tool_results}

# User Input
User query: {user_query}

User preferences: {user_preferences}"""

    trip_plan_json = call_llm(system_prompt, user_prompt)
    trip_plan_json = clean_json_string(trip_plan_json)

    # Parse the JSON response
    try:
        trip_plan = json.loads(trip_plan_json)
    except json.JSONDecodeError:
        # Fallback to default plan if JSON parsing fails
        trip_plan = {
            "route": locations or ["Tokyo", "Kyoto", "Osaka"],
            "description": "A classic Japan itinerary covering major cities with rich history and culture"
        }

    # Save to shared memory
    shared_memory.write_memory("Trip Planner",
                               f"Plan trip based on tool results and user input",
                               str(trip_plan))

    print("trip_plan : ", trip_plan)
    print("tool_results : ", tool_results)

    return {
        "trip_plan": trip_plan,
        "tool_results": tool_results
    }