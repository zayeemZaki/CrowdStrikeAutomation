import os
import sys
import yaml
from falconpy import ODS
from GetToken import getToken

def load_config(file_path):
    """ Load configuration from a yaml file """
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
    token = getToken()

    falcon = ODS(client_id=config['client_id'], client_secret=config['client_secret'])

    scan_payload = {
        "cloud_ml_level_detection": 0,
        "cloud_ml_level_prevention": 0,
        "cpu_priority": 0,
        "description": "On Demand Scan Description",
        "endpoint_notification": True,
        "file_paths": ["C://"],
        "hosts": ["host_id"],
        "initiated_from": "manual",
        "max_duration": 0,
        "max_file_size": 0,
        "pause_duration": 0,
        "quarantine": True,
        "sensor_ml_level_detection": 0,
        "sensor_ml_level_prevention": 0
    }

    try:
        response = falcon.create_scan(body=scan_payload)
        print("Scan response:", response)
    except Exception as e:
        print(f"Error creating scan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
