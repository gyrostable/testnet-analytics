import os
import pickle
from typing import final

import pandas as pd
from dotenv import load_dotenv
from web3 import Web3

import constants

load_dotenv()

web3 = Web3(Web3.WebsocketProvider("wss://kovan.infura.io/ws/v3/{}".format(os.environ.get("INFURA_API_KEY"))))

def get_datetime_from_block(block_number: int):
    timestamp = web3.eth.get_block(block_number).timestamp
    return pd.to_datetime(timestamp, unit = "s")

def make_final_df():

    with open('raw_data/mints.pkl', 'rb') as handle:
        mints = pickle.load(handle)

    clean = []
    for mint in mints:
        clean_dict = {}
        clean_dict["caller_address"] = mint["args"]["minter"].lower()
        clean_dict["amount"] = mint["args"]["amount"]
        clean_dict["event"] = mint["event"]
        clean_dict["log_index"] = mint["logIndex"]
        clean_dict["transaction_index"] = mint["transactionIndex"]
        clean_dict["transaction_hash"] = mint["transactionHash"]
        clean_dict["block_hash"] = mint["blockHash"]
        clean_dict["block_number"] = mint["blockNumber"]
        clean.append(clean_dict)

    mints_df = pd.DataFrame(clean)

    bot_addresses = pd.read_csv("raw_data/bot_addresses.csv", names = ["address", "is_bot"])
    real_addresses = list(bot_addresses[bot_addresses["is_bot"] == False]["address"])
    bot_filter = mints_df.caller_address.isin(real_addresses)
    clean_df = mints_df[bot_filter]

    sorted_df = clean_df.sort_values(by=["block_number"])
    final_df = sorted_df.drop_duplicates(subset=["caller_address"]).reset_index(drop=True)

    final_df["datetime"] = final_df["block_number"].apply(get_datetime_from_block)

    final_df["unique_mint_number"] = final_df.index +1

    final_df = final_df.set_index(final_df["block_number"])

    final_df.to_csv("unique_mint_transactions.csv")

if __name__ == "__main__":
    make_final_df()
