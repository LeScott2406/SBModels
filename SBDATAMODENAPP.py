#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import requests
import io

# Function to load data from GitHub
@st.cache_data
def load_data():
    file_url = 'https://github.com/LeScott2406/SBModels/raw/refs/heads/main/Updated_Data_With_Models_and_Percentiles_Optimized_v4.xlsx'

    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raises an error if the request fails
        file_content = io.BytesIO(response.content)
        data = pd.read_excel(file_content)
        data.fillna(0, inplace=True)
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load data: {e}")
        return None

# Load data
data = load_data()

# If data failed to load, stop execution
if data is None:
    st.stop()

# Streamlit App Header
st.title('SB Player Models')

# Left Sidebar for Filters
st.sidebar.header('Filters')

# Age Filter
age_min, age_max = int(data['Age'].min()), int(data['Age'].max())
age_range = st.sidebar.slider('Select Age Range', min_value=age_min, max_value=age_max, value=(age_min, age_max))

# Usage Filter
usage_min, usage_max = int(data['Usage'].min()), int(data['Usage'].max())
usage_range = st.sidebar.slider('Select Usage Range', min_value=usage_min, max_value=usage_max, value=(usage_min, usage_max))

# Position Filter
all_positions = data['Position'].unique().tolist()
positions = st.sidebar.multiselect('Select Positions', options=all_positions, default=all_positions)

# Competition Filter
all_competitions = data['Competition'].unique().tolist()
competitions = st.sidebar.multiselect('Select Competitions', options=all_competitions, default=all_competitions)

# Team Filter (Dependent on Competition)
if competitions:
    teams_in_competition = data[data['Competition'].isin(competitions)]['Team'].unique()
    teams = st.sidebar.multiselect('Select Teams', options=teams_in_competition.tolist(), default=teams_in_competition.tolist())
else:
    teams = st.sidebar.multiselect('Select Teams', options=data['Team'].unique().tolist(), default=[])

# Role Filter (Single Selection)
roles = [
    'Dominant Defender Percentile', 'Ball Playing Defender Percentile', 
    'Defensive Fullback Percentile', 'Attacking Fullback Percentile', 
    'Holding Midfielder Percentile', 'Ball Progressor Percentile', 
    'Number 10 Percentile', 'Box Crasher Percentile', 
    'Half Space Creator Percentile', 'Inverted Winger Percentile', 
    'Creative Winger Percentile', 'Advanced Striker Percentile', 
    'Physical Striker Percentile', 'Creative Striker Percentile'
]
role = st.sidebar.selectbox('Select Role', options=roles)

# Apply Filters to Data
filtered_data = data[
    (data['Age'] >= age_range[0]) & 
    (data['Age'] <= age_range[1]) & 
    (data['Usage'] >= usage_range[0]) & 
    (data['Usage'] <= usage_range[1])
]

if positions:
    filtered_data = filtered_data[filtered_data['Position'].isin(positions)]
if competitions:
    filtered_data = filtered_data[filtered_data['Competition'].isin(competitions)]
if teams:
    filtered_data = filtered_data[filtered_data['Team'].isin(teams)]

# Function to Determine Best Role
def get_best_role(row):
    position = row['Position']
    role_categories = {
        'Defender': ['Dominant Defender Percentile', 'Ball Playing Defender Percentile'],
        'Fullback': ['Defensive Fullback Percentile', 'Attacking Fullback Percentile'],
        'Midfielder': ['Holding Midfielder Percentile', 'Ball Progressor Percentile', 
                       'Number 10 Percentile', 'Box Crasher Percentile', 'Half Space Creator Percentile'],
        'Winger': ['Half Space Creator Percentile', 'Inverted Winger Percentile', 'Creative Winger Percentile'],
        'Striker': ['Advanced Striker Percentile', 'Physical Striker Percentile', 'Creative Striker Percentile']
    }

    if position in role_categories:
        best_role = max(role_categories[position], key=lambda r: row.get(r, 0))
        return best_role
    return None

# Apply Best Role Calculation
filtered_data['Best Role'] = filtered_data.apply(get_best_role, axis=1)

# Display Data in Table
columns_to_display = ['Name', 'Team', 'Age', 'Usage', 'Position', role, 'Best Role']
st.dataframe(filtered_data[columns_to_display])
