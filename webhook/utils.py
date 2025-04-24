from .client import HospitableClient
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


def check_booking_availability(
    property_id ,
    property_name ,
    city_name,
    check_in ,
    check_out 
):
    """
    Check the availability of a property for the specified dates.

    Args:
        property_id (str, optional): The ID of the property to check availability for.
        property_name (str, optional): The name of the property (if ID is not provided).
        check_in  (str, optional): Start date in YYYY-MM-DD format (e.g., '2025-04-22').
        check_out (str, optional): End date in YYYY-MM-DD format (e.g., '2025-04-25').

    Returns:
        dict: A dictionary with 'available' (bool) and 'message' (str) indicating availability.
    """
    # Ensure at least one identifier is provided
    # if not property_id and not property_name:
    #     return {"available": False, "message": " Please provide either a property ID or property name."}
    property_ids = []

    # Ensure dates are provided
    if not check_in  or not check_out:
        return {"available": False, "message": " Please provide both check_in  and check_out."}

    # Convert date strings to datetime objects
    try:
        
        
        start = datetime.strptime(check_in , "%Y-%m-%d").date()
        end = datetime.strptime(check_out, "%Y-%m-%d").date()
        if start >= end:
            return {"available": False, "message": "End date must be after start date."}
    except ValueError:
        return {"available": False, "message": "Dates must be in YYYY-MM-DD format (e.g., 2025-04-22)."}

# ekkane hoy toba dubai er property filter kora lagbe get properites by country create kore den

    try:
        # Fetch property data based on the provided name, city, or country
        if property_name and not property_id:
            # Get property by name
            property_data = client.get_property_by_name(property_name)
            property_id = property_data.get("data", [{}])[0].get("id")

            if not property_id:
                return {"available": False, "message": f"Property '{property_name}' not found."}

        elif city_name and not property_id:
            # Get property by city
            property_data = client.get_property_by_city(city_name)
            if len(property_data.get("data", [])) > 0:
                property_ids = [prop.get("id") for prop in property_data.get("data", [])]
                # print("Property IDs in city:", property_ids)
            else:
                return {"available": False, "message": f"No properties found in {city_name}."}


        # Fetch reservations for the properties
        reservations_data = client.get_reservations_by_properties(property_ids=property_ids).get("data", [])
        # print("Reservations data:", reservations_data)

        # Date overlap check with existing reservations
        for booking in reservations_data:
            # Skip cancelled reservations
            if booking.get("status") == "cancelled":
                continue

            booked_start = datetime.fromisoformat(booking["arrival_date"].replace("Z", "+00:00")).date()
            booked_end = datetime.fromisoformat(booking["departure_date"].replace("Z", "+00:00")).date()

            # Check for overlap: start < booked_end and end > booked_start
            if start < booked_end and end > booked_start:
                return {
                    "available": False,
                    "message": f"Property is already booked from {booked_start} to {booked_end}."
                }

        return {"available": True, "message": "Property is available for these dates."}

    except Exception as e:
        return {"available": False, "message": f"Failed to check availability: {str(e)}"}


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

    # Create the messages structure for the API request
    messages = [{"role": "system", "content": "You are an assistant that summarizes conversations, and it's important to keep track of who said what."}]
    messages.extend([{"role": entry["role"], "content": entry["content"]} for entry in formatted_messages])
    
    # Call the OpenAI API to summarize the conversation using client.chat.completions.create
    try:
        summary_response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or whichever model you're using for summarization
            messages=messages,
            # temperature=0.7  # Uncomment if you want to specify temperature
        )
        summary = summary_response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error in summarizing conversation: {e}")
        return None


