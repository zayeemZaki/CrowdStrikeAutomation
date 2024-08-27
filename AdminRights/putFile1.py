import requests
import logging
from GetToken import getToken
from GetDeviceId import getDeviceId

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Script details
script_name = 'ip_configuration.ps1'
script_content = "Write-Host 'Hello, CrowdStrike!'"


# API endpoints
upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"
initiate_session_url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
run_script_url = "https://api.crowdstrike.com/real-time-response/entities/active-responder-command/v1"
list_scripts_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"

def get_script_list(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    logging.info('Retrieving list of uploaded scripts')
    
    response = requests.get(list_scripts_url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise

def check_script_exists(token, script_name):
    scripts = get_script_list(token)
    for script in scripts.get('resources', []):
        if script['name'] == script_name:
            logging.info(f"Script '{script_name}' already exists with ID: {script['id']}")
            return script['id']
    return None

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

def initiate_session(token, host_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'host_ids': [host_id]
    }
    
    logging.info(f'Initiating session on host: {host_id}')
    
    response = requests.post(initiate_session_url, headers=headers, json=payload)
    try:
        response.raise_for_status()  # Raises exception for HTTP errors
        logging.info(f"Session initiated on host '{host_id}' successfully!")
        logging.debug('Response: %s', response.json())
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise

def run_script(token, session_id, script_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'base_command': 'runscript',
        'command_string': f'runscript -CloudFile={script_id}',
        'session_id': session_id
    }
    
    logging.info(f'Running script: {script_name} on session: {session_id}')
    
    response = requests.post(run_script_url, headers=headers, json=payload)
    try:
        response.raise_for_status()  # Raises exception for HTTP errors
        logging.info(f"Script '{script_name}' executed successfully on session '{session_id}'!")
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

    device_id = getDeviceId(token, "FS-39141")
    if not device_id:
        print(f"Device ID not found for hostname: {device_id}")
        exit()

    try:
        # Check if the script already exists
        script_id = check_script_exists(token, script_name)
        if not script_id:
            # Upload PowerShell script if it does not exist
            upload_response = upload_script(token)
            script_id = upload_response['resources'][0]['id']

        # Host ID where you want to run the script
        host_id = device_id

        # Initiate a session on the target host
        session_response = initiate_session(token, host_id)
        session_id = session_response['resources'][0]['session_id']  # Adjust if different

        # Run the uploaded script on the target host
        run_script(token, session_id, script_id)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
