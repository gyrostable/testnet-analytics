import csv
from numpy import NaN
import pandas as pd
import json
import pickle as pkl

# level 1 - address minting in pamm
# 0x29e858A3d3AE4ab92426c8C279f8E8ae64Edfda7
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl1_supply.pkl", "rb") as f:
    raw_level_1 = pd.DataFrame(pkl.load(f))

# level 2 - nft minters
# 0xe870dbF309100C3f6ab765A5c0B25bec01B6B320
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl2.csv") as g:
    raw_level_2 = pd.DataFrame(csv.reader(g))

# level 25 - registration events
# 0x028437cF5dB90B367e392Ee971639824684D8295
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl25.csv") as h:
    raw_level_25 = pd.DataFrame(csv.reader(h))
    
# level 3 - snapshot voters
# graphql api
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl3.json", "rb") as i:
    raw_level_3 = pd.DataFrame(json.load(i))

# match minter list against bot list --- load raw_level_1; return lvl1
def load_lvl1(df: pd.DataFrame):
    
    # format pamm minter addresses
    minter = [] 
    for y in df["args"]:
        minter.append(y['minter'])
        
    # df, drop nans, lowercase, ensure type consistency, remove duplicates & keep first
    lvl1_raw = pd.DataFrame(minter, columns=['address'])
    lvl1_no_nan = lvl1_raw[(lvl1_raw['address']!=NaN)]
    lvl1_mergable = pd.DataFrame(lvl1_no_nan['address'].str.lower()).astype(str)
    lvl1_mergable.drop_duplicates(keep='first',ignore_index=True,inplace=True)
                                                                
    # level 1 - bot addresses minting in pamm
    bots_raw = pd.read_csv('/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/Testnet analytics - bot_vsc.csv')
    # drop blanks, select bots, ensure type consistency
    bots_raw.dropna(axis=0,inplace=True)
    bots = pd.DataFrame(bots_raw[bots_raw.is_bot == True].astype(str))
    bots_mergable = pd.DataFrame(bots['address'].str.lower())

    # stack raw & bots to remove all duplicates
    stacked = pd.concat([lvl1_mergable, bots_mergable], ignore_index=True, sort=False)
    lvl1 = stacked.drop_duplicates(ignore_index=True, keep=False)
    # lvl1 = stacked.loc[stacked.duplicated(keep=False), :]
    
    # ensure correct formatting
    lvl1['correct_address'] = lvl1['address'].map(len)    
    lvl1_formatted = lvl1[lvl1['correct_address']==42].drop('correct_address',axis=1)
    
    return pd.DataFrame(lvl1_formatted).applymap(lambda f: f.lower() if type(f) == str else f)

def load_lvl2(df:pd.DataFrame):
    df.columns = df.iloc[0]
    df_2 = pd.DataFrame(df).rename(columns={'From':'address'}).drop(0)
    lvl2 = pd.DataFrame(df_2['address']).astype(str)
        
    return lvl2.applymap(lambda f: f.lower() if type(f) == str else f)

def load_lvl25(df:pd.DataFrame):
    df.columns = df.iloc[0]
    lvl25 = pd.DataFrame(df['From']).rename(columns = {'From': 'address'}).drop(0).astype(str)
    lvl25['address'].str.lower()
        
    return lvl25.applymap(lambda f: f.lower() if type(f) == str else f)

def load_lvl3(df:pd.DataFrame):

    lvl3_dict = {'address':[]}
    for i in df['data']['votes']:
        lvl3_dict['address'].append(i['voter'])
    lvl3 = pd.DataFrame(lvl3_dict).astype(str)
    lvl3['address'].str.lower()
   
    return pd.DataFrame(lvl3).applymap(lambda f: f.lower() if type(f) == str else f)

def merge_levels(df:pd.DataFrame):
    
    # load data & slight modifications
    lvl_1 = load_lvl1(df).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_2 = load_lvl2(raw_level_2).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_25 = load_lvl25(raw_level_25).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_3 = load_lvl3(raw_level_3).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    
    # stack + get uniques
    stacked_addresses = pd.concat([lvl_1,lvl_2,lvl_25,lvl_3], axis=0)
    uniques = stacked_addresses.drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    
    # merge on uniques
    lvl1 = pd.merge(uniques,lvl_1, on='address', how='inner').rename(columns={'address': 'lvl1'})
    lvl2 = pd.merge(uniques,lvl_2, on='address', how='inner').rename(columns={'address': 'lvl2'})
    lvl25 = pd.merge(uniques,lvl_25, on='address', how='inner').rename(columns={'address': 'lvl25'})
    lvl3 = pd.merge(uniques,lvl_3, on='address', how='inner').rename(columns={'address': 'lvl3'})

    stacked = pd.concat([uniques, lvl1,lvl2,lvl25,lvl3],axis=1)
    early_levels = stacked.apply(lambda s: stacked['address'].where(stacked['address'].isin(s)))
    
    # improve readability - return bool, convert into binary
    early_levels_readable = early_levels.notnull().astype('int')
    early_levels_readable['address']=early_levels['address']

    return pd.DataFrame(early_levels_readable)

if __name__ == '__main__':
    final = merge_levels(raw_level_1)
    
    # count participation, subtract 'index' column
    final['score'] = final.sum(axis=1,numeric_only=True)
    
    # print(final.groupby(['lvl1','lvl2','lvl25','lvl3']).size().reset_index(name='frequency'))
    
    # print(final.groupby('lvl1').size().reset_index(name='frequency'))
    # print(final.groupby('lvl2').size().reset_index(name='frequency'))
    # print(final.groupby('lvl25').size().reset_index(name='frequency'))
    # print(final.groupby('lvl3').size().reset_index(name='frequency'))


    
    # final.to_clipboard()
    # output
    final.to_csv('/Users/jonas/Workspace/Local/Drop/results/early_levels_stats.csv')
    print('done')
