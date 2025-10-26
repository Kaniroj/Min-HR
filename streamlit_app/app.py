import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------------------------------------------
# 🧭 SIDKONFIGURATION
# ---------------------------------------------------
st.set_page_config(page_title="Job Ads Dashboard", layout="wide")
st.title("📊 Job Ads Dashboard (Min-HR)")

# ---------------------------------------------------
# ❄️ SNOWFLAKE CONNECTION
# ---------------------------------------------------
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        user="KANILLA",
        password="Mihabadi19821982!",
        account="gjdnchx-yb01210",
        warehouse="COMPUTE_WH",
        database="HR_ANALYTICS",
        schema="TRANSFORMED",
        role="ACCOUNTADMIN"
    )

conn = init_connection()

# ---------------------------------------------------
# 📥 DATA FETCH FUNKTION
# ---------------------------------------------------
@st.cache_data(ttl=600)
def load_data(query):
    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    cur.close()
    return df

# ---------------------------------------------------
# 🔹 LADDA MODELLER FRÅN DBT
# ---------------------------------------------------
summary_query = "SELECT * FROM TRANSFORMED_MARTS.JOB_ADS_SUMMARY;"
employers_query = "SELECT * FROM TRANSFORMED_MARTS.EMPLOYERS_TOP;"
regional_query = "SELECT * FROM TRANSFORMED_STAGING.JOB_ADS_STAGING;"  # För kartan

job_summary = load_data(summary_query)
top_employers = load_data(employers_query)
regional_data = load_data(regional_query)

