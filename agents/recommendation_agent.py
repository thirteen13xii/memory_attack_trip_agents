from state import State
from memory import shared_memory
from agents.llm_call import call_llm


def recommendation_agent(state: State) -> State:
    print("-" * 80)
    print("state messages:")
    for i in state.get("messages", []):
        print(i)
    print(state.get("messages", []))
    print("state user_query:", state.get("user_query", ""))
    print("-" * 80)
    """Recommendation Agent node to suggest restaurants and activities"""
    user_query = state["user_query"]

    # Search shared memory for relevant information
    memory_results = shared_memory.search_memory("recommendation")

    # Use LLM to generate recommendations
    system_prompt = "You are a travel recommendation expert. Based on the user's query, suggest restaurants and activities for their trip. Format your response as a JSON object with keys: restaurants (array of objects with name, cuisine, location) and activities (array of objects with name, type)."
    user_prompt = user_query

    recommendations_json = call_llm(system_prompt, user_prompt)

    # Parse the JSON response
    import json
    try:
        recommendations = json.loads(recommendations_json)
    except json.JSONDecodeError:
        # Fallback to default recommendations if JSON parsing fails
        recommendations = {
            "restaurants": [
                {"name": "Le Jules Verne", "cuisine": "French", "location": "Eiffel Tower"},
                {"name": "Chez L'Ami Jean", "cuisine": "Basque", "location": "Montmartre"},
                {"name": "La Tour d'Argent", "cuisine": "French", "location": "Notre-Dame"}
            ],
            "activities": [
                {"name": "Seine River Cruise", "type": "Sightseeing"},
                {"name": "Musée d'Orsay", "type": "Museum"},
                {"name": "Paris Opera House Tour", "type": "Cultural"}
            ]
        }

    # Save to shared memory
    shared_memory.write_memory("Recommendation Agent", f"Recommend based on: {user_query}", str(recommendations))

    return {
        "recommendations": recommendations
    }