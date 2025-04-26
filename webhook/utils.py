# from .client import HospitableClient
from client import HospitableClient
from datetime import datetime

import openai
from datetime import datetime

client = HospitableClient()  # Initialize the API client

def get_property_details(property_id=None) :
    """
    Fetch details of properties. If a property ID is provided, returns details for that specific property.
    If no property ID is provided, returns details for all properties.

    Args:
        property_id (str, optional): The ID of the property to fetch details for. If None, fetches all properties.

    Returns:
        dict: A dictionary containing property details. For a single property, returns the property data.
              For all properties, returns a list of property data.
    """
    try:
        if property_id:
            get_p = [property_id,] 
            # Fetch details for a specific property
            property_data = client.get_listings(get_p)
            return property_data.get("data", {})
        else:
            # Fetch details for all properties
            properties_data = client.get_listings().get("data", [])
            data = preprocessed_property_data(properties_data)                # need to process the property data
            return data

    except Exception as e:
        # Handle potential API errors
        return {"error": f"Failed to fetch property details: {str(e)}"}



def check_booking_availability(property_id=None, property_name=None, city_name=None, check_in=None, check_out=None):
    """
    Check the availability of a property or properties in a city for the specified dates.

    Args:
        property_id (str, optional): The ID of the property to check availability for.
        property_name (str, optional): The name of the property (if ID is not provided).
        city_name (str, optional): The city where the property is located.
        check_in (str, optional): Start date in YYYY-MM-DD format (e.g., '2025-06-10').
        check_out (str, optional): End date in YYYY-MM-DD format (e.g., '2025-06-15').

    Returns:
        dict: A dictionary with 'available' (bool) and 'message' (str) indicating availability.
    """
    # Ensure dates are provided
    if not check_in or not check_out:
        return {"available": False, "message": "Please provide both check_in and check_out dates."}

    try:
        start = datetime.strptime(check_in, "%Y-%m-%d").date()
        end = datetime.strptime(check_out, "%Y-%m-%d").date()
        if start >= end:
            return {"available": False, "message": "Check-out date must be after check-in date."}
    except ValueError:
        return {"available": False, "message": "Dates must be in YYYY-MM-DD format (e.g., 2025-06-10)."}

    # Determine property IDs to check
    property_ids = []
    properties_data = []

    if property_id:
        property_ids = [property_id,]
    elif property_name:
        property_data = client.get_property_by_name(property_name)
        if not property_data.get("data"):
            return {"available": False, "message": f"Property '{property_name}' not found."}
        property_ids = [property_data["data"][0]["id"]]
    elif city_name:
        properties_data = client.get_property_by_city(city_name).get("data", [])
        if not properties_data:
            return {"available": False, "message": f"No properties found in {city_name}."}
        property_ids = [prop["id"] for prop in properties_data]
    else:
        return {"available": False, "message": "Please provide property_name, or city_name."}

    # Check availability for each property
    available_properties = []
    for prop_id in property_ids:
        reservations = client.get_reservations_by_properties(property_ids=[prop_id]).get("data", [])
        is_available = True
        for booking in reservations:
            if booking.get("status") == "cancelled":
                continue
            booked_start = datetime.fromisoformat(booking["arrival_date"].replace("Z", "+00:00")).date()
            booked_end = datetime.fromisoformat(booking["departure_date"].replace("Z", "+00:00")).date()
            if start < booked_end and end > booked_start:
                is_available = False
                break
        if is_available:
            # Get property name for response (if available)
            prop_name = prop_id
            if properties_data:
                prop_name = next((prop["name"] for prop in properties_data if prop["id"] == prop_id), prop_id)
            available_properties.append(prop_name)

    # Generate response
    if available_properties:
        if len(property_ids) == 1:
            return {"available": True, "message": "The property is available for these dates."}
        else:
            return {
                "available": True,
                "message": f"The following properties in {city_name} are available: {', '.join(available_properties)}"
            }
    else:
        if len(property_ids) == 1:
            return {"available": False, "message": "The property is not available for these dates."}
        else:
            return {
                "available": False,
                "message": f"No properties in {city_name} are available for these dates."
            }


