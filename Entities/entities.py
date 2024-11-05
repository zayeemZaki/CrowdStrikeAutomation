import requests
import pandas as pd
from datetime import datetime, timezone
from GetToken import getToken

graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

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

# List of parameters to be queried
parameters = [
    "accountCreationEndTime",
    "accountCreationStartTime",
    "accountExpirationEndTime",
    "accountExpirationStartTime",
    "accountLocked",
    "after",
    "agentIds",
    "all",
    "any",
    "archived",
    "associationBindingTypes",
    "before",
    "businessRoles",
    "cloudEnabled",
    "cloudOnly",
    "dataSources",
    "departments",
    "directMemberOfActiveDirectoryGroups",
    "directMemberOfContainers",
    "domains",
    "emailAddresses",
    "enabled",
    "enabledOrUnmanaged",
    "entityIds",
    "first",
    "hasAccount",
    "hasAgedPassword",
    "hasAgent",
    "hasExposedPassword",
    "hasLinkedAccounts",
    "hasNeverExpiringPassword",
    "hasOpenIncidents",
    "hasVulnerableOs",
    "hasWeakPassword",
    "hostNames",
    "impersonator",
    "inactive",
    "last",
    "learned",
    "marked",
    "maxRiskScoreSeverity",
    "memberOfActiveDirectoryGroups",
    "memberOfContainers",
    "minRiskScoreSeverity",
    "mostRecentActivityEndTime",
    "mostRecentActivityStartTime",
    "mostRecentOnPremiseActivityEndTime",
    "mostRecentOnPremiseActivityStartTime",
    "mostRecentSSOActivityEndTime",
    "mostRecentSSOActivityStartTime",
    "not",
    "ous",
    "passwordLastChangeEndTime",
    "passwordLastChangeStartTime",
    "primaryDisplayNames",
    "riskFactorTypes",
    "roles",
    "samAccountNames",
    "secondaryDisplayNames",
    "shared",
    "sortKey",
    "sortOrder",
    "stale",
    "types",
    "unmanaged",
    "watched"
]

user_input = {}

# Get inputs from user
print("Please specify the parameters you want to use for the query. Press Enter to skip a parameter.\n")
for param in parameters:
    value = input(f"Enter value for {param}: ")
    if value:
        user_input[param] = value

# Construct the dynamic part of the GraphQL query
query_filters = []
for key, value in user_input.items():
    if key == "first" or key == "last":
        query_filters.append(f'{key}: {value}')
    elif key == "types":
        query_filters.append(f'{key}: [{value}]')
    else:
        if value.lower() == "true":
            value = "true"
        elif value.lower() == "false":
            value = "false"
        else:
            value = f'"{value}"'
        query_filters.append(f'{key}: {value}')

query_filters_string = ", ".join(query_filters)

# Query to fetch entities based on user input
entity_query = f"""
query {{
    entities({query_filters_string}) {{
        nodes {{
            primaryDisplayName
            secondaryDisplayName
            hasRole(type: HumanUserAccountRole)
            riskScore
            riskScoreSeverity
            accounts {{
                ... on ActiveDirectoryAccountDescriptor {{
                    domain
                }}
            }}
            ... on EndpointEntity {{
                mostRecentActivity
            }}
        }}
    }}
}}
"""

response = requests.post(graphqlUrl, headers=headers, json={'query': entity_query})

if response.status_code == 200:
    data = response.json()
    users = data.get('data', {}).get('entities', {}).get('nodes', [])
    allEntities = []

    for user in users:
        primaryName = user.get('primaryDisplayName')
        secondaryName = user.get('secondaryDisplayName')
        isHuman = user.get('hasRole')
        riskScore = user.get('riskScore')
        riskScoreSeverity = user.get('riskScoreSeverity')
        domain = user.get('accounts', [{}])[0].get('domain')
        mostRecentActivity = user.get('mostRecentActivity')

        # Calculate inactive period, if available
        if mostRecentActivity:
            mostRecentActivityDate = datetime.fromisoformat(mostRecentActivity.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            inactivePeriod = (datetime.now(timezone.utc) - mostRecentActivityDate).days
        else:
            inactivePeriod = None

        allEntities.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain, inactivePeriod))

    data = {
        'Primary Name': [user[0] for user in allEntities],
        'Secondary Name': [user[1] for user in allEntities],
        'Is Human': [user[2] for user in allEntities],
        'Risk Score': [user[3] for user in allEntities],
        'Risk Severity': [user[4] for user in allEntities],
        'Domain': [user[5] for user in allEntities],
        'Inactive Period (days)': [user[6] for user in allEntities],
    }

    df = pd.DataFrame(data)

    # Perform sorting based on user input
    print("\nPlease enter how you want to sort the accounts:")
    print(" 1. type \"risk score\" to sort based on risk score.")
    print(" 2. type \"is human\" to sort based on if host is human.")
    print(" 3. type \"domain\" to sort based on the domain.")
    print(" 4. type \"inactive period\" to sort based on the inactive period.")
    
    sortingBasedOn = input("-").lower()

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
