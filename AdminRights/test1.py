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

# Initialize RealTimeResponse object
falcon = RealTimeResponse(
    client_id=config['client_id'],
    client_secret=config['client_secret']
)

# Test with a basic command like 'ipconfig'
response = falcon.execute_command(
    base_command="run",
    command_string="ipconfig",  # Simple command to list network configuration
    session_id=session_id,
    persist=True
)

# Check response
if response['status_code'] == 201:
    print("Basic command executed successfully")
    print(response['body'])
else:
<<<<<<< HEAD
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

    # Check the full response for deeper insights
    print(f"API Response: {response}")

    # Check response
    if response['status_code'] == 201:
        print(f"Command executed successfully for user: {username}")
    else:
        print(f"Failed to execute command: {response['body']['errors'][0]['message']}")
=======
    print(f"Failed to execute command: {response['body']['errors'][0]['message']}")
>>>>>>> 1c579bff06c01d5337586b62a5a4159fad050aef
