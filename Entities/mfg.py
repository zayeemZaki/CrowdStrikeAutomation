import requests
import pandas as pd

def getToken():
    auth_payload = {
        'client_id': 'write_your_client_id',  # Replace with your actual client ID
        'client_secret': 'write_your_client_secret'  # Replace with your actual client secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post('https://api.crowdstrike.com/oauth2/token', data=auth_payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("Failed to obtain token:", response.status_code, response.text)
        return None

API_URL = "https://api.crowdstrike.com/identity-protection/combined/graphql/v1"
TOKEN = getToken()

if TOKEN:
    query_template = """
    {
      entities(departments: ["MFG Support"], types: [USER], first: 50%s) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          primaryDisplayName
          secondaryDisplayName
          isHuman: hasRole(type: HumanUserAccountRole)
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    end_cursor = ""
    all_entities = []

    while True:
        cursor_clause = f', after: "{end_cursor}"' if end_cursor else ""
        query = query_template % cursor_clause
        response = requests.post(API_URL, json={"query": query}, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            entities = result["data"]["entities"]["nodes"]
            all_entities.extend(entities)
            
            page_info = result["data"]["entities"]["pageInfo"]
            if page_info["hasNextPage"]:
                end_cursor = page_info["endCursor"]
            else:
                break
        else:
            print("Query failed:", response.status_code, response.text)
            break

    df = pd.json_normalize(all_entities)

    # Write to Excel file
    excel_file = "entities.xlsx"
    df.to_excel(excel_file, index=False)

    print(f"All entities have been written to {excel_file}")
else:
    print("Exiting script due to token retrieval failure.")
