import requests
from GetToken import getToken

def query_reports(access_token, filter_criteria):
    url = 'https://api.crowdstrike.com/intel/queries/reports/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filter': filter_criteria,
        'limit': 10  
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('resources', [])

def get_report_details(access_token, report_ids):
    url = 'https://api.crowdstrike.com/intel/entities/reports/v1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': report_ids
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('resources', [])

token = getToken()
filter_criteria = "target_countries:'united states'"
report_ids = query_reports(token, filter_criteria)
print(f"Found {len(report_ids)} reports.")
    
if report_ids:
    report_details = get_report_details(token, ','.join(report_ids))
    print("Report Details:", report_details)
else:
    print("No reports found.")

