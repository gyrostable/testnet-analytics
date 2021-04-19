import json
import os
import pickle
import urllib
import urllib.request
from itertools import tee
from typing import Iterable, List, Tuple, TypeVar
from urllib.parse import urljoin

import pandas as pd
from dotenv import load_dotenv
from ratelimit import limits

import constants

load_dotenv()

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

@limits(calls=5, period=1)
def call_api(bucket):
	URL =  'https://api-kovan.etherscan.io/api?module=account&action=txlistinternal&address={}&startblock={}&endblock={}&sort=asc&apikey={}'.format(constants.BOT_MASTER_CONTRACT, bucket[0], bucket[1], os.environ.get("ETHERSCAN_API_KEY"))
	data = urllib.request.urlopen(URL).read().decode()
	obj = json.loads(data)

	results = obj['result']

	if len(results) == 1000:
		raise Exception('Exceeded 10k limit for single API call. Try using more buckets.')

	if obj['message'] == 'NOTOK':
		raise Exception('API response: {}'.format(obj['message']))

	return obj


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

	master_list = []

	for bucket in windows:

		print('Getting data for bucket range' + str(bucket) + ' of ' + str(BUCKETS)+ ' ranges in total.')
		response = call_api(bucket)

		master_list.append(response['result'])	

	return master_list

def extract_bot_addresses(master_list: List):
	flat_txs = [item for sublist in master_list for item in sublist]
	bot_addresses = [transaction['to'] for transaction in flat_txs]

	with open('raw_data/bot_addresses.pkl', 'wb') as handle:
 		pickle.dump(bot_addresses, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	master_list = get_data(10000)
	extract_bot_addresses(master_list)





