import requests
from GetToken import getToken

def query_actors(access_token, filter_criteria):
    url = 'https://api.crowdstrike.com/intel/queries/actors/v1'
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

def get_actor_details(access_token, actor_ids):
    url = 'https://api.crowdstrike.com/intel/entities/actors/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': actor_ids
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('resources', [])


token = getToken()
filter_criteria = "target_countries:'china'"
actor_ids = query_actors(token, filter_criteria)
print(f"Found {len(actor_ids)} actors.")
    
if actor_ids:
    actor_details = get_actor_details(token, ','.join(actor_ids))
    print("Actor Details:", actor_details)
else:
    print("No actors found.")


#(Snort, Suricata, YARA)