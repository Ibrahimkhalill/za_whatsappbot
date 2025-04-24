
from django.urls import path
from .views import *
urlpatterns = [
   path("webhook/", whatsapp_webhook),
  
   path("hospitable/get_all_reservation/",hospitable_properties_reservations, name="get_all_reservations"),
]
