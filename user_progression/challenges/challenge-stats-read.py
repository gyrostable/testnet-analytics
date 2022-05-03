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
       
    blockheight = []
    for z in df['blockNumber']:
        blockheight.append(z)
        
    # create and zip lists   
    zipped_df = pd.DataFrame(zip(challengers, challenges,challenge_score), columns=['user_address',
                        'challenge','challenge_score'])
    
    # ensure format consistency of address
    zipped_df['user_address'] = zipped_df['user_address'].str.lower()
    zipped_df['address_len'] = zipped_df['user_address'].map(len)    
    clean_df = zipped_df[zipped_df['address_len']==42].drop('address_len',axis=1)
    
    # observe last activity
    user_address_clean = pd.Series(clean_df['user_address']).tolist()
    last_activity = pd.DataFrame(zip(user_address_clean,blockheight),columns=['address','last_challenge_activity'])

    return pd.DataFrame(clean_df), pd.DataFrame(last_activity)

# merge lists into df and format for readability --- load clean_df; return mapped_df
def map_events (df:pd.DataFrame):
      
    mapped_df=df[0]

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

    mapped_df['challenge'] = df[0]['challenge'].map(REMAP_CLASS)
    
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

# replace 0 with 1 (for invalid & privPolicy) and then fill nans with 0
def replace_nans(df:pd.DataFrame):
    
    transformed_df = df.replace(0,1)
    binaried_df = transformed_df.fillna(0)
    
    cols = binaried_df.columns
    no_nan_df = binaried_df[cols[1:]].apply(np.int64)
    no_nan_df.insert(0,'address',binaried_df['address'])
    
    # optional: drop columns or keep as activity receipt
    no_nan_df_smaller = no_nan_df.drop(['privPolicy','invalid'], axis=1) 
        
    return pd.DataFrame(no_nan_df_smaller)

