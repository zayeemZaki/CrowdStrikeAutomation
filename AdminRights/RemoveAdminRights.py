import requests
from GetToken import getToken   
from GetDeviceId import getDeviceId
from GetRtrSessionId import initiateRtrSession

#function to remove admin rights
def removeAdminRights(token, session_id, username):
   print(token, session_id, username)
   url = "https://api.crowdstrike.com/real-time-response/entities/active-responder-command/v1"
   headers = {
       "Authorization": f"Bearer {token}",
       "Accept": "application/json"
   }
   data = {
       "base_command": "runscript",
       "command_string": f"Remove-LocalGroupMember -Group 'Administrators' -Member '{username}'",
       "session_id": session_id
   }
   response = requests.post(url, headers=headers, json=data)
   response.raise_for_status()
   return response.json()

#gets token
token = getToken()
if token: print('Authentication successful')
else:
    print('Authentication failed:')
    exit()


#gets device id from hostname
hostname = input("Please input target hostname: ") #takes host name as input
device_id = getDeviceId(token, hostname)


#gets session id using device id
session_id = initiateRtrSession(token, device_id)


username = input("Please enter target device username: ") #takes username as input

#Calls remove Admin rights function and stores the result in result variable
result = removeAdminRights(token, session_id, username)

#prints final result
print("Command Execution Result:", result)


"""
not working
"""