import requests
from GetToken import getToken



def search_iocs(access_token, filter_criteria):
    url = 'https://api.crowdstrike.com/intel/queries/iocs/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filter': filter_criteria  # FQL filter
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['resources']

def get_ioc_details(access_token, ioc_ids):
    url = 'https://api.crowdstrike.com/intel/entities/iocs/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': ioc_ids
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['resources']

def main():
    
    token = getToken()

    filter_criteria = "indicator_type:'md5'"
    
    iocs = search_iocs(token, filter_criteria)
    print(f"Found {len(iocs)} IOCs.")
    
    if iocs:
        ioc_ids = ','.join(iocs)
        ioc_details = get_ioc_details(token, ioc_ids)
        print("IOC Details:", ioc_details)
    else:
        print("No IOCs found.")

if __name__ == '__main__':
    main()
