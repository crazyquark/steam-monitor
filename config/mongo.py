import os
MONGO_PATH = 'mongo:27017' if os.environ.get(
    'CONTAINER') == 'docker' else 'localhost:27018'
