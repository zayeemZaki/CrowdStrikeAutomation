import requests
import pandas as pd
from GetToken import getToken

def find_alerts(token):
    url = "https://api.crowdstrike.com/alerts/queries/alerts/v2"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
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
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()


# main code
token = getToken()

# Get the list of alert IDs
alerts_response = find_alerts(token)

if 'resources' in alerts_response:
    alert_ids = alerts_response['resources']
    
    # Now, get the details for these alerts
    try:
        if alert_ids:
            alert_details_response = get_alert_details(token, alert_ids)
            
            if 'resources' in alert_details_response:
                alerts_data = alert_details_response['resources']
                
                # Convert list of alert details to DataFrame
                df = pd.DataFrame(alerts_data)
                
                # Output the DataFrame to a CSV file
                df.to_csv('alerts.csv', index=False)
                
                print("Alert details have been written to alerts.csv")
            else:
                print("Error retrieving alert details:", alert_details_response.get('errors'))
        else:
            print("No alerts found.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

else:
    print("Error retrieving alerts:", alerts_response.get('errors'))
