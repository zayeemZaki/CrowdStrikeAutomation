import requests
import json
from GetToken import getToken

def get_device_details(token, device_ids):
    devices_details_url = 'https://api.crowdstrike.com/devices/entities/devices/v2'
    device_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    detailed_devices = []
    # Break down device_ids into smaller chunks to avoid request size limits
    chunk_size = 5000  # Adjust the chunk size according to your needs

    for i in range(0, len(device_ids), chunk_size):
        chunk = device_ids[i:i + chunk_size]
        payload = {
            'ids': chunk
        }
        response = requests.post(devices_details_url, headers=device_headers, json=payload)
        
        if response.status_code != 200:
            print(f'Failed to get device details for chunk starting at index {i}: {response.text}')
            continue

        detailed_devices.extend(response.json().get('resources', []))

    return detailed_devices

token = getToken()

# Retrieve the list of device IDs
devices_url = 'https://api.crowdstrike.com/devices/queries/devices/v1'
device_headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get(devices_url, headers=device_headers)

if response.status_code != 200:
    print(f'Failed to get devices: {response.text}')
    exit()

device_ids = response.json().get('resources', [])
print(f'Found Device IDs: {len(device_ids)}')

# Retrieve device details
device_details = get_device_details(token, device_ids)

# Extract and print IP addresses
for device in device_details:
    if 'local_ip' in device:
        print(f"Device {device['device_id']} has IPs: {device['local_ip']}")
    else:
        print(f"Device {device['device_id']} has no local IP information.")

# Optional: Save the details to a file
with open('device_ip_addresses.json', 'w') as file:
    json.dump(device_details, file, indent=4)

print(f'Total Devices: {len(device_details)}')
