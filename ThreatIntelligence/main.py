import requests
from GetToken import getToken

def search_indicators(access_token, filter_criteria):
    url = 'https://api.crowdstrike.com/intel/queries/indicators/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filter': filter_criteria 
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('resources', [])

def get_indicator_details(access_token, indicator_ids):
    url = 'https://api.crowdstrike.com/intel/entities/indicators/GET/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'ids': indicator_ids
    }
    response = requests.post(url, headers=headers, json=data) 
    response.raise_for_status()
    return response.json().get('resources', [])

def main():
    try:
        token = getToken()

        filter_criteria = "(indicator_type:'md5' OR indicator_type:'sha256') AND created_date:>'2022-01-01T00:00:00Z'"
        
        indicators = search_indicators(token, filter_criteria)
        print(f"Found {len(indicators)} indicators.")
        
        if indicators:
            indicator_ids = indicators  
            indicator_details = get_indicator_details(token, indicator_ids)
            print("Indicator Details:", indicator_details)
        else:
            print("No indicators found.")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
