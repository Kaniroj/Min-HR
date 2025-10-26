import snowflake.connector
import pandas as pd
import streamlit as st

st.title("🔍 Kontroll av kolumner i JOB_ADS_RESOURCE")

try:
    conn = snowflake.connector.connect(
        user="KANILLA",
        password="Mihabadi19821982!",
        account="gjdnchx-yb01210",
        warehouse="COMPUTE_WH",
        database="HR_ANALYTICS",
        schema="STAGING",
        role="ACCOUNTADMIN"
    )
    st.success("✅ Anslutning till Snowflake lyckades!")

    query = """
    SHOW COLUMNS IN HR_ANALYTICS.STAGING.JOB_ADS_RESOURCE;
    """

    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    cur.close()

    st.subheader("📋 Kolumner i JOB_ADS_RESOURCE:")
    st.dataframe(df[["column_name", "data_type"]])

except Exception as e:
    st.error(f"❌ Fel: {e}")
finally:
    try:
        conn.close()
    except:
        pass
