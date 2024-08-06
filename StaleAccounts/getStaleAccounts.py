import requests
import pandas as pd
from datetime import datetime, timezone
from GetToken import getToken
from LoadConfig import load_config  # loads config.yaml

# Load config
config = load_config('config.yaml')
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'
rest_api_url = 'https://api.crowdstrike.com/alerts/entities/alerts/v1'

# Get token
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

sortingBasedOn = input("-").lower()

# Query to fetch stale user entities
entity_query = """
query {
    entities(types: [USER], stale: true, first: 100) {
        nodes {
            primaryDisplayName
            secondaryDisplayName
            hasRole(type: HumanUserAccountRole)
            riskScore
            riskScoreSeverity
            accounts {
                ... on ActiveDirectoryAccountDescriptor {
                    domain
                }
            }
            ... on EndpointEntity {
                mostRecentActivityEndTime
            }
        }
    }
}
"""

response = requests.post(graphqlUrl, headers=headers, json={'query': entity_query})

if response.status_code == 200:
    data = response.json()
    users = data.get('data', {}).get('entities', {}).get('nodes', [])
    allStaleUsers = []

    for user in users:
        primaryName = user.get('primaryDisplayName')
        secondaryName = user.get('secondaryDisplayName')
        isHuman = user.get('hasRole')
        riskScore = user.get('riskScore')
        riskScoreSeverity = user.get('riskScoreSeverity')
        domain = user.get('accounts', [{}])[0].get('domain')
        mostRecentActivityEndTime = user.get('mostRecentActivityEndTime')

        # Calculate inactive period
        if mostRecentActivityEndTime:
            mostRecentActivityDate = datetime.fromisoformat(mostRecentActivityEndTime.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            inactivePeriod = (datetime.now(timezone.utc) - mostRecentActivityDate).days
        else:
            inactivePeriod = None

        allStaleUsers.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain, inactivePeriod))
        
    
    data = {
        'Primary Name': [user[0] for user in allStaleUsers],
        'Secondary Name': [user[1] for user in allStaleUsers],
        'Is Human': [user[2] for user in allStaleUsers],
        'Risk Score': [user[3] for user in allStaleUsers],
        'Risk Severity': [user[4] for user in allStaleUsers],
        'Domain': [user[5] for user in allStaleUsers],
        'Inactive Period (days)': [user[6] for user in allStaleUsers],
    }

    df = pd.DataFrame(data)

    # Perform sorting based on user input
    if sortingBasedOn == "risk score":
        df = df.sort_values(by='Risk Score', ascending=False)
    elif sortingBasedOn == "is human":
        df = df.sort_values(by='Is Human', ascending=False)
    elif sortingBasedOn == "domain":
        df = df.sort_values(by='Domain')
    elif sortingBasedOn == "inactive period":
        df = df.sort_values(by='Inactive Period (days)', ascending=False)
    else:
        print('Invalid input. Exiting.')
        exit()
    
    pd.set_option('display.max_rows', None)
    print("\n", df, "\n")
else:
    print('Failed to retrieve users:', response.status_code, response.text)
