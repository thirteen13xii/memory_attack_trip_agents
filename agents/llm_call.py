import os
from langchain_openai import ChatOpenAI
from tools.search_activities_restaurants_hotels import (
    search_activities_restaurants_hotels,
)
from tools.search_tourist_attractions import search_tourist_attractions

model = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-f9ab1844e7c34fdda33610cdd86c04a7",
)

model_with_tools = model.bind_tools(
    [search_activities_restaurants_hotels, search_tourist_attractions]
)


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    """Call LLM with system prompt and user prompt"""
    try:
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call the LLM
        response = model_with_tools.invoke(messages)

        # Save log
        save_llm_log(system_prompt, user_prompt, response)

        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"messages": ""}


def call_llm_without_tools(
    system_prompt: str, user_prompt: str, temperature: float = 0.7
):
    """Call LLM with system prompt and user prompt"""
    try:
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call the LLM
        response = model.invoke(messages)

        # Save log
        save_llm_log(system_prompt, user_prompt, response)

        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"messages": ""}


def save_llm_log(system_prompt: str, user_prompt: str, response):
    """Save LLM call log to file"""
    # Create log directory if it doesn't exist
    log_dir = "llm_call_log"
    os.makedirs(log_dir, exist_ok=True)

    # Find next available file number
    i = 1
    while os.path.exists(os.path.join(log_dir, f"{i}.txt")):
        i += 1

    # Create log file
    log_file = os.path.join(log_dir, f"{i}.txt")

    # Prepare log content
    log_content = f"System Prompt:\n{system_prompt}\n\nUser Prompt:\n{user_prompt}\n\nResponse:\n{response}\n"

    # Write to file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_content)


if __name__ == "__main__":
    result = call_llm("你是一个故人，请用文言文回复", "你好")
    print(result)
