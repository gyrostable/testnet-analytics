# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 12:04:43 2021

@author: Ariah
"""

import json
import os
import time
import urllib.request

import pandas as pd
from dotenv import load_dotenv

import constants

'''Direct all_addresses to list of addresses we want to consider'''
all_addresses = pd.read_csv("raw_data/export-tokenholders-for-contract-0xd0474aEBA181987A81352842d446Fc6c65481417.csv")['HolderAddress']

'''check internal txs for coming from this address'''
bad_contract = "0x013F92F17E014F0c3182fb299Df9a7dec5Cab893"

'''load api_key from .env'''
load_dotenv()
api_key = os.getenv('ETHERSCAN_API_KEY')

#address_ok = '0x00000000b9d747ef42d224e572a5b7e6488929c8' #example
#address_bot = '0x5f04aDD14be953dECc50A0970423Dc760fd6Fe16' #example


###############################################################################

'''Compose Etherscan API url'''
def eth_url(module, action, address):
    if module not in ['account']:
        raise Exception('{} not valid module'.format(module))
    if action not in ['txlistinternal']:
        raise Exception('{} not valid action'.format(action))
    return 'http://api-kovan.etherscan.io/api?module={}&action={}&address={}&startblock={}&endblock={}&sort=asc'.format(module, action, address, constants.START_BLOCK, constants.END_BLOCK)

'''Query Etherscan API'''
def from_etherscan(url, api_key):
    url += '&apikey={}'.format(api_key)
    data = urllib.request.urlopen(url).read().decode()
    obj = json.loads(data)
    return obj

'''Checks whether Etherscan API limit has been used (5 calls/s)'''
def check_api_limit(data):
    if data['message'] == "NOTOK":
        return True
    
    return False

'''
Checks whether the given data contains transactions from the bot contract (bad_contract)
data input should be the txlistinternal for a given address
Outputs whether that address is a bot
'''
def check_for_bot(data, bad_contract):    
    assert check_api_limit(data) == False
    
    for entry in data["result"]:
        if entry['from'].lower() == bad_contract.lower():
            return True
    
    return False


'''
Checks which addresses are bots, i.e., contain transactions from the bot contract (bad_contract)
Input addresses is list of addresses to check
Returns dictionary with keys=addresses and values=True/False of whether address is a bot
Processing may take a while b/c of Etherscan API limiting
Console will print when it reaches each 1000 increment of addresses as status update
'''
def check_for_bots(all_addresses, bad_contract):
    bot_dict = {}
    count = 0
    for address in all_addresses:
        url = eth_url('account','txlistinternal',address)
        data = from_etherscan(url, api_key)
        if check_api_limit(data) == True:
            time.sleep(1)
            print("Sleeping 1 second")
            data = from_etherscan(url, api_key)
        
        is_bot = check_for_bot(data, bad_contract)
        count += 1
        if count % 1000 == 0:
            print(count)
        bot_dict[address] = is_bot
    
    return bot_dict


if __name__ == "__main__":
    bot_dict = check_for_bots(all_addresses, bad_contract)
    with open('raw_data/bot_addresses.csv','w') as f:
        for key in bot_dict.keys():
            f.write("{},{}\n".format(key, bot_dict[key]))


