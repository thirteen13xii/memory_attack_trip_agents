from state import State
from memory import shared_memory
from agents.llm_call import call_llm, call_llm_without_tools
from langchain_core.messages import ToolMessage, AIMessage
import json


def clean_json_string(json_str: str) -> str:
    """Clean JSON string by removing Markdown code block markers"""
    cleaned_str = json_str.strip()
    if cleaned_str.startswith("```json"):
        cleaned_str = cleaned_str[7:]
    if cleaned_str.endswith("```"):
        cleaned_str = cleaned_str[:-3]
    return cleaned_str.strip()


def recommendation_agent(state: State) -> State:
    print("=" * 80)
    print(f"tool messages: {state.get('messages', [])}")
    print("state messages:")
    for i in state.get("short_term_memory", []):
        print("-" * 80)
        print(i)
        print("-" * 80)
    print("=" * 80)
    """Recommendation Agent node to suggest restaurants and activities"""
    user_query = state["user_query"]
    user_preferences = state.get("user_preferences", {})
    assessment_result = state.get("assessment_result", {})
    messages = state.get("messages", [])
    short_term_memory = state.get("short_term_memory", [])

    # Get assessment suggestions
    assessment_suggestions = assessment_result.get("suggestion", "")

    # Search shared memory for relevant information
    memory_results = shared_memory.search_memory(
        "Plan related activities, dining options, and hotel accommodations during the trip based on assessment suggestions, memory info, and user input"
    )
    # Format memory results for prompt
    memory_info = (
        "\n".join([f"- {item}" for item in memory_results])
        if memory_results
        else "No relevant information found in memory"
    )

    # Check if last message is a tool message
    is_tool_message = False
    tool_result = None
    search_activities_results = state.get("search_activities_results", [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "tool_call_id") and last_message.tool_call_id:
            is_tool_message = True
            tool_result = last_message.content
            # Parse tool_result as JSON and add to search_activities_results
            try:
                cleaned_tool_result = clean_json_string(tool_result)
                tool_json = json.loads(cleaned_tool_result)
                # Ensure search_activities_results is a list
                if not isinstance(search_activities_results, list):
                    search_activities_results = []
                # Add the parsed tool result to the list
                search_activities_results.append(tool_json)
            except json.JSONDecodeError as e:
                print(f"Error parsing tool result as JSON: {e}")
            except Exception as e:
                print(f"Error processing tool result: {e}")

    updated_messages = messages.copy()
    recommendations = {}

    # 情况1:首次进入——》应该调用工具
    # 情况2:经过assessment_agent再进入该节点——》缺少信息，再次调用工具/信息足够，不需要调用工具
    if not is_tool_message:
        # First, use LLM to determine locations and which tool to use
        system_prompt = """###You are a professional trip planner. 
####Based on the assessment suggestions(The assessment suggestions here are those targeting the existing plan. To avoid confusion with other suggestions, they are specifically referred to as AS here.), shared memory information,user input and existing tool search results(Supplementary information obtained from past use of tools), Decide on activities, dining options, and accommodations for the trip, and determine if tools are needed to gather additional information.
###If there are no AS, it indicates that you are entering this section for the first time, and you need to call tools to gather information
###If there are AS, please determine whether the existing information is sufficient for making modifications based on the suggestions—if not, you also need to call tools.
###If you call the tool, please query only one location. And do not use hierarchical place names, such as "shanghai-xuhui","Beijing, China"," Tokyo, Japan" — just enter "shanghai","Beijing" or "Japan".
###Only one tool call is allowed per round.
###Determine whether it is necessary to use the tool(For example, no existing tool search results, or additional tool information is needed.), and if not,format your response as a JSON object.
like:
{
    "restaurants": [
        {"name": "Le Jules Verne", "location": "shanghai-xuhui","description":"..."},
        {"name": "Chez L'Ami Jean", "location": "nanjing-jiangsu","description":"..."},
        {"name": "La Tour d'Argent", "location": "...","description":"..."}
    ],
    "activities": [
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."}
    ],
    "hotels": [
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."}
    ]
}
###The activities I'm referring to here are local activities, such as cultural festivals or entertainment events, not activities like sightseeing.
###All the above locations should be labeled in the format of "Level 1 Area-Level 2 Area", where Level 1 Area refers to the division of the target place, and Level 2 Area refers to the division of the Level 1 Area.
###If there are tool call results, please remember that the tool returns JSON data of activity, dining, and hotel rankings during the trip. You need to determine these elements for the trip based on the ranking suggestions.
###Each restaurant/activity/hotel in the plan should include corresponding descriptive recommendations(description) and location. 
###Focus on the restaurant/activity/hotel itself, not on daily schedules or route. 
###Only consider which restaurant/activity/hotel are suitable to include in the travel route, without taking time factors into account.
###If there are AS and determine that the information is sufficient(no tool call is needed), please consider them together with the existing tool search results.Generate a JSON response based on the information from both sources.
"""

        user_prompt = f"""# AS:
{assessment_suggestions}

# Shared Memory Information:
{memory_info}

# User Input
User query: {user_query}

User preferences: {user_preferences}

#Existing tool search results
search results:{search_activities_results}
"""

        result = call_llm(system_prompt, user_prompt)

        # Extract content from the result
        if result and result.get("messages"):
            ai_message = result["messages"][0]
            if hasattr(ai_message, "tool_calls") and ai_message.tool_calls:
                print("有 tool call")
            else:
                content = getattr(ai_message, "content", "")
                recommendations_json = clean_json_string(content)
                try:
                    recommendations = json.loads(recommendations_json)
                    # Save to shared memory
                    shared_memory.write_memory(
                        "Recommendation Agent",
                        f"Recommend based on tool results and user input",
                        str(recommendations),
                    )
                except json.JSONDecodeError:
                    print("recommendations_json 无法解析:", recommendations_json)
            updated_messages.append(ai_message)
            short_term_memory.append(ai_message)
        else:
            print("recommendation_agent failed result result:", result)

    # 情况3:首次进入该节点，调用完工具后再次进入该节点——》不再调用工具，直接返回结果
    # 情况4:经过assessment_agent调用完工具再进入该节点——》不再调用工具，结合AS返回结果
    else:
        # Process tool result and generate recommendations
        system_prompt = """###You are a professional trip planner. 
####Based on the assessment suggestions(The assessment suggestions here are those targeting the existing plan. To avoid confusion with other suggestions, they are specifically referred to as AS here.), shared memory information,user input and existing tool search results(Supplementary information obtained from past use of tools), Decide on activities, dining options, and accommodations for the trip, and determine if tools are needed to gather additional information.
####Based on the tool results, create detailed recommendations for activities, dining options, and hotel accommodations during the trip. 
###If there are AS, please combine the AS with the tool results to generate the recommendations; if not, you only need to generate the recommendations based on the tool results.
###please remember that the tool returns JSON data of activity, dining, and hotel rankings during the trip. You need to determine these elements for the trip based on the ranking suggestions.
###Format your response as a JSON object.
like:
{
    "restaurants": [
        {"name": "Le Jules Verne", "location": "shanghai-xuhui","description":"..."},
        {"name": "Chez L'Ami Jean", "location": "nanjing-jiangsu","description":"..."},
        {"name": "La Tour d'Argent", "location": "...","description":"..."}
    ],
    "activities": [
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."}
    ],
    "hotels": [
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."},
        {"name": "...", "location": "...","description":"..."}
    ]
}
###The activities I'm referring to here are local activities, such as cultural festivals or entertainment events, not activities like sightseeing.
###All the above locations should be labeled in the format of "Level 1 Area-Level 2 Area", where Level 1 Area refers to the division of the target place, and Level 2 Area refers to the division of the Level 1 Area.
###Each restaurant/activity/hotel in the plan should include corresponding descriptive recommendations(description) and location. 
###Focus on the restaurant/activity/hotel itself, not on daily schedules or route. 
###Only consider which restaurant/activity/hotel are suitable to include in the travel route, without taking time factors into account.
###Please respond only in JSON format, do not reply with other statements.
"""

        user_prompt = f"""# AS:
{assessment_suggestions}

# Shared Memory Information:
{memory_info}

# User Input
User query: {user_query}

User preferences: {user_preferences}

#Existing tool search results
search results:{search_activities_results}
"""

        result = call_llm_without_tools(system_prompt, user_prompt)

        # Extract content from the result
        if result and result.get("messages"):
            ai_message = result["messages"][0]
            content = getattr(ai_message, "content", "")
            updated_messages.append(ai_message)
            short_term_memory.append(ai_message)
        else:
            content = ""

        # Parse the recommendations
        try:
            cleaned_content = clean_json_string(content)
            recommendations = json.loads(cleaned_content)
        except json.JSONDecodeError:
            # Fallback to default recommendations if JSON parsing fails
            print("can not parse content:", content)

        # Save to shared memory
        shared_memory.write_memory(
            "Recommendation Agent",
            f"Recommend based on tool results and user input",
            str(recommendations),
        )

    print("recommendations : ", recommendations)
    return {
        "messages": updated_messages,
        "short_term_memory": short_term_memory,
        "recommendations": recommendations,
        "search_activities_results": search_activities_results,
    }
