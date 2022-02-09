# from https://github.com/serum-community/pyserum

import pyserum
from pyserum.connection import conn
from pyserum.market import Market

# pyserum.get_token_mints()
# token mint: https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/token-mints.json
# pyserum.get_live_markets()
# markets: https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json

# consider https://mango.rpcpool.com/946ef7337da3f5b8d3e4a34e7f88
rpcConnection = conn("https://api.mainnet-beta.solana.com/")

# market_address = "5LgJphS6D5zXwUVPU7eCryDBkyta3AidrJ5vjNU6BcGW" # Address for BTC/USDC
market_address = "7xMDbYTCqQEcK2aM9LbetGtNFJpzKdfXzLL5juaLh4GJ" # SOL/USDC

# Load the given market
print("Loading markets...")
market = Market.load(rpcConnection, market_address)
print(f'Market {market}')

print("Loading asks...")
asks = market.load_asks()

# Show all current ask order
print("Ask Orders:")
for ask in asks:
    print("Order id: %d, price: %f, size: %f." % (
          ask.order_id, ask.info.price, ask.info.size))
print("\n")
# Show all current bid order
print("Bid Orders:")
bids = market.load_bids()
for bid in bids:
    print(f"Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")