import requests
import pandas as pd

def get_token(client_id, client_secret):
    auth_payload = {
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        'https://api.crowdstrike.com/oauth2/token',
        data=auth_payload,
        headers=headers
    )
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Failed to obtain token: {response.status_code}, {response.text}")

def query_entities(token, department_name, output_file="entities.xlsx"):
    API_URL = "https://api.crowdstrike.com/identity-protection/combined/graphql/v1"
    query_template = """
    {
      entities(departments: ["%s"], types: [USER], first: 50%s) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          primaryDisplayName
          secondaryDisplayName
          isHuman: hasRole(type: HumanUserAccountRole)
          riskScore
          roles {
            type
          }
          accounts {
            dataSource
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    end_cursor = ""
    all_entities = []

    while True:
        cursor_clause = f', after: "{end_cursor}"' if end_cursor else ""
        query = query_template % (department_name, cursor_clause)
        response = requests.post(API_URL, json={"query": query}, headers=headers)

        if response.status_code == 200:
            result = response.json()
            entities = result["data"]["entities"]["nodes"]
            all_entities.extend(entities)
            
            page_info = result["data"]["entities"]["pageInfo"]
            if page_info.get("hasNextPage"):
                end_cursor = page_info.get("endCursor")
            else:
                break
        else:
            raise Exception(f"Query failed: {response.status_code}, {response.text}")

    # Convert to DataFrame and save to Excel
    df = pd.json_normalize(all_entities)
    df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":

    CLIENT_ID = write_client_id #Replace
    CLIENT_SECRET = write_client_secret #Replace
    DEPARTMENT_NAME = "MFG Support"  # Correct it as it is case sensitive

    try:
        token = get_token(CLIENT_ID, CLIENT_SECRET)
        query_entities(token, DEPARTMENT_NAME)
    except Exception as e:
        print(f"Error: {e}")
