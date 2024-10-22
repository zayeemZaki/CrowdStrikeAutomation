import falconpy
import os
import sys
import yaml
from GetDeviceId import getDeviceId
from GetToken import getToken

def load_config(file_path):
    """ Load configuration from a YAML file """
    if not os.path.isfile(file_path):
        print(f"Configuration file {file_path} does not exist.")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error reading the YAML file: {e}")
        sys.exit(1)

def main():
    config = load_config('config.yaml')

    falcon = falconpy.UserManagement(
        client_id=config['client_id'],
        client_secret=config['client_secret']
    )

    try:
        # Gets all available role ids
        get_available_role_ids = falcon.get_available_role_ids()
        print("Available role ids: ", get_available_role_ids)

        user_name = ""

        token = getToken()
        deviceID = getDeviceId(token, user_name)

        # Initialize `admin_role_id` variable
        admin_role_id = next((role for role in get_available_role_ids['body']['resources'] if role['name'] == "Admin Role"), {}).get('id', None)
        
        if not admin_role_id:
            print("Admin role ID not found.")

        # Gets user's role ids
        user_roles_response = falcon.get_user_role_ids(user_id=deviceID)
        user_roles = user_roles_response['body']['resources']

        if admin_role_id in user_roles:
            revoke_response = falcon.revoke_user_role_ids(user_id=deviceID, roles=[admin_role_id])
            print("Admin role revoked successfully.")
        else:
            print("User does not have the admin role.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
