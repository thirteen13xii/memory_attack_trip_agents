from tools.api import api


def search_tourist_attractions(location: str):
    """Search for tourist attractions in a location.

    Args:
        location: The location to search in (e.g., "Paris, France").Only enter one large location (where the user wants to go), and do not enter small locations like 'Beijing, China'.

    Returns:
        A dictionary with search results in the format:
        {
            "location": location,
            "attractions": [
                {"name": "Attraction Name", "rating": 4.8, "description": "Description of the attraction"},
                {"name": "Attraction Name", "rating": 4.7, "description": "Description of the attraction"},
                {"name": "Attraction Name", "rating": 4.6, "description": "Description of the attraction"}
            ]
        }
    """
    print(f"成功调用search_tourist_attractions for location: {location}")

    # System prompt to instruct LLM to return JSON format
    system_prompt = """You are a travel assistant that provides information about tourist attractions.
Please return a JSON object with information about the top tourist attractions in the given location.
The JSON should have the following structure:
{
    "location": "[Location]",
    "attractions": [
        {"name": "[Attraction Name]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Attraction Name]", "rating": [Rating], "description": "[Description]"},
        {"name": "[Attraction Name]", "rating": [Rating], "description": "[Description]"}
    ]
}
Please include at least 3 attractions, each with a name, a rating (between 1-5), and a brief description.
Only return the JSON object, no additional text."""

    # User prompt with the location
    user_prompt = (
        f"Please provide information about the top tourist attractions in {location}."
    )

    # Call LLM API
    result = api(system_prompt, user_prompt)

    # Extract content from the result
    if result and result.get("messages"):
        response = result["messages"][0]
        content = getattr(response, "content", "")
        print(f"search_tourist_attractions tool response: {content}")
        return content
    else:
        print("Error: No response from API")
        # Fallback response
        return {}