# ---------------------------------------------------
# 📝 BESKRIVNING
# ---------------------------------------------------
st.markdown("""
<div style="background-color:#2c3e50; padding:15px; border-radius:8px; 
            max-width:900px; margin-bottom:20px; color:#ffffff;">
<p style="font-size:16px; line-height:1.6;">
Den här dashboarden visar en översikt över jobbannonser baserat på data i Snowflake.
Du kan se antal annonser per yrkesområde, vilka arbetsgivare som annonserar mest, 
och hur annonserna är fördelade över Sveriges regioner på kartan nedan.
</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# 📊 DASHBOARD-LAYOUT (flikar)
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Job Ads Summary", "🏢 Top Employers", "🗺️ Karta över Sverige"])

# =====================================================
# 📈 TAB 1: JOB ADS SUMMARY
# =====================================================
with tab1:
    st.subheader("Antal annonser per yrkesområde")

    col1, col2, col3 = st.columns(3)
    col1.metric("Totalt antal annonser", int(job_summary["JOB_COUNT"].sum()))
    col2.metric("Unika yrkesområden", job_summary["OCCUPATION_FIELD"].nunique())
    col3.metric("Data uppdaterad", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))

    st.dataframe(job_summary, use_container_width=True)

    fig = px.bar(
        job_summary.sort_values("JOB_COUNT", ascending=False),
        x="OCCUPATION_FIELD",
        y="JOB_COUNT",
        text="JOB_COUNT",
        title="📊 Antal annonser per yrkesområde",
        color="JOB_COUNT",
        color_continuous_scale="Blues"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title=None,
        yaxis_title="Antal annonser",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 🏢 TAB 2: TOP EMPLOYERS
# =====================================================
with tab2:
    st.subheader("Företag som annonserar mest")

    col1, col2 = st.columns(2)
    st.write(top_employers.columns)
    col1.metric("Antal arbetsgivare", top_employers["EMPLOYER"].nunique())
    col2.metric("Totalt antal annonser", int(top_employers["TOTAL_ADS"].sum()))

    st.dataframe(top_employers, use_container_width=True)

    fig2 = px.bar(
        top_employers.sort_values("TOTAL_ADS", ascending=True).tail(15),
        x="TOTAL_ADS",
        y="EMPLOYER",
        orientation="h",
        text="TOTAL_ADS",
        title="🏢 Topp arbetsgivare efter antal annonser",
        color="TOTAL_ADS",
        color_continuous_scale="Greens"
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        xaxis_title="Antal annonser",
        yaxis_title=None,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 🗺️ TAB 3: KARTA ÖVER SVERIGE
# =====================================================
with tab3:
    st.subheader("Sverigekarta över jobbannonser")

    # ---- Hämta geojson för Sveriges regioner ----
    @st.cache_data
    def load_geojson():
        url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/SWE.geo.json"
        return requests.get(url).json()

    geojson = load_geojson()

    # ---- Förbered data ----
    regional_data = regional_data[["WORKPLACE_REGION", "OCCUPATION_FIELD", "VACANCIES"]]

    # Filter 1: Yrkesområde
    selected_field = st.selectbox(
        "🗂️ Välj yrkesområde (eller visa alla)",
        ["Alla"] + sorted(regional_data["OCCUPATION_FIELD"].dropna().unique())
    )

    if selected_field != "Alla":
        filtered = regional_data[regional_data["OCCUPATION_FIELD"] == selected_field]
    else:
        filtered = regional_data.copy()

    # Filter 2: Region (för zoom)
    regions = sorted(filtered["WORKPLACE_REGION"].dropna().unique())
    selected_region = st.selectbox("📍 Välj region (eller visa hela Sverige)", ["Alla"] + regions)

    # Summera antal jobb per region
    regional_summary = (
        filtered.groupby("WORKPLACE_REGION")["VACANCIES"]
        .sum()
        .reset_index()
        .rename(columns={"VACANCIES": "TOTAL_JOBS"})
    )

    # Hitta vanligaste yrkesområde per region
    top_field = (
        filtered.groupby(["WORKPLACE_REGION", "OCCUPATION_FIELD"])["VACANCIES"]
        .sum()
        .reset_index()
        .sort_values(["WORKPLACE_REGION", "VACANCIES"], ascending=[True, False])
    )
    top_field = top_field.groupby("WORKPLACE_REGION").first().reset_index()
    top_field = top_field.rename(columns={"OCCUPATION_FIELD": "TOP_FIELD"})

    # Slå ihop
    regional_summary = pd.merge(regional_summary, top_field, on="WORKPLACE_REGION", how="left")

    # ---- Koordinater för regionerna ----
    region_coords = {
        "Stockholms län": [59.3, 18.0],
        "Västra Götalands län": [57.7, 12.0],
        "Skåne län": [55.9, 13.6],
        "Uppsala län": [59.9, 17.6],
        "Östergötlands län": [58.4, 15.6],
        "Jönköpings län": [57.8, 14.2],
        "Norrbottens län": [67.9, 21.6],
        "Västerbottens län": [64.5, 18.7],
        "Södermanlands län": [59.0, 16.5],
        "Hallands län": [56.7, 12.8],
        "Värmlands län": [59.6, 13.0],
        "Örebro län": [59.3, 15.3],
        "Dalarnas län": [60.6, 14.7],
        "Västmanlands län": [59.6, 16.2],
        "Gävleborgs län": [61.3, 16.3],
        "Kronobergs län": [56.8, 14.7],
        "Kalmar län": [56.7, 16.3],
        "Gotlands län": [57.5, 18.5],
        "Blekinge län": [56.2, 15.6],
        "Västernorrlands län": [62.9, 17.9],
        "Jämtlands län": [63.3, 14.2],
    }

    if selected_region != "Alla" and selected_region in region_coords:
        center_lat, center_lon = region_coords[selected_region]
        zoom_level = 6
    else:
        center_lat, center_lon = 62.0, 15.0
        zoom_level = 4

    # ---- Rita karta ----
    fig3 = px.choropleth_mapbox(
        regional_summary,
        geojson=geojson,
        locations="WORKPLACE_REGION",
        featureidkey="properties.name",
        color="TOTAL_JOBS",
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        title=f"Antal annonser per region{' för ' + selected_field if selected_field != 'Alla' else ''}",
        hover_name="WORKPLACE_REGION",
        hover_data={"TOTAL_JOBS": True, "TOP_FIELD": True},
        zoom=zoom_level,
        center={"lat": center_lat, "lon": center_lon},
        opacity=0.75
    )

    # ---- Lägg till siffror direkt på kartan ----
    text_markers = go.Scattermapbox(
        lat=[region_coords[r][0] for r in regional_summary["WORKPLACE_REGION"] if r in region_coords],
        lon=[region_coords[r][1] for r in regional_summary["WORKPLACE_REGION"] if r in region_coords],
        mode="text",
        text=[f"{int(v):,}" for v in regional_summary["TOTAL_JOBS"]],
        textfont=dict(size=12, color="black", family="Arial Black"),
        textposition="top center",
        showlegend=False
    )

    fig3.add_trace(text_markers)

    fig3.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar=dict(title="Antal jobb")
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <p style="font-size:14px; color:gray;">
    🗺️ Kartan visar antal jobbannonser per region baserat på data i Snowflake.  
    Hovra för att se vanligaste yrkesområde.  
    Siffrorna på kartan visar totalt antal annonser per region.  
    Välj en region för att zooma in.
    </p>
    """, unsafe_allow_html=True)
