import requests
from GetToken import getToken
import json

SCRIPT_NAME = 'SimpleIPConfig'

FALCON_BASE_URL = 'https://api.crowdstrike.com'
# PowerShell script content embedded directly in the Python script
SCRIPT_CONTENT = '''
Write-Output "IP Configuration:"
Get-NetIPConfiguration | Format-Table -Property InterfaceAlias, IPv4Address, IPv6Address, DefaultGateway
'''
# Authenticate and get token
token = getToken()
if not token:
    print('Authentication failed')
    exit()

def upload_script(token):
    url = f'{FALCON_BASE_URL}/real-time-response/entities/scripts/v1'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'name': SCRIPT_NAME,
        'permission_type': 'public',  # Options: 'private', 'group', 'public'
        'content': SCRIPT_CONTENT
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Script '{SCRIPT_NAME}' uploaded successfully!")
        return response.json()
    else:
        raise Exception(f'Error uploading script: {response.status_code} - {response.text}')

if __name__ == '__main__':
    try:

        # Upload PowerShell script
        upload_script(token)

    except Exception as e:
        print(f"An error occurred: {e}")



