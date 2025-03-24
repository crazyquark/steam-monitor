import os
MONGO_PATH = 'mongo_steam:27017' if os.environ.get('CONTAINER') == 'docker' else 'localhost:27017'
