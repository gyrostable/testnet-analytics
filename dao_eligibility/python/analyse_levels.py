import pickle as pkl
import pandas as pd
import numpy as np

# load user data 
with open("/Users/jonas/Workspace/Local/Drop/challengers.pkl", "rb") as f:
    object = pkl.load(f)
raw_df = pd.DataFrame(object)

# pull relevant info --- load raw_df; return clean_df
def initialize (df:pd.DataFrame):

    challenges = []
    challengers = []
    challenge_score = []
    
    for y in df["args"]:
        challenge_score.append(y['metadata'])
        challenges.append(y['checkName'].decode('utf-8').rstrip('\x00'))
        challengers.append(y['user'])
       
    # create and zip lists   
    zipped_df = pd.DataFrame(zip(challengers, challenges,challenge_score), columns=['user_address',
                        'challenge','challenge_score'])
    
    # ensure format consistency of address
    zipped_df['user_address'] = zipped_df['user_address'].str.lower()
    zipped_df['address_len'] = zipped_df['user_address'].map(len)    
    clean_df = zipped_df[zipped_df['address_len']==42].drop('address_len',axis=1)
    
    return pd.DataFrame(clean_df)

# merge lists into df and format for readability --- load clean_df; return mapped_df
def map_events (df:pd.DataFrame):
      
    mapped_df=df

    REMAP_CLASS = {
        'poap': 'ch_1',
        'sybilList': 'ch_2',
        'bankless': 'ch_4_weak',
        'govVoters': 'ch_3',
        'communityCalls': 'ch_4_comm',
        'highInvolvement': 'ch_4_strong',
        'virtualEvents':'ch_4_weak',
        "additionalPOAPs": 'ch_4_scores',
        'github': 'ch_6_github',
        'phone': 'ch_6_phone',
        'twitter': 'ch_6_twitter',
        'discord1': 'invalid',
        'privacyPolicy': 'privPolicy',
        'stackOvFl': 'ch_7_stack',
        'githubFollowers': 'ch_7_git',
        'discord-challenge-1': 'ch_5',
        'twitterFollowers': 'ch_7_twitter',
        'instagram': 'ch_7_ig',
        'reddit': 'ch_7_reddit',
        'fb': 'ch_7_fb',
        'twitter-standardised': 'ch_6_twitter',
        'github-standardised': 'ch_6_github',
        'coinbase': 'ch_8_coinbase',
        'discord': 'ch_8_contributors',
        'megaWhitelist': 'ch_8_defiwl',
        'minecraft': 'ch_7_minecraft',
        'goldfinchKYC': 'ch_8_goldfinch'}

    mapped_df['challenge'] = df['challenge'].map(REMAP_CLASS)
    
    return pd.DataFrame(mapped_df)

# group & count challenges by address ---  load mapped_df; return bloated_df
def get_scores (df:pd.DataFrame):
    
    # groupby address; load set with challenge column entries
    grouped_df = df.groupby('user_address').aggregate(list) 
   
    challenge_stack = [set(x) for x in grouped_df['challenge']]
   
    # loop for stacked uniques;
    challenge_stack_uniques = set()
    for challenger_set in challenge_stack:
      challenge_stack_uniques |= challenger_set
    
    # slight modifications
    challenge_stack_uniques.add('address')
    sorted_challenge_stack_uniques = sorted(challenge_stack_uniques)
    
    # populate an expanded & scored df
    df_bloated = pd.DataFrame(columns=sorted_challenge_stack_uniques, index = list(range(len(grouped_df))))
    
    for index, (user_address, data) in enumerate(grouped_df.iterrows()):
        challenges = zip(data['challenge'], data['challenge_score'])
        for challenge, value in challenges:
            df_bloated.iloc[index]['address'] = user_address
            df_bloated.iloc[index][challenge] = value
    
    df_bloated_reduced = df_bloated.drop(['ch_7_ig','ch_7_fb'],axis=1)
    
    return pd.DataFrame(df_bloated_reduced)

