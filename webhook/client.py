import requests
import os
from dotenv import load_dotenv
load_dotenv()

class HospitableClient:
    def __init__(self):
        self.api_key = os.getenv("HOSPITABLE_API_KEY")
        self.base_url = os.getenv("HOSPITABLE_API_BASE")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        })

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_listings(self) -> dict:
        resp = self.session.get(self._url("/properties"))
        resp.raise_for_status()
        return resp.json()

    def get_reservations_by_properties(self, property_ids: list, check_in: str = None, check_out: str = None):
        url = self._url("/reservations")

        # Params তৈরি করুন
        params = []
        for prop_id in property_ids:
            params.append(('properties[]', prop_id))
            
        if check_in:
            params.append(('start_date', check_in))
        if check_out:
            params.append(('end_date', check_out))
            
        print("params",params)
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_property_by_name(self, name: str):
        # Get all properties
        resp = self.session.get(self._url("/properties"))
        resp.raise_for_status()
        
        # Filter properties by name
        properties = resp.json().get("data", [])
        filtered_properties = [prop for prop in properties if name.lower() in prop.get("name", "").lower()]
        
        return {"data": filtered_properties}
    
    
    def get_property_by_city(self, city: str):
        # Get all properties
        resp = self.session.get(self._url("/properties"))
        resp.raise_for_status()
        
        # Filter properties by city
        properties = resp.json().get("data", [])
        filtered_properties = [
            prop for prop in properties if city.lower() in prop.get("address", {}).get("city", "").lower()
        ]
        
        # print("filtered_properties",filtered_properties)
        return {"data": filtered_properties}
    
    
    # ibrahim vai only one property return koren
    def get_property_by_id(self, property_id: str):
        resp = self.session.get(self._url(f"/properties/{property_id}"))
        resp.raise_for_status()
        return resp.json()


