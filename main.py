import streamlit as st
from modules import data_preprocessing
from modules import data_processing
from modules.data_processing import compute_team_stats
import matplotlib.pyplot as plt
import pandas as pd
import os


def main():
    # Determine the output path
    output_path = './data/avemaria.csv'
  
    # File upload
    uploaded_file = st.file_uploader("Choose a file", type="csv")
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        input_path = './data/' + uploaded_file.name
        with open(input_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        # Preprocess the uploaded file
        data_preprocessing.preprocess_data(input_path, output_path)

    # Load the data
    data = pd.read_csv(output_path)
    st.write(data)
  
    # Display the team stats
    st.header("Team Statistics")
    team_stats_df = data_processing.compute_team_stats(data)
    st.dataframe(team_stats_df)

    # Get the explosive play yard threshold from the user
    st.header("Explosive Plays")
    explosive_play_yards = st.number_input("Enter the minimum number of yards for a play to be considered explosive", min_value=1, value=15)

    # Compute the explosive play stats and display them
    explosive_play_stats_df = data_processing.compute_explosive_play_stats(data, explosive_play_yards)
    st.dataframe(explosive_play_stats_df)  

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
