import requests
import json

r = requests.post(
    'http://127.0.0.1:8000/query',
    json={'query': 'What is the weather in London and convert 18 celsius to fahrenheit?'}
)
print(json.dumps(r.json(), indent=2))