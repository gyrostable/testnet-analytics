import csv
import pandas as pd
import numpy as np

def merge():
    # change challenge-progression-stats-detail to challenge-progression-stats-overview for summed scores, adapt range
    with open("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-details-weighted.csv") as a:
        late_levels = pd.read_csv(a,usecols=list(range(1,23)))
        # late_levels = pd.read_csv(a,usecols=list(range(1,21)))
        
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
    df['sybil_score'] = pd.DataFrame(df[sybil_score_list].sum(axis=1))
    
    # -- define cut-offs for filter --
    filtered_df = pd.DataFrame()
    filtered_df = df[(df['passed_levels']>0) & (df['sybil_score']>4) | (df['passed_levels']>4) & (df['sybil_score']>0)]

    return filtered_df

if __name__ == '__main__':
    
    # -- init -- 
    combined_data = merge()
    overview = condense(combined_data)
    column_list = list(overview.columns)[7:28]    

    # -- group into buckets --
    overview['rarity_groups'] = (overview['sybil_score'].apply(lambda tier: {1:1, 2:1, 3:1, 4:2, 5:2 , 6:2, 7:2, 8:2, 9:3, 10:3, 11:3, 12:3, 13:3, 14:3, 15:3}.get(tier,4)))
    # print(overview.groupby('rarity_groups').size().reset_index(name='frequency'))
    
    # -- data comparison -- 
    # overview.to_json("/Users/jonas/Workspace/Local/Drop/results/unweighted-filtered.json")
    # temp = overview.groupby(by=column_list,axis=0,as_index=False).count().to_dict()

    # -- easy exports -- 
    # overview.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-overview.csv')
    
    # -- challenge completion counts per challenge -- 
    # aggregated
    # print(overview[column_list].astype(bool).sum(axis=0,numeric_only=True))
    
    # per value
    # value_count_challenges = ({c: overview[c].value_counts().drop(index=0).to_dict() for c in column_list})
    # for key, value in value_count_challenges.items():
    #     print(key, value)

    #  -- amount of passed challenges --     
    # print(overview.groupby('passed_challenges').size().reset_index(name='frequency'))
    
    #  -- grouped sybil score count -- 
    # print(overview.groupby('sybil_score').size().reset_index(name='frequency'))

    #  -- level completion counts -- 
    # print(overview.groupby('passed_levels').size().reset_index(name='frequency'))