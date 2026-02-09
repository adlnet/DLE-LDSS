import requests

def fetch_uid_repo(microservice_url):
    response = requests.get(f"{microservice_url}/api/uid-repo/", timeout=10)
    if response.status_code == 200:
        return response.json()  # Return the UID data
    else:
        raise ValueError("Failed to fetch UID repo")
