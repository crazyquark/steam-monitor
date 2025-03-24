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


def store(data, client=connect_mongo()):
    db = client.steam
    user = data['user']
    user_db = db[user]
    print(data)

    del data['user']
    user_db.insert_one(data)
