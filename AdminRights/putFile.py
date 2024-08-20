import os
import requests
import json
import time
from LoadConfig import load_config
from GetToken import getToken
from GetRtrSessionId import initiateRtrSession
from GetDeviceId import getDeviceId

# Load configuration
config = load_config('config.yaml')
rtr_url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
command_url = "https://api.crowdstrike.com/real-time-response/entities/put-files/v1"

# Authenticate and get token
token = getToken()
if not token:
    print('Authentication failed')
    exit()

# Get device ID from hostname
hostname = input("Please input target hostname: ")
device_id = getDeviceId(token, hostname)
if not device_id:
    print(f"Device ID not found for hostname: {hostname}")
    exit()

session_id = initiateRtrSession(token, device_id)
if not session_id:
    print(f'Failed to initiate RTR session for device ID: {device_id}')
    exit()

local_file_path = "hello.txt"
remote_file_path = "C:\\Documents\\file.txt"

def upload_file(token, session_id, local_file_path, remote_file_path):
    url = f"{command_url}"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    files = {
        'file': open(local_file_path, 'rb')
    }
    data = {
        'file_name': os.path.basename(local_file_path),
        'description': 'Uploaded from automation script'
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code in range(200, 300):
        print("File uploaded successfully")
    else:
        raise Exception("Failed to upload file: " + response.text)

def close_rtr_session(token, session_id):
    url = f"{rtr_url}/{session_id}"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code in range(200, 300):
        print("RTR session closed")
    else:
        raise Exception("Failed to close RTR session: " + response.text)

def main():
    try:
        upload_file(token, session_id, local_file_path, remote_file_path)
        time.sleep(5)
        close_rtr_session(token, session_id)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
