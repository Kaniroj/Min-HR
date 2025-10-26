
import requests

base = "https://taxonomy.api.jobtechdev.se/v1"
endpoints = [
    "/taxonomy",
    "/taxonomy/occupation-field",
    "/taxonomy/occupation-fields",
    "/terms/occupation-field",
    "/terms/occupation-fields",
    "/concepts/occupation-field",
    "/concepts/occupation-fields",
    "/terms?taxonomy=occupation-field",
    "/concepts?type=occupation-field",
]

for ep in endpoints:
    url = base + ep if not ep.startswith("http") else ep
    try:
        print(f"Testing: {url}")
        r = requests.get(url, timeout=10)
        print(f"→ Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Success! Response example:")
            print(r.json())
            break
    except Exception as e:
        print(f"{url} → error: {e}")
