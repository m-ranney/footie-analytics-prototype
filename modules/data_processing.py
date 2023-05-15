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
