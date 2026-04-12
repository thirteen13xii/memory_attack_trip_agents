from state import State
from memory import shared_memory
from agents.llm_call import call_llm


def meeting_scheduler(state: State) -> State:
    print("-" * 80)
    print("state messages:")
    for i in state.get("messages", []):
        print(i)
    print(state.get("messages", []))
    print("state user_query:", state.get("user_query", ""))
    print("-" * 80)
    """Meeting Scheduler node to arrange schedule"""
    user_query = state["user_query"]

    # Search shared memory for relevant information
    memory_results = shared_memory.search_memory("meeting")

    # Use LLM to generate meeting schedule
    system_prompt = "You are a professional meeting scheduler. Based on the user's query, create a detailed schedule for their trip with specific times and activities. Format your response as a JSON object with a key 'meetings' that contains an array of objects with 'time' and 'activity' keys."
    user_prompt = user_query

    schedule_json = call_llm(system_prompt, user_prompt)

    # Parse the JSON response
    import json
    try:
        meeting_schedule = json.loads(schedule_json)
    except json.JSONDecodeError:
        # Fallback to default schedule if JSON parsing fails
        meeting_schedule = {
            "meetings": [
                {"time": "Day 1, 10:00 AM", "activity": "Eiffel Tower Visit"},
                {"time": "Day 1, 2:00 PM", "activity": "Louvre Museum"},
                {"time": "Day 2, 10:00 AM", "activity": "Notre-Dame Cathedral"},
                {"time": "Day 2, 2:00 PM", "activity": "Montmartre"},
                {"time": "Day 3, 9:00 AM", "activity": "Versailles Palace"}
            ]
        }

    # Save to shared memory
    shared_memory.write_memory("Meeting Scheduler", f"Schedule based on: {user_query}", str(meeting_schedule))

    return {
        "meeting_schedule": meeting_schedule
    }