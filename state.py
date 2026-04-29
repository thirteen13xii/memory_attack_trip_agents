from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class State(TypedDict):
    """Graph state for travel planning workflow"""

    messages: list[BaseMessage]
    short_term_memory: list[BaseMessage]
    user_query: str
    user_preferences: dict
    encrypted_info: dict
    trip_plan: dict
    recommendations: dict
    meeting_schedule: dict
    assessment_result: dict
    report: str
    reply: str
    conversation_history: list
    phone_number: str
    search_activities_results: list[dict]
    search_attractions_results: list[dict]
    bank_card_number: str
    tool_use_num: int
