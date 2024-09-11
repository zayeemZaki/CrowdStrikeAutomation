import requests
import time
import pandas as pd
from GetToken import getToken

FILE_PATH = 'actor_details.xlsx'
FILE_NAME = 'actor_details.xlsx'

# Upload the file to Falcon Sandbox
def upload_file(access_token, file_path, file_name):
    url = f"https://api.crowdstrike.com/samples/entities/samples/v2?file_name={file_name}&comment=auto-analysis"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream'
    }
    with open(file_path, 'rb') as file:
        response = requests.post(url, headers=headers, data=file)
    response.raise_for_status()
    return response.json()['resources'][0]['sha256']

# Submit the uploaded file for analysis
def submit_for_analysis(access_token, sha256, file_name, environment_id=110):
    url = "https://api.crowdstrike.com/falconx/entities/submissions/v1"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "sandbox": [
            {
                "sha256": sha256,
                "environment_id": environment_id,
                "submit_name": file_name
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['resources'][0]['id']

# Check the progress of the analysis
def check_analysis_status(access_token, submission_id):
    url = f"https://api.crowdstrike.com/falconx/entities/submissions/v1?ids={submission_id}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['resources'][0]

# Download the analysis report
def get_analysis_report(access_token, submission_id):
    url = f"https://api.crowdstrike.com/falconx/entities/reports/v1?ids={submission_id}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['resources'][0]

# Extract IOCs from the analysis report
def extract_iocs_from_report(report):
    iocs = []
    if 'ioc_report_strict_json_artifact_id' in report:
        ioc_report_id = report['ioc_report_strict_json_artifact_id']
        iocs = download_ioc_report(access_token, ioc_report_id)
    return iocs

# Download the IOC report
def download_ioc_report(access_token, ioc_report_id):
    url = f"https://api.crowdstrike.com/falconx/entities/artifacts/v1?id={ioc_report_id}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


access_token = getToken()
sha256 = upload_file(access_token, FILE_PATH, FILE_NAME)
submission_id = submit_for_analysis(access_token, sha256, FILE_NAME)

print(f"File submitted successfully with submission ID: {submission_id}")

# Polling for analysis completion
while True:
    status = check_analysis_status(access_token, submission_id)
    state = status['state']
    if state == 'success':
        print("Analysis completed successfully.")
        break
    elif state == 'error':
        print("Error in analysis.")
        break
    else:
        print(f"Analysis state: {state}. Sleeping for 30 seconds.")
        time.sleep(30)

# Retrieve and handle the analysis report
report = get_analysis_report(access_token, submission_id)
iocs = extract_iocs_from_report(report)
print("Extracted IOCs:", iocs)

# Optionally save IOCs to a file
df_iocs = pd.DataFrame(iocs)
output_filename = "iocs.xlsx"
df_iocs.to_excel(output_filename, index=False)
print(f"IOCs have been saved to {output_filename}")
