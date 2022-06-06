import csv
from numpy import NaN
import pandas as pd
import json
import pickle as pkl

# level 1 - address minting in pamm
# 0x29e858A3d3AE4ab92426c8C279f8E8ae64Edfda7
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl1_supply.pkl", "rb") as f:
    raw_level_1_mint = pd.DataFrame(pkl.load(f))

# level 1 - address supplying assets to samm
# 0x6EAe312f00B4EE0640BF4e3D0A08Cda36F206bcc
with open('/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl1_samm.pkl', 'rb') as g:
    raw_level_1_samm = pd.DataFrame(pkl.load(g))
        
# level 2 - nft minters
# 0xe870dbF309100C3f6ab765A5c0B25bec01B6B320
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl2.csv") as h:
    raw_level_2_nft = pd.DataFrame(csv.reader(h))
    
# level 2 - level completed check
with open('/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl2_arb.pkl', 'rb') as i:
    raw_level_2_full = pd.DataFrame(pkl.load(i))

# level 25 - registration events
# 0x028437cF5dB90B367e392Ee971639824684D8295
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl25.csv") as j:
    raw_level_25 = pd.DataFrame(csv.reader(j))
    
# level 3 - snapshot voters
# graphql api
with open("/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl3.json", "rb") as k:
    raw_level_3 = pd.DataFrame(json.load(k))

# match minter list against bot list --- load raw_level_1; return lvl1
def load_lvl1_mint(df: pd.DataFrame):
    
    # format pamm minter addresses
    minter = [] 
    for y in df["args"]:
        minter.append(y['minter'])
        
    # df, drop nans, lowercase, ensure type consistency, remove duplicates & keep first
    lvl1_mint = pd.DataFrame(minter, columns=['address'])
    lvl1_mint_no_nan = lvl1_mint[(lvl1_mint['address']!=NaN)]
    lvl1_mint_mergable = pd.DataFrame(lvl1_mint_no_nan['address'].str.lower()).astype(str)
    lvl1_mint_mergable.drop_duplicates(keep='first',ignore_index=True,inplace=True)
                                                                
    # level 1 - bot addresses minting in pamm
    bots_raw = pd.read_csv('/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/Testnet analytics - bot_vsc.csv')
    # drop blanks, select bots, ensure type consistency
    bots_raw.dropna(axis=0,inplace=True)
    bots = pd.DataFrame(bots_raw[bots_raw.is_bot == True].astype(str))
    bots_mergable = pd.DataFrame(bots['address'].str.lower())

    # stack raw & bots to remove all duplicates
    stacked = pd.concat([lvl1_mint_mergable, bots_mergable], ignore_index=True, sort=False)
    lvl1_mint = stacked.drop_duplicates(ignore_index=True, keep=False)
    # lvl1 = stacked.loc[stacked.duplicated(keep=False), :]
    
    # ensure correct formatting
    lvl1_mint['correct_address'] = lvl1_mint['address'].map(len)    
    lvl1_mint_formatted = lvl1_mint[lvl1_mint['correct_address']==42].drop('correct_address',axis=1)
    
    return pd.DataFrame(lvl1_mint_formatted).applymap(lambda f: f.lower() if type(f) == str else f)

