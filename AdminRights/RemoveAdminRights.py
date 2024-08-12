import requests
from GetToken import getToken   
from GetDeviceId import getDeviceId
from GetRtrSessionId import initiateRtrSession
from LoadConfig import load_config # loads config.yaml

from falconpy import RealTimeResponse


config = load_config('config.yaml')


# Gets token
token = getToken()
if token: 
    print('Authentication successful')
else:
    print('Authentication failed:')
    exit()

# Gets device ID from hostname
hostname = input("Please input target hostname: ") # Takes hostname as input
device_id = getDeviceId(token, hostname)

# Gets session ID using device ID
session_id = initiateRtrSession(token, device_id)

# Takes username as input
username = input("Please enter target device username: ")

# Calls remove admin rights function and stores the result in result variable
# result = removeAdminRights(token, session_id, username)


# Do not hardcode API credentials!
falcon = RealTimeResponse(client_id=config['client_id'],
                          client_secret=config['client_secret']
                          )

<<<<<<< HEAD
command_string = f"Remove-LocalGroupMember -Group 'Administrators' -Member '{username}'\""
=======
command_string = r"Remove-LocalGroupMember -Group 'Administrators' -Member '{}'".format(username)
>>>>>>> 1d4454f (updated command_string)

response = falcon.execute_active_responder_command(base_command="runscript",
                                                   command_string=f"runscript -Raw=```{command_string}```",
                                                   persist=True,
                                                   session_id=session_id
                                                   )

print(response)


# Prints final result
# print("Command Execution Result:", result)



#Please input target hostname: fs-39141
#Please enter target device username: miller-test-la