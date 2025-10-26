
import requests
import json

url = "https://jobsearch.api.jobtechdev.se/search"

# Prova att söka med occupation-field, men också med occupation-name
params_list = [
    {"q": "data", "limit": 5},
    {"occupation-field": "Data/IT", "limit": 5},
    {"occupation-name": "Data engineer", "limit": 5}
]

for params in params_list:
    print("\n🔍 Testar med:", params)
    r = requests.get(url, params=params)
    print("Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Antal träffar:", len(data.get("hits", [])))
        if len(data.get("hits", [])) > 0:
            print(json.dumps(data["hits"][0], indent=2, ensure_ascii=False))
            break
