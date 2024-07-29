import requests
import pandas as pd
from GetToken import getToken   
from LoadConfig import load_config # loads config.yaml
config = load_config('config.yaml')
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

#gets token
token = getToken
if token: print('Authentication successful')
else:
    print('Authentication failed:')
    exit()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

query = """
query {
  entities(types: [USER], stale: true, sortKey: RISK_SCORE, sortOrder: DESCENDING, first: 100) {
    nodes {
      primaryDisplayName
      secondaryDisplayName
      isHuman: hasRole(type: HumanUserAccountRole)
      riskScore
      riskScoreSeverity
      accounts {
        ... on ActiveDirectoryAccountDescriptor {
          domain
        }
      }
    }
  }
}
"""

response = requests.post(graphqlUrl, headers=headers, json={'query': query})

if response.status_code == 200:
    data = response.json()
    users = data.get('data', {}).get('entities', {}).get('nodes', [])
    allStaleUsers = []

    for user in users:
        primaryName = user.get('primaryDisplayName')
        secondaryName = user.get('secondaryDisplayName')
        isHuman = user.get('isHuman')
        riskScore = user.get('riskScore')
        riskScoreSeverity = user.get('riskScoreSeverity')
        allStaleUsers.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity))

    data = {
        'Primary Name' : [user[0] for user in allStaleUsers],
        'Secondary Name' : [user[1] for user in allStaleUsers],
        'Is Human' : [user[2] for user in allStaleUsers],
        'Risk Score' : [user[3] for user in allStaleUsers],
        'Risk Severity' : [user[4] for user in allStaleUsers],
    }

    pd.set_option('display.max_rows', None)

    # Create DataFrame 
    df = pd.DataFrame(data) 
    
    print("\n", df, "\n")

else:
    print('Failed to retrieve users:', response.status_code, response.text)
 
#inactive_period

