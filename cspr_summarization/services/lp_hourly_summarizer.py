from cspr_summarization.entities.Blocks import *
from cspr_summarization.entities.UniswapV2Pair import UniswapV2Pair as AllPairs
from cspr_summarization.entities.PairCreatedEvent import *
from cspr_summarization.entities.PairBurnEvent import *
from cspr_summarization.entities.PairMintEvent import *
from cspr_summarization.entities.PairSwapEvent import *
from cspr_summarization.entities.PairSyncEvent import *
from cspr_summarization.entities.TokenTotalSupply import *
import pandas as pd


class LpHourlySummarizer:

  def summarize(self, start_hour, end_hour):
    # get the blocks that have been created between start_date and end_date
    block_table = Blocks.objects.filter(timestamp_utc__range=(start_hour, end_hour)).values('block_number', 'timestamp_utc').order_by('-timestamp_utc')
    df_blocks = pd.DataFrame.from_records(block_table)
    
  
    # get the pairs of those blocks (that means we get the pairs that have been created between start_hour and end_hour)
    pair_created_event_table = PairCreatedEvent.objects.filter(block_number__in=df_blocks['block_number'].values).values('pair')
    pair_created_event = pd.DataFrame.from_records(pair_created_event_table)
    print(pair_created_event)

