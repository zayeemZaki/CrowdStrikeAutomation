import requests
from GetToken import getToken

script_name = 'ipconfig.ps1'
script_content = """
# PowerShell script content here
Get-ChildItem "C:\\"
"""

upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"

token = getToken()
if not token:
    print('Authentication failed')
    exit()

def upload_script(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    files = {
        'file': (script_name, script_content, 'application/octet-stream')
    }
    
    payload = {
        'name': script_name,
        'permission_type': 'public',
    }

    response = requests.post(upload_url, headers=headers, files=files, data=payload)
    if response.status_code == 201:
        print(f"Script '{script_name}' uploaded successfully!")
        return response.json()
    else:
        raise Exception(f'Error uploading script: {response.status_code} - {response.text}')

if __name__ == '__main__':
    try:
        upload_script(token)
    except Exception as e:
        print(f"An error occurred: {e}")
