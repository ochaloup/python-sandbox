# from https://github.com/serum-community/pyserum

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List
from pyserum.connection import get_live_markets
from pyserum.connection import conn
from pyserum.market import Market
from pyserum.market.types import MarketInfo
from solana.keypair import Keypair
from solana.rpc.api import Client
from tomlkit import key


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
        "--market-name",
        type=str,
        help="Market name (see https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json)",
        default='SOL/USDC'
    )
    parser.add_argument(
        "-c",
        "--connection",
        type=str,
        help="RPC connection URL (consider https://api.mainnet-beta.solana.com/ or https://mango.rpcpool.com/946ef7337da3f5b8d3e4a34e7f88)",
        default="https://api.mainnet-beta.solana.com/"
    )
    return parser.parse_args()

def get_market(market_name:str) -> MarketInfo:
    # pyserum.connection.get_token_mints()
    # token mint: https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/token-mints.json
    # markets: https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json
    markets: List[MarketInfo] = get_live_markets()
    market_info:MarketInfo = next(filter(lambda market: market.name == market_name, markets))
    if not market_info:
        raise ValueError(f'Market {market_name} is not available at Serum as a live market')
    return market_info



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



# TODO: make main :-)
######################### MAIN #########################
args = get_args()

keypair_file = Path(args.keypair)
if not keypair_file.is_file():
    raise ValueError(f"Provided path '{args.keypair}' to keypair does not exist or is not a file")
keypair = Keypair.from_secret_key(keypair_file.read_bytes())

market_info: MarketInfo = get_market(args.market_name)
rpc_connection: Client = conn(args.connection)

# Load the given market
print(f"Loading markets for {market_info.name} :: {market_info.address}")
market: Market = Market.load(rpc_connection, market_info.address)

# TODO: ...
market.place_order()


