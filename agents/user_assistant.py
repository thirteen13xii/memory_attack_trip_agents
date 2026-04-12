from state import State
from memory import shared_memory
from agents.llm_call import call_llm
from langchain_core.messages import AIMessage, HumanMessage


def user_assistant(state: State) -> State:
    print("-"*80)
    print("state messages:",state.get("messages", []))
    print("state user_query:",state.get("user_query", ""))
    print("-"*80)
    """User Assistant node to handle conversation and determine if entering travel planning flow"""
    user_query = state["user_query"]

    # Use LLM to determine if the query is travel-related and generate appropriate response
    is_travel_query, response = handle_user_query(user_query)

    # Save to shared memory
    shared_memory.write_memory("User Assistant", user_query, f"Identified as travel query: {is_travel_query}")

    # Update conversation history
    conversation_history = state.get("conversation_history", [])
    conversation_history.append({"role": "user", "content": user_query})
    conversation_history.append({"role": "assistant", "content": response})

    print("user_assistant response :",response)

    # Create message object
    assistant_message = AIMessage(content=response)

    # Update messages list
    updated_messages = state.get("messages", []) + [assistant_message]

    return {
        "messages": updated_messages,
        "user_query": user_query,
        "conversation_history": conversation_history,
        "is_travel_query": is_travel_query
    }


def handle_user_query(query: str) -> tuple[bool, str]:
    """Use LLM to determine if a query is travel-related and generate appropriate response"""
    system_prompt = "You are a helpful assistant. First, determine if the user's query is related to travel planning. Then, generate an appropriate response based on that determination.\n\nFormat your response as follows:\n[TRAVEL_RELATED: YES/NO]\n[RESPONSE: Your response here]"
    user_prompt = query

    result = call_llm(system_prompt, user_prompt)

    if not result or not result.get("messages"):
        print("error: handle_user_query failed result:",result)
        return False,""

    # Extract content from the AIMessage
    ai_message = result["messages"][0]
    content = getattr(ai_message, "content", "")
    if not content:
        print("error: handle_user_query failed content:", content)
        return False, ""
    # Use the extracted content
    result = content

    # Parse the response
    lines = result.split('\n')
    is_travel = False
    response = ""

    for line in lines:
        if line.startswith('[TRAVEL_RELATED:'):
            is_travel = 'YES' in line
        elif line.startswith('[RESPONSE:'):
            response = line[len('[RESPONSE:'):].strip()

    # Fallback if parsing fails
    if not response:
        if is_travel:
            response = "I'll help you plan your trip. Let's start by gathering some information."
        else:
            response = "I see you're not asking about travel planning. How can I assist you with other matters?"

    return is_travel, response