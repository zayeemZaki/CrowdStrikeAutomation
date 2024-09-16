import requests
from GetToken import getToken

IOC_QUERY_URL = "https://api.crowdstrike.com/iocs/queries/indicators/v1"
IOC_DETAIL_URL = "https://api.crowdstrike.com/iocs/entities/indicators/v1"

# Query IOCs
def query_ioc_ids(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(IOC_QUERY_URL, headers=headers)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to query IOCs: {response.text}")

# Get detailed information for each IOC
def get_ioc_details(token, ioc_ids):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {'ids': ','.join(ioc_ids)}
    response = requests.get(IOC_DETAIL_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to get IOC details: {response.text}")

def get_ioc_details_single(token, ioc_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {'ids': ioc_id}
    response = requests.get(IOC_DETAIL_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to get IOC details for {ioc_id}: {response.text}")

def detect_iocs():
    token = getToken()
    ioc_ids = query_ioc_ids(token)
    
    if not ioc_ids:
        print("No IOCs detected.")
        return

    # Debugging step: Print the IOC IDs
    print(f"IOC IDs: {ioc_ids}")
    
    # Fetch details for each IOC ID one by one
    for ioc_id in ioc_ids[:5]:  # Limiting to 5 for testing
        try:
            ioc_details = get_ioc_details_single(token, ioc_id)
            for ioc in ioc_details:
                print(f"IOC ID: {ioc['id']}, Type: {ioc['type']}, Value: {ioc['value']}, Severity: {ioc['severity']}")
        except Exception as e:
            print(f"Error fetching IOC details: {e}")


if __name__ == "__main__":
    detect_iocs()
