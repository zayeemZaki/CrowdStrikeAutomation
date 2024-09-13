# manage_incidents.py
import requests
import pandas as pd
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

# main code
token = getToken()

# Get the list of incident IDs
incidents_response = find_incidents(token)

if 'resources' in incidents_response:
    incident_ids = incidents_response['resources']
    
    # Now, get the details for those incidents
    if incident_ids:
        incident_details_response = get_incident_details(token, incident_ids)
        
        if 'resources' in incident_details_response:
            incidents_data = incident_details_response['resources']
            
            # Convert list of incidents to DataFrame
            df = pd.DataFrame(incidents_data)
            
            # Output the DataFrame to a CSV file
            df.to_csv('incidents.csv', index=False)
            
            print("Incident details have been written to incidents.csv")
        else:
            print("Error retrieving incident details:", incident_details_response.get('errors'))
    else:
        print("No incidents found.")
else:
    print("Error retrieving incidents:", incidents_response.get('errors'))
