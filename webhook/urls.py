
from django.urls import path
from .views import *
urlpatterns = [
   path("webhook/", whatsapp_webhook)
]
