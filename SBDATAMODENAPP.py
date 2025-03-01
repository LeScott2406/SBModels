import streamlit as st
import pandas as pd
import requests
import io

# Function to load data
@st.cache_data
def load_data():
    file_url = "https://github.com/LeScott2406/SBModels/raw/refs/heads/main/Updated_Data_With_Models_and_Percentiles_Optimized_v4.xlsx"
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        file_content = io.BytesIO(response.content)
        data = pd.read_excel(file_content, engine="openpyxl")
        data.fillna(0, inplace=True)
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data
data = load_data()

# If data failed to load, stop execution
if data is None:
    st.stop()

# Sidebar Filters
st.sidebar.header("Filters")

# Age filter
if "Age" in data.columns and not data["Age"].isnull().all():
    age_min, age_max = int(data["Age"].min()), int(data["Age"].max())
    age_range = st.sidebar.slider("Select Age Range", min_value=age_min, max_value=age_max, value=(age_min, age_max))
else:
    age_range = (0, 100)  # Default safe range

# Usage filter
if "Usage" in data.columns and not data["Usage"].isnull().all():
    usage_min, usage_max = float(data["Usage"].min()), float(data["Usage"].max())
    usage_range = st.sidebar.slider("Select Usage Range", min_value=usage_min, max_value=usage_max, value=(usage_min, usage_max))
else:
    usage_range = (0.0, 100.0)

# Height filter (starts from 0)
if "Height" in data.columns and not data["Height"].isnull().all():
    height_min, height_max = float(data["Height"].min()), float(data["Height"].max())
    height_range = st.sidebar.slider("Select Height Range (cm)", min_value=height_min, max_value=height_max, value=(height_min, height_max))
else:
    height_range = (0.0, 250.0)  # Default range

# Position filter
position_options = data["Position"].dropna().unique().tolist()
position_options.insert(0, "All")
positions = st.sidebar.multiselect("Select Positions", options=position_options, default=position_options)

# League filter
league_options = data["League"].dropna().unique().tolist()
league_options.insert(0, "All")
league = st.sidebar.multiselect("Select League", options=league_options, default=league_options)

# Role filter
roles = ["Dominant Defender Percentile", "Ball Playing Defender Percentile", "Defensive Fullback Percentile", "Attacking Fullback Percentile", 
         "Holding Midfielder Percentile", "Ball Progressor Percentile", "Number 10 Percentile", "Box Crasher Percentile", "Half Space Creator Percentile", "Zone Mover Percentile",
         "Inverted Winger Percentile", "Creative Winger Percentile", "Advanced Striker Percentile", "Physical Striker Percentile", "Creative Striker Percentile", "Game Breaker Percentile"]

selected_role = st.sidebar.selectbox("Select Role", roles)

# Apply filters
filtered_data = data[
    (data["Age"].between(age_range[0], age_range[1])) &
    (data["Usage"].between(usage_range[0], usage_range[1])) &
    (data["Height"].between(height_range[0], height_range[1])) &
    ((data["Position"].isin(positions)) if "All" not in positions else True) &
    ((data["League"].isin(league)) if "All" not in league else True)
]

# Determine Best Role
def best_role(row):
    position_roles = {
        "Defender": ["Dominant Defender Percentile", "Ball Playing Defender Percentile"],
        "Fullback": ["Defensive Fullback Percentile", "Attacking Fullback Percentile", "Zone Mover"],
        "Midfielder": ["Holding Midfielder Percentile", "Ball Progressor Percentile", 
                       "Number 10 Percentile", "Box Crasher Percentile", "Half Space Creator Percentile", "Zone Mover", "Game Breaker"],
        "Winger": ["Half Space Creator Percentile", "Inverted Winger Percentile", "Creative Winger Percentile", "Zone Mover", "Game Breaker"],
        "Striker": ["Advanced Striker Percentile", "Physical Striker Percentile", "Creative Striker Percentile", "Game Breaker"],
    }
    for pos, roles in position_roles.items():
        if row["Position"] in pos:
            return max(roles, key=lambda role: row.get(role, 0))
    return "Unknown"

filtered_data["Best Role"] = filtered_data.apply(best_role, axis=1)

# Display Data
st.title("SB Player Models")
st.write("### Filtered Players")

st.dataframe(filtered_data[["Name", "Team", "Age", "Usage", "Height", "Position", selected_role, "Best Role"]])
