import csv
from decimal import Decimal
from operator import itemgetter

import requests
from brownie import chain, interface, web3
from cachetools import LRUCache, cached
from eth_abi import encode_single
from eth_utils import encode_hex
from tqdm import tqdm

api = 'https://safe-transaction.mainnet.gnosis.io/api/v1'
ychad = '0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52'


@cached(LRUCache(1000))
def token_name(address):
    if address is None:
        return 'ETH'
    if address == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85':
        return 'ENS'
    token = interface.ERC20(address)
    try:
        return token.symbol()
    except ValueError:
        return address


@cached(LRUCache(1000))
def decimals(address):
    token = interface.ERC20(address)
    try:
        return 10 ** token.decimals()
    except ValueError:
        return 1 # no info, fallback to raw value


@cached(LRUCache(1000))
def ens_token_id_to_name(token_id):
    subgraph = 'https://api.thegraph.com/subgraphs/name/ensdomains/ens'
    query = '{ domains(where: {labelhash: "%s"}) { name } }'
    labelhash = encode_hex(encode_single('uint', token_id))
    response = requests.post(subgraph, json={'query': query % labelhash})
    response.raise_for_status()
    try:
        return response.json()['data']['domains'][0]['name']
    except IndexError:
        return token_id


@cached(LRUCache(1000))
def ens_reverser(address):
    if address == ychad:
        return 'ychad.eth'
    reverser = web3.ens.reverser(address)
    if reverser is None:
        return address
    namehash = web3.ens.namehash(web3.ens.reverse_domain(address))
    name = reverser.caller().name(namehash)
    return name or address


def format_amount(x):
    if 'type' not in x or x['type'] == 'ETHER_TRANSFER':
        return Decimal(x['value']) / 10 ** 18
    elif x['type'] == 'ERC20_TRANSFER':
        return Decimal(x['value']) / decimals(x['tokenAddress'])
    elif x['type'] == 'ERC721_TRANSFER':
        return ens_token_id_to_name(int(x['tokenId']))
    raise NotImplementedError('unknown transfer type')


def parse_transaction(tx):
    if 'type' in tx:
        # incoming tx
        return {
            'date': tx['executionDate'],
            'from': ens_reverser(tx['from']),
            'to': ens_reverser(tx['to']),
            'amount': format_amount(tx),
            'currency': token_name(tx['tokenAddress']),
            'tx_hash': tx['transactionHash'],
        }
    else:
        # outgoing tx
        if not tx['isExecuted'] and not tx['isSuccessful']:
            return
        return {
            'date': tx['executionDate'],
            'from': ens_reverser(tx['safe']),
            'to': ens_reverser(tx['to']),
            'amount': format_amount(tx),
            'currency': token_name(None),
            'tx_hash': tx['transactionHash'],
        }


def populate_erc20_transfers(row):
    tx = chain.get_transaction(row['tx_hash'])
    tx.wait(1)
    if 'Transfer' not in tx.events:
        return []
    return [
        {
            'date': row['date'],
            'from': ens_reverser(t['from'] if 'from' in t else t['src']),
            'to': ens_reverser(t['to'] if 'to' in t else t['dst']),
            'amount': Decimal(t['value'] if 'value' in t else t['wad']) / decimals(t.address),
            'currency': token_name(t.address),
            'tx_hash': row['tx_hash'],
        }
        for t in tx.events['Transfer']
    ]


def fetch_transactions(address):
    starting_urls = [f'{api}/safes/{address}/transactions/', f'{api}/safes/{address}/incoming-transfers/']
    transactions = []
    for next_url in starting_urls:
        while next_url:
            print(next_url)
            response = requests.get(next_url)
            response.raise_for_status()
            data = response.json()
            next_url = data['next']
            for tx in tqdm(data['results']):
                parsed = parse_transaction(tx)
                if parsed is None:
                    continue
                transactions.append(parsed)
                # gnosis-safe api for outgoing txs omits erc20 trasnfers so we populate them by hand
                if str(parsed['from']) == 'ychad.eth':
                    transactions.extend(populate_erc20_transfers(parsed))

    return sorted(transactions, key=itemgetter('date'))


def write_csv(transactions, out_name):
    with open(out_name, 'wt') as f:
        header = 'date,from,to,amount,currency,tx_hash'.split(',')
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        writer.writerows(transactions)

    print(f'written to {out_name}')


def audit():
    write_csv(fetch_transactions(ychad), 'ychad-audit.csv')
