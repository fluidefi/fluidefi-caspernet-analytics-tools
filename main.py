import sys
sys.dont_write_bytecode = True

# Django specific settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from cspr_summarization.entities.HourlyData import HourlyData
import pandas as pd
from cspr_summarization.services.lp_hourly_summarizer import LpHourlySummarizer
import pytz
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)


start_hour = HourlyData.objects.values('close_timestamp_utc').order_by('-close_timestamp_utc').first()
start_hour = start_hour['close_timestamp_utc'].replace(microsecond=0, second=0, minute=0)
end_hour = (start_hour + timedelta(hours=1))



summarizer = LpHourlySummarizer(start_hour, end_hour)
summarizer.init_hourly_data()
if len(summarizer.last_hour_block_numbers) > 0 :
  summarizer.sync_consumer()
  summarizer.mint_consumer()
  summarizer.burn_consumer()
  summarizer.swap_consumer()
  summarizer.close_lp_token_supply_consumer()
  summarizer.max_block_consumer()
else:
  logging.info('No blocks have been created on the last hour')