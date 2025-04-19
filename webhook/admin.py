from django.contrib import admin
from .models import WhatsAppMessage

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('wa_id', 'sender_name', 'message_type', 'timestamp', 'message_text','reply')
    search_fields = ('wa_id', 'sender_name', 'message_text')
