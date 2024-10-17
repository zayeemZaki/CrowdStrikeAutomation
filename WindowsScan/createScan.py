from falconpy import APIHarnessV2
import os
import yaml
import sys
    
# Function to load configuration
def load_config(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: Configuration file '{file_path}' not found.")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except yaml.YAMLError as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)


config = load_config('config.yaml')
hosts = [""]  
file_paths = [""]


falcon = APIHarnessV2(
                    client_id=config['client_id'],
                    client_secret=config['client_secret']
                    )

BODY = {
  "cloud_ml_level_detection": 2,
  "cloud_ml_level_prevention": 2,
  "cpu_priority": 1,
  "description": "string",
  "endpoint_notification": True,
  "file_paths": [
    file_paths
  ],
  "hosts": [
    hosts
  ],
  "initiated_from": "falcon_adhoc",
  "max_duration": 2,
  "max_file_size": 4,
  "pause_duration": 2,
  "quarantine": True,
  "sensor_ml_level_detection": 2,
  "sensor_ml_level_prevention": 2
}

response = falcon.command("create_scan", body=BODY)

print(response)
