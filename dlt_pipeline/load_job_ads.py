import dlt
import requests
import json
from datetime import datetime

# --------------------------------------
# 🔹 Funktion för att hämta annonser med pagination
# --------------------------------------
def fetch_ads(field_name, field_id, limit=100, max_offset=2000):
    """
    Hämtar annonser från JobTech API baserat på occupation-field-ID.
    Returnerar alla annonser (inte bara första sidan).
    Lägger till tidsstämpel (fetch_time) för varje annons.
    """
    print(f"📡 Hämtar annonser för: {field_name}")
    url = "https://jobsearch.api.jobtechdev.se/search"
    offset = 0

    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "occupation-field": field_id
        }

        response = requests.get(url, params=params, headers={"accept": "application/json"})
        response.raise_for_status()

        data = response.json()
        hits = data.get("hits", [])

        if not hits:
            print(f"⚠️ Inga fler annonser för {field_name} (offset={offset})")
            break

        print(f"✅ Hämtade {len(hits)} annonser (offset={offset}) för {field_name}")

        fetch_time = datetime.utcnow().isoformat()  # Lägg till tidsstämpel (UTC)
        for ad in hits:
            ad["fetch_time"] = fetch_time
            ad["occupation_field_name"] = field_name
            yield ad

        if len(hits) < limit or offset > max_offset:
            break

        offset += limit


# --------------------------------------
# 🔹 DLT Resource
# --------------------------------------
@dlt.resource(write_disposition="append")
def job_ads_resource():
    """
    Itererar över alla valda yrkesområden och hämtar annonser.
    """
    fields = {
        "Data/IT": "2t2x_QsB_sS5",
        "Administration, ekonomi, juridik": "4t2x_RdB_wS7",
        "Transport, distribution, lager": "6t2x_StB_pS3"
    }

    for field_name, field_id in fields.items():
        yield from fetch_ads(field_name, field_id)


# --------------------------------------
# 🔹 DLT Pipeline
# --------------------------------------
if __name__ == "__main__":
    print("🚀 JobTech DLT-pipeline startar...")

    pipeline = dlt.pipeline(
        pipeline_name="jobtech_ads",
        destination="snowflake",
        dataset_name="staging"
    )

    load_info = pipeline.run(job_ads_resource, table_name="job_ads")

    print("✅ Pipeline körd klart!")
    print(load_info)
