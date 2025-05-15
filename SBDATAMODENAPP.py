import streamlit as st
import pandas as pd
import requests
import io

# Google Sheets direct export link (ensure it's publicly shared!)
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1Rr7Pv4AmxvYaDCuwbz0iMYVv2_jwMgtwcA6gAqR8AoA/export?format=csv&gid=2066338457"

# Load data from Google Sheets with better error handling
@st.cache_data(show_spinner="Loading data...")
def load_data():
    try:
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()

        # Check for invalid HTML response (e.g. Google sign-in page)
        if "html" in response.headers.get("Content-Type", "").lower():
            raise ValueError("Google Sheets response is not a valid CSV file. Check sharing permissions.")

        file_content = io.BytesIO(response.content)
        df = pd.read_csv(file_content)
        df.fillna(0, inplace=True)
        return df

    except Exception as e:
        st.error(f"⚠️ Error loading data from Google Sheets: {e}")
        return pd.DataFrame()  # Return empty DataFrame instead of None

# Load data
data = load_data()
data = load_data()

# If data is empty, stop execution safely
if data.empty:
    st.warning("No data available to display. Please check the source or try again later.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filters")

# Age filter
if "Age" in data.columns and not data["Age"].isnull().all():
    age_min, age_max = int(data["Age"].min()), int(data["Age"].max())
    age_range = st.sidebar.slider("Select Age Range", min_value=age_min, max_value=age_max, value=(age_min, age_max))
else:
    age_range = (0, 100)

# Usage filter
if "Usage" in data.columns and not data["Usage"].isnull().all():
    usage_min, usage_max = float(data["Usage"].min()), float(data["Usage"].max())
    usage_range = st.sidebar.slider("Select Usage Range", min_value=usage_min, max_value=usage_max, value=(usage_min, usage_max))
else:
    usage_range = (0.0, 100.0)

# Position filter
position_options = data["Position"].dropna().unique().tolist()
position_options.insert(0, "All")
positions = st.sidebar.multiselect("Select Positions", options=position_options, default=position_options)

# League filter
league_options = data["League"].dropna().unique().tolist()
league_options.insert(0, "All")
league = st.sidebar.multiselect("Select League", options=league_options, default=league_options)

# Role filter
roles = [
    "Dominant Defender Percentile", "Ball Playing Defender Percentile", "Defensive Fullback Percentile", 
    "Attacking Fullback Percentile", "Holding Midfielder Percentile", "Ball Progressor Percentile", 
    "Number 10 Percentile", "Box Crasher Percentile", "Half Space Creator Percentile", "Zone Mover Percentile",
    "Inverted Winger Percentile", "Creative Winger Percentile", "Advanced Striker Percentile", 
    "Physical Striker Percentile", "Creative Striker Percentile", "Game Breaker Percentile", 
    "Flyer Percentile", "Disruptor Percentile"
]
selected_role = st.sidebar.selectbox("Select Role", roles)

# Apply filters
filtered_data = data[
    (data["Age"].between(age_range[0], age_range[1])) &
    (data["Usage"].between(usage_range[0], usage_range[1])) &
   ((data["Position"].isin(positions)) if "All" not in positions else True) &
    ((data["League"].isin(league)) if "All" not in league else True)
]

# Determine Best Role
def best_role(row):
    position_roles = {
        "Defender": ["Dominant Defender Percentile", "Ball Playing Defender Percentile"],
        "Fullback": ["Defensive Fullback Percentile", "Attacking Fullback Percentile", "Zone Mover", "Flyer"],
        "Midfielder": [
            "Holding Midfielder Percentile", "Ball Progressor Percentile", 
            "Number 10 Percentile", "Box Crasher Percentile", "Half Space Creator Percentile", 
            "Zone Mover", "Game Breaker", "Disruptor"
        ],
        "Winger": [
            "Half Space Creator Percentile", "Inverted Winger Percentile", 
            "Creative Winger Percentile", "Zone Mover", "Game Breaker", "Flyer"
        ],
        "Striker": [
            "Advanced Striker Percentile", "Physical Striker Percentile", 
            "Creative Striker Percentile", "Game Breaker"
        ],
    }
    for pos, roles in position_roles.items():
        if row["Position"] in pos:
            return max(roles, key=lambda role: row.get(role, 0))
    return "Unknown"

filtered_data["Best Role"] = filtered_data.apply(best_role, axis=1)

# Display Data
st.title("SB Player Models")
st.write("### Filtered Players")

st.dataframe(filtered_data[["Name", "Team", "Age", "Usage", "Position", selected_role, "Best Role"]])
