# manage_detections.py
import requests
from GetToken import getToken

def find_detections(token):
    url = "https://api.crowdstrike.com/detects/queries/detects/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_detection_details(token, detection_ids):
    url = "https://api.crowdstrike.com/detects/entities/summaries/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": detection_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


#main code
token = getToken()

detections = find_detections(token)
print("detections: ", detections)

for detection in detections:
    detections_details = get_detection_details(token, detection)
    print(detections_details)