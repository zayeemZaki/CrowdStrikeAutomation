import requests
import pandas as pd
from GetToken import getToken

def find_behaviors(token):
    url = "https://api.crowdstrike.com/incidents/queries/behaviors/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
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
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()


# main code
token = getToken()

# Get the list of behavior IDs
behaviors_response = find_behaviors(token)

if 'resources' in behaviors_response:
    behavior_ids = behaviors_response['resources']
    
    # Now, get the details for these behaviors
    try:
        if behavior_ids:
            behavior_details_response = get_behavior_details(token, behavior_ids)
            
            if 'resources' in behavior_details_response:
                behaviors_data = behavior_details_response['resources']
                
                # Convert list of behavior details to DataFrame
                df = pd.DataFrame(behaviors_data)
                
                # Output the DataFrame to a CSV file
                df.to_csv('behaviors.csv', index=False)
                
                print("Behavior details have been written to behaviors.csv")
            else:
                print("Error retrieving behavior details:", behavior_details_response.get('errors'))
        else:
            print("No behaviors found.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

else:
    print("Error retrieving behaviors:", behaviors_response.get('errors'))
