import streamlit as st
import pandas as pd
import requests
import io

# Function to load data
@st.cache_data
def load_data():
    file_url = "https://github.com/LeScott2406/SBModels/raw/refs/heads/main/Updated_Data_With_Models_and_Percentiles_Optimized_v4.xlsx"  # Update with actual URL
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raises an error if the request fails
        file_content = io.BytesIO(response.content)
        data = pd.read_excel(file_content, engine="openpyxl")  # Ensure openpyxl is installed
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
age_min, age_max = int(data["Age"].min()), int(data["Age"].max())
age_range = st.sidebar.slider("Select Age Range", min_value=age_min, max_value=age_max, value=(age_min, age_max))

# Usage filter
usage_min, usage_max = float(data["Usage"].min()), float(data["Usage"].max())
usage_range = st.sidebar.slider("Select Usage Range", min_value=usage_min, max_value=usage_max, value=(usage_min, usage_max))

# Position filter (Fix: Added 'All' to the options correctly)
position_options = data["Position"].unique().tolist()  
position_options.insert(0, "All")  # Add 'All' at the start
positions = st.sidebar.multiselect("Select Positions", options=position_options, default=position_options)

# Competition filter
competition_options = data["Competition"].unique().tolist()
competition_options.insert(0, "All")
competitions = st.sidebar.multiselect("Select Competitions", options=competition_options, default=competition_options)

# Team filter (Dynamic based on competition selection)
if "All" in competitions:
    filtered_teams = data["Team"].unique().tolist()
else:
    filtered_teams = data[data["Competition"].isin(competitions)]["Team"].unique().tolist()

filtered_teams.insert(0, "All")
teams = st.sidebar.multiselect("Select Teams", options=filtered_teams, default=filtered_teams)

# Role filter
roles = ["Dominant Defender", "Ball Playing Defender", "Defensive Fullback", "Attacking Fullback", 
         "Holding Midfielder", "Ball Progressor", "Number 10", "Box Crasher", "Half Space Creator", 
         "Inverted Winger", "Creative Winger", "Advanced Striker", "Physical Striker", "Creative Striker"]

selected_role = st.sidebar.selectbox("Select Role", roles)

# Apply filters
filtered_data = data[
    (data["Age"].between(age_range[0], age_range[1])) &
    (data["Usage"].between(usage_range[0], usage_range[1])) &
    ((data["Position"].isin(positions)) if "All" not in positions else True) &
    ((data["Competition"].isin(competitions)) if "All" not in competitions else True) &
    ((data["Team"].isin(teams)) if "All" not in teams else True)
]

# Determine Best Role
def best_role(row):
    position_roles = {
        "Defender": ["Dominant Defender Percentile", "Ball Playing Defender Percentile"],
        "Fullback": ["Defensive Fullback Percentile", "Attacking Fullback Percentile"],
        "Midfielder": ["Holding Midfielder Percentile", "Ball Progressor Percentile", 
                       "Number 10 Percentile", "Box Crasher Percentile", "Half Space Creator Percentile"],
        "Winger": ["Half Space Creator Percentile", "Inverted Winger Percentile", "Creative Winger Percentile"],
        "Striker": ["Advanced Striker Percentile", "Physical Striker Percentile", "Creative Striker Percentile"],
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

