import streamlit as st
from modules import data_preprocessing
from modules import data_processing
import matplotlib.pyplot as plt
import pandas as pd
import os


def compute_team_stats(data):
    team_stats = []

    # Loop over each unique team
    for team in data['poss'].unique():
        team_data = data[data['poss'] == team]

        # 1. Total and average yards on first down
        first_down_data = team_data[team_data['down'] == '1st']
        total_yards_first_down = first_down_data['yards'].sum()
        avg_yards_first_down = first_down_data['yards'].mean()

        # 2. Total explosive plays (>= 15 yards), divided into pass and run
        explosive_data = team_data[team_data['yards'] >= 15]
        total_explosive_plays = explosive_data.shape[0]
        explosive_pass_plays = explosive_data[explosive_data['playtype'] == 'Pass'].shape[0]
        explosive_rush_plays = explosive_data[explosive_data['playtype'] == 'Rush'].shape[0]

        # 3. Percentage of plays that are third down
        third_down_data = team_data[team_data['down'] == '3rd']
        total_plays = team_data.shape[0]
        third_down_plays = third_down_data.shape[0]
        third_down_percentage = (third_down_plays / total_plays) * 100 if total_plays > 0 else 0

        # Add to the list of team stats
        team_stats.append([
            team,
            total_yards_first_down,
            avg_yards_first_down,
            total_explosive_plays,
            explosive_pass_plays,
            explosive_rush_plays,
            total_plays,
            third_down_plays,
            third_down_percentage,
        ])

    # Convert to DataFrame and add column names
    team_stats_df = pd.DataFrame(team_stats, columns=[
        'Team',
        'Total Yards 1st Down',
        'Avg Yards 1st Down',
        'Total Explosive Plays',
        'Explosive Pass Plays',
        'Explosive Rush Plays',
        'Total Plays',
        '3rd Down Plays',
        '3rd Down %'
    ])

    return team_stats_df

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
    team_stats_df = compute_team_stats(data)
    st.dataframe(team_stats_df)

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
