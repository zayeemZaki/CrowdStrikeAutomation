import os
import sys
import yaml
from falconpy import APIHarnessV2

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

def main():
    config = load_config('config.yaml')

    falcon = APIHarnessV2(client_id=config['client_id'], 
                 client_secret=config['client_secret']
                 )

    BODY = {
        "cloud_ml_level_detection": 2,
        "cloud_ml_level_prevention": 2,
        "cpu_priority": 2,
        "description": "On Demand Scan Description",
        "endpoint_notification": True,
        "file_paths": ["C:\\Windows"],
        "hosts": ["host_id"],
        "initiated_from": "manual",
        "max_duration": 2,
        "max_file_size": 60,
        "pause_duration": 2,
        "quarantine": True,
        "sensor_ml_level_detection": 2,
        "sensor_ml_level_prevention": 2
    }

    try:
        response = falcon.command("create_scan", body=BODY)

        
        if response.get('status_code') == 200 or response.get('status_code') == 201:
            print("Scan created successfully.")
            print("Response:", response)
        else:
            print("Error creating scan:")
            print(f"Status Code: {response.get('status_code')}")
            print(f"Error Message: {response.get('body', {}).get('errors')}")
    except Exception as e:
        print(f"Exception while creating scan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
