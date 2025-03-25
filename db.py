import os
from pymongo import MongoClient
from config.mongo import MONGO_PATH


def connect_mongo():
    from urllib.parse import quote_plus
    uri = "mongodb://%s:%s@%s" % (
        quote_plus(os.environ['MONGO_INITDB_ROOT_USERNAME']), quote_plus(os.environ['MONGO_INITDB_ROOT_PASSWORD']), quote_plus(MONGO_PATH))
    client = MongoClient(uri)

    return client


def get_data(user, dbname, single=True, client=connect_mongo()):
    db = client.steam[user][dbname]
    return db.find_one() if single else db.find()


def store(data, dbname, client=connect_mongo()):
    if not dbname:
        return

    user = data['user']
    db = client.steam[user][dbname]
    print(data)

    del data['user']
    db.insert_one(data)