def preprocessed_property_data(properties_data):
    """
    Preprocess the property data to a more structured and user-friendly format.
    """
    preprocessed_data = []
    
    for prop in properties_data:
        property_info = {
            "id": prop.get("id"),
            "name": prop.get("name"),
            "public_name": prop.get("public_name", "N/A"),
            # "picture": prop.get("picture", "N/A"),
            "address": prop.get("address", {}).get("display", "N/A"),
            "city": prop.get("address", {}).get("city", "N/A"),
            "country": prop.get("address", {}).get("country_name", "N/A"),
            "coordinates": {
                "latitude": prop.get("address", {}).get("coordinates", {}).get("latitude", "N/A"),
                "longitude": prop.get("address", {}).get("coordinates", {}).get("longitude", "N/A"),
            },
            "timezone": prop.get("timezone", "N/A"),
            "listed": prop.get("listed", False),
            "currency": prop.get("currency", "N/A"),
            "summary": prop.get("summary", "N/A"),
            "description": prop.get("description", "N/A"),
            "checkin": prop.get("checkin", "N/A"),
            "checkout": prop.get("checkout", "N/A"),
            "amenities": prop.get("amenities", []),
            "capacity": prop.get("capacity", {}),
            # "room_details": prop.get("room_details", []),
            # "property_type": prop.get("property_type", "N/A"),
            # "room_type": prop.get("room_type", "N/A"),
            "house_rules": prop.get("house_rules", {}),
            "calendar_restricted": prop.get("calendar_restricted", False)
        }

        # You may add additional processing here to handle custom cases

        # Append processed property data to the final list
        preprocessed_data.append(property_info)

    return preprocessed_data



def process_conversation(msg, client):
    # Check if the message list is empty
    if not msg:
        return "No previous messages"
    
    # Format the fetched messages into a list with roles (user and assistant)
    formatted_messages = []
    for m in msg:
        formatted_messages.append({"role": "user", "content": m.message_text})
        if m.reply:
            formatted_messages.append({"role": "assistant", "content": m.reply})
        # Add the system message that provides context for summarizing property details
    # system_prompt = """
    #     You are an assistant tasked with summarizing conversations involving property bookings and related topics. 
    #     Summaries should be clear, distinguishing between user and assistant messages, and highlight key details like:
    #     - property_name, address, description, Booking Dates, Arrival/Departure Dates, Check-in/Check-out Times.
    #     - Reservation Status, Number of Guests, Room Details, Amenities, Property Type, House Rules, Calendar Restrictions, Capacity, Tags.
        
    #     Ensure responses are concise, clear, and address user questions effectively.
    #     """   
        
    system_prompt = """
        You are an assistant tasked with summarizing conversations that involve property bookings, details, and related topics. Your summaries should maintain clarity and should always distinguish between user and assistant messages. Make sure to highlight important details, such as booking dates, location, amenities, and other property-specific data.

        The conversation may involve mentions of properties like:
        - "public_name" (e.g., 'The Walk Flat')
        - "address", including city, country, and postcode
        - "description", "summary", and details about the property (such as amenities, check-in/out times, and specific features)
        - "platform" (e.g., 'airbnb')
        - "platform_id" (e.g., 'HMJR3D3MHP')
        - "reservation status", including booking details like dates and guests

        Key details to include in your summary:
        - **Property Name**: Name of the property (e.g., The Walk Flat).
        - **Address**: Full address, including street, city, country, postcode, and coordinates.
        - **Description & Summary**: Short and detailed descriptions of the property (e.g., location, key features, proximity to nearby landmarks).
        - **Booking Dates**: The exact dates the user made the booking.
        - **Arrival and Departure Dates**: The dates the guest is scheduled to arrive and depart.
        - **Check-in and Check-out Times**: The exact times for checking in and checking out.
        - **Reservation Status**: Status of the reservation (e.g., accepted, pending).
        - **Number of Guests**: Include the total number of guests, adults, children, infants, and pets.
        - **Room Details**: Information about room types (e.g., one bedroom with a double bed and a couch bed).
        - **Amenities**: Important amenities offered by the property (e.g., pool, Wi-Fi, kitchen, air conditioning, parking, elevator).
        - **Property Type**: Type of property (e.g., condominium).
        - **Room Type**: Type of room (e.g., entire home).
        - **House Rules**: Include house rules (e.g., pets allowed, smoking allowed, events allowed).
        - **Calendar Restrictions**: Whether the property has calendar restrictions (e.g., availability for long-term stays).
        - **Capacity**: Maximum guest capacity, number of bedrooms, and number of bathrooms.
        - **Tags**: Any relevant tags for the property (e.g., suitable for families, business travelers, etc.).
        
        If the user has asked for specific details about the property or reservation, ensure those are included in the summary, such as:
        - Check-in/Check-out dates
        - Number of guests
        - Room features (e.g., bed types, number of rooms)
        - Property features (e.g., pool, free parking)
        - House rules (e.g., smoking, pets allowed)
        - Other relevant property-specific data

        Ensure the summary is concise, clear, and covers the user's questions or information requests effectively.
        """
    
    
    # Create the messages structure for the API request
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend([{"role": entry["role"], "content": entry["content"]} for entry in formatted_messages])
    
    # Call the OpenAI API to summarize the conversation using client.chat.completions.create
    try:
        summary_response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or whichever model you're using for summarization
            messages=messages,
            max_tokens=150,  # Adjust the max tokens as needed
            # temperature=0.7  # Uncomment if you want to specify temperature
        )
        summary = summary_response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error in summarizing conversation: {e}")
        return None


