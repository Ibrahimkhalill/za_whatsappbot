from openai import OpenAI
import os, json
from dotenv import load_dotenv
from .bot_utilities import tools 
from webhook.models import WhatsAppMessage
from .utils import check_booking_availability, get_property_details, process_conversation

load_dotenv()

o = OpenAI(api_key=os.getenv("OPENAI_SUPPORT_API_KEY"))


def airbnb_support_bot(prompt, sender_id):
        
    # Fetch the latest 10 WhatsApp messages from the database
    msg = WhatsAppMessage.objects.filter(wa_id=sender_id).order_by('-timestamp')[:4]
    
    conversations = process_conversation(msg, o)
    print("formatted_messages", type(conversations), conversations)
    
    try:
        # System message designed to handle multilingual inputs and scenario-specific logic
        system_message = {
            "role": "system",
           "content": (
               f"previous conversations: {conversations} "
                "You are a customer support assistant for an Airbnb host,"    # capable of responding in any language based on the user's input. "
                "Assist customers with inquiries about property features, amenities (e.g., Wi-Fi), booking processes, pricing, and check-in/check-out times. "
                "Key responsibilities: "
                "- For availability inquiries, call the 'check_booking_availability' tool with property_id (or property_name) and check-in/check-out dates in YYYY-MM-DD format. "
                "- For property feature or amenity questions (e.g., Wi-Fi, bedrooms), call the 'get_property_details' tool with property_id if provided, or without for all properties. "
                # "- Provide pricing and negotiate within reasonable limits (e.g., reduce price slightly if requested, like from 65 to 55 OMR). "
                "- Share property details, such as Wi-Fi passwords (e.g., 12456789), building access codes (e.g., #2024#), or media links (e.g., Instagram: https://www.instagram.com/sialia.chalet). "
                "- Adjust check-in/check-out times if feasible (e.g., allow 10 AM check-in instead of 1 PM if no conflicting bookings, after checking availability). "
                "- For booking confirmation, request a bank transfer to the number 96967808 and allow partial payments (e.g., 20 OMR deposit). "
                "- Handle special requests, such as date changes or cancellations, with flexibility (e.g., allow date changes with prior notice). "
                "- For unrelated queries, politely redirect to property or booking topics. "
                "- Respond in a friendly, professional tone, using slight colloquialisms (e.g., 'OK', 'طيب', or 'تمام') to match the conversational style. "
                "- If the user repeats requests (e.g., availability for the same dates), confirm or clarify consistently using conversation history. "
                "- if user loss the track of convsersation, and anyting like hello, hi, respond with a friendly greeting and take him to actual conversation. "
                "- Provide location details (e.g., Barka, Bousher, or near specific landmarks) when asked, using placeholders if exact details are unavailable. "
                "Keep responses concise, clear, helpful and context-based."
           )
        }

        # Prepare the messages for the OpenAI API
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]


        # Call OpenAI's GPT model
        response = o.chat.completions.create(
            model="gpt-4o",
            tools=tools,
            tool_choice="auto",
            messages=messages
            # temperature=0.7
        )

        # Extract the assistant's reply safely
        
        # Handle the response
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            message = choice.message

            # Check for tool calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute the appropriate tool
                    if function_name == "check_booking_availability":
                        result = check_booking_availability(
                            property_id=arguments.get("property_id"),
                            property_name=arguments.get("property_name"),
                            city_name = arguments.get("city_name"),
                            check_in=arguments.get("check_in"),
                            check_out=arguments.get("check_out")
                        )
                        # print( "Availability check result:", result)
                        return f"Availability check: {result['message']}"
                    elif function_name == "get_property_details":
                        result = get_property_details(
                            property_id=arguments.get("property_id")
                        )
                        return f"Property details: {json.dumps(result, indent=2)}"

            # Return direct text response if no tool call
            print("reply",message.content.strip())
            return message.content.strip() if message.content else "Error: No valid response content."

        # return "Error: No valid response from OpenAI."

    except Exception as e:
        return f"An error occurred: {e}"
    
    
    
    
    
    
    # property_name="The Walk Flat",
    # start_date="2025-04-22",
    # end_date="2025-04-25"

    
    
    
    
    
    
    
    
    
    
    
    
    
#     Scenario 1: Booking for Specific Dates (Standard Booking)
# English Conversation: Guest: Hello, I'd like to book your apartment in Dubai from June 10 to June 15 for 2 people. Is it available, and what's the price?
# Chatbot (English): Hello! I'd be happy to help. Let me check... Yes, the apartment is available from June 10–15. The total for 5 nights is $500 (including all fees). Standard check-in is at 3 PM and checkout at 11 AM. Would you like to confirm this booking?
# Guest: Yes, that sounds great. How can I confirm the booking?
# Chatbot (English): To confirm, I will send you a secure payment link for $500. You can pay with a credit/debit card via Stripe or use PayPal. Do you have a preference?
# Guest: Paying by card is fine.
# Chatbot (English): Alright, I've sent a Stripe payment link here: [link]. Please complete the payment, and I'll confirm your booking immediately.
# Guest: Okay, I just paid.
# Chatbot (English): Thank you! I see the payment has been received. Your booking is now confirmed for June 10–15 🎉. We'll send your confirmation and check-in details shortly. Is there anything else I can help you with?
# Guest: No, that's all. Thank you!
# Chatbot (English): You're very welcome! I'm here if you need anything. Looking forward to hosting you. Have a great day!