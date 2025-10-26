import requests

url = "https://jobsearch.api.jobtechdev.se/search"
params = {"limit": 50}
r = requests.get(url, params=params)
r.raise_for_status()

data = r.json()
fields = {}

for hit in data.get("hits", []):
    occ = hit.get("occupation_field")
    if occ:
        fields[occ["label"]] = occ["concept_id"]

print("\n📊 Upptäckta occupation fields och deras ID:\n")
for label, cid in fields.items():
    print(f"- {label}: {cid}")
