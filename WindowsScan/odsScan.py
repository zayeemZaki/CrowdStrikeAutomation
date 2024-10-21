from falconpy import ODS
from GetToken import getToken
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
token = getToken()

falcon = ODS(client_id=config['client_id'],
        client_secret=config['client_secret'])

scan_payload = {
    "host_ids": [""],
    "filter": "string",
    "date_ranges": [
        {
            "from": "2024-01-01T00:00:00Z",
            "to": "2024-01-02T00:00:00Z"
        }
    ]
}

response = falcon.create_scan(body=scan_payload)
print(response)
