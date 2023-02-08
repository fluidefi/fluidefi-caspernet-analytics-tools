import psycopg2
import os
import pandas as pd
import numpy as np
from django.apps import apps

pd.set_option('display.max_columns', None)

gcp_conn = psycopg2.connect(
  host='localhost',
  dbname='casper_aggregator_db',
  user='postgres',
  password='postgres', #os.getenv('DB_PASSWORD'),
  port=5432,
)

# LP Block summarizer calculation

query = f'''select pair address, blocks.block_number, blocks.timestamp_utc timestamp_utc  
        from all_pairs ap 
        join pair_created_event pe on ap.contract_address = pe.pair
        join blocks on pe.block_number = blocks.block_number
        '''

#query = 'select * from all_pairs'
#df_all_pairs = pd.read_sql(query, gcp_conn)

#query = 'select * from pair_created_event'
#df_pair_created_event = pd.read_sql(query, gcp_conn)

#query = 'select * from blocks'
df_blocks = pd.read_sql_table('blocks', gcp_conn)



# Get the model
MyModel = apps.get_model('app_name', 'MyModel')

# Get the queryset
queryset = MyModel.objects.all()

# Convert the queryset to a list of dictionaries
data = list(queryset.values())

# Create the DataFrame
df = pd.DataFrame(data)


print(df_blocks)