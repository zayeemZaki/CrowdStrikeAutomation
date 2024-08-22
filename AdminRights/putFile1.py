import requests
from GetToken import getToken

# Script details
script_name = 'ipconfig.ps1'
script_content = """
# PowerShell script content here
Get-ChildItem "C:\\"
"""

# API endpoint to upload scripts
upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"

# Authenticate and get token
token = getToken()
if not token:
    print('Authentication failed')
    exit()

def upload_script(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'name': script_name,
        'permission_type': 'public', 
        'content': script_content,
    }
    
    response = requests.post(upload_url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Script '{script_name}' uploaded successfully!")
        return response.json()
    else:
        raise Exception(f'Error uploading script: {response.status_code} - {response.text}')

if __name__ == '__main__':
    try:
        # Upload PowerShell script
        upload_script(token)
    except Exception as e:
        print(f"An error occurred: {e}")
