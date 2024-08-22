import requests

def get_batch_id(token, host_ids):
    url = "https://api.crowdstrike.com/real-time-response/combined/batch-init-session/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "host_ids": host_ids
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in range(200, 300):
        try:
            batch_id = response.json().get('batch_id')
            if batch_id:
                return batch_id
            else:
                raise Exception("Batch ID not found in response")
        except KeyError:
            print("Unexpected response structure:", response.json())
            raise Exception("Failed to parse response from get_batch_id")
    else:
        raise Exception("Failed to initiate batch session: " + response.text)