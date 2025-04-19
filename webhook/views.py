from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from datetime import datetime
from .bot import airbnb_support_bot
import json

from .models import WhatsAppMessage

VERIFY_TOKEN = "zakriya37872"

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ WEBHOOK_VERIFIED")
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse("Forbidden", status=403)

    elif request.method == "POST":
        print("📩 POST REQUEST RECEIVED")

        try:
            body = json.loads(request.body.decode("utf-8"))
            print("📦 Raw Body:\n", json.dumps(body, indent=2))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])

                    print("📞 Contacts:", contacts)
                    print("💬 Messages:", messages)

                    if not messages:
                        continue

                    contact_map = {
                        c.get("wa_id"): c.get("profile", {}).get("name", "Unknown")
                        for c in contacts
                    }

                    for message in messages:
                        sender_id = message.get("from")
                        sender_name = contact_map.get(sender_id, "Unknown")
                        message_type = message.get("type")
                        
                        

                        if message_type == "text":
                            text_body = message.get("text", {}).get("body", "")
                            timestamp = make_aware(datetime.fromtimestamp(int(message.get("timestamp"))))
                            
                            
                            
                            reply =  airbnb_support_bot(text_body)
                           
                            WhatsAppMessage.objects.create(
                                wa_id=sender_id,
                                sender_name=sender_name,
                                message_type=message_type,
                                message_text=text_body,
                                timestamp=timestamp,
                                reply = reply
                            )

                            print(f"🔔 New message from {sender_name} ({sender_id}) - Type: {message_type}")
                            print(f"📝 Full Message: {json.dumps(message, indent=2)}")

            return HttpResponse("EVENT_RECEIVED", status=200)

        return HttpResponse("Not Found", status=404)

    return HttpResponse("Method Not Allowed", status=405)
