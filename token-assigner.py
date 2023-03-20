# This script is used for having grinded vanity addres to be a Solana token account
# that could be moved to a different owner
# ----------------
# Requirements: 
## pip install solders argparse
# ----------------
# Usage:
## python token-assigner.py

import os
import json
from argparse import ArgumentParser
from pathlib import Path
from solders.message import Message # type: ignore
from solders.transaction import Transaction # type: ignore
from solders.system_program import transfer, TransferParams
from solders.pubkey import Pubkey as PublicKey # type: ignore
from solders.keypair import Keypair # type: ignore
from solana.rpc.api import Client
from solders.hash import Hash # type: ignore

SOL_TO_LAMPORTS = 1000000000

parser = ArgumentParser()
parser.add_argument('-u', '--rpc', metavar='', type=str, required=False, default="https://api.devnet.solana.com")
parser.add_argument('-k', '--keypair', metavar='', type=str, required=False, default="~/.config/solana/id.json")
args = parser.parse_args()

# args processing
args.keypair = args.keypair.strip()
if args.keypair.startswith('~'):
    args.keypair = os.path.expanduser(args.keypair)
path = Path(args.keypair)
with path.open() as f:
    keypair = json.load(f)
loaded_keypair = Keypair.from_bytes(bytes(keypair))

print('rpc to be used', args.rpc)
print('keypair pubkey loaded', loaded_keypair.pubkey())

instruction = transfer(
    TransferParams(
        from_pubkey = loaded_keypair.pubkey(),
        to_pubkey = PublicKey.from_string("7xUpLb33Bp3yGKVsARWzAQiYanXL1ujx3136qoJCLWXN"),
        lamports = SOL_TO_LAMPORTS
    )
)
client = Client(args.rpc, timeout=30)
recent_blockhash = client.get_recent_blockhash()
blockhash = Hash.from_string(recent_blockhash['result']['value']['blockhash'])
print(recent_blockhash)
message = Message([instruction], loaded_keypair.pubkey())
tx = Transaction([loaded_keypair], message, blockhash)
client.send_transaction(tx, loaded_keypair)