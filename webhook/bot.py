from openai import OpenAI
import os
from dotenv import load_dotenv
from webhook.models import WhatsAppMessage

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_SUPPORT_API_KEY"))  # Load your OpenAI API key from environment variables


def load_knowledge_base(txt_path: str) -> str:
    """
    Read a text file (e.g., JSON-lines) and return its full content.
    """
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Knowledge base file not found: {txt_path}")
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()


# Attempt to preload 'output.txt' as default KB
DEFAULT_KB_PATH = 'output.txt'
try:
    DEFAULT_KB_CONTENT = load_knowledge_base(DEFAULT_KB_PATH)
except FileNotFoundError:
    DEFAULT_KB_CONTENT = None



def airbnb_support_bot(prompt):
    """
    A multilingual customer support bot for an Airbnb host, tuned for booking inquiries, pricing negotiations,
    and property-related questions based on provided scenarios. Detects and responds in the user's input language.
    """
    try:
        # System message designed to handle multilingual inputs and scenario-specific logic
        system_message = {
            "role": "system",
            "content": (
                f"Knowledge Base:\n{DEFAULT_KB_CONTENT}"
                "You are a customer support assistant for an Airbnb host, capable of responding in any language based on the user's input. "
                "Assist customers with inquiries about property features, amenities (e.g., Wi-Fi), booking processes, pricing, and check-in/check-out times. "
                "Key responsibilities: "
                "- Confirm availability for requested dates and clarify if unavailable. "
                "- Provide pricing and negotiate within reasonable limits (e.g., reduce price slightly if requested, like from 65 to 55 OMR). "
                "- Share property details, such as Wi-Fi passwords (e.g., 12456789), building access codes (e.g., #2024#), or media links (e.g., Instagram: https://www.instagram.com/sialia.chalet). "
                "- Adjust check-in/check-out times if feasible (e.g., allow 10 AM check-in instead of 1 PM if no conflicting bookings). "
                "- For booking confirmation, request a bank transfer to the number 96967808 and allow partial payments (e.g., 20 OMR deposit). "
                "- Handle special requests, such as date changes or cancellations, with flexibility (e.g., allow date changes with prior notice). "
                "- For unrelated queries, politely redirect to property or booking topics. "
                "- Respond in a friendly, professional tone, using slight colloquialisms (e.g., 'OK', 'طيب', or 'تمام') to match the conversational style. "
                "- Detect the user's language and respond in the same language, maintaining cultural sensitivity. "
                "- If the user repeats requests (e.g., availability for the same dates), confirm or clarify consistently. "
                "- Provide location details (e.g., Barka, Bousher, or near specific landmarks) when asked, using placeholders if exact details are unavailable. "
                "Keep responses concise and focused, ensuring clarity and helpfulness."
            )
        }

        # Prepare the messages for the OpenAI API
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        msg = WhatsAppMessage.objects.order_by('-timestamp')[:10]
        # Format as simple user messages
        formatted_messages = [f"User: {m.message}" for m in msg]

        print(formatted_messages)
        print("msg",msg)

        # Call OpenAI's GPT model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages + formatted_messages,
            temperature=0.7  # Balanced creativity for natural responses
        )

        # Extract and return the assistant's response
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"An error occurred: {e}"
