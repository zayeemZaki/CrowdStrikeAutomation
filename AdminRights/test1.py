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

# Initialize RealTimeResponse object
falcon = RealTimeResponseAdmin(
    client_id=config['client_id'],
    client_secret=config['client_secret']
)

# Test with a basic command like 'ipconfig'
response = falcon.execute_admin_command(
    base_command="run",
    command_string="ps",  
    session_id=session_id,
    persist=True
)


# Check the full response for deeper insights
print(f"API Response: {response}")

# Check response
if response['status_code'] == 201:
    print("Basic command executed successfully")
    print(response)
else:
    print(f"Failed to execute command: {response['body']['errors'][0]['message']}")
