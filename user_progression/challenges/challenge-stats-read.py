from distutils.command.clean import clean
import pickle as pkl
from tokenize import group
import pandas as pd
import numpy as np


# load user data 
with open("/Users/jonas/Workspace/Local/Drop/challengers.pkl", "rb") as f:
    object = pkl.load(f)
raw_df = pd.DataFrame(object)

# pull relevant info --- load raw_df; return clean_df
def initialize (df:pd.DataFrame):

    help_challenge = []
    help_challenger = []
    help_challenge_score = []

    for y in df["args"]:
        help_challenge_score.append(y['metadata'])
        help_challenge.append(y['checkName'].decode('utf-8').rstrip('\x00'))
        help_challenger.append(y['user'])

    # create and zip lists
    list_challenge = pd.Series(help_challenge).tolist()
    list_challenger = pd.Series(help_challenger).tolist()
    list_challenge_score = pd.Series(help_challenge_score).tolist()
    
    zipped_df = pd.DataFrame(zip(list_challenger, list_challenge,list_challenge_score), columns=['user_address',
                        'challenge','challenge_score'])
    
    # ensure format consistency of address
    zipped_df['user_address'] = zipped_df['user_address'].str.lower()
    zipped_df['correct_address'] = zipped_df['user_address'].map(len)    
    clean_df = zipped_df[zipped_df['correct_address']==42].drop('correct_address',axis=1)
    
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
    
    return pd.DataFrame(df_bloated)

# metadata for ch4 all in ch_4-scores; split on ch_4-xx according to internal logic: comm, strong, weak --- load bloated_df; return operational_df
def format_lvl4_data(df: pd.DataFrame):
    
    # iterate through rows with stacked challenge value
    for index, row in df.iterrows():
        stacked_score = df['ch_4_scores'][index]
        
        # filter for missing values & split by complete or partial stack of scores
        if pd.notna(stacked_score) == True:
            
            # full stack of scores
            if len(str(stacked_score)) == 7:
                # comm -- can be two digit value, if last value of float is 0 rewrite with single digit value, otherwise two digit value
                comm_score = str(stacked_score)[:2]
                if str(comm_score)[1:] == 0:
                    df['ch_4_comm'][index] = int(comm_score[:1])
                else:
                    df['ch_4_comm'][index] = int(comm_score)
                
                # strong
                strong_score = str(stacked_score)[2:4]
                if strong_score[:1] == 0:
                    df['ch_4_strong'][index] = int(strong_score[1:2])
                else:
                    df['ch_4_comm'][index] = int(strong_score)
                    
                # weak has three digits in stack
                weak_score = str(stacked_score)[5:]
                if weak_score[:1] == 0:
                    df['ch_4_weak'][index] = int(weak_score[1:2])
                else:
                    df['ch_4_weak'][index] = int(weak_score)

 
            # partial stack of scores
            if len(str(stacked_score)) == 4:
                # comm is missing
                # strong
                strong_score = str(stacked_score)[:2]     
                if int((strong_score)[1:2]) == 0:
                    df['ch_4_strong'][index] = int(strong_score[:1])
                else:
                    df['ch_4_strong'][index] = int(strong_score)
                    
                # weak
                weak_score = str(stacked_score)[2:]
                if weak_score[:1] == 0:
                      df['ch_4_weak'][index] = int(weak_score[1:])
                else:
                    df['ch_4_weak'][index] = int(weak_score)
            
            # partial stack of scores
            if len(str(stacked_score)) < 3:
                # comm is missing
                # strong is missing
                # weak
                df['ch_4_weak'][index] = stacked_score
     
    # sync with other df structure: 0 = 1; NaN = 0 
    df['ch_4_comm'].replace(0, np.NaN, inplace=True)
    df['ch_4_weak'].replace(0, np.NaN, inplace=True)
    df['ch_4_strong'].replace(0, np.NaN, inplace=True)
            
    return pd.DataFrame(df).drop('ch_4_scores',axis=1)

# replace 0 with 1 and then fill nans with 0
def replace_nans(df:pd.DataFrame):
    
    transformed_df = df.replace(0,1)
    binaried_df = transformed_df.fillna(0)
    
    cols = binaried_df.columns
    no_nan_df = binaried_df[cols[1:]].apply(np.int64)
    no_nan_df.insert(0,'address',binaried_df['address'])
        
    return pd.DataFrame(no_nan_df)

