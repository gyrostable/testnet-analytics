import pickle

import pandas as pd

with open('raw_data/mints.pkl', 'rb') as handle:
    mints = pickle.load(handle)

with open('raw_data/redeems.pkl', 'rb') as handle:
    redeems = pickle.load(handle)

clean = []
for mint in mints:
    clean_dict = {}
    clean_dict["caller_address"] = mint["args"]["minter"]
    clean_dict["amount"] = mint["args"]["amount"]
    clean_dict["event"] = mint["event"]
    clean_dict["log_index"] = mint["logIndex"]
    clean_dict["transaction_index"] = mint["transactionIndex"]
    clean_dict["transaction_hash"] = mint["transactionHash"]
    clean_dict["block_hash"] = mint["blockHash"]
    clean_dict["block_number"] = mint["blockNumber"]
    clean.append(clean_dict)

mints_df = pd.DataFrame(clean)

clean = []
for redeem in redeems:
    clean_dict = {}
    clean_dict["caller_address"] = redeem["args"]["redeemer"]
    clean_dict["amount"] = redeem["args"]["amount"]
    clean_dict["event"] = redeem["event"]
    clean_dict["log_index"] = redeem["logIndex"]
    clean_dict["transaction_index"] = redeem["transactionIndex"]
    clean_dict["transaction_hash"] = redeem["transactionHash"]
    clean_dict["block_hash"] = redeem["blockHash"]
    clean_dict["block_number"] = redeem["blockNumber"]
    clean.append(clean_dict)

redeems_df = pd.DataFrame(clean)

master_df = pd.concat([mints_df, redeems_df])

bot_addresses = pd.read_csv("bot_addresses.csv", names = ['addresses', 'isbot'])
bot_addresses=bot_addresses[bot_addresses['isbot']==True]

bot_address_list = list(bot_addresses['addresses'])

bot_filter = ~master_df.caller_address.isin(bot_address_list)

clean_df = master_df[bot_filter]

KNOWN_BOT_ADD = '0x4c39D086deA12Cf50D68F352689041263D74D965'