def load_lvl1_samm(df:pd.DataFrame):
    
    # load samm LP addresses
    lps = [] 
    for u in df["args"]:
        lps.append(u['caller'])
        
    # df, drop nans, lowercase, ensure type consistency, remove duplicates & keep first
    lvl1_lp = pd.DataFrame(lps, columns=['address'])
    lvl1_lp_no_nan = lvl1_lp[(lvl1_lp['address']!=NaN)]
    lvl1_lp_mergable = pd.DataFrame(lvl1_lp_no_nan['address'].str.lower()).astype(str)
    lvl1_lp_mergable.drop_duplicates(keep='first',ignore_index=True,inplace=True)
    
    # bot addresses minting in pamm
    bots_raw = pd.read_csv('/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/Testnet analytics - bot_vsc.csv')
    # drop blanks, select bots, ensure type consistency
    bots_raw.dropna(axis=0,inplace=True)
    bots = pd.DataFrame(bots_raw[bots_raw.is_bot == True].astype(str))
    bots_mergable = pd.DataFrame(bots['address'].str.lower())
    
    # stack LPs & bots to remove all duplicates
    stacked_2 = pd.concat([lvl1_lp_mergable, bots_mergable], ignore_index=True, sort=False)
    lvl1_lp = stacked_2.drop_duplicates(ignore_index=True, keep=False)
    
    # ensure correct formatting
    lvl1_lp['correct_address'] = lvl1_lp['address'].map(len)    
    lvl1_lp_formatted = lvl1_lp[lvl1_lp['correct_address']==42].drop('correct_address',axis=1)
    
    return lvl1_lp_formatted.applymap(lambda f: f.lower() if type(f) == str else f)

def load_lvl2_nft(df:pd.DataFrame):
    
    # load nft
    df.columns = df.iloc[0]
    df_2 = pd.DataFrame(df).rename(columns={'From':'address'}).drop(0)
    lvl2_nft = pd.DataFrame(df_2['address']).astype(str)
        
    return lvl2_nft.applymap(lambda f: f.lower() if type(f) == str else f)

def load_lvl2_full(df:pd.DataFrame):
    
   # completion checkmark
    lvl2_full = []
    for o in df['args']:
        lvl2_full.append(o['user'])
    
    lvl2_full_df = pd.DataFrame(lvl2_full).rename(columns={0:'address'}).drop(0)

    return lvl2_full_df.applymap(lambda f: f.lower() if type(f) == str else f)

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

    lvl_1_mint = load_lvl1_mint(df).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_1_lp = load_lvl1_samm(raw_level_1_samm).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_2_nft = load_lvl2_nft(raw_level_2_nft).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_2_full = load_lvl2_full(raw_level_2_full).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_25 = load_lvl25(raw_level_25).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    lvl_3 = load_lvl3(raw_level_3).drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    
    # stack + get uniques
    stacked_addresses = pd.concat([lvl_1_mint,lvl_1_lp,lvl_2_nft,lvl_2_full,lvl_25,lvl_3], axis=0)
    uniques = stacked_addresses.drop_duplicates(subset='address', keep='first').reset_index(drop=True)
    
    # merge on uniques
    lvl1_mint = pd.merge(uniques,lvl_1_mint, on='address', how='inner').rename(columns={'address': 'lvl1_mint'})
    lvl1_lp = pd.merge(uniques,lvl_1_lp, on='address', how='inner').rename(columns={'address': 'lvl1_lp'})
    lvl2_nft = pd.merge(uniques,lvl_2_nft, on='address', how='inner').rename(columns={'address': 'lvl2_nft'})
    lvl2_full = pd.merge(uniques,lvl_2_full, on='address', how='inner').rename(columns={'address': 'lvl2_full'})
    lvl25 = pd.merge(uniques,lvl_25, on='address', how='inner').rename(columns={'address': 'lvl25'})
    lvl3 = pd.merge(uniques,lvl_3, on='address', how='inner').rename(columns={'address': 'lvl3'})

    stacked = pd.concat([uniques, lvl1_mint,lvl1_lp, lvl2_nft,lvl2_full, lvl25,lvl3],axis=1)
    early_levels = stacked.apply(lambda s: stacked['address'].where(stacked['address'].isin(s)))
    
    # improve readability - return bool, convert into binary
    early_levels_readable = early_levels.notnull().astype('int')
    early_levels_readable['address']=early_levels['address']

    return pd.DataFrame(early_levels_readable)

if __name__ == '__main__':
    
    early_levels = merge_levels(raw_level_1_mint)
    # print(early_levels.groupby(['lvl1_mint', 'lvl1_lp', 'lvl2_nft', 'lvl2_full', 'lvl25','lvl3']).size().reset_index(name='frequency'))
    
    # output
    # final.to_clipboard()