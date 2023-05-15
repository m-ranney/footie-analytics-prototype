import pandas as pd
import numpy as np
import re
import sqlite3

def preprocess_data(input_path, output_path):
    """
    Preprocesses a football data file.

    Args:
    input_path: str. The path to the input file.
    output_path: str. The path to the output file.

    Returns:
    None.
    """
    df = pd.read_csv(input_path)

    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    df.to_sql('my_table', conn, index=False)
    df.dropna(how='all', inplace=True)
    
    # Add here all the preprocessing steps you've described
    df.dropna(how='all', inplace=True)

    df.columns = ['one', 'two']
    
    # Add a new column called 'half'
    df['half'] = ''

    # Initialize the current half value
    current_half = 1
    
    # Loop through the rows
    for i, row in df.iterrows():
        # If the cell in column 1 contains "Start of 1st Half"
        if "Start of 1st Half" in row['one']:
            current_half = 1
        # If the cell in column 1 contains "Start of 2nd Half"
        elif "Start of 2nd Half" in row['one']:
            current_half = 2

        # Set the 'half' column for this row and all following rows to the current half value
        df.loc[i:, 'half'] = current_half
    
    # Add a new column called 'quarter'
    df['quarter'] = ''
    
    # Initialize the current quarter value
    current_quarter = 1
    
    # Loop through the rows
    for i, row in df.iterrows():
        # Check the value in column 'one' to determine the quarter
        if "Start of 1st Half" in row['one']:
            current_quarter = 1
        elif "Start of Quarter #2" in row['one']:
            current_quarter = 2
        elif "Start of 2nd Half" in row['one']:
            current_quarter = 3
        elif "Start of Quarter #4" in row['one']:
            current_quarter = 4
        
        # Set the 'quarter' column for this row and all following rows to the current quarter value
        df.loc[i:, 'quarter'] = current_quarter
    
    def fill_poss(row):
        match = re.search(r'(.*?) at \d{2}:\d{2}', row['one'])
        if match:
            return match.group(1)
        else:
            return np.nan # return NaN if the pattern is not found
    
    # Apply the function to each row
    df['poss'] = df.apply(fill_poss, axis=1)
    
    # Forward-fill the NaN values
    df['poss'].fillna(method='ffill', inplace=True)
    
    def fill_down(row):
        match = re.search(r'^(1st|2nd|3rd|4th)', row['one'])
        if match:
            return match.group(1)
        else:
            return np.nan # return NaN if the pattern is not found
    
    df['down'] = df.apply(fill_down, axis=1)
    
    def fill_to_go(row):
        match = re.search(r'and (.*?) at', row['one'])
        if match:
            return match.group(1)
        else:
            return np.nan # return NaN if the pattern is not found
    
    df['to_go'] = df.apply(fill_to_go, axis=1)
    
    def fill_playtype(row):
        # Define the list of words to search for and their corresponding play types
        words = [('Pass', 'Pass'), 
                 ('Rush', 'Rush'), 
                 ('Sacked', 'Pass'), 
                 ('Sack', 'Pass'), 
                 ('Field Goal', 'Field Goal'), 
                 ('Punt', 'Punt'), 
                 ('Kickoff', 'Kickoff')]
    
        # Check if the value in the 'two' column is a string
        if isinstance(row['two'], str):
            # Iterate over the words
            for word, playtype in words:
                if re.search(word, row['two'], re.IGNORECASE):
                    return playtype
        
        return np.nan # return NaN if no match is found or the value is not a string
    
    # Apply the function to each row
    df['playtype'] = df.apply(fill_playtype, axis=1)
    
    def fill_yards(row):
        # Check if the value in the 'two' column is a string
        if isinstance(row['two'], str):
            # Match the word 'for' followed by a space, then either 'no gain', 'loss of' followed by a number and 'yard(s)', or just a number and 'yard(s)'
            match = re.search(r'for (no gain|loss of (\d+) yard(s)?|(\d+) yard(s)?)', row['two'], re.IGNORECASE)
            if match:
                if match.group(1) == 'no gain':
                    return 0
                elif 'loss of' in match.group(1):
                    return -int(match.group(2))
                else:
                    return int(match.group(4))
        
        return np.nan # return NaN if no match is found or the value is not a string
    
    # Apply the function to each row
    df['yards'] = df.apply(fill_yards, axis=1)
    
    def fill_outcome(row):
        # Define the list of words to search for and their corresponding outcomes
        words = [('Touchdown', 'Touchdown'), 
                 ('Penalty', 'Penalty'),
                 ('Interception', 'Interception'),
                 ('Intercepted', 'Interception'),
                 ('Fumble', 'Fumble'),
                 ('Fumbled', 'Fumble'),
                 ('1st Down', '1st Down'),
                 ('Kick Attempt Good', 'Kick Attempt Good'),
                 ('Kick Attempt Failed', 'Kick Attempt Failed'),
                 ('Touchback', 'Touchback'),
                 ('Sack', 'Sack'),
                 ('Sacked', 'Sack'),
                 ('Blocked', 'Blocked'),
                 ('No Play', 'No Play'),
                 ('Incomplete', 'Incomplete')]
    
        # Check if the value in the 'two' column is a string
        if isinstance(row['two'], str):
            # Initialize the last match found to NaN
            last_match = np.nan
            # Iterate over the words
            for word, outcome in words:
                if re.search(word, row['two'], re.IGNORECASE):
                    last_match = outcome
            return last_match
        
        return np.nan # return NaN if no match is found or the value is not a string
    
    # Apply the function to each row
    df['outcome'] = df.apply(fill_outcome, axis=1)
    
    # Remove rows with NaN values in column 'two'
    df.dropna(subset=['two'], inplace=True)
    
    # Remove rows where column 'one' contains the word "total"
    df = df[~df['one'].str.contains(r'(?i)\btotal\b')]
    
    # Drop rows with "drive start" in column 'two'
    df = df[~df['two'].str.contains('drive start', case=False)]
    
    # Remove rows with 'NaN' in specified columns
    df = df.dropna(subset=['playtype', 'yards', 'outcome'], how='all')
    
    # Rearrange column order (keeping one and two for data checking right now)
    df = df[['half', 'quarter', 'poss', 'down', 'to_go', 'playtype', 'yards', 'outcome', 'one', 'two']]
    

    df.to_csv(output_path, index=False)
