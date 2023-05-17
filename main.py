import streamlit as st
from modules import data_preprocessing
from modules import data_processing
from modules.data_processing import load_data, filter_data, compute_team_stats, compute_explosive_play_stats, compute_down_stats
import matplotlib.pyplot as plt
import pandas as pd
import os
from streamlit_lottie import st_lottie
import json

def main():
    st.markdown("<h1 style='text-align: center;'>Football Statistics</h1>", unsafe_allow_html=True)

    # Read the lottie JSON file
    with open('football_v2.json', 'r') as f:
        lottie_dict = json.load(f)
    
    left_co, cent_co,last_co = st.columns(3)
    with cent_co:
        st_lottie(lottie_dict, width=200)

    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a file", type="csv")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file is not None:

        st.empty()  # This line will clear the previous elements (like the lottie animation) from the page
        
        # Save the uploaded file to a temporary location
        input_path = './data/' + uploaded_file.name
        output_path = './data/preprocessed_' + uploaded_file.name
        with open(input_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        # Preprocess the uploaded file
        data_preprocessing.preprocess_data(input_path, output_path)

        # Load the data
        data = pd.read_csv(output_path)
      
        # Display the team stats
        st.header("Team Statistics")
        selected_team = st.selectbox("Select a team", data['poss'].unique(), key='team_select_1')
        team_stats = data_processing.compute_team_stats(data, selected_team)
        st.table(pd.DataFrame(team_stats, index=[selected_team]).T)
    
    
        # Get the explosive play yard threshold from the user
        st.header("Explosive Plays")
        explosive_play_yards = st.number_input("Enter the minimum number of yards for a play to be considered explosive", min_value=1, value=15)
    
        # Compute the explosive play stats, transpose the DataFrame, and display it
        explosive_play_stats_df = data_processing.compute_explosive_play_stats(data, explosive_play_yards).transpose()
        st.dataframe(explosive_play_stats_df)
    
        # Add a selector for the team
        st.header("Breakdown by Down")
        unique_teams = list(data['poss'].unique())
        selected_team2 = st.selectbox("Select a team", unique_teams, key='team_select_2')
    
        # Compute and display the down stats for the selected team
        down_stats_df = data_processing.compute_down_stats(data, selected_team2).transpose()
        st.dataframe(down_stats_df)
      
        # Sidebar for filtering
        st.sidebar.header("Filter options")
    
        # Collect filter options
        unique_poss = list(data['poss'].unique())
        selected_poss = st.sidebar.multiselect('Select teams', unique_poss, unique_poss)
    
        unique_down = list(data['down'].unique())
        selected_down = st.sidebar.selectbox('Select down', unique_down)
    
        unique_playtype = list(data['playtype'].unique())
        selected_playtype = st.sidebar.multiselect('Select playtype', unique_playtype, unique_playtype)
    
        min_yards, max_yards = int(data['yards'].min()), int(data['yards'].max())
        selected_yards = st.sidebar.slider('Select a range of yards', min_yards, max_yards, (min_yards, max_yards))
    
        # Filter the data based on user selections
        filtered_data = data[
            (data['poss'].isin(selected_poss)) &
            (data['down'] == selected_down) &
            (data['yards'] >= selected_yards[0]) & (data['yards'] <= selected_yards[1]) &
            (data['playtype'].isin(selected_playtype))
        ]
    
        # Display filtered data
        st.header("Filtered Data")
        st.dataframe(filtered_data)
    
        # Generate the plot
        if st.sidebar.button("Generate Plot"):
            st.header("Total Yards Gained by Each Team")
            plot_data = filtered_data.groupby(['poss', 'playtype'])['yards'].sum().sort_values()
            plot_data.unstack().plot(kind='bar')
            plt.xlabel('Team')
            plt.ylabel('Total Yards')
            plt.title('Total Yards Gained by Each Team')
            st.pyplot(plt)

if __name__ == "__main__":
    main()
