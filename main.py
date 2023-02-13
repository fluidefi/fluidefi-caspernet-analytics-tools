import sys
sys.dont_write_bytecode = True

# Django specific settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from cspr_summarization.entities.Blocks import *
from cspr_summarization.entities.UniswapV2Pair import UniswapV2Pair as AllPairs
from cspr_summarization.entities.PairCreatedEvent import *
from cspr_summarization.entities.PairBurnEvent import *
from cspr_summarization.entities.PairMintEvent import *
from cspr_summarization.entities.PairSwapEvent import *
from cspr_summarization.entities.PairSyncEvent import *
from cspr_summarization.entities.TokenTotalSupply import *
import pandas as pd
from cspr_summarization.services.lp_hourly_summarizer import LpHourlySummarizer
import pytz
from datetime import datetime




timestamp_string = '2023-01-09 09:55:00.000000 +00:00'
timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
start_hour = timestamp_obj.astimezone(pytz.UTC)

timestamp_string = '2023-01-09 10:00:00.000000 +00:00'
timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
end_hour = timestamp_obj.astimezone(pytz.UTC)


summarizer = LpHourlySummarizer()
summarizer.summarize(start_hour, end_hour)



############################################################################
## All the above code will be deleted from here it's just for testing
## it will refactored and moved to the lp_hourly_summarizer
############################################################################

# Get data from the database using the Django ORM
block_table = Blocks.objects.filter(timestamp_utc__gte).values('block_number', 'timestamp_utc')
df_blocks = pd.DataFrame.from_records(block_table)


all_pairs_table = AllPairs.objects.values('contract_address')
df_all_pairs = pd.DataFrame.from_records(all_pairs_table)

pair_created_event_table = PairCreatedEvent.objects.values('pair', 'block_number')
df_pair_created_event = pd.DataFrame.from_records(pair_created_event_table)

pair_burn_event_table = PairBurnEvent.objects.values('id', 'amount0', 'amount1', 'address', 'block_number')
df_pair_burn_event = pd.DataFrame.from_records(pair_burn_event_table)

pair_mint_event_table = PairMintEvent.objects.values('id', 'amoun0', 'amount1', 'address', 'block_number')
df_pair_mint_event = pd.DataFrame.from_records(pair_mint_event_table)

pair_swap_event_table = PairSwapEvent.objects.values('volume0_in', 'volume0_out', 'volume1_in', 'volume1_out', 'address', 'block_number')
df_pair_swap_event = pd.DataFrame.from_records(pair_swap_event_table)

pair_sync_event_table = PairSyncEvent.objects.values('address', 'block_number')
df_pair_sync_event = pd.DataFrame.from_records(pair_sync_event_table)

token_total_supply_table = TokenTotalSupply.objects.values('total_supply', 'token_address', 'block_number')
df_token_total_supply = pd.DataFrame.from_records(token_total_supply_table)

print(pair_created_event_table)




# Assuming that the data for the tables are stored in dataframes with the following names:
# all_pairs, pair_created_event, blocks, raw_pair_sync_event, raw_pair_swap_event, raw_pair_mint_event, raw_pair_burn_event, and token_total_supply

# Join the pair_created_event and all_pairs dataframes on the contract_address column
merged_df1 = pd.merge(df_all_pairs, df_pair_created_event, left_on='contract_address', right_on='pair', how='inner')

# Join the merged dataframe with the blocks dataframe on the block_number column
merged_df2 = pd.merge(merged_df1, df_blocks, on='block_number', how='inner')

# Perform left joins with the raw_pair_sync_event, raw_pair_swap_event, raw_pair_mint_event, and raw_pair_burn_event dataframes
merged_df3 = pd.merge(merged_df2, df_pair_sync_event, on=['address', 'block_number'], how='left')
merged_df4 = pd.merge(merged_df3, df_pair_mint_event, on=['address', 'block_number'], how='left')
merged_df5 = pd.merge(merged_df4, df_pair_burn_event, on=['address', 'block_number'], how='left')
#merged_df6 = pd.merge(merged_df5, df_pair_swap_event, on=['address', 'block_number'], how='left')

print(merged_df5.columns)
print(df_token_total_supply.columns)

# Perform a left join with the token_total_supply dataframe
final_df = pd.merge(merged_df5, df_token_total_supply, on=['token_address', 'block_number'], how='left')

# Use the "groupby" method to group the dataframe by the block_number and pair columns
grouped_df = final_df.groupby(['block_number', 'pair']).agg({
    'timestamp_utc': np.max,
    'reserve1': np.max,
    'reserve0': np.max,
    'id': {'num_mints': 'count'},
    'id': {'num_burns': 'count'},
    'amount0': {'mints_0': 'sum', 'burns_0': 'sum'},
    'amount1': {'mints_1': 'sum', 'burns_1': 'sum'},
    'amount0_in': {'volume_in_0': 'sum'},
    'amount1_in': {'volume_in_1': 'sum'},
    'amount0_out': {'volume_out_0': 'sum'},
    'amount1_out': {'volume_out_1': 'sum'},
    'close_lp_token_supply': np.max
})
print(grouped_df)
# Reset the index to make the



result = (
    Blocks.objects
    .filter(pair_created_event__address=F('pair'))
    .annotate(
        pair=F('paircreatedevent__pair'),
        sync_count=Count('rawpairsyncevent', filter=Q(rawpairsyncevent__address=F('pair')) & Q(rawpairsyncevent__block_number=F('block_number'))),
        mint_count=Count('rawpairmintevent', filter=Q(rawpairmintevent__address=F('pair')) & Q(rawpairmintevent__block_number=F('block_number'))),
        timestamp_utc=F('timestamp_utc'),
        total_supply=F('token_total_supply__total_supply'),
    )
    .values('block_number', 'pair', 'sync_count', 'mint_count', 'timestamp_utc', 'total_supply')
    .distinct()
)

df = pd.DataFrame.from_records(result)

