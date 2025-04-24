
# Define the tools list for OpenAI API
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_property_details",
            "description": "Fetch details of the properties. Can specify a property ID to get details for a specific property.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The ID of the property to fetch details for. If not provided, details for all properties are returned."
                    }
                },
                "required": []  # property_id is optional
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_booking_availability",
            "description": "Check if a property is available for booking between the specified check-in and check-out dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The ID of the property to check availability for. Optional if property_name is provided."
                    },
                    "property_name": {
                        "type": "string",
                        "description": "The name of the property to check availability for. Optional if property_id is provided."
                    },
                    "city_name": {
                        "type": "string",
                        "description": "The city where the property is located. Optional if provided alone, returns all available properties in the city."
                    },
                    "check_in": {
                        "type": "string",
                        "description": "Check-in date in YYYY-MM-DD format (e.g., '2025-04-22')."
                    },
                    "check_out": {
                        "type": "string",
                        "description": "Check-out date in YYYY-MM-DD format (e.g., '2025-04-25')."
                    }
                },
                "required": ["check_in", "check_out"]
            }
        }
    }
]