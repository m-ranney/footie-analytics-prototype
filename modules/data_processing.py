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

def compute_team_stats(data, team):
    # Convert the values in the 'poss' column to lowercase
    data['poss'] = data['poss'].str.lower()
    data['playtype'] = data['playtype'].str.lower()
    data['ball_half'] = data['ball_half'].str.lower()
    data['outcome'] = data['outcome'].str.lower()

    team_data = data[data['poss'] == team.lower()]
    
    total_plays = team_data.shape[0]
    pass_plays = team_data[team_data['playtype'] == 'pass'].shape[0]
    rush_plays = team_data[team_data['playtype'] == 'rush'].shape[0]
    
    percent_pass_plays = pass_plays / total_plays if total_plays > 0 else 0
    percent_rush_plays = rush_plays / total_plays if total_plays > 0 else 0

    scores = team_data[team_data['outcome'].isin(['touchdown', 'field goal'])].shape[0]
    total_drives = team_data['drive'].nunique()
    drives_per_score = scores / total_drives if total_drives > 0 else 0

    first_downs = team_data[team_data['down'] == '1st'].shape[0]
    first_downs_per_drive = (first_downs - total_drives) / total_drives if total_drives > 0 else 0
    first_down_rate = (first_downs - total_drives) / total_plays if total_plays > 0 else 0

    redzone_rushes = team_data[(team_data['playtype'] == 'rush') & 
                               (team_data['ball_half'] == 'opponents') & 
                               (team_data['yardline'] <= 20)].shape[0]
    
    redzone_passes = team_data[(team_data['playtype'] == 'pass') & 
                               (team_data['ball_half'] == 'opponents') & 
                               (team_data['yardline'] <= 20)].shape[0]

    total_yards_per_drive = team_data.groupby('drive')['yards'].sum().mean()

    team_stats = {
        'Total Plays': total_plays,
        '% of Pass Plays': percent_pass_plays,
        '% of Rush Plays': percent_rush_plays,
        'Drives per Score': drives_per_score,
        '1st Downs per Drive': first_downs_per_drive,
        '1st Down Rate': first_down_rate,
        'Runs in Red Zone': redzone_rushes,
        'Passes in Red Zone': redzone_passes,
        'Average Yards per Drive': total_yards_per_drive,
    }

    return team_stats
  

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

    # Set the 'Team' column as the index
    explosive_play_stats_df.set_index('Team', inplace=True)

    return explosive_play_stats_df

def compute_down_stats(data, team):
    down_stats = []
  
    # Ensure 'to_go' is numeric
    data['to_go'] = pd.to_numeric(data['to_go'], errors='coerce')

    for down in ['1st', '2nd', '3rd', '4th']:
        down_data = data[(data['poss'] == team) & (data['down'] == down)]

        total_yards = down_data['yards'].sum()

        pass_plays = down_data[down_data['playtype'] == 'Pass']
        num_pass_plays = pass_plays.shape[0]
        total_pass_yards = pass_plays['yards'].sum()

        rush_plays = down_data[down_data['playtype'] == 'Rush']
        num_rush_plays = rush_plays.shape[0]
        total_rush_yards = rush_plays['yards'].sum()

        total_team_yards = data[data['poss'] == team]['yards'].sum()
        percent_yardage = (total_yards / total_team_yards) * 100 if total_team_yards > 0 else 0

        passes_under_5_to_go = pass_plays[pass_plays['to_go'] < 5].shape[0]
        runs_over_5_to_go = rush_plays[rush_plays['to_go'] > 5].shape[0]

        down_stats.append([
            down,
            total_yards,
            num_pass_plays,
            total_pass_yards,
            num_rush_plays,
            total_rush_yards,
            percent_yardage,
            passes_under_5_to_go,
            runs_over_5_to_go
        ])

    down_stats_df = pd.DataFrame(down_stats, columns=[
        'Down',
        'Total Yards Gained',
        'Number of Pass Plays',
        'Total Pass Yards',
        'Number of Rush Plays',
        'Total Rush Yards',
        '% of Yardage Gained',
        'Passes w/ Under 5 to go',
        'Runs w/ Over 5 to go'
    ])

    down_stats_df.set_index('Down', inplace=True)

    return down_stats_df
