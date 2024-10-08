#Edit Script with octet-stream
import time
import requests
import logging
from GetToken import getToken
from GetDeviceId import getDeviceId
from GetRtrSessionId import initiateRtrSession

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

username = input("Please enter target device username: ")

# Script details
script_name = 'removeAdminRights.ps1'
script_content = f"Remove-LocalGroupMember -Group 'Administrators' -Member '{username}'"

# API endpoints
upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"
initiate_session_url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
run_script_url = "https://api.crowdstrike.com/real-time-response/entities/active-responder-command/v1"
list_scripts_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"

def get_script_list(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }    
    response = requests.get(list_scripts_url, headers=headers)
    try:
        response.raise_for_status()
        response_json = response.json()
        return response_json
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
        logging.info('Response: %s', response.json())
        print("Upload Script Response:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise


def run_script(token, session_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'base_command': 'runscript',
        'command_string': f'runscript -CloudFile={script_name}',
        'session_id': session_id
    }
    
    logging.info(f'Running script: {script_name} on session: {session_id}')
    
    response = requests.post(run_script_url, headers=headers, json=payload)
    try:
        response.raise_for_status()  # Raises exception for HTTP errors
        logging.info(f"Script '{script_name}' executed successfully on session '{session_id}'!")
        logging.info('Response: %s', response.json())
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise

def edit_script(token, script_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    files = {
        'id': (None, script_id),
        'name': (None, script_name),
        'permission_type': (None, 'public'),
        'file': (script_name, script_content, 'application/octet-stream')
    }
    
    logging.info(f'Updating script: {script_name}')
    
    response = requests.patch(upload_url, headers=headers, files=files)
    try:
        response.raise_for_status()  # Raises exception for HTTP errors
        logging.info(f"Script '{script_name}' updated successfully!")
        logging.info('Response: %s', response.json())
        print("Update Script Response:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise


def is_device_online(token, device_id):
    url = "https://api.crowdstrike.com/devices/entities/online-state/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': device_id
    }
    
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        data = response.json()
        if data['resources']:
            state = data['resources'][0].get('state')
            logging.info(f"Device {device_id} is currently {state}")
            return state == 'online'
        else:
            logging.error(f"Failed to get online state for device {device_id}")
            return False
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP Error: {e} - {response.text}')
        raise
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise


if __name__ == '__main__':
    token = getToken()
    if not token:
        logging.error('Authentication failed')
        exit(1)

    hostname = input("Please input target hostname: ")
    device_id = getDeviceId(token, hostname)
    if not device_id:
        print(f'Failed to retrieve device ID for hostname: {hostname}')
        exit()

    try:
        script_id = check_script_exists(token, script_name)
        if not script_id:
            upload_script(token)
        else:
            edit_script(token, script_id)

        while True:
            status = is_device_online(token, device_id)
            if status:
                session_id = initiateRtrSession(token, device_id)
                if not session_id:
                    print(f'Failed to initiate RTR session for device ID: {device_id}')
                    exit()
                run_script(token, session_id)
                break 
            else:
                user_input = input("Do you want to keep retrying? (Type: \"Y\" for yes and \"N\" for no)")
                if user_input == "Y":
                    logging.info("Device is offline. Waiting before retrying...")
                    time.sleep(60)
                else:
                    break

    except Exception as e:
        logging.error(f"An error occurred: {e}")
