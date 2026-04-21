from state import State
from memory import shared_memory
from agents.llm_call import call_llm, call_llm_without_tools


def meeting_scheduler(state: State) -> State:
    print("-" * 80)
    print("here is meeting_scheduler!!!")
    print("-" * 80)
    """Meeting Scheduler node to create route planning map based on trip plan and recommendations"""
    user_query = state["user_query"]
    trip_plan = state.get("trip_plan", {})
    recommendations = state.get("recommendations", {})

    # Search shared memory for relevant information
    memory_results = shared_memory.search_memory(
        "Create route planning map based on trip plan and recommendations"
    )
    # Format memory results for prompt
    memory_info = (
        "\n".join([f"- {item}" for item in memory_results])
        if memory_results
        else "No relevant information found in memory"
    )

    # Use LLM to generate route planning map
    system_prompt = """###You are a professional travel itinerary planner. 
####Based on the trip plan and recommendations, create a detailed route planning map with time nodes, locations, types, and descriptions.
###The route planning map should include:
- time: Specific time node (e.g., "Day 1, 10:00 AM")
- location: Location with format "Level 1 Area-Level 2 Area" (e.g., "shanghai-xuhui")
- type: Type of activity (e.g., "activity", "scenery", "restaurant", "hotel", "flight", etc.)
- description: Brief description of the activity or location

###You can only use trip_plan and recommendations to create this route planning map; that is to say, plans related to travel factors such as activity locations can only come from trip_plan and recommendations.
###Trip_plan is the suggested travel route, and recommendations are the suggested activities, restaurants, and hotels during the trip."
###Format your response as a JSON object with a key 'route_plan' that contains an array of objects with 'time', 'location', 'type', and 'description' keys.

###Example response:
{
  "route_plan": [
    {
      "time": "Day 1, 9:00 AM",
      "location": "shanghai-pudong",
      "type": "flight",
      "description": "Arrive at Shanghai Pudong International Airport"
    },
    {
      "time": "Day 1, 11:00 AM",
      "location": "shanghai-xuhui",
      "type": "hotel",
      "description": "Check in at Grand Hyatt Shanghai"
    },
    {
      "time": "Day 1, 2:00 PM",
      "location": "shanghai-xuhui",
      "type": "scenery",
      "description": "Visit Yu Garden, a classical Chinese garden"
    },
    {
      "time": "Day 1, 6:00 PM",
      "location": "shanghai-xuhui",
      "type": "restaurant",
      "description": "Dinner at Din Tai Fung, famous for dim sum"
    },
    {
      "time": "Day 2, 10:00 AM",
      "location": "shanghai-pudong",
      "type": "activity",
      "description": "Shanghai Disney Resort day trip"
    }
  ]
}

###Please respond only in JSON format, do not reply with other statements.
"""

    user_prompt = f"""# Trip Plan:
{trip_plan}

# Recommendations:
{recommendations}

# User Query:
{user_query}

# Shared Memory Information:
{memory_info}
"""

    result = call_llm_without_tools(system_prompt, user_prompt)

    # Parse the JSON response
    import json

    meeting_schedule = {}
    if result and result.get("messages"):
        ai_message = result["messages"][0]
        content = getattr(ai_message, "content", "")
        try:
            # Clean and parse JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            meeting_schedule = json.loads(content.strip())
        except json.JSONDecodeError:
            # Fallback to default schedule if JSON parsing fails
            print("Error parsing JSON response, using fallback schedule")
    else:
        # Fallback if no response from LLM
        print("No response from LLM, using fallback schedule")

    # Save to shared memory
    shared_memory.write_memory(
        "Meeting Scheduler",
        f"Route plan based on trip plan and recommendations",
        str(meeting_schedule),
    )

    print("meeting_schedule : ", meeting_schedule)
    return {"meeting_schedule": meeting_schedule}
