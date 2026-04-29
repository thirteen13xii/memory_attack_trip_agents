from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="deepseek-v4-pro",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-f9ab1844e7c34fdda33610cdd86c04a7",
    model_kwargs={
        "reasoning_effort": "max",
        "extra_body": {"thinking": {"type": "enabled"}},
    },
)


def api(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    """Call LLM with system prompt and user prompt"""
    try:
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call the LLM
        response = model.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"messages": ""}
