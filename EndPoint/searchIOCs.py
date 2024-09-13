import requests
from GetToken import getToken

CROWDSTRIKE_IOC_SEARCH_URL = 'https://api.crowdstrike.com/indicators/queries/iocs/v1'

token = getToken()

def search_iocs():
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    search_params = {
        'types': 'hash_sha256',
        'values': ['<SHA256_HASH>'] 
    }
    response = requests.get(CROWDSTRIKE_IOC_SEARCH_URL, headers=headers, params=search_params)
    response.raise_for_status()
    return response.json()

ioc_results = search_iocs()
if 'resources' in ioc_results:
    print("IOC Search Results:")
    for ioc_id in ioc_results['resources']:
        print(f'IOC ID: {ioc_id}')
else:
    print("No IOCs found.")
