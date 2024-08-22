import os
import base64
import requests
from falconpy import APIHarness

# Configuration
client_id = 'your_client_id'
client_secret = 'your_client_secret'
cloud_region = 'us-1'  # or another appropriate region
hostname = 'hostname_to_deploy_to'
file_path = 'path_to_your_file'

# Initialize API harness
falcon = APIHarness(client_id=client_id, client_secret=client_secret, base_url=f"https://api.{cloud_region}.crowdstrike.com")

# Step 1: Authenticate and get OAuth token
falcon.token

# Step 2: Upload the file
with open(file_path, 'rb') as file:
    file_content = file.read()
file_encoded = base64.b64encode(file_content)

upload_payload = {
    'name': os.path.basename(file_path),
    'description': 'File deployed via API',
    'content': file_encoded.decode('utf-8')
}

upload_response = falcon.command('UploadSampleV3', upload_payload)

if upload_response['status_code'] != 201:
    raise Exception(f"Failed to upload file: {upload_response}")

file_id = upload_response['body']['resources'][0]['file_sha256']

# Step 3: Get the host ID for the host we want to deploy to
host_response = falcon.command('QueryDevicesByFilter', {'filter': f'hostname:"{hostname}"'})
if not host_response['body']['resources']:
    raise Exception(f"No host found with hostname: {hostname}")

host_id = host_response['body']['resources'][0]

# Step 4: Deploy the file
deploy_payload = {
    'host_ids': [host_id],
    'file_id': file_id,
    'task_type': 'retrieve'      # 'retrieve' is for download
}

deploy_response = falcon.command('RosterActionV1', deploy_payload)

if deploy_response['status_code'] != 201:
    raise Exception(f"Failed to deploy file: {deploy_response}")

print(f"File deployed successfully to host: {hostname}")
