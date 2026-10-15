import requests
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self):
        self.base_url = os.getenv('API_URL', 'https://homeder.ru/api/v1')
        self.api_key = os.getenv('API_KEY', '')
        self.headers = {'X-API-Key': self.api_key}
    
    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs['headers'] = {**kwargs.get('headers', {}), **self.headers}
        
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
    
    def create_user(self, full_name, tg_id, bio=""):
        return self._request('POST', '/users/', json={
            'full_name': full_name,
            'tg_id': tg_id,
            'bio': bio
        })
    
    def get_user_by_tg(self, tg_id):
        return self._request('GET', f'/users/by-tg/{tg_id}')
    
    def create_property(self, owner_id, price, title, description, city=""):
        return self._request('POST', '/properties/', json={
            'owner_id': owner_id,
            'price': price,
            'title': title,
            'description': description,
            'city': city
        })
    
    def add_to_favorites(self, user_id, prop_id):
        return self._request('POST', '/favorites/', json={
            'user_id': user_id,
            'prop_id': prop_id
        })
    
    def get_favorites(self, user_id):
        return self._request('GET', f'/favorites/user/{user_id}')
    
    def health_check(self):
        return self._request('GET', '/health')

api = APIClient()
