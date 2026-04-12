def search_activities_restaurants_hotels(location: str, category: str = None):
    """Search for activities, restaurants, or hotels in a location.

    Args:
        location: The location to search in (e.g., "Paris, France")
        category: Optional category filter (e.g., "activities", "restaurants", "hotels")

    Returns:
        A dictionary with search results
    """
    print("成功调用search_activities_restaurants_hotels")
    # Placeholder implementation
    return {
        "location": location,
        "category": category,
        "results": [
            {"name": "Sample Activity", "type": "activity", "rating": 4.5},
            {"name": "Sample Restaurant", "type": "restaurant", "rating": 4.2},
            {"name": "Sample Hotel", "type": "hotel", "rating": 4.8}
        ]
    }