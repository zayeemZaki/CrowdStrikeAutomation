import os
import sys
import yaml
from falconpy import IdentityProtection

def load_config(file_path):
    """Load configuration from a YAML file."""
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} does not exist.")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

config = load_config('config.yaml')

falcon = IdentityProtection(client_id=config['client_id'], client_secret=config['client_secret'])

idp_query = """
query ($after: Cursor) {
  entities(types: [USER], archived: false, learned: false, first: 100, after: $after) {
    nodes {
      primaryDisplayName
      accounts {
        ... on ActiveDirectoryAccountDescriptor {
          domain
          admin
          lastActivity
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

variables = {
    "after": None
}

def get_stale_admin_accounts():
    stale_admin_accounts = []
    has_more_results = True

    while has_more_results:
        response = falcon.graphql(query=idp_query, variables=variables)

        if 'errors' in response:
            print("Error in API response:", response['errors'])
            break

        if 'data' not in response:
            print("Unexpected response structure:", response)
            break

        entities = response['data'].get('entities', {}).get('nodes', [])
        for user in entities:
            for account in user.get('accounts', []):
                if account.get('admin') and account.get('lastActivity') > 30:
                    stale_admin_accounts.append({
                        "username": user['primaryDisplayName'],
                        "domain": account['domain'],
                        "last_activity": account['lastActivity']
                    })

        page_info = response['data'].get('entities', {}).get('pageInfo', {})
        has_more_results = page_info.get('hasNextPage', False)
        variables['after'] = page_info.get('endCursor')

    return stale_admin_accounts

stale_admin_accounts = get_stale_admin_accounts()

if stale_admin_accounts:
    print("Stale Admin Accounts (Inactive > 30 days):")
    for account in stale_admin_accounts:
        print(f"Username: {account['username']}, Domain: {account['domain']}, Last Activity: {account['last_activity']} days ago")
else:
    print("No stale admin accounts found or an error")
