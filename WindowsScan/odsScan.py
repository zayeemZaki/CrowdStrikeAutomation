import os
import sys
import time
import requests
import yaml
from falconpy import ODS
from GetDeviceId import getDeviceId
from GetToken import getToken
from collections import deque

def load_config(file_path):
    """Load configuration from a YAML file."""
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} does not exist.")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

def is_device_online(token, device_id):
    url = "https://api.crowdstrike.com/devices/entities/online-state/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': device_id
    }
    
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        data = response.json()
        if data['resources']:
            state = data['resources'][0].get('state')
            return state == 'online'
        else:
            return False
    except requests.exceptions.HTTPError as e:
        raise Exception("HTTPError: " + str(e))
    except Exception as e:
        raise Exception("Error: " + str(e))

def main():
    config = load_config('config.yaml')
    token = getToken()
    falcon = ODS(client_id=config['client_id'], client_secret=config['client_secret'])

    hosts = [""]  # Replace with host IDs
    host_ids = [getDeviceId(token, host) for host in hosts if host]

    if not host_ids:
        print("No valid host IDs found.")
        sys.exit(1)

    # Use a deque to manage the hosts queue
    hosts_queue = deque(host_ids)

    while hosts_queue:
        current_host_id = hosts_queue.popleft()
        print(f"Checking if device {current_host_id} is online...")
        if is_device_online(token, current_host_id):
            print(f"Device {current_host_id} is online. Proceeding with scan creation.")
            
            BODY = {
                "cloud_ml_level_detection": 2,
                "cloud_ml_level_prevention": 2,
                "cpu_priority": 2,
                "description": "On Demand Scan Description",
                "endpoint_notification": True,
                "file_paths": ["C:\\Windows"],
                "hosts": [current_host_id],
                "initiated_from": "manual",
                "max_duration": 2,
                "max_file_size": 60,
                "pause_duration": 2,
                "quarantine": True,
                "sensor_ml_level_detection": 2,
                "sensor_ml_level_prevention": 2
            }

            try:
                response = falcon.create_scan(body=BODY)

                if response.get('status_code') in [200, 201]:
                    print("Scan created successfully.")
                    scan_info = response.get('body', {}).get('resources', [])[0]
                    print(f"Scan ID: {scan_info.get('id')}")
                    print(f"Status: {scan_info.get('status')}")
                    print(f"Created On: {scan_info.get('created_on')}")
                else:
                    print("Error creating scan:")
                    print(f"Status Code: {response.get('status_code')}")
                    print(f"Error Message: {response.get('body', {}).get('errors')}")
            except Exception as e:
                print(f"Exception while creating scan: {e}")
                sys.exit(1)
            
        else:
            print(f"Device {current_host_id} is offline. Moving to the end of the queue and retrying in 60 seconds...")
            hosts_queue.append(current_host_id)
            time.sleep(60)  # Delay before retrying

if __name__ == "__main__":
    main()
