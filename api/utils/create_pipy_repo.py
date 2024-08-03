import requests
import json

nexus_url = 'http://localhost:8081/service/rest/v1/repositories/pypi/hosted'
username = 'admin'
password = 'secret123'

repo_data = {
    "name": "onlexnet",
    "online": True,
    "storage": {
        "blobStoreName": "default",
        "strictContentTypeValidation": True,
        "writePolicy": "allow"
    },
    "cleanup": None,
    "component": {
        "proprietaryComponents": True
    },
    "format": "pypi",
    "type": "hosted"
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(nexus_url, auth=(username, password), headers=headers, data=json.dumps(repo_data))

if response.status_code == 201:
    print("Repozytorium zostało pomyślnie utworzone.")
else:
    print(f"Błąd podczas tworzenia repozytorium: {response.status_code} - {response.text}")
