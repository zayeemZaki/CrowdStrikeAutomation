import requests
import pandas as pd
from GetToken import getToken   
from LoadConfig import load_config # loads config.yaml
config = load_config('config.yaml')
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

#gets token
token = getToken()
if token: print('Authentication Successful')
else:
    print('Authentication failed:')
    exit()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print("\nPlease enter how you want to sort the Stale Accounts:") 
print(" 1. type \"risk score\" to sort based on risk score.")
print(" 2. type \"is human\" to sort basd on if host is human.")
print(" 3. type \"domain\" to sort based on the domain.")

sortingBasedOn = input("-")

if sortingBasedOn == "risk score":
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
          {
            countEntities(types: [USER] hasWeakPassword: true)
          }
        }
      }
    }
    """
elif sortingBasedOn == "is human":
    query = """
    query {
      entities(types: [USER], stale: true, sortKey: IS_HUMAN, sortOrder: DESCENDING, first: 100) {
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

elif sortingBasedOn == "domain":
    query = """
    query {
      entities(types: [USER], stale: true, sortKey: DOMAIN, sortOrder: DESCENDING, first: 100) {
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
        domain = user.get('domain')
        allStaleUsers.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain))

    data = {
        'Primary Name' : [user[0] for user in allStaleUsers],
        'Secondary Name' : [user[1] for user in allStaleUsers],
        'Is Human' : [user[2] for user in allStaleUsers],
        'Risk Score' : [user[3] for user in allStaleUsers],
        'Risk Severity' : [user[4] for user in allStaleUsers],
        'Domain' : [user[5] for user in allStaleUsers],
    }

    pd.set_option('display.max_rows', None)

    # Create DataFrame 
    df = pd.DataFrame(data) 
    
    print("\n", df, "\n")

else:
    print('Failed to retrieve users:', response.status_code, response.text)
 
"""
inactive_period

countEntities(types: [USER] stale: true)

better if else
"""