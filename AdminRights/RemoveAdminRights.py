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

# Get username
username = input("Please enter target device username: ")

# Initialize RealTimeResponseAdmin object
falcon = RealTimeResponseAdmin(client_id=config['client_id'],
                               client_secret=config['client_secret'])

# PowerShell command to remove the user from local administrators
command_string = f"Remove-LocalGroupMember -Group 'Administrators' -Member '{username}'"

# Execute the PowerShell command via RTR
response = falcon.execute_admin_command(base_command="runscript",
                                        command_string=command_string,
                                        session_id=session_id,
                                        persist=True)

# Check response
if response['status_code'] == 201:
    print(f"Command executed successfully for user: {username}")
else:
    print(f"Failed to execute command: {response['body']['errors'][0]['message']}")



# Prints final result
# print("Command Execution Result:", result)



