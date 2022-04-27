import csv
import pandas as pd
import numpy as np

def merge():
    # change challenge-progression-stats-detail to challenge-progression-stats-overview for summed scores, adapt range
    with open("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-detail.csv") as a:
        late_levels = pd.read_csv(a,usecols=list(range(1,22)))
            
    # slight formatting
    late_levels['address'] = late_levels['address'].str.lower()

    with open("/Users/jonas/Workspace/Local/Drop/results/early_levels_stats_exp.csv") as b:
        early_levels = pd.DataFrame(csv.reader(b))
        # add headers & drop first row/ column
        early_levels.columns = early_levels.iloc[0]
        early_levels = early_levels.iloc[1: , 1:]
        
        # slight formatting
        early_levels['address'] = early_levels['address'].str.lower()
    
    # merge
    merged = pd.merge(early_levels,late_levels, on='address', how='outer')
        
    # slight formatting
    filled = merged.fillna(0)
    cols = merged.columns
    complete = filled[cols[1:]].apply(np.int64)
    complete.insert(0,'address',merged['address'])
    
    # complete.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-bloated.csv')
    return complete

def condense(df:pd.DataFrame):
    
    overview = pd.DataFrame()
    overview['address'] = df['address']
    
    early_levels_df = ['lvl1_mint', 'lvl1_lp', 'lvl2_nft', 'lvl2_full', 'lvl25','lvl3']
    syb_cols_df = ['ch_1', 'ch_2', 'ch_3', 'ch_4_comm', 'ch_4_strong', 'ch_4_weak', 'ch_5', 'ch_6_github', 'ch_6_phone', 'ch_6_twitter', 'ch_7_git', 'ch_7_minecraft', 'ch_7_reddit', 'ch_7_stack', 'ch_7_twitter', 'ch_8_coinbase', 'ch_8_contributors', 'ch_8_defiwl', 'ch_8_goldfinch']

    overview['passed_levels'] = pd.DataFrame(df[early_levels_df].sum(axis=1,numeric_only=True))
    overview['sybil_score'] = pd.DataFrame(df[syb_cols_df].sum(axis=1,numeric_only=True))
    overview['last_active'] = pd.DataFrame(df['last_challenge_activity'])
    
    # define cut-offs for filter
    overview_filtered = overview[(overview['passed_levels']>0) & (overview['sybil_score']>0)]
    # overview_filtered = overview[(overview['passed_levels']>=4) & (overview['sybil_score']>=1) | (overview['passed_levels']>=2) & (overview['sybil_score']>=3) | (overview['passed_levels']>=1) & (overview['sybil_score']>=5)]
    
    return overview_filtered

if __name__ == '__main__':
    
    # init
    result = merge()
    overview = condense(result)

    # export
    overview.to_clipboard()
    print('yay')
    # print(overview)
    # overview.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-overview.csv')