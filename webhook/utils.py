from .client import HospitableClient

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
        print("property_name", property_name)
        print("city_name", city_name)
        if property_name and not property_id:
            # Assume client.get_property_by_name returns a property ID
            property_data = client.get_property_by_name(property_name)
            property_id = property_data.get("data", [{}])[0].get("id")  # Safely get the id

            if not property_id:
                return {"available": False, "message": f"Property '{property_name}' not found."}
            
                        # Fetch reservations for the property
            reservations_data = client.get_reservations_by_properties(
                property_ids=[property_id]
            ).get("data", [])
            
        elif city_name and not property_id:    
            property_data = client.get_property_by_city(city_name)
            property_ids = property_data.get("data", [{}])[0].get("id")  # Safely get the id

            # if not property_id:
            #     return {"available": False, "message": f"Property '{property_name}' not found."}
            
            reservations_data = client.get_reservations_by_properties(
                property_ids=property_ids
            ).get("data", [])
        
        # Check for date overlaps with existing reservations
        for booking in reservations_data:
            # Skip cancelled reservations
            if booking.get("status") == "cancelled":
                continue

            # Parse booked dates in ISO format
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