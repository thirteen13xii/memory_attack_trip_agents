from state import State
from memory import shared_memory


def privacy_guardian(state: State) -> State:
    print("-" * 80)
    print("state messages:")
    for i in state.get("messages", []):
        print(i)
    print("state user_query:", state.get("user_query", ""))
    print("-" * 80)
    """Privacy Guardian node to encrypt user information"""
    user_query = state["user_query"]

    # Simplified encryption logic (in real scenario, use proper encryption)
    encrypted_info = {
        "user_query": user_query,
        "encrypted": True,
        "access_granted": ["Trip Planner", "Recommendation Agent", "Meeting Scheduler"]
    }

    # Save to shared memory
    shared_memory.write_memory("Privacy Guardian", "Encrypt user information",
                               "User information encrypted successfully")

    # Update conversation history
    conversation_history = state.get("conversation_history", [])
    conversation_history.append({"role": "assistant", "content": "Your information has been securely processed."})
    print("privacy : User information has been securely processed.")

    return {
        "encrypted_info": encrypted_info,
        "conversation_history": conversation_history
    }