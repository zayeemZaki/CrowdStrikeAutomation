import requests
from GetToken import getToken

IOC_QUERY_URL = "https://api.crowdstrike.com/iocs/queries/indicators/v1"
IOC_DETAIL_URL = "https://api.crowdstrike.com/iocs/entities/indicators/v1"

# Define severity levels as numerical values for proper comparison
severity_map = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}

# Query IOCs with pagination handling
def query_ioc_ids(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    ioc_ids = []
    next_cursor = None
    while True:
        params = {}
        if next_cursor:
            params['cursor'] = next_cursor
        
        response = requests.get(IOC_QUERY_URL, headers=headers, params=params)
        if response.status_code == 200:
            json_response = response.json()
            ioc_ids.extend(json_response.get('resources', []))  # Append the results to the list
            next_cursor = json_response.get('meta', {}).get('pagination', {}).get('next_cursor')
            
            # If there is no next_cursor, we are done
            if not next_cursor:
                break
        else:
            raise Exception(f"Failed to query IOCs: {response.text}")
    
    return ioc_ids

# Get detailed information for each IOC
def get_ioc_details_single(token, ioc_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {'ids': ioc_id}
    response = requests.get(IOC_DETAIL_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to get IOC details for {ioc_id}: {response.text}")

def get_detections_for_ioc(token, ioc_value):
    url = "https://api.crowdstrike.com/detects/queries/detects/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    fql_filter = f"behaviors.ioc_value:'{ioc_value}'"
    
    params = {
        'filter': fql_filter
    }
    print(f"Querying detections with filter: {fql_filter}")  # Debugging step

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to get detections for IOC: {response.text}")

def get_detection_details(token, detection_ids):
    url = "https://api.crowdstrike.com/detects/entities/summaries/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": detection_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def format_detection_details(detection_details):
    formatted_details = []
    for detection in detection_details.get('resources', []):
        host_info = detection.get("device", {})  # Fetch host information
        behaviors = detection.get("behaviors", [{}])[0]  # Fetch behaviors related to the detection
        detail = {
            "Detection ID": detection.get("detection_id", "N/A"),
            "Timestamp": behaviors.get("timestamp", "N/A"),
            "Severity": detection.get("max_severity_displayname", "N/A"),
            "Severity_DIGITS": behaviors.get("severity", "N/A"),
            "Status": detection.get("status", "N/A"),
            "Description": behaviors.get("description", "N/A"),  # Fetching description from behaviors
            "Host": host_info.get("hostname", "N/A"),  # Correct key for hostname
            "Type": behaviors.get("ioc_type", "N/A"),
            "Value": behaviors.get("ioc_value", "N/A"),
            "IOC_id": detection.get("ioc_id", "N/A"),
            "sha256": behaviors.get("sha256", "N/A")
        }
        formatted_details.append(detail)
    return formatted_details


# Function to print formatted detection details
def print_detection_details(formatted_details):
    for detail in formatted_details:
        print("\n--- Detection Details ---")
        for key, value in detail.items():
            print(f"{key}: {value}")
        print("-" * 50)


def get_ioc_details_by_id(token):
    while True:
        ioc_id = input("Enter the IOC ID to get more detailed information (or type 'Stop' to exit): ").strip()
        if ioc_id.lower() == "stop":
            break
        
        try:
            ioc_details = get_ioc_details_single(token, ioc_id)
            
            if not ioc_details:
                print("No details found for the provided IOC ID.")
                continue
            

            ioc = ioc_details[0]  # As you're fetching details for one specific IOC ID, get the first element
            print(f"\n--- Detailed Information for IOC ID: {ioc['id']} ---")
            print(f"Type: {ioc['type']}")
            print(f"Value: {ioc['value']}")
            print(f"Severity: {ioc.get('severity', 'N/A')}")
            print(f"Description: {ioc.get('description', 'N/A')}")
            print(f"Created On: {ioc.get('created_on', 'N/A')}")
            print(f"Created By: {ioc.get('created_by', 'N/A')}")
            print(f"Modified On: {ioc.get('modified_on', 'N/A')}")
            print(f"Modified By: {ioc.get('modified_by', 'N/A')}")
            print(f"Deleted: {ioc['deleted']}")

            print("-" * 50)
                    
            # Get detection details related to this IOC if needed
            detection_ids = get_detections_for_ioc(token, ioc['value'])
            if detection_ids:
                detection_details_response = get_detection_details(token, detection_ids)
                formatted_details = format_detection_details(detection_details_response)
                print_detection_details(formatted_details)
            else:
                print("No detections found for the provided IOC ID.")

        except Exception as e:
            print(f"Error fetching IOC details: {e}")




def filter_criteria():
    # Ask for filtering options
    min_severity = input("Enter the minimum severity to display (low, medium, high, critical, or leave empty for all): ").strip().lower()
    ioc_type = input("Enter the IOC type to filter (md5, sha256, domain, or leave empty for all): ").strip().lower()
    date_filter = input("Filter by creation date? (yes/no): ").strip().lower()

    date_range = None
    if date_filter == "yes":
        start_date = input("Enter start date (YYYY-MM-DD) or leave empty: ").strip()
        end_date = input("Enter end date (YYYY-MM-DD) or leave empty: ").strip()
        date_range = (start_date, end_date)

    return min_severity, ioc_type, date_range

def filter_ioc_by_date(ioc, date_range):
    start_date, end_date = date_range
    created_date = ioc.get('created_timestamp')

    if created_date:
        if start_date and created_date < start_date:
            return False
        if end_date and created_date > end_date:
            return False
    return True

def detect_iocs():
    token = getToken()
    ioc_ids = query_ioc_ids(token)
    
    if not ioc_ids:
        print("No IOCs detected.")
        return
    
    # Get filter criteria from the user
    min_severity, ioc_type, date_range = filter_criteria()

    # Convert the severity to numerical value
    min_severity_value = severity_map.get(min_severity, 0)

    for ioc_id in ioc_ids:
        try:
            ioc_details = get_ioc_details_single(token, ioc_id)
            for ioc in ioc_details:
                severity = ioc.get('severity', 'unknown').lower()  # Handle missing severity
                type_of_ioc = ioc.get('type', 'unknown').lower()  # Get the IOC type

                # Map severity to numerical value and filter
                ioc_severity_value = severity_map.get(severity, 0)
                
                # Filter by severity
                if min_severity_value and ioc_severity_value < min_severity_value:
                    continue
                
                # Filter by IOC type
                if ioc_type and ioc_type != type_of_ioc:
                    continue

                # Filter by date range if applicable
                if date_range and not filter_ioc_by_date(ioc, date_range):
                    continue
                
                # Print IOC details
                print(f"IOC ID: {ioc['id']}, Type: {ioc['type']}, Value: {ioc['value']}, Severity: {severity}")
                print(f"IOC Description: {ioc.get('description', 'N/A')}")
                print("-" * 50)
        except Exception as e:
            print(f"Error fetching IOC details: {e}")

    # Ask if the user wants to get more detailed information for a specific IOC
    more_details = input("Do you want to get detailed information for a specific IOC? (yes/no): ").strip().lower()
    if more_details == 'yes':
        get_ioc_details_by_id(token)

if __name__ == "__main__":
    detect_iocs()