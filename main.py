from workflow import chain

if __name__ == "__main__":
    # Example usage
    initial_state = {
        "user_query": "I want to plan a trip to Japan for 9 days",
        "user_preferences": {
            "budget": "medium",
            "interests": ["art", "history", "food"],
            "transportation": "public",
            "accommodation": "hotel"
        },
        "conversation_history": [],
        "phone_number": "1234567890"
    }

    print("#######Starting travel planning workflow...#######")
    print("="*80)
    result = chain.invoke(initial_state)

    print("\n=== Final Result ===")
    print("Reply:")
    print(result.get("reply", "No reply generated"))

    print("\n=== Conversation History ===")
    for message in result.get("conversation_history", []):
        print(f"{message['role']}: {message['content']}")

    print("\n=== Trip Report ===")
    print(result.get("report", "No report generated"))