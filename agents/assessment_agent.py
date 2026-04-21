from state import State
from memory import shared_memory
from agents.llm_call import call_llm, call_llm_without_tools


def assessment_agent(state: State) -> State:
    print("-" * 80)
    print("here is assessment_agent!!!")
    print("state messages:")
    for i in state.get("messages", []):
        print(i)
    print("state trip_plan:", state.get("trip_plan", ""))
    print("state recommendations:", state.get("recommendations", ""))
    print("state tool_use_num:", state.get("tool_use_num", ""))
    print("-" * 80)
    """Assessment Agent node to evaluate if there are conflicts between trip plan and recommendations"""
    trip_plan = state.get("trip_plan", {})
    recommendations = state.get("recommendations", {})
    tool_use_num = state.get("tool_use_num", 0)  # Default to 3 if not provided

    # Check if tool_use_num is 0
    if tool_use_num <= 0:
        print("Tool use limit reached, returning default assessment")
        assessment_result = {"no_conflict": True}
        # Save to shared memory
        shared_memory.write_memory(
            "Assessment Agent", "Evaluate plan conflicts", str(assessment_result)
        )
        return {"assessment_result": assessment_result, "tool_use_num": tool_use_num}

    # Use LLM to assess conflicts
    system_prompt = """###You are a travel plan assessor. 
####Based on the trip plan and recommendations, evaluate if they can form a complete and conflict-free travel route.
###If they cannot form a complete and conflict-free travel route, provide a JSON response with:
- has_conflict: true
- conflict_reason: a string explaining the conflict
- suggestion: a string suggesting how to resolve the conflict

###If they can form a complete and conflict-free travel route, provide a JSON response with:
- no_conflict: true

###Please respond only in JSON format, do not reply with other statements.

###Example response for conflict:
{
    "has_conflict": true,
    "conflict_reason": "The trip plan includes destinations that are too far apart for the given time frame",
    "suggestion": "Adjust the route to include destinations that are closer together or increase the trip duration"
}

###Example response for no conflict:
{
    "no_conflict": true
}
"""

    user_prompt = f"""# Trip Plan:
{trip_plan}

# Recommendations:
{recommendations}

# Give suggestions times:
You have {tool_use_num}  chances left to give suggestions.Please provide suggestions that can be corrected within the remaining chances.
"""

    result = call_llm_without_tools(system_prompt, user_prompt)

    # Parse the JSON response
    import json

    assessment_result = {}
    if result and result.get("messages"):
        ai_message = result["messages"][0]
        content = getattr(ai_message, "content", "")
        try:
            # Clean and parse JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            assessment_result = json.loads(content.strip())
        except json.JSONDecodeError:
            print("assessment_result 无法解析:", assessment_result)
    else:
        # Fallback if no response from LLM
        print("assessment_result failed result result:", result)

    # Save to shared memory
    shared_memory.write_memory(
        "Assessment Agent", "Evaluate plan conflicts", str(assessment_result)
    )

    # Decrement tool_use_num
    tool_use_num -= 1
    print(f"Tool use remaining: {tool_use_num}")
    print("assessment_result:", assessment_result)

    return {"assessment_result": assessment_result, "tool_use_num": tool_use_num}
