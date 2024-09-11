import requests
import pandas as pd
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

def get_actor_details(access_token, actor_id):
    url = 'https://api.crowdstrike.com/intel/entities/actors/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': actor_id
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('resources', [])

token = getToken()
# filter_criteria = "target_countries:'china' AND motivation:'financial' AND last_activity_date:>'2022-01-01'"
filter_criteria = "last_activity_date:>'2024-01-01'"

actor_ids = query_actors(token, filter_criteria)
print(f"Found {len(actor_ids)} actors.")

actor_details_list = []
if actor_ids:
    for actor_id in actor_ids:
        details = get_actor_details(token, actor_id)
        if details:
            actor_details_list.extend(details)

    df = pd.DataFrame(actor_details_list)
    print("Actor Details DataFrame:")
    print(df)

    output_filename = "actor_details.xlsx"
    df.to_excel(output_filename, index=False)
    print(f"Actor details have been saved to {output_filename}")
else:
    print("No actors found.")
