import pandas as pd

def load_data():
    return pd.read_csv('data/avemaria.csv')

def filter_data(data, selected_teams, selected_downs, selected_playtypes, selected_yards_range):
    return data[
        (data['poss'].isin(selected_teams)) & 
        (data['down'] == selected_downs) & 
        (data['yards'] >= selected_yards_range[0]) & (data['yards'] <= selected_yards_range[1]) &
  	    (data['playtype'].isin(selected_playtypes))
    ]

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


def compute_explosive_play_stats(data, explosive_play_yards=15):
    # Initialize an empty list to store the stats for each team
    explosive_play_stats = []

    # Loop over each unique team
    for team in data['poss'].unique():
        # Filter the data for the current team
        team_data = data[data['poss'].str.lower() == team.lower()]

        # Compute the total yards for the team
        total_yards = team_data['yards'].sum()

        # Filter the data for explosive plays
        explosive_data = team_data[team_data['yards'] >= explosive_play_yards]

        # Compute the required statistics
        total_explosive_plays = explosive_data.shape[0]
        explosive_passes = explosive_data[explosive_data['playtype'].str.lower() == 'pass'].shape[0]
        explosive_rushes = explosive_data[explosive_data['playtype'].str.lower() == 'rush'].shape[0]
        explosive_tds = explosive_data[explosive_data['outcome'].str.lower() == 'touchdown'].shape[0]
        total_yards_from_ex = explosive_data['yards'].sum()
        avg_yards_per_ex = total_yards_from_ex / total_explosive_plays if total_explosive_plays > 0 else 0
        perc_of_total_yards_from_ex = (total_yards_from_ex / total_yards) * 100 if total_yards > 0 else 0

        # Add the stats for the current team to the list
        explosive_play_stats.append([
            team,
            total_explosive_plays,
            explosive_passes,
            explosive_rushes,
            explosive_tds,
            total_yards_from_ex,
            avg_yards_per_ex,
            perc_of_total_yards_from_ex
        ])

    # Convert the list to a DataFrame and add column names
    explosive_play_stats_df = pd.DataFrame(explosive_play_stats, columns=[
        'Team',
        'Total Explosive Plays',
        'Explosive Passes',
        'Explosive Rushes',
        'Explosive TDs',
        'Total Yards from Ex',
        'Avg Yards per Ex',
        '% of Total Yards from Ex'
    ])

    return explosive_play_stats_df
