import os
from dotenv import load_dotenv

load_dotenv()

host='localhost'
dbname='casper_aggregator_db'
user='postgres'
password='postgres' #os.getenv('DB_PASSWORD'),
port=5432  # TODO - change this to the tunnel port yu are using for fl_agg_univ2
