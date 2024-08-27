import requests
import logging
from GetToken import getToken

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Script details
script_name = 'ipconfig12.ps1'
script_content = "Write-Host 'Hello, CrowdStrike!'"

# API endpoint to upload scripts
upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"

def upload_script(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    files = {
        'name': (None, script_name),
        'permission_type': (None, 'public'),
        'file': (script_name, script_content, 'application/octet-stream')
    }
    
    logging.info(f'Uploading script: {script_name}')
    
    response = requests.post(upload_url, headers=headers, files=files)
    try:
        response.raise_for_status()  # Raises exception for HTTP errors
        logging.info(f"Script '{script_name}' uploaded successfully!")
        logging.debug('Response: %s', response.json())
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise

if __name__ == '__main__':
    # Authenticate and get token
    token = getToken()
    if not token:
        logging.error('Authentication failed')
        exit(1)

    try:
        # Upload PowerShell script
        upload_script(token)
    except Exception as e:
        logging.error(f"An error occurred during script upload: {e}")
