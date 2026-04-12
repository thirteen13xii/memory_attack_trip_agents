from langchain_openai import ChatOpenAI
from tools.search_activities_restaurants_hotels import search_activities_restaurants_hotels
from tools.search_tourist_attractions import search_tourist_attractions

model = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-f9ab1844e7c34fdda33610cdd86c04a7"
)

model_with_tools = model.bind_tools([
    search_activities_restaurants_hotels,
    search_tourist_attractions
])

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    """Call LLM with system prompt and user prompt"""
    try:
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Call the LLM
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"messages": ""}

def call_llm_without_tools(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    """Call LLM with system prompt and user prompt"""
    try:
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Call the LLM
        response = model.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"messages": ""}


if __name__ == "__main__":
    result=call_llm("你是一个故人，请用文言文回复","你好")
    print(result)