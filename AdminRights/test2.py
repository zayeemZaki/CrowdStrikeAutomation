from falconpy import RealTimeResponseAdmin
from GetToken import getToken
from GetDeviceId import getDeviceId
from GetRtrSessionId import initiateRtrSession
from LoadConfig import load_config

# Load configuration
config = load_config('config.yaml')

# Authenticate and get token
token = getToken()
if not token:
    print('Authentication failed')
    exit()

# Get device ID from hostname
hostname = input("Please input target hostname: ")
device_id = getDeviceId(token, hostname)
if not device_id:
    print(f'Failed to retrieve device ID for hostname: {hostname}')
    exit()

# Initiate RTR session
session_id = initiateRtrSession(token, device_id)
if not session_id:
    print(f'Failed to initiate RTR session for device ID: {device_id}')
    exit()

# Initialize RealTimeResponseAdmin object
falcon = RealTimeResponseAdmin(
    client_id=config['client_id'],
    client_secret=config['client_secret']
)

# Attempt to run a simple PowerShell command
command_string = 'whoami'

response = falcon.execute_admin_command(
    base_command="run",
    command_string=command_string,
    session_id=session_id,
    persist=True
)

# Check response
if response['status_code'] == 201:
    print("Command executed successfully")
    print(response['body'])
else:
    print(f"Failed to execute command: {response['body']['errors'][0]['message']}")
