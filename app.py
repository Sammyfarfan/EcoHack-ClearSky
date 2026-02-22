import streamlit as st
import pandas as pd
import ast
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="Chelsea Air Quality", layout="wide")

# ----------------------------
# Data loaders
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/sensor_data.csv")
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"], errors="coerce")
    df["pm25"] = pd.to_numeric(df["pm25"], errors="coerce")

    # Parse geo dict (stored as string)
    df["geo"] = df["geo"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df["lat"] = df["geo"].apply(lambda d: d.get("lat") if isinstance(d, dict) else None)
    df["lon"] = df["geo"].apply(lambda d: d.get("lon") if isinstance(d, dict) else None)

    return df

@st.cache_data
def load_sites():
    sites = pd.read_csv("data/Chelsea sensor list.csv")
    sites["ID"] = sites["ID"].astype(str).str.strip()
    return sites

# ----------------------------
# Helpers
# ----------------------------
def pm25_category(x):
    if pd.isna(x): return "No data"
    if x <= 12: return "Good"
    if x <= 35.4: return "Moderate"
    if x <= 55.4: return "Unhealthy (Sensitive Groups)"
    if x <= 150.4: return "Unhealthy"
    return "Very Unhealthy"

def color_for(cat):
    return {
        "Good": [0, 200, 0, 200],
        "Moderate": [255, 215, 0, 200],
        "Unhealthy (Sensitive Groups)": [255, 140, 0, 200],
        "Unhealthy": [255, 0, 0, 200],
        "Very Unhealthy": [128, 0, 128, 200],
        "No data": [120, 120, 120, 120],
    }[cat]

def advice(cat):
    return {
        "Good": "Great time to be outside.",
        "Moderate": "Most people are fine. If you have asthma, take breaks.",
        "Unhealthy (Sensitive Groups)": "If you have asthma or heart conditions, limit outdoor activity.",
        "Unhealthy": "Limit outdoor time. Consider staying indoors.",
        "Very Unhealthy": "Avoid outdoor activity. Stay indoors if possible.",
        "No data": "No recent reading available.",
    }[cat]

# ----------------------------
# UI
# ----------------------------
st.title("Chelsea Air Quality — Easy View")

# Refresh button
if st.button("Refresh latest readings"):
    st.cache_data.clear()
    st.rerun()

df = load_data()
sites = load_sites()

# Latest reading per sensor
latest = (
    df.sort_values("timestamp_local")
      .groupby("sn", as_index=False)
      .tail(1)
      .reset_index(drop=True)
)

# Join human-friendly locations
latest = latest.merge(
    sites[["ID", "Location Description"]],
    left_on="sn", right_on="ID", how="left"
)

latest["label"] = latest["Location Description"].fillna(latest["sn"])
latest["category"] = latest["pm25"].apply(pm25_category)
latest["color"] = latest["category"].apply(color_for)

# Overall Chelsea status (mean PM2.5)
overall_pm = latest["pm25"].mean()
overall_cat = pm25_category(overall_pm)
st.info(f"Overall Chelsea right now: {overall_cat} (Avg PM2.5: {overall_pm:.1f} µg/m³)")

# Last-hour change (uses last 2 datapoints per sensor)
recent = (
    df.sort_values("timestamp_local")
      .groupby("sn")
      .tail(2)
      .dropna(subset=["pm25"])
)

def change_last_two(group):
    if len(group) < 2:
        return pd.Series({"change": 0.0})
    return pd.Series({"change": group["pm25"].iloc[-1] - group["pm25"].iloc[0]})

change_df = recent.groupby("sn").apply(change_last_two).reset_index()
latest = latest.merge(change_df, on="sn", how="left")
latest["change"] = latest["change"].fillna(0.0)

# Biggest improvement banner (most negative change)
improved = latest.sort_values("change").iloc[0]
st.success(f"Biggest improvement (last two readings): {improved['label']} ({improved['change']:.1f} µg/m³)")

# Location selector (search by typing)
selected_label = st.selectbox(
    "Search or choose a location",
    sorted(latest["label"].unique())
)
selected = latest[latest["label"] == selected_label].iloc[0]

left, right = st.columns([1, 2])

with left:
    st.markdown("## Right now")
    st.markdown(
        f"<h1 style='font-size:60px; margin:0'>{selected['category']}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"### PM2.5: **{selected['pm25']:.1f} µg/m³**" if pd.notna(selected["pm25"]) else "### PM2.5: **No data**"
    )
    st.markdown(
        f"### Updated: **{selected['timestamp_local'].strftime('%I:%M %p')}**" if pd.notna(selected["timestamp_local"]) else "### Updated: Unknown"
    )
    st.markdown("### What should I do?")
    st.markdown(f"**{advice(selected['category'])}**")

    st.markdown("---")
    st.markdown("### Highest PM2.5 right now")
    hotspots = latest.sort_values("pm25", ascending=False).head(5)[["label", "pm25", "category", "timestamp_local"]]
    st.dataframe(hotspots, use_container_width=True, hide_index=True)

with right:
    map_df = latest.dropna(subset=["lat", "lon"]).copy()

    # Make circle size reflect pollution (clamp to keep it readable)
    # If pm25 is missing, size defaults small
    map_df["radius"] = (map_df["pm25"].fillna(1).clip(lower=1, upper=80) * 10)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
    )

    view = pdk.ViewState(
        latitude=float(map_df["lat"].mean()),
        longitude=float(map_df["lon"].mean()),
        zoom=13
    )

    tooltip = {
        "html": "<b>{label}</b><br/>PM2.5: {pm25} µg/m³<br/>{category}<br/>Updated: {timestamp_local}",
        "style": {"backgroundColor": "black", "color": "white", "fontSize": "14px"}
    }

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip))

    st.markdown("### Color Guide")
    st.markdown("""
🟢 **Good** (0–12)  
🟡 **Moderate** (12–35.4)  
🟠 **Unhealthy for Sensitive Groups** (35.4–55.4)  
🔴 **Unhealthy** (55.4–150.4)  
🟣 **Very Unhealthy** (150.4+)  
""")

st.markdown("---")
st.markdown("## 24-Hour Trend")

sensor = selected["sn"]
hist = df[df["sn"] == sensor].sort_values("timestamp_local")

if hist["timestamp_local"].notna().any():
    last_time = hist["timestamp_local"].max()
    hist = hist[hist["timestamp_local"] >= last_time - pd.Timedelta(hours=24)]

fig = px.line(hist, x="timestamp_local", y="pm25", title=f"PM2.5 — {selected_label}")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Data Transparency & Limits")
st.markdown("""
- Data comes from community air sensors (QuantAQ iSUPER).
- Low-cost sensors may drift; readings may have gaps.
- We show the most recent reading per location, plus a simple 24-hour trend.
- “Biggest improvement” uses the last two readings available per sensor (may not be exactly 60 minutes).
""")