# rescored sybil challenge results --- load operational_df; return rescored_df
def rescore_points(df: pd.DataFrame):
        
    df.loc[df['ch_1'] > 0, 'ch_1'] = 4
    df.loc[df['ch_2'] > 0, 'ch_2'] = 3
    df.loc[df['ch_3'] > 0, 'ch_3'] = 2
    
    df.loc[df['ch_4_comm'] > 0, 'ch_4_comm'] = 2
    df.loc[df['ch_4_strong'] > 0, 'ch_4_strong'] = 3
    df.loc[df['ch_4_weak'] > 0, 'ch_4_weak'] = 1
        
    # extra point if incl in list
    extra_twitter_ama_points = ['0x92Cfeb4a41B8472D029cAC2eA3F7238690B56845', '0x4F50238eb2faB34ABbAbF8aC09F39ACA22a8A2A2', '0x124ac4BE876bB5826Cb3c9600b13611aE63eb427', '0xdB86B02928C47CB1c1D231B21732E6C639b28051', '0xeC8B674534384315F0c0e824Fc7A8aFd9dCa6182', '0x7C64C7E5Fe83274D6F55f1e4857Ba3061de42aB9', '0xDC4f1519028f3D13BF50ecC97Ee834D23895A490', '0xc86E128BC107aDEf038EE86871331c5BDdbe9C76', '0xE48608C7Da53A6481A46Bb247759b6d3B0eDc6AF', '0x64AEB121fc52446a54F5cEeC5Cb029b0C638937B', '0x95A18Fc2C740f341B09A788Bf6e86E5D30d8A149', '0xF85eAA24be0B4e24eFCb30ebb9dC126a0D0e2650', '0xFE042b1Aeb471CFf2e1A6709E5682533D19CbCc7', '0xcC6abB752A8bB38A915d808DF0A257173ef8Ba45', '0x150765A99c5e0Cf58e56ea41E92d110e2747002c', '0x1a693a0cc4F6aF763540192A8027c9FD7496E7Ac', '0x72ee9539Ae62D2f5c485b3cC46E064132617424A', '0x13a945AF443ffc5F745E2A32F44f71Adf6a97Eb1', '0x08A19Fae09dbC7d91170FdAb11Ee5a63c4610da0', '0x227179eD22661F446450Aa5EFe0a6Ac45A8bc2CB', '0x142Bd982260F206E6996B20C6b4B8a5e044be54B', '0xD60cADe1dfBc4bD2852b42209D2062b96b31E25f', '0x030a65cbA02Dc25709E841512264BdC5bbC5b192', '0x7a113bAFf3dA1833CBc3cCf642754C35e8e430a5', '0x3b6D17c0734b277EF7264b73753adaF930BA8f06', '0x98d8D5A6DE6e6b4001146858Afb10Ed07b3961F8', '0x496e4550f419e9be6ee1364781C42636F70A590E', '0x9CEa73CD04d170334Cd209f56884D98EC2Fdd3A5', '0x832e5BC3c6A9F93BF949DC295833EC7ce485571D', '0x7bF4c8FD9Cc55fdFF50Cc12319585B30fe2bc6b7', '0xDcdB53E8E1123BAA64a0B7d3Da13E360CA843797', '0xa689100C8feBcbDc92137B6A6BbBfDa305A6d319', '0xf32F045f3CB8f1B70CF0895766a305e11EF720b9', '0x664e596c96B5686d98a70bbfBCdbf5Ee3D39f090', '0x55760B731D66fB4ffFe34Ab3372268844944C436', '0xd315D1ae47Df5f7fcb0A8B3A1C6CEb3dAa554e89', '0xd908C0B105a237c790d805C87c2eB960283866a1', '0xCCb127BC2C133C2cBDa089a05722ecA109ACC6e1', '0xE1fD946Fc1270dc6Cc9fef9f666596b11139704f', '0x5F367BF126FDa56D88BA88a8978D5496c66B3569', '0x548fAC51A7518aD8d7139B199fEc71263340994A']
  
    for addr in extra_twitter_ama_points:
        df.loc[df['address'] == addr, 'ch_5'] = df['ch_5'] + 2
    else:
        df.loc[df['ch_5'] > 0, 'ch_5'] = df['ch_5'] + 1

    # logic: normal: 1; score of 5 (summed with 7) if 6 matches 7
    df.loc[df['ch_6_github'] > 0,'ch_6_github'] = 1
    df.loc[df['ch_6_github'] == df['ch_7_git'],'ch_6_github'] = 3
    
     # logic: normal: 1; score of 4 (summed with 7) if 6 matches 7
    df.loc[df['ch_6_twitter'] > 0,'ch_6_twitter'] = 1
    df.loc[df['ch_6_twitter'] == df['ch_7_twitter'],'ch_6_twitter'] = 3
    
    df.loc[df['ch_6_phone'] > 0,'ch_6_phone'] = 2
    
    df.loc[df['ch_7_git'] > 0, 'ch_7_git'] = 2
    df.loc[df['ch_7_twitter'] > 0, 'ch_7_twitter'] = 2
    df.loc[df['ch_7_minecraft'] > 0, 'ch_7_minecraft'] = 1
    df.loc[df['ch_7_reddit'] > 0, 'ch_7_reddit'] = 3
    df.loc[df['ch_7_stack'] > 0, 'ch_7_stack'] = 3
    
    # update contributor rescoring as per feedback
    # df.loc[df['ch_8_contributors'] > 0, 'ch_8_contributors'] = 5
    df.loc[df['ch_8_coinbase'] > 0, 'ch_8_coinbase'] = 5
    df.loc[df['ch_8_defiwl'] > 0, 'ch_8_defiwl'] = 2
    df.loc[df['ch_8_goldfinch'] > 0, 'ch_8_goldfinch'] = 5
    
    # df.loc[df['invalid'] > 0, 'invalid'] = -1
    # df.loc[df['privPolicy'] > 0, 'privPolicy'] = -1
    return df
    
