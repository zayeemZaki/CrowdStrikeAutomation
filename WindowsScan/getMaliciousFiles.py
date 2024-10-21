import os
import yaml
import sys
import logging
from falconpy import APIHarnessV2
from GetDeviceId import getDeviceId
from GetToken import getToken

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(file_path):
    """ Load configuration from a yaml file """
    if not os.path.isfile(file_path):
        logging.error(f"Error: Configuration file '{file_path}' not found.")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logging.error(f"Error reading configuration file: {e}")
        sys.exit(1)

def query_malicious_files(falcon, host_id):
    """ Query malicious files for a specified host """
    try:
        filters = f"host_id:'{host_id}'"
        response = falcon.command("query_malicious_files", filter=filters)
        
        if response['status_code'] == 200 and 'resources' in response['body']:
            ids = response['body']['resources']
            if ids:
                logging.info(f"Malicious file IDs for host {host_id}:")
                for file_id in ids:
                    print(file_id)
            else:
                logging.info(f"No malicious files found for host {host_id}.")
        else:
            logging.error(f"Unexpected response or no resources found: {response}")

        return response['body']['resources'] if 'resources' in response['body'] else []
    except Exception as e:
        logging.error(f"Error executing command: {e}")
        sys.exit(1)

def get_file_details(falcon, file_id):
    """ Get details about a specific file ID """
    try:
        response = falcon.command("get_malicious_files_by_ids", ids=file_id)
        if response['status_code'] == 200 and 'resources' in response['body']:
            file_details = response['body']['resources'][0]
            print(f"Details of file ID {file_id}:")
            print(f"  Filepath: {file_details['filepath']}")
            print(f"  Filename: {file_details['filename']}")
            print(f"  Hash: {file_details['hash']}")
            print(f"  Severity: {file_details['severity']}")
            print(f"  Quarantined: {file_details['quarantined']}")
            print(f"  Last Updated: {file_details['last_updated']}")
        else:
            logging.error(f"Unexpected response or no resources found: {response}")
    except Exception as e:
        logging.error(f"Error retrieving file details: {e}")
        sys.exit(1)

def main():
    config = load_config('config.yaml')
    token = getToken()

    falcon = APIHarnessV2(
        client_id=config['client_id'],
        client_secret=config['client_secret']
    )

    hosts = [""]
    device_ids = ['b9e1afd1cd38473b8d35ffa992ba5aa0'] # added default id for testing

    for host in hosts:
        device_ids.append(getDeviceId(token, host))

    print(device_ids)
    all_ids = []
    for device in device_ids:
        ids = query_malicious_files(falcon, device)
        all_ids.extend(ids)
    
    if all_ids:
        selected_id = input("Please enter the ID you want to get details about: ")
        if selected_id in all_ids:
            get_file_details(falcon, selected_id)
        else:
            logging.error(f"The ID {selected_id} is not found in the list of malicious file IDs.")
    else:
        logging.info("No malicious file IDs found for the specified hosts.")

if __name__ == "__main__":
    main()
