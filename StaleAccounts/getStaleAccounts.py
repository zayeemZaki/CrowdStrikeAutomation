import requests
import pandas as pd
from GetToken import getToken
from LoadConfig import load_config # loads config.yaml

config = load_config('config.yaml')
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

# Gets token
token = getToken()
if token:
    print('Authentication Successful')
else:
    print('Authentication failed:')
    exit()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Query to get the count of stale user entities
count_query = """
query {
  countEntities(types: [USER], stale: true)
}
"""

count_response = requests.post(graphqlUrl, headers=headers, json={'query': count_query})

if count_response.status_code == 200:
    count_data = count_response.json()
    stale_users_count = count_data.get('data', {}).get('countEntities', 0)
    print(f"\nTotal number of stale user entities: {stale_users_count}\n")
else:
    print('Failed to retrieve entity count:', count_response.status_code, count_response.text)
    exit()

print("Please enter how you want to sort the Stale Accounts:")
print(" 1. type \"risk score\" to sort based on risk score.")
print(" 2. type \"is human\" to sort based on if host is human.")
print(" 3. type \"domain\" to sort based on the domain.")
print(" 4. type \"inactive period\" to sort based on the inactive period.")

sortingBasedOn = input("-")

# Dictionary to map user input to GraphQL query parts
query_map = {
    "risk score": """
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
              inactivePeriod: inactive_period
            }
          }
        }
    """,
    "is human": """
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
              inactivePeriod: inactive_period
            }
          }
        }
    """,
    "domain": """
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
              inactivePeriod: inactive_period
            }
          }
        }
    """,
    "inactive period": """
        query {
          entities(types: [USER], stale: true, sortKey: INACTIVE_PERIOD, sortOrder: DESCENDING, first: 100) {
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
              inactivePeriod: inactive_period
            }
          }
        }
    """
}

query = query_map.get(sortingBasedOn)
if query is None:
    print('Invalid input. Exiting.')
    exit()

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
        domain = user.get('accounts', [{}])[0].get('domain')
        inactivePeriod = user.get('inactivePeriod')
        allStaleUsers.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain, inactivePeriod))

    data = {
        'Primary Name': [user[0] for user in allStaleUsers],
        'Secondary Name': [user[1] for user in allStaleUsers],
        'Is Human': [user[2] for user in allStaleUsers],
        'Risk Score': [user[3] for user in allStaleUsers],
        'Risk Severity': [user[4] for user in allStaleUsers],
        'Domain': [user[5] for user in allStaleUsers],
        'Inactive Period': [user[6] for user in allStaleUsers],
    }

    pd.set_option('display.max_rows', None)

    # Create DataFrame
    df = pd.DataFrame(data)

    print("\n", df, "\n")
else:
    print('Failed to retrieve users:', response.status_code, response.text)
