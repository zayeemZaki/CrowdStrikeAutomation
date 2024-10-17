import time
import requests
import json
from GetToken import getToken

def start_scan(token, hosts, host_groups, file_paths):
    url = 'https://api.crowdstrike.com/ods/entities/scans/v1'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'hosts': hosts,
        'host_groups': host_groups,
        'file_paths': file_paths,
        'scan_exclusions': [],
        'initiated_from': 'falcon_adhoc',
        'cpu_priority': 1,
        'description': 'API Scan Initiated',
        'quarantine': True,
        'endpoint_notification': True,
        'pause_duration': 2,
        'sensor_ml_level_detection': 2,
        'sensor_ml_level_prevention': 2,
        'cloud_ml_level_detection': 2,
        'cloud_ml_level_prevention': 2,
        'max_duration': 2
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print('Scan started successfully.')
        response_data = response.json()
        print(json.dumps(response_data, indent=2))
        return response_data['resources'][0]['id'] 
    else:
        print('Failed to start scan.')
        print(f'Status code: {response.status_code}')
        print(f'Response: {response.text}')
        return None

def get_scan_details(token, scan_id):
    url = f'https://api.crowdstrike.com/ods/entities/scans/v1?ids={scan_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print('Scan details retrieved successfully.')
        scan_details = response.json()
        print(json.dumps(scan_details, indent=2))
        return scan_details['resources'][0]  # Assuming we're interested in the first resource
    else:
        print('Failed to retrieve scan details.')
        print(f'Status code: {response.status_code}')
        print(f'Response: {response.text}')
        return None

def poll_scan_status(token, scan_id):
    while True:
        scan_details = get_scan_details(token, scan_id)
        if scan_details:
            status = scan_details['state']
            print(f'Scan status: {status}')
            if status in ['complete', 'canceled', 'failed']:
                return scan_details
        time.sleep(30)  # Wait for 30 seconds before polling again

def get_malicious_file_ids_from_scan(scan_details):
    if 'malicious_files' in scan_details:
        malicious_files = scan_details['malicious_files']
        malicious_file_ids = [file['id'] for file in malicious_files]
        print('Malicious File IDs from the Scan:')
        print(malicious_file_ids)
        return malicious_file_ids
    else:
        print('No malicious files found in the scan.')
        return []

def get_malicious_file_details(token, file_ids):
    base_url = 'https://api.crowdstrike.com/ods/entities/malicious-files/v1'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'ids': ','.join(file_ids)
    }
    
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        print('Malicious file details retrieved successfully.')
        print(json.dumps(response.json(), indent=2))
    else:
        print('Failed to retrieve malicious file details.')
        print(f'Status code: {response.status_code}')
        print(f'Response: {response.text}')

# Obtain the token
token = getToken()

# Define scan parameters
hosts = []
host_groups = []  
file_paths = ['C:\\Windows']

# Start the scan
scan_id = start_scan(token, hosts, host_groups, file_paths)
if scan_id:
    # Poll scan status until completion
    scan_details = poll_scan_status(token, scan_id)
    if scan_details:
        # Get malicious file IDs from the completed scan
        malicious_file_ids = get_malicious_file_ids_from_scan(scan_details)
        if malicious_file_ids:
            # Get details for the malicious file IDs
            get_malicious_file_details(token, malicious_file_ids)
