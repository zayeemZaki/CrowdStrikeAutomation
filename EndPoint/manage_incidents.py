# manage_incidents.py
import requests
from GetToken import getToken

def find_incidents(token):
    url = "https://api.crowdstrike.com/incidents/queries/incidents/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_incident_details(token, incident_ids):
    url = "https://api.crowdstrike.com/incidents/entities/incidents/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": incident_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


#main code
token = getToken()

incidents = find_incidents(token)
print("incidents: ", incidents)

for incident in incidents:
    incident_details = get_incident_details(token, incident)
    print(incident_details)