# apply sybil challenge weights --- load operational_df; return weighted_df
def apply_weights(df: pd.DataFrame):
    
    weighted_df = pd.DataFrame()
    weights = {'address': [], 'w1': 4, 'w2': 3, 'w3': 2, 'w4_weak': 1,'w4_strong': 3, 'w4_comm': 2, 
               'w6_twitter': 1, 'w6_github': 1, 'w6_phone': 2, 'w7_stack': 3, 'w7_git': 3, 
               'w7_twitter': 2, 'w7_reddit': 2, 'w7_minecraft': 1, 'w8_goldfinch': 5, 'w8_defiwl': 2,
               'w8_contributors': 1, 'w8_coinbase': 5}

    weighted_df['address'] = df['address']
    weighted_df['w_ch_1'] = df['ch_1']*weights['w1']
    weighted_df['w_ch_2'] = df['ch_2']*weights['w2']
    weighted_df['w_ch_3'] = df['ch_3']*weights['w3']  
    
    weighted_df['w_ch_4_weak'] = df['ch_4_weak']*weights['w4_weak']
    weighted_df['w_ch_4_strong'] = df['ch_4_strong']*weights['w4_strong']
    weighted_df['w_ch_4_comm'] = df['ch_4_comm']*weights['w4_comm']

    # extra case
    # weighted_df['w_ch_5'] = df['ch_5']*weights['w5']
    
    df.loc[df['ch_5'] == 1,'w_ch_5'] = 2
    df.loc[df['ch_5'] == 2,'w_ch_5'] = 3
    df.loc[df['ch_5'] == 3,'w_ch_5'] = 5

    weighted_df['w_ch_5'] = df['w_ch_5']

    # extra case
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

    # --- conditional bonus points --- 
    df.loc[(df['ch_6_github'] == df['ch_7_git']) & (df['ch_6_github'] != 0),'github_bonus'] = 1
    weighted_df['github_bonus'] = df['github_bonus']
    weighted_df['github_bonus'].replace(0, np.NaN, inplace=True)
    
    df.loc[(df['ch_6_twitter'] == df['ch_7_twitter']) & (df['ch_6_twitter'] != 0),'twitter_bonus'] = 1
    weighted_df['twitter_bonus'] = df['twitter_bonus']
    weighted_df['twitter_bonus'].replace(0, np.NaN, inplace=True)
    
    return pd.DataFrame(weighted_df)

# not used: count sybil points per address --- load weighted_df; return final_df
def count_points(df: pd.DataFrame):
    final_df = {}
    col_list = list(df)

    final_df['address'] = df['address']
    col_list.remove('address')
    final_df['points'] = df[col_list].sum(axis=1)

    return pd.DataFrame(final_df)

# add blockheight from last challenge activity
def last_activity(rescored_df:pd.DataFrame, blockheight:pd.DataFrame):

    # print(len(blockheight))
    blockheight.drop_duplicates(subset='address', keep='last',inplace=True, ignore_index=True)
    final_tracked_df = pd.merge(rescored_df,blockheight, on='address', how='inner')

    return pd.DataFrame(final_tracked_df)

# cycle through functions --- load raw_df; return weighted_df
def main_function(df: pd.DataFrame):
    clean_df = initialize(df)
    mapped_df = map_events(clean_df)
    scored_df = get_scores(mapped_df)
    operational_df = format_lvl4_data(scored_df)
    operational_cleaned_df = replace_nans(operational_df)
      
    weighted_df = apply_weights(operational_cleaned_df)
    # rescored_df = rescore_points(operational_cleaned_df)
    
    # last_active_df = last_activity(weighted_df,clean_df[1])
    # weighted_df = apply_weights(operational_cleaned_df)      
    
    return pd.DataFrame(weighted_df)

# export and final presentation of current points
if __name__ == '__main__':
    overview = main_function(raw_df)

    # overview['address'][overview['ch_5']>0].to_clipboard()
    # print(len(overview[overview['ch_1']>0]))

    overview.to_csv("/Users/jonas/Workspace/Local/Drop/results/challenge-progression-stats-detail.csv")
    # print(overview)
    # overview.to_clipboard()
    print('yay')