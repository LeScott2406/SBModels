import streamlit as st
import pandas as pd
import requests
import io

# Google Sheets direct export link (ensure it's publicly shared!)
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1Rr7Pv4AmxvYaDCuwbz0iMYVv2_jwMgtwcA6gAqR8AoA/export?format=xlsx"


# Load data from Google Sheets with caching
@st.cache_data(show_spinner="Loading data...")
def load_data():
    try:
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()

        # Check for invalid HTML response (Google login page, etc.)
        if "html" in response.headers.get("Content-Type", "").lower():
            raise ValueError("Google Sheets response is not a valid Excel file. Check sharing permissions.")

        # Read Excel directly from bytes
        df = pd.read_excel(io.BytesIO(response.content))
        df.fillna(0, inplace=True)
        return df

    except Exception as e:
        st.error(f"⚠️ Error loading data from Google Sheets: {e}")
        return pd.DataFrame()  # Return empty DataFrame

# Load the data
data = load_data()
if data.empty:
    st.warning("No data available. Please check the source.")
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

# Role filter including your new models
roles = [
    "Dominant Defender Rank", "Ball Playing Defender Rank", "Defensive Fullback Rank",
    "Attacking Fullback Rank", "Holding Midfielder Rank", "Ball Progressor Rank",
    "Number 10 Rank", "Box Crasher Rank", "Half Space Creator Rank", "Zone Mover Rank",
    "Inverted Winger Rank", "Creative Winger Rank", "Advanced Striker Rank",
    "Physical Striker Rank", "Creative Striker Rank", "Game Breaker Rank",
    "Flyer Rank", "Disruptor Rank", "Ground Eaters Rank",
]
selected_role = st.sidebar.selectbox("Select Role", roles)

# Apply filters
filtered_data = data[
    (data["Age"].between(age_range[0], age_range[1])) &
    (data["Usage"].between(usage_range[0], usage_range[1])) &
    ((data["Position"].isin(positions)) if "All" not in positions else True) &
    ((data["League"].isin(league)) if "All" not in league else True)
]

# Determine Best Role based on max ZScore per position
def best_role(row):
    position_roles = {
        "Defender": ["Dominant Defender Rank", "Ball Playing Defender Rank", "Disruptor Rank", "Ground Eaters Rank"],
        "Fullback": ["Defensive Fullback Rank", "Attacking Fullback Rank", "Zone Mover Rank"],
        "Midfielder": [
            "Holding Midfielder Rank", "Ball Progressor Rank", "Number 10 Rank", "Box Crasher Rank",
            "Half Space Creator Rank", "Zone Mover Rank", "Game Breaker Rank", "Disruptor Rank", "Ground Eaters Rank"
        ],
        "Winger": ["Half Space Creator Rank", "Inverted Winger Rank", "Creative Winger Rank", "Zone Mover Rank", "Game Breaker Rank", "Flyer Rank"],
        "Striker": ["Advanced Striker Rank", "Physical Striker Rank", "Creative Striker Rank", "Game Breaker Rank"]
    }

    roles_for_position = position_roles.get(row["Position"], [])
    if not roles_for_position:
        return "Unknown"
    return max(roles_for_position, key=lambda role: row.get(role, 0))

filtered_data["Best Role"] = filtered_data.apply(best_role, axis=1)

# Display Data
st.title("SB Player Models")
st.write("### Filtered Players")

st.dataframe(
    filtered_data[
        ["Name", "Team", "Age", "Usage", "Position", selected_role, "Best Role",
         "Prevention Rank", "Possession Rank", "Progression Rank",
         "Penetration Rank", "Production Rank", "Pressure Rank"]
    ]
)
