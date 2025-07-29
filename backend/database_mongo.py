import os
from pymongo import MongoClient

# Get the MongoDB connection URL from the environment variables
MONGO_URL = os.environ.get('MONGO_DATABASE_URL')

# Create a client instance
client = MongoClient(MONGO_URL)

# This is a helper function we'll use in our API endpoints
# It makes it easy to get the database instance


def get_database():
    return client.impala_db  # We'll name our database 'impala_db'


# You can add a quick test here to verify the connection
if __name__ == '__main__':
    db = get_database()
    print("Successfully connected to MongoDB!")
    print(f"Server Info: {client.server_info()}")
