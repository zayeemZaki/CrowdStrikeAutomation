import requests
import pandas as pd
from GetToken import getToken

def find_detections(token):
    url = "https://api.crowdstrike.com/detects/queries/detects/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
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
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

# main code
token = getToken()

# Get the list of detection IDs
detections_response = find_detections(token)

if 'resources' in detections_response:
    detection_ids = detections_response['resources']
    
    # Now, get the details for these detections
    try:
        if detection_ids:
            detection_details_response = get_detection_details(token, detection_ids)
            
            if 'resources' in detection_details_response:
                detections_data = detection_details_response['resources']
                
                # Convert list of detections to DataFrame
                df = pd.DataFrame(detections_data)
                
                # Output the DataFrame to a CSV file
                df.to_csv('detections.csv', index=False)
                
                print("Detection details have been written to detections.csv")
            else:
                print("Error retrieving detection details:", detection_details_response.get('errors'))
        else:
            print("No detections found.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

else:
    print("Error retrieving detections:", detections_response.get('errors'))
