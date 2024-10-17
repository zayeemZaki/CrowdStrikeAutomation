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
        print(json.dumps(response.json(), indent=2))
    else:
        print('Failed to retrieve scan details.')
        print(f'Status code: {response.status_code}')
        print(f'Response: {response.text}')

def find_malicious_file_ids(token, filter_query='', offset=0, limit=5, sort=''):
    url = f'https://api.crowdstrike.com/ods/queries/malicious-files/v1?filter={filter_query}&offset={offset}&limit={limit}&sort={sort}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print('Malicious file IDs retrieved successfully.')
        response_data = response.json()
        print(json.dumps(response_data, indent=2))
        return response_data['resources']
    else:
        print('Failed to retrieve malicious file IDs.')
        print(f'Status code: {response.status_code}')
        print(f'Response: {response.text}')
        return None

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
    # Get scan details
    get_scan_details(token, scan_id)

# Find malicious file IDs
filter_query = ''
offset = 0
limit = 5
sort = ''

malicious_file_ids = find_malicious_file_ids(token, filter_query, offset, limit, sort)
if malicious_file_ids:
    print('List of Malicious File IDs:')
    for file_id in malicious_file_ids:
        print(file_id)

    # Get details for malicious file IDs
    get_malicious_file_details(token, malicious_file_ids)
