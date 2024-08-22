import os
import requests
import time
from LoadConfig import load_config
from GetToken import getToken
from GetRtrSessionId import initiateRtrSession
from GetDeviceId import getDeviceId

# Load configuration
config = load_config('config.yaml')
command_url = "https://api.crowdstrike.com/real-time-response/entities/put-files/v1"
deploy_url = "https://api.crowdstrike.com/real-time-response/combined/batch-active-responder-command/v1"
check_files_url = "https://api.crowdstrike.com/real-time-response/entities/put-files/v1"
execute_url = "https://api.crowdstrike.com/real-time-response/combined/batch-active-responder-command/v1"

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

local_file_path = "ipconfig.ps1"
remote_file_path = "C:\\Documents\\ipconfig.ps1"

def get_batch_id(token, host_ids):
    url = "https://api.crowdstrike.com/real-time-response/combined/batch-init-session/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "host_ids": host_ids
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in range(200, 300):
        try:
            batch_id = response.json().get('batch_id')
            if batch_id:
                print(f"Batch ID: {batch_id}")
                return batch_id
            else:
                print("Batch id response: ", response)
                raise Exception("Batch ID not found in response")
        except KeyError:
            print("Unexpected response structure:", response.json())
            raise Exception("Failed to parse response from get_batch_id")
    else:
        raise Exception("Failed to initiate batch session: " + response.text)

def get_uploaded_files(token):
    url = check_files_url
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code in range(200, 300):
        try:
            return response.json()['resources']
        except KeyError:
            print("Unexpected response structure:", response.json())
            raise Exception("Failed to parse response from get_uploaded_files")
    else:
        raise Exception("Failed to get list of uploaded files: " + response.text)

def file_exists_in_cloud(file_list, file_name):
    for file in file_list:
        file_basename = os.path.basename(file['name'])
        if file_basename == file_name:
            return file['sha256']
    return None

def upload_file_to_cloud(token, local_file_path):
    url = command_url
    headers = {
        'Authorization': f'Bearer {token}',
    }
    files = {
        'file': open(local_file_path, 'rb')
    }
    data = {
        'name': os.path.basename(local_file_path)
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code in range(200, 300):
        try:
            file_list = get_uploaded_files(token)
            print("File list:", file_list)
            file_name = os.path.basename(local_file_path)
            sha256 = file_exists_in_cloud(file_list, file_name)
            if sha256:
                print("File uploaded successfully with sha256:", sha256)
                return sha256
            else:
                raise Exception("Uploaded file does not appear in the cloud storage")
        except KeyError:
            print("Unexpected response structure:", response.json())
            raise Exception("Failed to parse response from upload_file_to_cloud")
    else:
        raise Exception("Failed to upload file: " + response.text)

def list_files_on_host(token, batch_id, remote_directory):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "base_command": "ls",
        "command_string": f"ls {remote_directory}",
        "batch_id": batch_id
    }
    response = requests.post(execute_url, headers=headers, json=data)
    if response.status_code in range(200, 300):
        response_data = response.json()
        print("Files listed successfully on host")
        print(response_data)
        return response_data
    else:
        raise Exception("Failed to list files on host: " + response.text)

def deploy_file_to_host(token, batch_id, sha256, remote_file_path):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "base_command": "put",
        "batch_id": batch_id,
        "command_string": f"put {sha256} {remote_file_path}",
        "file": {
            "sha256": sha256,
            "file_path": remote_file_path
        }
    }
    response = requests.post(deploy_url, headers=headers, json=data)
    response_data = response.json()
    if response.status_code in range(200, 300):
        print("File deployed to host successfully")
        print("Deploy to host response: ", response_data)
        return response_data
    else:
        raise Exception("Failed to deploy file to host: " + response.text)
    


def execute_script_on_host(token, batch_id, remote_file_path):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "base_command": "runscript",
        "command_string": f"powershell -ExecutionPolicy Bypass -File {remote_file_path}",
        "batch_id": batch_id
    }
    response = requests.post(execute_url, headers=headers, json=data)
    response_data = response.json()
    if response.status_code in range(200, 300):
        print("Script executed on host successfully")
        print(response_data)
    else:
        print("Failed to execute script on host:", response.text)
    
    task_data = response_data['combined']['resources'].get(device_id, {})
    if 'errors' in task_data:
        for error in task_data['errors']:
            print(f"Error Code: {error['code']}, Message: {error['message']}")

    if not task_data.get('complete', False):
        print(f"Command incomplete on device: {device_id}. Check the status or the validity of the command.")
    if task_data.get('stderr', ''):
        print(f"Error output from script on host: {task_data['stderr']}")

def main():
    try:
        file_list = get_uploaded_files(token)
        file_name = os.path.basename(local_file_path)
        sha256 = file_exists_in_cloud(file_list, file_name)

        if sha256:
            print("File already exists in CrowdStrike cloud.")
        else:
            sha256 = upload_file_to_cloud(token, local_file_path)
        
        print("sha256:", sha256)

        # Get batch ID
        batch_id = get_batch_id(token, [device_id])

        # List files before deployment for debugging
        print("Listing files in C:\\Documents\\ before deployment")
        files_before_deployment = list_files_on_host(token, batch_id, "C:\\Documents\\")
        print("Files before deployment:", files_before_deployment)
        
        # Deploy the file to the host
        deploy_response = deploy_file_to_host(token, batch_id, sha256, remote_file_path)
        print("Deploy response:", deploy_response)
        
        # List files after deployment to verify
        print("Listing files in C:\\Documents\\ after deployment")
        files_after_deployment = list_files_on_host(token, batch_id, "C:\\Documents\\")
        print("Files after deployment:", files_after_deployment)
        
        # Execute the script on the host
        execute_script_on_host(token, batch_id, remote_file_path)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()