# apply sybil challenge weights --- load operational_df; return weighted_df
def apply_weights(df: pd.DataFrame):
    
    weighted_df = {}
    weights = {'address': [], 'w1': 3, 'w2': 2, 'w3': 2, 'w4_weak': 1,'w4_strong': 3, 'w4_comm': 2, 
               'w5': 3, 'w6_twitter': 2, 'w6_github': 2, 'w6_phone': 3, 'w7_stack': 3, 'w7_git': 2, 
               'w7_twitter': 2, 'w7_reddit': 2, 'w7_minecraft': 1, 'w8_goldfinch': 3, 'w8_defiwl': 2,
               'w8_contributors': 2, 'w8_coinbase': 3, 'wprivPolicy': 1}

    weighted_df['address'] = df['address']
    weighted_df['w_ch_1'] = df['ch_1']*weights['w1']
    weighted_df['w_ch_2'] = df['ch_2']*weights['w2']
    weighted_df['w_ch_3'] = df['ch_3']*weights['w3']  
    
    weighted_df['w_ch_4_weak'] = df['ch_4_weak']*weights['w4_weak']
    weighted_df['w_ch_4_strong'] = df['ch_4_strong']*weights['w4_strong']
    weighted_df['w_ch_4_comm'] = df['ch_4_comm']*weights['w4_comm']

    weighted_df['w_ch_5'] = df['ch_5']*weights['w5']

    weighted_df['w_ch_6_twitter'] = df['ch_6_twitter']*weights['w6_twitter']
    weighted_df['w_ch_6_github'] = df['ch_6_github']*weights['w6_github']
    weighted_df['w_ch_6_phone'] = df['ch_6_phone']*weights['w6_phone']

    weighted_df['w_ch_7_stack'] = df['ch_7_stack']*weights['w7_stack']
    weighted_df['w_ch_7_git'] = df['ch_7_git']*weights['w7_git']
    weighted_df['w_ch_7_twitter'] = df['ch_7_twitter']*weights['w7_twitter']
    weighted_df['w_ch_7_reddit'] = df['ch_7_reddit']*weights['w7_reddit']
    weighted_df['w_ch_7_minecraft'] = df['ch_7_minecraft'] * \
        weights['w7_minecraft']

    weighted_df['w_ch_8_goldfinch'] = df['ch_8_goldfinch'] * \
        weights['w8_goldfinch']
    weighted_df['w_ch_8_defiwl'] = df['ch_8_defiwl']*weights['w8_defiwl']
    weighted_df['w_ch_8_contributors'] = df['ch_8_contributors'] * \
        weights['w8_contributors']
    weighted_df['w_ch_8_coinbase'] = df['ch_8_coinbase']*weights['w8_coinbase']

    weighted_df['wprivPolicy'] = df['privPolicy']*weights['wprivPolicy']

    return pd.DataFrame(weighted_df)

# count sybil points per address --- load weighted_df; return final_df
def count_points(df: pd.DataFrame):
    final_df = {}
    col_list = list(df)

    final_df['address'] = df['address']
    col_list.remove('address')
    final_df['points'] = df[col_list].sum(axis=1)

    return pd.DataFrame(final_df)

# cycle through functions --- load raw_df; return weighted_df
def main_function(df: pd.DataFrame):
    clean_df = initialize(df)
    mapped_df = map_events(clean_df)
    scored_df = get_scores(mapped_df)
    operational_df = format_lvl4_data(scored_df)
    operational_cleaned_df = replace_nans(operational_df)
    
    operational_cleaned_df.to_csv("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-detail.csv")
    
    weighted_df = apply_weights(operational_cleaned_df).drop('wprivPolicy', axis=1)      
    # weighted_df.to_csv("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-detail.csv")
    
    return pd.DataFrame(weighted_df)

# export and final presentation of current points
if __name__ == '__main__':
    overview = main_function(raw_df)
    # print(challenges['passed'].value_counts())

    print(overview)
    print('yay')
    
    # overview.to_csv("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-overview.csv")