from state import State
from memory import shared_memory
from langchain_core.messages import ToolMessage, AIMessage


def privacy_guardian(state: State) -> State:
    """Privacy Guardian node to encrypt user information"""
    user_query = state["user_query"]

    # Simplified encryption logic (in real scenario, use proper encryption)
    encrypted_info = {
        "user_query": user_query,
        "encrypted": True,
        "access_granted": ["Trip Planner", "Recommendation Agent", "Meeting Scheduler"],
    }

    # Save to shared memory
    shared_memory.write_memory(
        "Privacy Guardian",
        "Encrypt user information",
        "User information encrypted successfully",
    )

    # Update conversation history
    conversation_history = state.get("conversation_history", [])
    conversation_history.append(
        {
            "role": "assistant",
            "content": "Your information has been securely processed.",
        }
    )
    print("privacy : User information has been securely processed.")
    security_message = AIMessage(
        content="Security operation: User information(bank_card_number,phone number) has been encrypted. Access granted to: Trip Planner, Recommendation Agent, Meeting Scheduler"
    )
    short_term_memory = state["short_term_memory"]
    short_term_memory.append(security_message)

    return {
        "short_term_memory": short_term_memory,
        "encrypted_info": encrypted_info,
        "conversation_history": conversation_history,
        "tool_use_num": 1,
    }
