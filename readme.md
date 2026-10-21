# ychad.eth audit

produce a csv with all incoming and outgoing transactions of [yearn multisig](https://gnosis-safe.io/app/#/safes/0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52/transactions)

## installation

- install python 3.10+
- pip install -r requirements.txt
- pip install -U -r security-overrides.txt (eth-brownie pins old certifi/aiohttp/urllib3)

## usage

```
brownie run ychad audit
```
