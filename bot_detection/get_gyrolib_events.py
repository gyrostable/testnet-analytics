import pickle
from itertools import tee
from typing import Iterable, List, Tuple, TypeVar

import pandas as pd
from web3 import Web3

import constants

GYROLIB_ADDRESS = '0x29e858A3d3AE4ab92426c8C279f8E8ae64Edfda7'
GYROLIB_ABI = '[{"inputs":[{"internalType":"address","name":"gyroFundAddress","type":"address"},{"internalType":"address","name":"externalTokensRouterAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"redeemer","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Redeem","type":"event"},{"inputs":[{"internalType":"address[]","name":"_tokensIn","type":"address[]"},{"internalType":"uint256[]","name":"_amountsIn","type":"uint256[]"}],"name":"estimateMintedGyro","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokensOut","type":"address[]"},{"internalType":"uint256[]","name":"_amountsOut","type":"uint256[]"}],"name":"estimateRedeemedGyro","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"externalTokensRouter","outputs":[{"internalType":"contract BalancerExternalTokenRouter","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"fund","outputs":[{"internalType":"contract GyroFundV1","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getReserveValues","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address[]","name":"","type":"address[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getSupportedPools","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getSupportedTokens","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initializeOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokensIn","type":"address[]"},{"internalType":"uint256[]","name":"_amountsIn","type":"uint256[]"},{"internalType":"uint256","name":"_minAmountOut","type":"uint256"}],"name":"mintFromUnderlyingTokens","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokensOut","type":"address[]"},{"internalType":"uint256[]","name":"_amountsOut","type":"uint256[]"},{"internalType":"uint256","name":"_maxRedeemed","type":"uint256"}],"name":"redeemToUnderlyingTokens","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_fundAddress","type":"address"}],"name":"setFundAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_routerAddress","type":"address"}],"name":"setRouterAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokensIn","type":"address[]"},{"internalType":"uint256[]","name":"_amountsIn","type":"uint256[]"},{"internalType":"uint256","name":"_minGyroMinted","type":"uint256"}],"name":"wouldMintChecksPass","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_tokensOut","type":"address[]"},{"internalType":"uint256[]","name":"_amountsOut","type":"uint256[]"},{"internalType":"uint256","name":"_maxGyroRedeemed","type":"uint256"}],"name":"wouldRedeemChecksPass","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

web3 = Web3(Web3.WebsocketProvider("wss://kovan.infura.io/ws/v3/3201d7e703354a42a098a6475baa127d"))

gyrolib_contract = web3.eth.contract(address=GYROLIB_ADDRESS, abi=GYROLIB_ABI)

T = TypeVar('T')

def generate_buckets(start: int, end: int, buckets: int) -> Iterable[int]:
	diff = (end - start) / buckets
	for i in range(buckets):
		yield start + diff *i
	yield end

def pairwise(iterable: Iterable[T]) -> Iterable[Tuple[T,T]]:
	a, b = tee(iterable)
	next(b, None)
	return zip(a, b)


def get_data(BUCKETS: int):
	"""
	:START_BLOCK: starting range of blocks
	:END_BLOCK: ending range of blocks
	"""
	buckets = generate_buckets(constants.START_BLOCK, constants.END_BLOCK, BUCKETS)
	ranges = list(pairwise(buckets))
	windows = []
	for window in ranges:
		couple = (int(window[0]), int(window[1] - 1))
		windows.append(couple)

	mint_master = []
	redeem_master = []

	for bucket in windows:

		print('Getting data for bucket range' + str(bucket) + ' of ' + str(BUCKETS)+ ' ranges in total.')

		mint_filter = gyrolib_contract.events.Mint.createFilter(fromBlock=bucket[0], toBlock=bucket[1])
		mints = mint_filter.get_all_entries()
		mint_master.append(mints)

		redeem_filter = gyrolib_contract.events.Redeem.createFilter(fromBlock=bucket[0], toBlock=bucket[1])
		redeems = redeem_filter.get_all_entries()
		redeem_master.append(redeems)

	flat_mints = [item for sublist in mint_master for item in sublist]
	with open('raw_data/mints.pkl', 'wb') as handle:
		pickle.dump(flat_mints, handle, protocol=pickle.HIGHEST_PROTOCOL)
	
	# flat_redeems = [item for sublist in redeem_master for item in sublist]
	# with open('raw_data/redeems.pkl', 'wb') as handle:
	# 	pickle.dump(flat_redeems, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    get_data(2000)
