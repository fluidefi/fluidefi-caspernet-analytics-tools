from cspr_summarization.entities.Blocks import *
from cspr_summarization.entities.UniswapV2Pair import UniswapV2Pair as AllPairs
from cspr_summarization.entities.PairCreatedEvent import *
from cspr_summarization.entities.PairBurnEvent import *
from cspr_summarization.entities.PairMintEvent import *
from cspr_summarization.entities.PairSwapEvent import *
from cspr_summarization.entities.PairSyncEvent import *
from cspr_summarization.entities.TokenTotalSupply import *
from cspr_summarization.entities.HourlyData import *
import pandas as pd
import numpy as np
from django.db.models import F
from decimal import Decimal

class LpHourlySummarizer2:
  
  def __init__(self, start_hour, end_hour):
    self.start_hour = start_hour
    self.end_hour = end_hour
    blocks = Blocks.objects.filter(timestamp_utc__range=(self.start_hour, self.end_hour)).values('block_number', 'timestamp_utc').order_by('-timestamp_utc')
    self.last_hour_block_numbers = pd.DataFrame.from_records(blocks)
    all_pairs = AllPairs.objects.values('id', 'contract_address', 'token0_decimals', 'token1_decimals', 'token0_address', 'token1_address')
    self.all_pairs = pd.DataFrame.from_records(all_pairs)
  
  '''
  # create a record for each pair, with all values at zero
  '''
  def init_hourly_data(self):
    for index, pair in self.all_pairs.iterrows():
      hourly_data = HourlyData(pair['contract_address'], self.start_hour, self.end_hour)
      hourly_data.save()

  
  '''
  # setter needed for tests  
  '''
  def set_last_hour_block_numbers(self, last_hour_block_numbers):
    self.last_hour_block_numbers = last_hour_block_numbers
  
  '''
  # setter needed for tests  
  '''
  def set_all_airs(self, all_pairs):
    self.all_pairs = all_pairs

  '''
  # SyncEvents Summarization
  '''
  def sync_summarization(self):
    sync_table = PairSyncEvent.objects.filter(block_number__in=self.last_hour_block_numbers['block_number'].values).values('id', 'address','block_number', 'reserve0', 'reserve1')
    df_sync = pd.DataFrame.from_records(sync_table)
    # group by address and get reserve0 and reserve1 for the max block_number of each address
    close_reserves = df_sync.groupby('address').agg({'block_number': 'max', 'reserve0': 'first', 'reserve1': 'first'})
    # after the above agg, the address is considered as an index
    for address, item in close_reserves.iterrows():    
      # Updte DB rows
      HourlyData.objects.filter(address=address, open_timestamp_utc=self.start_hour).update(close_reserves_0=item['reserve0'], close_reserves_1=item['reserve1'])

  '''
  # MintEvents Summarization 
  '''
  def mint_summarization(self):
    mint_table = PairMintEvent.objects.filter(block_hash__in=self.last_hour_block_numbers['block_number'].values).values('id', 'address', 'block_number', 'amount0', 'amount1')#
    df_mint = pd.DataFrame.from_records(mint_table)
    # mints_sum_result
    mints_sum_result = pd.DataFrame({'num_mints':[], 'mints_0': [], 'mints_1': []})

    # loop through addresses within df_mint
    for index, pair in df_mint.iterrows():
      if pair['address'] in  mints_sum_result.index:
        mint_sum = mints_sum_result.loc[pair['address']]
        mint0 = Decimal(mint_sum['mints_0']) + Decimal(pair['amount0'])
        mint1 = Decimal(mint_sum['mints_1']) + Decimal(pair['amount1'])
        num_mints = mint_sum['num_mints'] + 1
        mints_sum_result.loc[pair['address']] = [num_mints, mint0, mint1]
      else:
        mints_sum_result.loc[pair['address']] = [1, pair['amount0'], pair['amount1']]
    for address, item in mints_sum_result.iterrows():
      HourlyData.objects.filter(address=address, open_timestamp_utc=self.start_hour).update(num_mints=item['num_mints'], mints_0=item['mints_0'], mints_1=item['mints_1'])

  '''
  # BurnEvents Summarization 
  '''
  def burn_summarization(self):
    burn_table = PairBurnEvent.objects.filter(block_hash__in=self.last_hour_block_numbers['block_number'].values).values('id', 'address', 'block_number', 'amount0', 'amount1')
    df_burn = pd.DataFrame.from_records(burn_table)
    # burns_sum_result
    burns_sum_result = pd.DataFrame({'num_burns':[], 'burns_0': [], 'burns_1': []})
    # loop through addresses within df_burn
    for index, pair in df_burn.iterrows():
      if pair['address'] in  burns_sum_result.index:
        burn_sum = burns_sum_result.loc[pair['address']]
        burn0 = Decimal(burn_sum['burns_0']) + Decimal(pair['amount0'])
        burn1 = Decimal(burn_sum['burns_1']) + Decimal(pair['amount1'])
        num_burns = burn_sum['num_burns'] + 1
        burns_sum_result.loc[pair['address']] = [num_burns, burn0, burn1]
      else:
        burns_sum_result.loc[pair['address']] = [1, pair['amount0'], pair['amount1']]
    for address, item in burns_sum_result.iterrows():
      HourlyData.objects.filter(address=address, open_timestamp_utc=self.start_hour).update(num_burns=item['num_burns'], burns_0=item['burns_0'], burns_1=item['burns_1'])
  
  '''
  # Close lp token supply
  '''
  def update_close_lp_token_supply(self):
    token_total_supply_table = TokenTotalSupply.objects.values()
    df_token_supply = pd.DataFrame.from_records(token_total_supply_table)
    close_total_supply = df_token_supply.groupby('token_address').agg({'block_number': 'max', 'total_supply': 'first'})
    for address, item in close_total_supply.iterrows():
      HourlyData.objects.filter(address=address, open_timestamp_utc=self.start_hour).update(close_lp_token_supply=item['total_supply'])
  
  '''
  # SwapEvents Summarization
  '''
  def swap_summarization(self):
    print('')
    
