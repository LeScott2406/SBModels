#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests

@st.cache_data
def load_data():
    file_url = 'https://github.com/LeScott2406/SBModels/raw/refs/heads/main/Updated_Data_With_Models_and_Percentiles_Optimized_v4.xlsx'
    response = requests.get(file_url)
    file_content = io.BytesIO(response.content)
    data = pd.read_excel(file_content)
    data.fillna(0, inplace=True)
    return data

# Load data
data = load_data()

# Streamlit App Header
st.title('SB Player Models')

# Left Sidebar for Filters
st.sidebar.header('Filters')

# Age Filter
age_min, age_max = data['Age'].min(), data['Age'].max()
age_range = st.sidebar.slider('Select Age Range', min_value=age_min, max_value=age_max, value=(age_min, age_max))

# Usage Filter
usage_min, usage_max = data['Usage'].min(), data['Usage'].max()
usage_range = st.sidebar.slider('Select Usage Range', min_value=usage_min, max_value=usage_max, value=(usage_min, usage_max))

# Position Filter
positions = st.sidebar.multiselect('Select Positions', options=data['Position'].unique().tolist(), default=data['Position'].unique().tolist() + ['All'])

# Competition Filter
competitions = st.sidebar.multiselect('Select Competitions', options=data['Competition'].unique().tolist(), default=data['Competition'].unique().tolist() + ['All'])

# Team Filter (Dependent on Competition)
selected_competitions = [comp for comp in competitions if comp != 'All']
if selected_competitions:
    teams_in_competition = data[data['Competition'].isin(selected_competitions)]['Team'].unique()
    teams = st.sidebar.multiselect('Select Teams', options=teams_in_competition.tolist(), default=teams_in_competition.tolist() + ['All'])
else:
    teams = st.sidebar.multiselect('Select Teams', options=data['Team'].unique().tolist(), default=data['Team'].unique().tolist() + ['All'])

# Role Filter
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

# Filter Data Based on User Selections
filtered_data = data[
    (data['Age'] >= age_range[0]) & 
    (data['Age'] <= age_range[1]) & 
    (data['Usage'] >= usage_range[0]) & 
    (data['Usage'] <= usage_range[1])
]

# Apply Position, Competition, and Team Filters
if 'All' not in positions:
    filtered_data = filtered_data[filtered_data['Position'].isin(positions)]
if 'All' not in competitions:
    filtered_data = filtered_data[filtered_data['Competition'].isin(competitions)]
if 'All' not in teams:
    filtered_data = filtered_data[filtered_data['Team'].isin(teams)]

# Calculate Best Role Based on Position
def get_best_role(row):
    position = row['Position']
    if position == 'Defender':
        return max(row['Dominant Defender Percentile'], row['Ball Playing Defender Percentile'])
    elif position == 'Fullback':
        return max(row['Defensive Fullback Percentile'], row['Attacking Fullback Percentile'])
    elif position == 'Midfielder':
        return max(row['Holding Midfielder Percentile'], row['Ball Progressor Percentile'], 
                   row['Number 10 Percentile'], row['Box Crasher Percentile'], row['Half Space Creator Percentile'])
    elif position == 'Winger':
        return max(row['Half Space Creator Percentile'], row['Inverted Winger Percentile'], row['Creative Winger Percentile'])
    elif position == 'Striker':
        return max(row['Advanced Striker Percentile'], row['Physical Striker Percentile'], row['Creative Striker Percentile'])
    return None

# Apply the Best Role calculation
filtered_data['Best Role'] = filtered_data.apply(get_best_role, axis=1)

# Display Data in Table
columns = ['Name', 'Team', 'Age', 'Usage', 'Position', role, 'Best Role']
st.dataframe(filtered_data[columns])