# metadata for ch4 all in ch_4-scores; split on ch_4-xx according to internal logic: comm, strong, weak --- load bloated_df; return operational_df
def normalize_scores(df: pd.DataFrame):
        
    # iterate through rows with stacked challenge value + increment by 1
    for index, row in df.iterrows():
    
        if len(str(df['ch_4_scores'][index])) >= 7:
            df['ch_4_comm'][index] = (df['ch_4_scores'][index] // 1000000)
            df['ch_4_strong'][index] = ((df['ch_4_scores'][index] % 1000000) // 1000)
            df['ch_4_weak'][index] = (df['ch_4_scores'][index] % 1000)
        
        if len(str(df['ch_4_scores'][index])) <= 4:
            df['ch_4_strong'][index] = ((df['ch_4_scores'][index] // 1000))
            df['ch_4_weak'][index] = (df['ch_4_scores'][index] % 1000)

        if len(str(df['ch_4_scores'][index])) <= 2:
            df['ch_4_weak'][index] = ((df['ch_4_scores'][index]))      

    return pd.DataFrame(df).drop('ch_4_scores',axis=1)

# replace 0 with 1 (for invalid & privPolicy, but also ch_6_git etc) and then fill nans with 0
def replace_nans(df:pd.DataFrame):
    
    # increment all bools by 1
    bool_challenge_returns = ['ch_1','ch_2','ch_6_github', 'ch_6_phone', 'ch_6_twitter',
       'ch_7_git', 'ch_7_minecraft', 'ch_7_reddit', 'ch_7_stack',
       'ch_7_twitter', 'ch_8_coinbase','ch_8_goldfinch']

    for ch in bool_challenge_returns:
        df[ch] = df[ch]+1

    # fill NaNs
    binaried_df = df.fillna(0)
    
    cols = binaried_df.columns
    no_nan_df = binaried_df[cols[1:]].apply(np.int64)
    no_nan_df.insert(0,'address',binaried_df['address'])
    
    # optional: drop columns or keep as activity receipt
    no_nan_df_smaller = no_nan_df.drop(['privPolicy','invalid'], axis=1)

    return pd.DataFrame(no_nan_df_smaller)
 
# apply sybil challenge weights --- load operational_df; return weighted_df
def apply_weights(df: pd.DataFrame):
    
    weighted_df = pd.DataFrame()
      
    weighted_df['address'] = df['address']
    weighted_df['w_ch_1'] = df['ch_1']*4
    weighted_df['w_ch_2'] = df['ch_2']*3
    weighted_df['w_ch_3'] = df['ch_3']*2    
    weighted_df['w_ch_4_weak'] = df['ch_4_weak']*1
    weighted_df['w_ch_4_strong'] = df['ch_4_strong']*3
    weighted_df['w_ch_4_comm'] = df['ch_4_comm']*2

    # --- conditional weights ---
    weighted_df['w_ch_5'] = df['ch_5'].apply(lambda w: {1: 2, 2: 3, 3: 5}.get(w, 0))

    weighted_df['w_ch_6_twitter'] = df['ch_6_twitter']*1
    weighted_df['w_ch_6_github'] = df['ch_6_github']*1
    weighted_df['w_ch_6_phone'] = df['ch_6_phone']*2
    
    weighted_df['w_ch_7_stack'] = df['ch_7_stack']*3
    weighted_df['w_ch_7_git'] = df['ch_7_git'].apply(lambda o: {1: 1, 2: 1, 3: 2}.get(o, 0)).astype(bool)*2    
    weighted_df['w_ch_7_twitter'] = (df['ch_7_twitter'].apply(lambda o: {1: 1, 2: 1, 3: 2, 4: 2}.get(o, 0)).astype(bool)*1)

    weighted_df['w_ch_7_reddit'] = df['ch_7_reddit']*2
    weighted_df['w_ch_7_minecraft'] = df['ch_7_minecraft']*1
    
    weighted_df['w_ch_8_goldfinch'] = df['ch_8_goldfinch'] * 5
    weighted_df['w_ch_8_defiwl'] = df['ch_8_defiwl']*2
    weighted_df['w_ch_8_contributors'] = df['ch_8_contributors'] * 1
    weighted_df['w_ch_8_coinbase'] = df['ch_8_coinbase']*5

    # --- conditional bonus points --- 
    df.loc[(df['ch_7_git'].apply(lambda o: {1: 1, 2: 1, 3: 2}.get(o, 0)) == 2),'github_bonus'] = 3
    weighted_df['github_bonus'] = df['github_bonus']
    weighted_df['github_bonus'].fillna(0, inplace=True)
    
    df.loc[(df['ch_7_twitter'].apply(lambda o: {1: 1, 2: 1, 3: 2, 4: 2}.get(o, 0)) == 2),'twitter_bonus'] = 3
    weighted_df['twitter_bonus'] = df['twitter_bonus']
    weighted_df['twitter_bonus'].fillna(0, inplace=True)
    
    return pd.DataFrame(weighted_df)

# cycle through functions --- load raw_df; return weighted_df
def main_function(df: pd.DataFrame):
    clean_df = initialize(df)
    mapped_df = map_events(clean_df)
    scored_df = get_scores(mapped_df)
    operational_df = normalize_scores(scored_df)
    
    operational_cleaned_df = replace_nans(operational_df)
    weighted_df = apply_weights(operational_cleaned_df)
        
    return pd.DataFrame(weighted_df)

# export 
if __name__ == '__main__':
    overview = main_function(raw_df)
            
    overview.to_csv("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-details-weighted.csv")