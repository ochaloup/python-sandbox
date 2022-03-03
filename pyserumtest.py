# from https://github.com/serum-community/pyserum

from argparse import ArgumentParser, Namespace
from http import client
from json import load as json_load_file, loads as json_load, dumps as json_dumps
from os import path
from pathlib import Path
from pyserum.connection import get_live_markets
from pyserum.connection import conn
from pyserum.market import Market
from pyserum.market.types import MarketInfo
from pyserum.open_orders_account import OpenOrdersAccount
from pyserum.enums import OrderType, Side
from requests import Session
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.types import TxOpts, TokenAccountOpts
from tomlkit import key
from typing import List

SPL_PROGRAM_ID  = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
TOKEN_LIST_URL = 'https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json'

######################### FUNCTIONS #########################
def get_args() -> Namespace:
    parser= ArgumentParser(description="PySerum API testing program")
    parser.add_argument(
        "-k",
        "--keypair",
        type=str,
        help="Path to a file with a keypair",
        required=True
    )
    parser.add_argument(
        "-m",
        "--market-name",  # pair name available at serum, like: SOL/USDC
        type=str,
        help="Market name as pair name (see https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json)",
        default="SOL/USDC"
    )
    parser.add_argument(
        "-s",
        "--side",
         type=str.upper, 
         default="SELL",
         choices=["BUY", "SELL"],
         help="Placing order to what side: BUY or SELL"
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="RPC connection URL (consider https://api.mainnet-beta.solana.com/ or https://mango.rpcpool.com/946ef7337da3f5b8d3e4a34e7f88)",
        default="https://mango.rpcpool.com/946ef7337da3f5b8d3e4a34e7f88"
    )
    return parser.parse_args()


def get_market_from_pair_name(pair_name:str) -> MarketInfo:
    # pyserum.connection.get_token_mints()
    # token mint: https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/token-mints.json
    # markets: https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json
    markets: List[MarketInfo] = get_live_markets()
    market_info:MarketInfo = next(filter(lambda market: market.name == pair_name, markets))
    if not market_info:
        raise ValueError(f'Market {pair_name} is not available at Serum as a live market')
    return market_info


def load_token_list():
    with Session() as session:
        response = session.get(TOKEN_LIST_URL)
        if response.status_code != 200:
            raise Exception(
                f"Cannot get data from {TOKEN_LIST_URL}, "
                f"response: {response.status_code}"
            )
        json_parsed = json_load(response.text)
        # for token in json_parsed["tokens"]:
        #     print(f">>> {token['address']}")
        if 'tokens' not in json_parsed:
            return None
        return json_parsed['tokens']


def show_orders(market:Market, limit:int = 5) -> None:
    print("Ask Orders:")
    asks = market.load_asks()
    for index, ask in enumerate(asks):
        print("Ask order id: %d, price: %f, size: %f." % (
            ask.order_id, ask.info.price, ask.info.size))
        if index >= limit:
            break

    print("Bid Orders:")
    bids = market.load_bids()
    for index, bid in enumerate(bids):
        print(f"Bid order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")
        if index >= limit:
            break


def load_keypair_file(filename: str) -> bytes:
    if not path.isfile(filename):
        raise ValueError(f"File with key '{filename}' does not exist")
    else:
        with open(filename) as key_file:
            data = json_load_file(key_file)
            return bytes(bytearray(data))


# TODO: make main :-)
######################### MAIN #########################
args = get_args()

keypair_file = Path(args.keypair)
if not keypair_file.is_file():
    raise ValueError(f"Provided path '{args.keypair}' to keypair does not exist or is not a file")
keypair = Keypair.from_secret_key(load_keypair_file(keypair_file))

# converting e.g. SOL/USDC to market metadata loaded from Serum, e.g. getting what is Solana address of the "pair/market" at Serum
market_info: MarketInfo = get_market_from_pair_name(args.market_name)
rpc_connection: Client = conn(endpoint=args.url, timeout=30)

# Load the given market
print(f"Loading markets for {market_info.name} :: {market_info.address}")
market: Market = Market.load(rpc_connection, market_info.address)

print(f"Loading existing token mint addresses in Solana ecosystem")
solana_existing_tokens = load_token_list()
(buy_token, sell_token) = tuple(args.market_name.split('/'))  # TODO: market name splitter could be maybe different
if not buy_token or not sell_token:
    raise Exception(f"Cannot split market pair name {args.market_name} to two sides")

placing_side = Side.BUY if Side.BUY.name == args.side else Side.SELL
token_name = buy_token if placing_side == Side.BUY else sell_token
token_info = next(filter(lambda token_data: token_data["symbol"] == token_name, solana_existing_tokens))
token_mint_address = token_info['address']
print(f"Going to {'BUY' if placing_side == Side.BUY else 'SELL'} with token {token_name} with mint address {token_mint_address}")

print(f"Loading SPL token addresses for {keypair.public_key}")
token_opts = TokenAccountOpts(program_id=SPL_PROGRAM_ID, encoding="jsonParsed")
resp = rpc_connection.get_token_accounts_by_owner(keypair.public_key, token_opts)
if 'result' not in resp or 'value' not in resp['result']:
    raise Exception(f'Getting token accounts by owner failed as no result provided: {resp}')
owning_spl_tokens = resp['result']['value']
try:
    spl_token_info = next(filter(lambda spl_token: spl_token["account"]["data"]["parsed"]["info"]["mint"] == token_mint_address, owning_spl_tokens))
    spl_token_address = spl_token_info["pubkey"]
except StopIteration:
    raise Exception(
        f"Account {keypair.public_key} does not own token with mint address {token_mint_address}"
        f"That address is received from fact of wanting to place order for token {token_name}"
    )
print(f'>>>>> {spl_token_address}')

# when no open order account exists, it's created
# payer is the SPL token account that will place the token amount at exchange
# owner is the wallet that can confirm/sing the token placing
print(f"Placing order for public key: {keypair.public_key}")
market.place_order(
    payer=spl_token_address,
    owner=keypair,
    side=Side.BUY,
    order_type=OrderType.LIMIT,
    limit_price=100.0,
    max_quantity=0.001,
    opts=TxOpts(skip_confirmation=False),
)

print(f"Loading Open Orders Account for owner public key: {keypair.public_key}")
open_orders_accounts: List[OpenOrdersAccount] = market.find_open_orders_accounts_for_owner(owner_address=keypair.public_key)
print(f'{open_orders_accounts}')

