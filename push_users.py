import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import click



@click.command()
@click.option('--user_file', 
       help='User file',
       required=True
       )
def main(user_file):
    uri = os.environ['MONGO_URI']
    client = MongoClient(uri, server_api=ServerApi('1'))
    agentv_db = client['agentv']
    users = agentv_db['user']
    
    with open(user_file, 'r') as f:
        us = json.load(f)
        
    result = users.insert_many(us)
    if result.acknowledged:
        print("Users are added")

if __name__ == '__main__':
    main()