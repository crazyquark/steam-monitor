import os
import datetime
from pymongo import MongoClient
from config.mongo import MONGO_PATH

def connect_mongo():
    from urllib.parse import quote_plus
    uri = "mongodb://%s:%s@%s" % (
        quote_plus(os.environ['MONGO_INITDB_ROOT_USERNAME']), quote_plus(os.environ['MONGO_INITDB_ROOT_PASSWORD']), quote_plus(MONGO_PATH))
    client = MongoClient(uri)

    return client

def store(data, client  = connect_mongo()):
    db = client.kraken
    eth_price_history = db.eth_price_history
    btc_price_history = db.btc_price_history

    # Price at which the last tx closed
    last_eth_price = data['XETHZEUR']['c'][0]
    last_btc_price = data['XXBTZEUR']['c'][0]

    eth_id = eth_price_history.insert_one({
        'price': last_eth_price,
        'date': datetime.datetime.now(tz=datetime.timezone.utc),
    }).inserted_id
    print(eth_id)

    btc_id = btc_price_history.insert_one({
        'price': last_btc_price,
        'date': datetime.datetime.now(tz=datetime.timezone.utc),
    }).inserted_id
    print(btc_id)