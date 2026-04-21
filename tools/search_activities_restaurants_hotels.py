from tools.api import api
import json


def search_activities_restaurants_hotels(location: str):
    """Search for activities, restaurants, or hotels in a location.

    Args:
        location: The location to search in (e.g., "Paris, France").Only enter one large location (where the user wants to go), and do not enter small locations like 'Beijing, China'.

    Returns:
        A JSON string with search results in the format:
        {
            "location": location,
            "activities": [
                {"name": "Activity Name", "rating": 4.8, "description": "Description of the activity"},
                {"name": "Activity Name", "rating": 4.7, "description": "Description of the activity"},
                {"name": "Activity Name", "rating": 4.6, "description": "Description of the activity"}
            ],
            "restaurants": [
                {"name": "Restaurant Name", "cuisine": "Cuisine Type", "rating": 4.8, "description": "Description of the restaurant"},
                {"name": "Restaurant Name", "cuisine": "Cuisine Type", "rating": 4.7, "description": "Description of the restaurant"},
                {"name": "Restaurant Name", "cuisine": "Cuisine Type", "rating": 4.6, "description": "Description of the restaurant"}
            ],
            "hotels": [
                {"name": "Hotel Name", "rating": 4.8, "description": "Description of the hotel"},
                {"name": "Hotel Name", "rating": 4.7, "description": "Description of the hotel"},
                {"name": "Hotel Name", "rating": 4.6, "description": "Description of the hotel"}
            ]
        }
    """
    print(f"成功调用search_activities_restaurants_hotels for location: {location}")

    # System prompt to instruct LLM to return JSON format
    system_prompt = """You are a travel assistant that provides information about activities, restaurants, and hotels.
Please return a JSON object with information about the top activities, restaurants, and hotels in the given location.
The JSON should have the following structure:
{
    "location": "[Location]",
    "activities": [
        {"name": "[Activity Name]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Activity Name]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Activity Name]", "rating": [Rating], "description": "[Description]"}
    ],
    "restaurants": [
        {"name": "[Restaurant Name]", "cuisine": "[Cuisine Type]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Restaurant Name]", "cuisine": "[Cuisine Type]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Restaurant Name]", "cuisine": "[Cuisine Type]", "rating": [Rating], "description": "[Description]"}
    ],
    "hotels": [
        {"name": "[Hotel Name]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Hotel Name]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Hotel Name]", "rating": [Rating], "description": "[Description]"}
    ]
}
The activities I'm referring to here are local activities, such as cultural festivals or entertainment events, not activities like sightseeing.
Please include at least 3 items for each category, each with a name, a rating (between 1-5), and a brief description.
For restaurants, also include the cuisine type.
Only return the JSON object, no additional text."""

    # User prompt with the location
    user_prompt = f"Please provide information about the top activities, restaurants, and hotels in {location}."

    # Call LLM API
    result = api(system_prompt, user_prompt)

    # Extract content from the result
    if result and result.get("messages"):
        response = result["messages"][0]
        content = getattr(response, "content", "")
        print(f"search_activities_restaurants_hotels tool response: {content}")
        return content
    else:
        print("Error: No response from API")
        # Fallback response
        return {}
