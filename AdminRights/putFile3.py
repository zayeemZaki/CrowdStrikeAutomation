#Edit script with normal url, getting scripts using different url

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
query_scripts_url = "https://api.crowdstrike.com/real-time-response/queries/scripts/v1"
upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"
run_script_url = "https://api.crowdstrike.com/real-time-response/entities/active-responder-command/v1"

def get_script_ids(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(query_scripts_url, headers=headers)
    response.raise_for_status()
    return response.json().get('resources', [])

def get_script_details(token, script_ids):
    if not script_ids:
        return []

    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {
        'ids': script_ids
    }
    response = requests.get(upload_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('resources', [])

def check_script_exists(token, script_name):
    script_ids = get_script_ids(token)
    scripts = get_script_details(token, script_ids)
    for script in scripts:
        if script['name'] == script_name:
            logging.info(f"Script '{script_name}' already exists with ID: {script['id']}")
            return script['id']
    return None

def upload_script(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'name': script_name,
        'permission_type': 'public',
        'content': script_content
    }

    logging.info(f'Uploading script: {script_name}')

    response = requests.post(upload_url, headers=headers, json=payload)
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

def edit_script(token, script_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'id': script_id,
        'name': script_name,
        'permission_type': 'public',
        'content': script_content
    }

    logging.info(f'Updating script: {script_name}')

    response = requests.patch(upload_url, headers=headers, json=payload)
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

def delete_script(token, script_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    url = f"{upload_url}/{script_id}"

    logging.info(f'Deleting script with ID: {script_id}')

    response = requests.delete(url, headers=headers)
    try:
        response.raise_for_status()  # Raises exception for HTTP errors
        logging.info(f"Script '{script_id}' deleted successfully!")
        return response.json()
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
        if script_id:
            delete_script(token, script_id)

        upload_script(token)

        session_id = initiateRtrSession(token, device_id)
        if not session_id:
            print(f'Failed to initiate RTR session for device ID: {device_id}')
            exit()

        run_script(token, session_id)

    except Exception as e:
        logging.error(f"An error occurred: {e}")