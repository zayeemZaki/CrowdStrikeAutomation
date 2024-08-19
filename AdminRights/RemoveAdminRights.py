from falconpy import RealTimeResponseAdmin, RealTimeResponse
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

# Get username
username = input("Please enter target device username: ")

# Initialize RealTimeResponseAdmin object
falcon = RealTimeResponseAdmin(
    client_id=config['client_id'],
    client_secret=config['client_secret']
)

# A basic but valid PowerShell command to remove user from local admin group
command_string = f"Remove-LocalGroupMember -Group 'Administrators' -Member '{username}'"

# Wrapping the command in double-quotes to avoid issues
full_command = f'run Command="{command_string}"'

# Execute the PowerShell command via RTR
response = falcon.execute_admin_command(
    base_command="runscript",
    command_string=full_command,
    session_id=session_id,
    persist=True
)

# Check the full response for deeper insights
print(f"API Response: {response}")

# Handle success or failure responses
if response['status_code'] == 201:
    print(f"Command executed successfully for user: {username}")
else:
    error_message = response.get('body', {}).get('errors', [{}])[0].get('message', 'Unknown error')
    print(f"Failed to execute command: {error_message}")