
import requests

url = "https://jobsearch.api.jobtechdev.se/search"
params = {"limit": 5}

r = requests.get(url, params=params)
r.raise_for_status()
data = r.json()

print("Exempel på datafält:")
for hit in data.get("hits", [])[:3]:
    print(hit.get("occupation_field", {}).get("label"))
