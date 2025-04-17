from django.db import models

class WhatsAppMessage(models.Model):
    wa_id = models.CharField(max_length=20)  # WhatsApp number (sender)
    sender_name = models.CharField(max_length=100, blank=True, null=True)
    message_type = models.CharField(max_length=20)
    message_text = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()

    received_at = models.DateTimeField(auto_now_add=True)  # when saved in DB

    def __str__(self):
        return f"{self.sender_name or 'Unknown'} - {self.message_text[:30]}"
