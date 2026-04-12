from state import State
from memory import shared_memory
from agents.llm_call import call_llm


def assessment_agent(state: State) -> State:
    """Assessment Agent node to evaluate if there are conflicts between trip plan, recommendations, and meeting schedule"""
    trip_plan = state.get("trip_plan", {})
    recommendations = state.get("recommendations", {})
    meeting_schedule = state.get("meeting_schedule", {})

    # Use LLM to assess conflicts
    system_prompt = "You are a travel plan assessor. Evaluate if there are conflicts between the trip plan, recommendations, and meeting schedule. Provide a JSON response with has_conflict (boolean), conflict_reason (string), and suggestion (string)."
    user_prompt = f"Trip Plan: {trip_plan}\nRecommendations: {recommendations}\nMeeting Schedule: {meeting_schedule}"

    assessment_json = call_llm(system_prompt, user_prompt)

    # Parse the JSON response
    import json
    try:
        assessment_result = json.loads(assessment_json)
    except json.JSONDecodeError:
        # Fallback to default assessment if JSON parsing fails
        has_conflict = False
        conflict_reason = ""

        if not trip_plan or not recommendations or not meeting_schedule:
            has_conflict = True
            conflict_reason = "Missing required planning components"
        else:
            trip_duration = trip_plan.get("duration", "")
            meeting_count = len(meeting_schedule.get("meetings", []))

            if "3 days" in trip_duration and meeting_count > 6:
                has_conflict = True
                conflict_reason = "Too many activities scheduled for the trip duration"

        assessment_result = {
            "has_conflict": has_conflict,
            "conflict_reason": conflict_reason,
            "suggestion": "Adjust the number of activities to fit within the available time" if has_conflict else "All plans are aligned"
        }

    # Save to shared memory
    shared_memory.write_memory("Assessment Agent", "Evaluate plan conflicts", str(assessment_result))

    return {
        "assessment_result": assessment_result
    }