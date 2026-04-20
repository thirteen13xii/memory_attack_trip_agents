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
        "Plan trip based on assessment suggestions, memory info, and user input"
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
    trip_plan = {}

    # 情况1:首次进入——》应该调用工具
    # 情况2:经过assessment_agent再进入该节点——》缺少信息，再次调用工具/信息足够，不需要调用工具
    if not is_tool_message:
        # First, use LLM to determine locations and which tool to use
        system_prompt = """###You are a professional trip planner. 
####Based on the assessment suggestions(The assessment suggestions here are those targeting the existing plan. To avoid confusion with other suggestions, they are specifically referred to as AS here.), shared memory information,user input and existing tool search results(Supplementary information obtained from past use of tools), determine the main locations for the trip and if need tool to use to gather information.
###If there are no AS, it indicates that you are entering this section for the first time, and you need to call tools to gather information
###If there are AS, please determine whether the existing information is sufficient for making modifications based on the suggestions—if not, you also need to call tools.
###Determine whether it is necessary to use the tool(For example, no existing tool search results, or additional tool information is needed.), and if not,format your response as a JSON object with keys: route (array of destinations), and description.
like:
{
  "route": ["Destination 1", "Destination 2", "Destination 3"],
  "description": "A detailed description of the trip route, including the highlights of each destination and the overall travel experience."
}
###If there are tool call results, please remember that the tool returns JSON data of tourist spot rankings. You need to determine the travel route based on the ranking suggestions and route planning.
###The plan should include a sequence of destinations and brief descriptions of each destination. 
###Focus on the route itself, not on daily schedules or specific activities. 
###Only consider which locations are suitable to include in the travel route, without taking time factors into account.
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
                trip_plan_json = clean_json_string(content)
                try:
                    trip_plan = json.loads(trip_plan_json)
                    # Save to shared memory
                    shared_memory.write_memory(
                        "Trip Planner",
                        f"Plan trip based on tool results and user input",
                        str(trip_plan),
                    )
                except json.JSONDecodeError:
                    print("trip_plan_json 无法解析:", trip_plan_json)
            updated_messages.append(ai_message)
        else:
            print("trip_planner failed result result:", result)

    # 情况3:首次进入该节点，调用完工具后再次进入该节点——》不再调用工具，直接返回结果
    # 情况4:经过assessment_agent调用完工具再进入该节点——》不再调用工具，结合AS返回结果
    else:
        # Process tool result and generate trip plan
        system_prompt = """###You are a professional trip planner.
####Based on the assessment suggestions(The assessment suggestions here are those targeting the existing plan. To avoid confusion with other suggestions, they are specifically referred to as AS here.), shared memory information,user input and existing tool search results(Supplementary information obtained from past use of tools), determine the main locations for the trip and if need tool to use to gather information. 
####Based on the tool results, create a detailed trip route plan. 
###If there are AS, please combine the AS with the tool results to generate the route; if not, you only need to generate the route based on the tool results.
###please remember that the tool returns JSON data of tourist spot rankings. You need to determine the travel route based on the ranking suggestions and route planning.
###Format your response as a JSON object with keys: route (array of destinations), and description.
like:
{
  "route": ["Destination 1", "Destination 2", "Destination 3"],
  "description": "A detailed description of the trip route, including the highlights of each destination and the overall travel experience."
}
###The plan should include a sequence of destinations and brief descriptions of each destination. 
###Focus on the route itself, not on daily schedules or specific activities. 
###Only consider which locations are suitable to include in the travel route, without taking time factors into account.
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
        else:
            content = ""

        # Parse the trip plan
        try:
            trip_plan = json.loads(content)
        except json.JSONDecodeError:
            # Fallback to default plan if JSON parsing fails
            print("can not parse content:", content)

        # Save to shared memory
        shared_memory.write_memory(
            "Trip Planner",
            f"Plan trip based on tool results and user input",
            str(trip_plan),
        )

    print("trip_plan : ", trip_plan)
    return {
        "messages": updated_messages,
        "trip_plan": trip_plan,
        "search_activities_results": search_activities_results,
    }
