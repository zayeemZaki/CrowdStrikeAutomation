# manage_alerts.py
import requests
from GetToken import getToken

def find_alerts(token):
    url = "https://api.crowdstrike.com/alerts/queries/alerts/v2"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_alert_details(token, alert_ids):
    url = "https://api.crowdstrike.com/alerts/entities/alerts/v2"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "composite_ids": alert_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()



#main code
token = getToken()

alerts = find_alerts(token)
print("Alerts: ", alerts)

for alert in alerts:
    alert_details = get_alert_details(token, alert)
    print(alert_details)