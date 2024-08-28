import requests
import os
import json
import hmac
import hashlib

def fetch_env_vars(api_token, vcs_type, username, reponame):
    """ Fetch environment variables for a specific project """
    url = f"https://circleci.com/api/v2/project/{vcs_type}/{username}/{reponame}/envvar"
    headers = {'Circle-Token': api_token}
    response = requests.get(url, headers=headers)
    return response.json()

def generate_hmac(secret_key, data):
    """ Generate HMAC for the given data using SHA256 """
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

def main():
    api_token = os.getenv('API_TOKEN')
    hmac_key = os.getenv('HMAC_SECRET_KEY')

    # Fetch CircleCI project details from environment variables
    vcs_type = os.getenv('CIRCLE_PROJECT_VCS_TYPE').strip()  # e.g., "github"
    if not vcs_type:
        vcs_type = 'github'
    username = os.getenv('CIRCLE_PROJECT_USERNAME').strip()  # e.g., "rewanthtammana"
    reponame = os.getenv('CIRCLE_PROJECT_REPONAME').strip()  # e.g., "test"

    print(f"Processing environment variables for project: {vcs_type}/{username}/{reponame}")

    env_vars = fetch_env_vars(api_token, vcs_type, username, reponame)
    hmac_projects = {}  # Dictionary to store hmac results and associated projects
    errors = []

    for item in env_vars.get('items', []):
        env_var_name = item['name']
        env_var_value = os.getenv(env_var_name)
        if env_var_value is None:
            errors.append(f"{vcs_type}/{username}/{reponame}/{env_var_name}")
            continue

        hmac_value = generate_hmac(hmac_key, env_var_value)

        # Organize HMAC results by HMAC value
        if hmac_value not in hmac_projects:
            hmac_projects[hmac_value] = []
        hmac_projects[hmac_value].append(f"{vcs_type}/{username}/{reponame}/{env_var_name}")

    # Output the results as JSON
    with open('hmac_results.json', 'w') as file:
        json.dump(hmac_projects, file, indent=4)

    # For logging or debugging purposes, print the JSON
    print(json.dumps(hmac_projects, indent=4))
    
    if errors:
        print("ERROR")
        print(errors)

if __name__ == "__main__":
    main()
