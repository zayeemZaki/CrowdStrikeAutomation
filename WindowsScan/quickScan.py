import requests
from GetToken import getToken
from falconpy import QuickScan
import sys
import yaml
import os

def load_config(file_path):
    """ Load configuration from a yaml file """
    if not os.path.isfile(file_path):
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        sys.exit(1)

config = load_config('config.yaml')
def find_detections(token):
    """ Get the list of detection IDs from the API """
    url = "https://api.crowdstrike.com/detects/queries/detects/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def get_detection_details(token, detection_ids):
    """ Get details of detections by their IDs """
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

def list_detections(detections):
    """ Display detections and ask user to select one """
    if not detections:
        print("No detections found.")
        return None

    print("\nAvailable Detections:")
    for idx, detection in enumerate(detections, 1):
        # Check available fields in each detection
        sha256 = detection.get('sha256', 'N/A')
        filename = detection.get('filename', 'N/A')
        print(f"{idx}. SHA256: {sha256}, Filename: {filename}")

    selected_index = int(input("\nEnter the number of the detection you want to scan: ")) - 1

    if 0 <= selected_index < len(detections):
        selected_hash = detections[selected_index].get('sha256')
        if selected_hash and selected_hash != 'N/A':
            return selected_hash
        else:
            print("Selected detection does not have a valid SHA256 hash.")
            return None
    else:
        print("Invalid selection.")
        return None

def quick_scan(token, selected_hash):
    """ Perform a Quick Scan on the selected hash """
    quickscan_falcon = QuickScan(client_id=config['client_id'], client_secret=config['client_secret'])

    # Prepare Quick Scan payload
    quick_scan_payload = {
        "samples": [selected_hash]
    }

    # Perform Quick Scan
    response = quickscan_falcon.scan_samples(body=quick_scan_payload)
    return response

# Main code
token = getToken()

# Get the list of detection IDs
detections_response = find_detections(token)

if 'resources' in detections_response:
    detection_ids = detections_response['resources']
    
    # Get the details for these detections
    if detection_ids:
        try:
            detection_details_response = get_detection_details(token, detection_ids)
            
            if 'resources' in detection_details_response:
                detections_data = detection_details_response['resources']

                # Debug: Print available fields for each detection
                for detection in detections_data:
                    print("\nDetection Details:", detection)

                # List detections and ask user to select one
                selected_hash = list_detections(detections_data)

                if selected_hash:
                    # Perform Quick Scan on the selected hash
                    scan_response = quick_scan(token, selected_hash)
                    print("\nQuick Scan Response:")
                    print(scan_response)
                else:
                    print("No valid selection made.")
            else:
                print("Error retrieving detection details:", detection_details_response.get('errors'))
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
    else:
        print("No detections found.")
else:
    print("Error retrieving detections:", detections_response.get('errors'))
