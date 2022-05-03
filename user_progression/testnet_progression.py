import csv
import pandas as pd
import numpy as np

def merge():
    # change challenge-progression-stats-detail to challenge-progression-stats-overview for summed scores, adapt range
    with open("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-detail.csv") as a:
        late_levels = pd.read_csv(a,usecols=list(range(1,23)))
        
    # -- slight formatting --
    late_levels['address'] = late_levels['address'].str.lower()

    with open("/Users/jonas/Workspace/Local/Drop/results/early_levels_stats_exp.csv") as b:
        early_levels = pd.DataFrame(csv.reader(b))
        # -- add headers & drop first row/ column --
        early_levels.columns = early_levels.iloc[0]
        early_levels = early_levels.iloc[1: , 1:]
        
        # -- slight formatting --
        early_levels['address'] = early_levels['address'].str.lower()
    
    # -- merge --
    merged = pd.merge(early_levels,late_levels, on='address', how='outer')
        
    # -- slight formatting --
    filled = merged.fillna(0)
    cols = merged.columns
    complete = filled[cols[1:]].apply(np.int64)
    complete.insert(0,'address',merged['address'])
    
    # complete.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-bloated.csv')
    
    return complete

def condense(df:pd.DataFrame):
    
    overview = pd.DataFrame()
    overview['address'] = df['address']
    
    # -- define sublists for data presentation --
    columns = list(df.columns)
    early_levels_list = columns[1:7]
    sybil_score_list = columns[7:]
    challenge_list = columns[7:26]

    # -- add relevant columns via sublists --
    df['passed_levels'] = pd.DataFrame(df[early_levels_list].astype(bool).sum(axis=1))
    df['passed_challenges'] = pd.DataFrame(df[challenge_list].astype(bool).sum(axis=1))
    df['sybil_score'] = pd.DataFrame(df[sybil_score_list].sum(axis=1,numeric_only=True))
    # overview['last_active'] = pd.DataFrame(df['last_challenge_activity'])

    filtered_df = pd.DataFrame()
    # -- define cut-offs for filter --
    filtered_df = df[(df['passed_levels']>0) & (df['sybil_score']>0)]
    # overview_filtered = overview[(overview['passed_levels']>=4) & (overview['sybil_score']>=1) | (overview['passed_levels']>=2) & (overview['sybil_score']>=3) | (overview['passed_levels']>=1) & (overview['sybil_score']>=5)]

    return filtered_df

if __name__ == '__main__':
    
    # -- init -- 
    combined_data = merge()
    overview = condense(combined_data)
    column_list = list(overview.columns)

    # -- easy exports -- 
    # overview.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-overview.csv')
    
    # -- challenge completion counts per challenge -- 
    # overview[column_list[7:26]].astype(bool).sum(axis=0,numeric_only=True).to_clipboard()
    print(overview[column_list[7:26]].astype(bool).sum(axis=0,numeric_only=True))

    #  -- amount of passed challenges --     
    print(overview.groupby('passed_challenges').size().reset_index(name='frequency'))
    # overview.groupby('passed_challenges').size().reset_index(name='frequency').to_clipboard()
    
    #  -- grouped sybil score count -- 
    print(overview.groupby('sybil_score').size().reset_index(name='frequency'))
    # overview.groupby('sybil_score').size().reset_index(name='frequency').to_clipboard()

    #  -- level completion counts -- 
    print(overview.groupby('passed_levels').size().reset_index(name='frequency'))
    # overview.groupby('passed_levels').size().reset_index(name='frequency').to_clipboard()

