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
execute_url = "https://api.crowdstrike.com/real-time-response/entities/execute-command/v1"

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
        # Extract just the file name from the full path
        file_basename = os.path.basename(file['name'])
        print("-------- - - -- - - -- - ")
        print(file_basename, file_name)
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
            # Fetch the list of currently uploaded files
            file_list = get_uploaded_files(token)
            print("File list:", file_list)
            # Check if the uploaded file exists in the cloud and get its SHA256
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

def deploy_file_to_host(token, device_id, sha256, remote_file_path, session_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "command": "put",
        "file": {
            "sha256": sha256,
            "file_path": remote_file_path
        },
        "host_ids": [device_id],
        "session_id": session_id
    }
    response = requests.post(deploy_url, headers=headers, json=data)
    if response.status_code in range(200, 300):
        print("File deployed to host successfully")
    else:
        raise Exception("Failed to deploy file to host: " + response.text)

def execute_script_on_host(token, device_id, session_id, remote_file_path):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "command": "runscript",
        "arguments": {
            "script_name": remote_file_path,
            "command_line": f"powershell -ExecutionPolicy Bypass -File {remote_file_path}"
        },
        "host_ids": [device_id],
        "session_id": session_id
    }
    response = requests.post(execute_url, headers=headers, json=data)
    if response.status_code in range(200, 300):
        print("Script executed on host successfully")
        print(response.json())
    else:
        raise Exception("Failed to execute script on host: " + response.text)

def main():
    try:
        file_list = get_uploaded_files(token)
        file_name = os.path.basename(local_file_path)
        sha256 = file_exists_in_cloud(file_list, file_name)

        if sha256:
            print("File already exists in CrowdStrike cloud.")
        else:
            sha256 = upload_file_to_cloud(token, local_file_path)
        
        print("sha256: ", sha256)

        # Deploy the file to the host
        deploy_file_to_host(token, device_id, sha256, remote_file_path, session_id)
        
        # Execute the script on the host
        execute_script_on_host(token, device_id, session_id, remote_file_path)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()




































# import os
# import requests
# import json
# import time
# from LoadConfig import load_config
# from GetToken import getToken
# from GetRtrSessionId import initiateRtrSession
# from GetDeviceId import getDeviceId

# # Load configuration
# config = load_config('config.yaml')
# rtr_url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
# command_url = "https://api.crowdstrike.com/real-time-response/entities/put-files/v1"

# # Authenticate and get token
# token = getToken()
# if not token:
#     print('Authentication failed')
#     exit()

# # Get device ID from hostname
# hostname = input("Please input target hostname: ")
# device_id = getDeviceId(token, hostname)
# if not device_id:
#     print(f"Device ID not found for hostname: {hostname}")
#     exit()

# session_id = initiateRtrSession(token, device_id)
# if not session_id:
#     print(f'Failed to initiate RTR session for device ID: {device_id}')
#     exit()

# local_file_path = "hello.txt"
# remote_file_path = "C:\\Documents\\hello.txt"







# def upload_file(token, session_id, local_file_path, remote_file_path):
#     url = f"{command_url}"
#     headers = {
#         'Authorization': f'Bearer {token}',
#     }
#     files = {
#         'file': open(local_file_path, 'rb')
#     }
#     data = {
#         'file_name': os.path.basename(local_file_path),
#         'description': 'Uploaded from automation script'
#     }
#     response = requests.post(url, headers=headers, files=files, data=data)
#     if response.status_code in range(200, 300):
#         print("File uploaded successfully")
#     else:
#         raise Exception("Failed to upload file: " + response.text)
    




# def close_rtr_session(token, session_id):
#     url = f"{rtr_url}/{session_id}"
#     headers = {
#         'Authorization': f'Bearer {token}'
#     }
#     response = requests.delete(url, headers=headers)
#     if response.status_code in range(200, 300):
#         print("RTR session closed")
#     else:
#         raise Exception("Failed to close RTR session: " + response.text)
    



# def main():
#     try:
#         upload_file(token, session_id, local_file_path, remote_file_path)
#         time.sleep(5)
#         close_rtr_session(token, session_id)
#     except Exception as e:
#         print(f"Error: {e}")




# if __name__ == "__main__":
#     main()
