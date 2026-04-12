from state import State
from memory import shared_memory
from agents.llm_call import call_llm
import os
from datetime import datetime


def report_generator(state: State) -> State:
    """Report Generator node to create trip recommendation Markdown report"""
    meeting_schedule = state.get("meeting_schedule", {})

    # Use LLM to generate humanized travel recommendations
    system_prompt = "You are a professional travel advisor. Based on the provided meeting schedule, create a comprehensive and humanized travel recommendation report. Include sections for daily itineraries, activity recommendations, dining suggestions, and practical tips. Make the report engaging and informative, as if written by a personal travel consultant. Format the report in Markdown with clear sections."
    user_prompt = f"Meeting Schedule: {meeting_schedule}"
    
    report = call_llm(system_prompt, user_prompt)
    
    # Fallback to default report if LLM call fails
    if not report:
        report = "# Travel Recommendation Report\n\n"
        report += "## Trip Overview\n"
        report += "Based on your scheduled activities, here's a comprehensive travel guide for your trip.\n\n"
        
        # Extract days from schedule
        days = {}
        schedule = meeting_schedule.get('schedule', [])
        for item in schedule:
            time = item.get('time', '')
            if 'Day' in time:
                day = time.split(',')[0]
                if day not in days:
                    days[day] = []
                days[day].append(item)
        
        # Add daily itineraries
        for day, items in days.items():
            report += f"## {day}\n"
            for item in items:
                time = item.get('time', '')
                location = item.get('location', '')
                activity = item.get('activity', '')
                restaurant = item.get('restaurant', '')
                hotel = item.get('hotel', '')
                
                report += f"### {time}\n"
                report += f"**Location:** {location}\n"
                report += f"**Activity:** {activity}\n"
                if restaurant:
                    report += f"**Restaurant:** {restaurant}\n"
                if hotel:
                    report += f"**Hotel:** {hotel}\n"
                report += "\n"
        
        report += "## Travel Tips\n"
        report += "- Make sure to check the opening hours of attractions in advance.\n"
        report += "- Carry comfortable walking shoes for sightseeing.\n"
        report += "- Try local cuisine at recommended restaurants.\n"
        report += "- Keep a copy of your itinerary handy.\n"

    # Create result directory if it doesn't exist
    result_dir = "result"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    # Generate Markdown filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join(result_dir, f"travel_recommendation_{timestamp}.md")
    
    # Save Markdown report
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Save to shared memory
    shared_memory.write_memory("Report Generator", "Generate travel recommendation Markdown", f"Markdown report saved to: {md_path}")

    return {
        "report": report,
        "md_path": md_path
    }