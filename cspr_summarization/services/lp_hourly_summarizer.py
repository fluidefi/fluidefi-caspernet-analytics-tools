from cspr_summarization.entities.Blocks import *
from cspr_summarization.entities.UniswapV2Pair import UniswapV2Pair as AllPairs
from cspr_summarization.entities.PairCreatedEvent import *
from cspr_summarization.entities.PairBurnEvent import *
from cspr_summarization.entities.PairMintEvent import *
from cspr_summarization.entities.PairSwapEvent import *
from cspr_summarization.entities.PairSyncEvent import *
from cspr_summarization.entities.TokenTotalSupply import *
import pandas as pd
from django.db.models import F
import decimal

class LpHourlySummarizer:

  def summarize(self, start_hour, end_hour):
    # get the blocks that have been created between start_date and end_date
    block_table = Blocks.objects.values('block_number', 'timestamp_utc').order_by('-timestamp_utc')
      #.filter(timestamp_utc__range=(start_hour, end_hour))
    df_blocks = pd.DataFrame.from_records(block_table)
    
    last_hour_block_numbers = df_blocks['block_number'].values

  
    # get the pairs of those blocks (that means we get the pairs that have been created between start_hour and end_hour)
    pair_created_event_table = PairCreatedEvent.objects.filter(block_number__in=last_hour_block_numbers).values('pair', 'block_number')
    df_pair_created_event = pd.DataFrame.from_records(pair_created_event_table)

    last_hour_pairs = df_pair_created_event['pair'].values
    #print('Pair created')
    #print(df_pair_created_event)
    # all pairs
    all_pairs_table = AllPairs.objects.filter(contract_address__in=df_pair_created_event['pair'].values).values('contract_address')
    df_all_pairs = pd.DataFrame.from_records(all_pairs_table)
    #print('All pairs')
    #print(df_all_pairs)

    print('close_reserves')
    sync_table = PairSyncEvent.objects.values()
    df_sync = pd.DataFrame.from_records(sync_table)
    close_reserves_0 = df_sync.groupby('address').agg({'block_number': 'max', 'reserve0': 'first'})
    close_reserves_1 = df_sync.groupby('address').agg({'block_number': 'max', 'reserve1': 'first'})

    print('mints')
    mints_table = PairMintEvent.objects.filter(block_number__in=last_hour_block_numbers).values('id','address', 'block_number', 'amount0', 'amount1')
    df_mints = pd.DataFrame.from_records(mints_table)
    # count & sum mints group by address (aka pair)
    df_num_mints = df_mints.groupby('address')['id'].count().reset_index(name='num_mints')
    df_mint0 = df_mints.groupby('address')['amount0'].sum().reset_index(name='mints_0')
    df_mint1 = df_mints.groupby('address')['amount1'].sum().reset_index(name='mints_1')

    print('burns')
    burns_table = PairBurnEvent.objects.filter(block_number__in=last_hour_block_numbers).values('id', 'address', 'block_number', 'amount0', 'amount1')
    df_burns = pd.DataFrame.from_records(burns_table)
    # count mints group by address (aka pair)
    df_num_burns = df_burns.groupby('address')['id'].count().reset_index(name='num_burns')
    df_burns0 = df_burns.groupby('address')['amount0'].sum().reset_index(name='burns_0')
    df_burns1 = df_burns.groupby('address')['amount1'].sum().reset_index(name='burns_1')
    print(df_num_burns)
    print(df_burns0)
    print(df_burns1)

    print('volumes')
    swap_table = PairSwapEvent.objects.filter(block_number__in=last_hour_block_numbers).values()
    #... continue here

    max_block_per_pair = df_pair_created_event.groupby('pair')['block_number'].max().reset_index(name='max_block')
    max_block_per_pair_list = max_block_per_pair[['pair', 'max_block']].apply(tuple, axis=1).tolist()
    total_supply_table = TokenTotalSupply.objects.filter(token_address__block_number__in = max_block_per_pair_list).values()
    total_supply = pd.DataFrame.from_records(total_supply_table)
    print(total_supply)
    print(max_block_per_pair)
