import pandas as pd
import pickle as pkl
import os
import json
import constants
from typing import Iterable, List, Tuple, TypeVar
from itertools import tee
from web3 import Web3
from dotenv import load_dotenv

# establish blockchain connection
load_dotenv()
infura_id = os.getenv("INFURA_API_ID")
web3 = Web3(Web3.WebsocketProvider(
    "wss://kovan.infura.io/ws/v3/" + infura_id))

# define contract information: mint
level1 =  Web3.toChecksumAddress('0x4Ac61ff8EEca99d67f434e60dacf638F546E4cBD')
level1_abi = json.loads('[{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "user","type": "address"}],"name": "LevelCompleted","type": "event"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "previousOwner","type": "address"},{"indexed": true,"internalType": "address","name": "newOwner","type": "address"}],"name": "OwnershipTransferred","type": "event"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "user","type": "address"},{"indexed": false,"internalType": "bytes32","name": "tx1","type": "bytes32"},{"indexed": false,"internalType": "bytes32","name": "tx2","type": "bytes32"}],"name": "TransactionsSet","type": "event"},{"inputs": [],"name": "clearPendingUsers","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "getPendingUsers","outputs": [{"internalType": "address[]","name": "","type": "address[]"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "user","type": "address"}],"name": "hasPlayed","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "user","type": "address"}],"name": "hasSucceeded","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "initializeOwner","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "owner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "renounceOwnership","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "user","type": "address"},{"internalType": "bool","name": "completed","type": "bool"}],"name": "setCompleted","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "bytes32","name": "tx1","type": "bytes32"},{"internalType": "bytes32","name": "tx2","type": "bytes32"}],"name": "setTransactions","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "newOwner","type": "address"}],"name": "transferOwnership","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "","type": "address"}],"name": "users","outputs": [{"internalType": "bool","name": "waitingForCheck","type": "bool"},{"internalType": "bool","name": "completed","type": "bool"},{"internalType": "bytes32","name": "tx1","type": "bytes32"},{"internalType": "bytes32","name": "tx2","type": "bytes32"}],"stateMutability": "view","type": "function"}]')

# # define contract information: gyd to samm
# level1 =  Web3.toChecksumAddress('0xd0474aEBA181987A81352842d446Fc6c65481417')

contract = web3.eth.contract(address=level1, abi=level1_abi)

#  define time periods
T = TypeVar('T')

def generate_buckets(start: int, end: int, buckets: int) -> Iterable[int]:
    diff = (int(end) - int(start)) / buckets
    for i in range(buckets):
        yield int(start) + int(diff) * i
    yield end


def pairwise(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

#  request data in time periods
def get_data(BUCKETS: int):
    """
    :START_BLOCK: starting range of blocks
    :END_BLOCK: ending range of blocks
    """
    buckets = generate_buckets(
        constants.START_BLOCK, constants.END_BLOCK, BUCKETS)
    ranges = list(pairwise(buckets))
    windows = []
    for window in ranges:
        couple = (int(window[0]), int(window[1]) - 1)
        windows.append(couple)

    completions_master = []

    for bucket in windows:
        print('Getting data for bucket range' + str(bucket) +
              ' of ' + str(BUCKETS) + ' ranges in total.')
        
# ---------------------------------
#    filter for relevant events
# ---------------------------------

        pass_filter = contract.events.LevelCompleted.createFilter(
            fromBlock=bucket[0], toBlock=bucket[1])
        completions = pass_filter.get_all_entries()
        completions_master.append(completions)

    flat_completions = [
        item for sublist in completions_master for item in sublist]

    with open('/Users/jonas/Workspace/Local/Drop/early_levels_raw_data/lvl2_arb.pkl', 'wb') as handle:
        pkl.dump(flat_completions, handle, protocol=pkl.HIGHEST_PROTOCOL)

# start
if __name__ == "__main__":
    get_data(10000)