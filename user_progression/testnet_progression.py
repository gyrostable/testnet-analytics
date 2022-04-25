import pandas as pd
import numpy as np

def merge():
    # change challenge-progression-stats-detail to challenge-progression-stats-overview for summed scores, adapt range
    with open("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-detail.csv") as a:
        late_levels = pd.read_csv(a,usecols=list(range(1,23)))
            
    # slight formatting
    late_levels['address'] = late_levels['address'].str.lower()

    with open("/Users/jonas/Workspace/Local/Drop/results/early_levels_stats.csv") as b:
        early_levels = pd.read_csv(b,sep=',', keep_default_na=False, na_values=[''],usecols=list(range(1,6)))
            
    # merge
    merged = pd.merge(early_levels,late_levels, on='address', how='outer')
    
    # slight formatting
    filled = merged.fillna(0)
    cols = merged.columns
    complete = filled[cols[1:]].apply(np.int64)
    complete.insert(0,'address',merged['address'])
    # complete.drop(['invalid','privPolicy'],axis=1,inplace=True)
    
    complete.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-bloated.csv')
    complete.to_clipboard()

    return complete

def condense(df:pd.DataFrame):
    
    overview = pd.DataFrame()
    overview['address'] = df['address']
    overview['passed_levels'] = pd.DataFrame(df[['lvl1','lvl2','lvl25','lvl3']].sum(axis=1))
    overview['sybil_score'] = pd.DataFrame(df[['ch_1', 'ch_2', 'ch_3','ch_4_comm', 'ch_4_strong', 'ch_4_weak', 'ch_5', 'ch_6_github','ch_6_phone', 'ch_6_twitter', 'ch_7_fb', 'ch_7_git', 'ch_7_ig','ch_7_minecraft', 'ch_7_reddit', 'ch_7_stack', 'ch_7_twitter','ch_8_coinbase', 
                                               'ch_8_contributors']].sum(axis=1))
    
    # define cut-offs for filter
    overview_filtered = overview[(overview['passed_levels']>=1) & (overview['sybil_score']>=5)]
    # overview_filtered = overview[(overview['passed_levels']>=4) & (overview['sybil_score']>=1) | (overview['passed_levels']>=2) & (overview['sybil_score']>=3) | (overview['passed_levels']>=1) & (overview['sybil_score']>=5)]
    
    return overview_filtered

if __name__ == '__main__':
    result = merge()
    # result.to_clipboard()
    overview = condense(result)
    
    print(overview)
    # overview.to_clipboard()
    # overview.to_csv('/Users/jonas/Workspace/Local/Drop/results/endstate-overview.csv')
    
    print('yay')