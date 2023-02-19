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




timestamp_string = '2023-01-09 09:55:39.648000 +00:00'
timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
start_hour = timestamp_obj.astimezone(pytz.UTC)

timestamp_string = '2023-01-12 01:47:19.936000 +00:00'
timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
end_hour = timestamp_obj.astimezone(pytz.UTC)


summarizer = LpHourlySummarizer(start_hour, end_hour)
summarizer.init_hourly_data()
summarizer.sync_summarization()
summarizer.mint_summarization()
summarizer.burn_summarization()
summarizer.swap_summarization()
summarizer.update_close_lp_token_supply()
summarizer.set_max_block()
