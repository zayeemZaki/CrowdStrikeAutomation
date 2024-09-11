# manage_behaviors.py
import requests
from GetToken import getToken

def find_behaviors(token):
    url = "https://api.crowdstrike.com/incidents/queries/behaviors/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_behavior_details(token, behavior_ids):
    url = "https://api.crowdstrike.com/incidents/entities/behaviors/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": behavior_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


#main code
token = getToken()

behaviors = find_behaviors(token)
print("Behaviors: ", behaviors)

for behavior in behaviors:
    behavior_details = get_behavior_details(token, behavior)
    print(behavior_details)