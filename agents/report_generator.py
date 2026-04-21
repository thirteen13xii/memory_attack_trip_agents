from state import State
from memory import shared_memory
from agents.llm_call import call_llm_without_tools
import os
from datetime import datetime


def report_generator(state: State) -> State:
    print("-" * 80)
    print("here is report_generator!!!")
    print("-" * 80)
    """Report Generator node to create trip recommendation Markdown report"""
    meeting_schedule = state.get("meeting_schedule", {})

    # Use LLM to generate humanized travel recommendations
    system_prompt = "You are a professional travel advisor. Based on the provided meeting schedule, create a comprehensive and humanized travel recommendation report. Include sections for daily itineraries, activity recommendations, dining suggestions, and practical tips. Make the report engaging and informative, as if written by a personal travel consultant. Format the report in Markdown with clear sections."
    user_prompt = f"Meeting Schedule: {meeting_schedule}"

    report = call_llm_without_tools(system_prompt, user_prompt)
    if report and report.get("messages"):
        report = report["messages"][0]
        report = getattr(report, "content", "")

    # Fallback to default report if LLM call fails
    if not report:
        print("No response from LLM, using fallback report")

    # Create result directory if it doesn't exist
    result_dir = "result"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Generate Markdown filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join(result_dir, f"travel_recommendation_{timestamp}.md")

    # Save Markdown report
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)

    # Save to shared memory
    shared_memory.write_memory(
        "Report Generator",
        "Generate travel recommendation Markdown",
        f"Markdown report saved to: {md_path}",
    )

    return {"report": report, "md_path": md_path}
