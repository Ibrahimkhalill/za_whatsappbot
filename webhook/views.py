from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from datetime import datetime
from .bot import airbnb_support_bot
import json
from dotenv import load_dotenv
load_dotenv()
from .models import WhatsAppMessage

VERIFY_TOKEN = "zakriya37872"
import os
import requests
from django.conf import settings

# settings.py এ রাখবেন:

def send_whatsapp_message(to_number: str, text: str) -> dict:
    """
    to_number: 'OM1234567890' or '+971501234567'
    """
    phone_id = os.getenv('WHATSAPP_PHONE_ID')
    token    = os.getenv('WHATSAPP_TOKEN')
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":    "application/json"
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


@csrf_exempt
def whatsapp_webhook(request):
    # … your GET handler …

    if request.method == "POST":
        body = json.loads(request.body.decode())
        if body.get("object") != "whatsapp_business_account":
            return HttpResponse("Not Found", status=404)

        # Grab the very first message in the payload (if any)
        entry   = body.get("entry", [])[0]
        change  = entry.get("changes", [])[0]
        value   = change.get("value", {})
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        if not messages:
            return HttpResponse("EVENT_RECEIVED", status=200)

        # Map wa_id to name once
        contact_map = {
            c["wa_id"]: c.get("profile", {}).get("name", "Unknown")
            for c in contacts
        }
        print("messages",messages)

        # Only handle the first message
        msg = messages[0]
        if msg.get("type") == "text":
            sender_id   = msg["from"]
            sender_name = contact_map.get(sender_id, "Unknown")
            text_body   = msg["text"]["body"]
            timestamp   = make_aware(
                datetime.fromtimestamp(int(msg["timestamp"]))
            )
            reply = airbnb_support_bot(text_body, sender_id)

            WhatsAppMessage.objects.create(
                wa_id        = sender_id,
                sender_name  = sender_name,
                message_type = "text",
                message_text = text_body,
                timestamp    = timestamp,
                reply        = reply
            )

            try:
                result = send_whatsapp_message(sender_id, reply)
                return JsonResponse(result, status=201)
            except Exception as e:
                return JsonResponse({"detail": str(e)}, status=400)

        return HttpResponse("EVENT_RECEIVED", status=200)
    return HttpResponse("Method Not Allowed", status=405)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .client import HospitableClient



from datetime import date

@api_view(['GET'])
def hospitable_properties_reservations(request):
    client = HospitableClient()
    
    try:
        # প্রথমে সব প্রপার্টি fetch করুন
        properties_data = client.get_listings().get("data", [])
        
        # print(properties_data)
        property_ids = [prop["id"] for prop in properties_data]

        if not property_ids:
            return Response({"detail": "No properties found."}, status=status.HTTP_404_NOT_FOUND)

        # reservation fetch করুন URL params দিয়ে
        today = date.today()
        start_date = today.replace(day=1).isoformat()
        end_date = today.isoformat()




        # do some filtering
        reservations_data = client.get_reservations_by_properties(
            property_ids=property_ids,
          
        )
        # print(reservations_data)

        return Response({
            "properties": properties_data,
            "reservations": reservations_data.get("data", [])
        })

    except Exception as exc:
        return Response(
            {"detail": f"Failed: {exc}"},
            status=status.HTTP_502_BAD_GATEWAY
        )



