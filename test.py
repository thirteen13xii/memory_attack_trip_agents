import os
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

        return {"messages": [response]}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"messages": ""}


if __name__ == "__main__":
    result = call_llm_without_tools(
        "", "你是什么模型，是v4吗，如果是，是v4-pro还是v4-flash"
    )
    print(result)

    # from openai import OpenAI

    # client = OpenAI(
    #     api_key="sk-f9ab1844e7c34fdda33610cdd86c04a7",
    #     base_url="https://api.deepseek.com",
    # )

    # # Turn 1
    # messages = [
    #     {
    #         "role": "user",
    #         "content": "你是什么模型，是v4吗，如果是，是v4-pro还是v4-flash",
    #     }
    # ]
    # response = client.chat.completions.create(
    #     model="deepseek-v4-pro",
    #     messages=messages,
    #     reasoning_effort="high",
    #     extra_body={"thinking": {"type": "enabled"}},
    # )
    # print(response)

    # reasoning_content = response.choices[0].message.reasoning_content
    # content = response.choices[0].message.content
    # print(reasoning_content)
    # print("-----------------")
    # print(content)
