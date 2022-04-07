import pandas as pd
import pickle as pkl
import os
import json
import constants
from typing import Iterable, List, Tuple, TypeVar
from itertools import tee
from web3 import Web3
from dotenv import load_dotenv


# establish connection
load_dotenv()
infura_id = os.getenv("INFURA_API_ID")
web3 = Web3(Web3.WebsocketProvider(
    "wss://kovan.infura.io/ws/v3/" + infura_id))

# define contract information
challenges = '0x0416BF4141f731C0Ce217C0A0a95C39224d84817'
challenges_abi = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"checkName","type":"bytes32"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"bytes32","name":"value","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"metadata","type":"uint256"}],"name":"CheckCompleted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"checkName","type":"bytes32"}],"name":"CheckDeregistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"checkName","type":"bytes32"}],"name":"CheckRegistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"checkName","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"oldWeight","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newWeight","type":"uint256"}],"name":"CheckWeightChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[{"internalType":"bytes32","name":"checkName","type":"bytes32"},{"internalType":"bytes32","name":"value","type":"bytes32"}],"name":"checkValueExists","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"checkWeights","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"computeUserScore","outputs":[{"internalType":"uint256","name":"score","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bytes32","name":"checkName","type":"bytes32"}],"name":"didCompleteCheck","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"checkName","type":"bytes32"},{"internalType":"bytes32","name":"value","type":"bytes32"}],"name":"getCheckResult","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bytes32","name":"checkName","type":"bytes32"}],"name":"getCheckValue","outputs":[{"components":[{"internalType":"bool","name":"done","type":"bool"},{"internalType":"uint256","name":"metadata","type":"uint256"}],"internalType":"struct SybilCheck.CheckValue","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initializeOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"listChecks","outputs":[{"internalType":"bytes32[]","name":"checks","type":"bytes32[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"checkName","type":"bytes32"},{"internalType":"uint256","name":"weight","type":"uint256"}],"name":"registerCheck","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"checkName","type":"bytes32"}],"name":"removeCheck","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bytes32","name":"checkName","type":"bytes32"},{"internalType":"bytes32","name":"value","type":"bytes32"},{"internalType":"uint256","name":"metadata","type":"uint256"}],"name":"setCheckCompleted","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"checkName","type":"bytes32"},{"internalType":"uint256","name":"weight","type":"uint256"}],"name":"updateCheckWeight","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

contract = web3.eth.contract(address=challenges, abi=challenges_abi)


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

    passed_challenges = []
    passed_challenges_master = []

    for bucket in windows:
        print('Getting data for bucket range' + str(bucket) +
              ' of ' + str(BUCKETS) + ' ranges in total.')

        pass_filter = contract.events.CheckCompleted.createFilter(
            fromBlock=bucket[0], toBlock=bucket[1])
        passed_challenges = pass_filter.get_all_entries()
        passed_challenges_master.append(passed_challenges)

    flat_challengers = [
        item for sublist in passed_challenges_master for item in sublist]

    with open('/Users/jonas/Workspace/Local/Drop/challengers.pkl', 'wb') as handle:
        pkl.dump(flat_challengers, handle, protocol=pkl.HIGHEST_PROTOCOL)

# start
if __name__ == "__main__":
    get_data(5000)