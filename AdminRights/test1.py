from falconpy import RealTimeResponse
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

# Initialize RealTimeResponse object
falcon = RealTimeResponse(
    client_id=config['client_id'],
    client_secret=config['client_secret']
)

# Test with a simple command first
test_command = "whoami"  # This is a simple command to check if RTR is working

# Execute the simple command
response = falcon.execute_command(
    base_command="runscript",
    command_string=f"run {test_command}",
    session_id=session_id,
    persist=True
)

# Check response
if response['status_code'] == 201:
    print("Test command executed successfully")
    print(response['body'])
else:
    print(f"Failed to execute test command: {response['body']['errors'][0]['message']}")

# If the test command works, then proceed with the full PowerShell script
if response['status_code'] == 201:
    command_string = f'''
    Import-Module Microsoft.PowerShell.LocalAccounts;
    if (Get-LocalUser -Name "{username}") {{
        Remove-LocalGroupMember -Group "Administrators" -Member "{username}";
    }} else {{
        Write-Host "User not found";
    }}
    '''
    
    response = falcon.execute_command(
        base_command="runscript",
        command_string=command_string,
        session_id=session_id,
        persist=True
    )

    # Check response
    if response['status_code'] == 201:
        print(f"Command executed successfully for user: {username}")
    else:
        print(f"Failed to execute command: {response['body']['errors'][0]['message']}")
