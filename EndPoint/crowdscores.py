# crowdscores.py
import requests
from GetToken import getToken

def get_crowdscores(token):
    url = "https://api.crowdstrike.com/incidents/combined/crowdscores/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()



#main code
token = getToken()

score = get_crowdscores(token)
print("Crowdscore: ", score)
