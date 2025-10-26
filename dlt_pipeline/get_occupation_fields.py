import requests

url = "https://taxonomy.api.jobtechdev.se/v1/terms?taxonomy=occupation-field"
headers = {"Accept": "application/json"}

response = requests.get(url, headers=headers, timeout=10)
print("Status:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("Tillgängliga occupation fields:\n")
    for item in data["terms"]:
        print(f"{item['preferred_label']} → {item['id']}")
else:
    print(response.text)
