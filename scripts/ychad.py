"""Yearn Vaults Aug-Oct Funding Request (Issue #354) budget entry generator."""
from __future__ import annotations

import json
from pathlib import Path

BUDGET_PERIOD = "2024-08 to 2024-10"
PRODUCT = "Vaults V3"

FUNDING_REQUESTS = {
    "Smart Contract Code and Strategy Development": 135_000,
    "Security and Monitoring": 44_550,
    "Business Development": 27_500,
    "WebOps": 90_216,
    "Production Engineering": 45_000,
}

TOTAL_FUNDING = sum(FUNDING_REQUESTS.values())


def build_budget_entry() -> dict:
    """Return a structured budget entry for the Vaults Aug-Oct funding request."""
    return {
        "issue": 354,
        "product": PRODUCT,
        "period": BUDGET_PERIOD,
        "line_items": [
            {"category": category, "amount_usd": amount}
            for category, amount in FUNDING_REQUESTS.items()
        ],
        "total_usd": TOTAL_FUNDING,
    }


def write_budget_json(output_path: str | Path = "budget_vaults_aug_oct.json") -> Path:
    """Write the budget entry to a JSON file and return the path."""
    path = Path(output_path)
    path.write_text(json.dumps(build_budget_entry(), indent=2) + "\n")
    return path


if __name__ == "__main__":
    written = write_budget_json()
    print(f"Wrote {written} ({TOTAL_FUNDING:,} USD total)")
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
    except (OverflowError, ValueError): # BadFunctionCallOutput
        return address

@cached(LRUCache(1000))
def decimals(address):
    token = interface.ERC20(address)
    try:
        return 10 ** token.decimals()
    except (OverflowError, ValueError): # BadFunctionCallOutput
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
            'nonce': '',
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
            'nonce': tx['nonce'],
            'amount': format_amount(tx),
            'currency': token_name(None),
            'tx_hash': tx['transactionHash'],
        }


def populate_erc20_transfers(row):
    tx = chain.get_transaction(row['tx_hash'])
    tx.wait(1)
    if 'Transfer' not in tx.events:
        return []

    dst = ['to', '_to', 'dst', 'receiver']
    src = ['from', '_from', 'src', 'sender']
    wad = ['value', '_value', 'wad', 'amount']
    return [
        {
            'date': row['date'],
            'from': ens_reverser(next(t[k] for k in src if k in t)),
            'to': ens_reverser(next(t[k] for k in dst if k in t)),
            'amount': Decimal(next(t[k] for k in wad if k in t)) / decimals(t.address),
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
        header = 'date,from,to,nonce,amount,currency,tx_hash'.split(',')
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        writer.writerows(transactions)

    print(f'written to {out_name}')


def audit():
    write_csv(fetch_transactions(ychad), 'ychad-audit.csv')
