import unittest
import pandas as pd 
from decimal import Decimal

from cspr_summarization.services.lp_hourly_summarizer import LpHourlySummarizer


class TestHourlySummarizer(unittest.TestCase):

  # Test sync summarizer
  def test_sync_summarizer(self):
    timestamp_string = '2023-01-09 09:55:39.648000 +00:00'
    timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
    start_hour = timestamp_obj.astimezone(pytz.UTC)

    timestamp_string = '2023-01-12 01:47:19.936000 +00:00'
    timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
    end_hour = timestamp_obj.astimezone(pytz.UTC)

    hourly_summarizer = LpHourlySummarizer(start_hour, end_hour)
    df_sync = pd.DataFrame({
      'id': [1, 2, 3, 4],
      'address':      ['cf56e3', 'cf56e3',
                       '800dee', '800dee'],
      'block_number': [1398801, 1398802, 
                       1398803, 1398804],
      'reserve0':     [144100081137, 143967281437,
                       1000000000, 59],
      'reserve1':     [919041928425877, 910434567551373,
                       919041928425879, 910434567551375]
    })

    expected_success_result = pd.DataFrame({
      'id': [4, 2],
      'address': ['800dee','cf56e3'],
      'block_number': [1398804, 1398802],
      'reserve0': [59, 143967281437],
      'reserve1': [910434567551375, 910434567551373]
    }, index=[3, 1])

    # get sync summarization data
    df_result = hourly_summarizer.sync_summarizer(df_sync)
    # test result should equal expected result
    self.assertTrue(expected_success_result.equals(df_result))

  # Test mint summarizer
  def test_mint_summarizer(self):
    timestamp_string = '2023-01-09 09:55:39.648000 +00:00'
    timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
    start_hour = timestamp_obj.astimezone(pytz.UTC)

    timestamp_string = '2023-01-12 01:47:19.936000 +00:00'
    timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
    end_hour = timestamp_obj.astimezone(pytz.UTC)

    hourly_summarizer = LpHourlySummarizer(start_hour, end_hour)
    df_mint = pd.DataFrame({
      'id': [1, 2, 3, 4],
      'address':      ['cf56e3', 'cf56e3',
                       '800dee', '800dee'],
      'block_number': [1398801, 1398802, 
                       1398803, 1398804],
      'amount0':     [144100081137, 143967281437,
                       1000000000, 59],
      'amount1':     [919041928425877, 910434567551373,
                       919041928425879, 910434567551375]
    })

    expected_success_result = pd.DataFrame({
      'num_mints': [2, 2],
      'mints_0': [Decimal(288067362574), Decimal(1000000059)],
      'mints_1': [Decimal(1829476495977250), Decimal(1829476495977254)]
    }, index=['cf56e3', '800dee'])

    # get summarized data
    df_result = hourly_summarizer.mint_summarizer(df_mint)
    # test result should equal expected result
    self.assertTrue(expected_success_result.equals(df_result))
  
  # Test burn summarizer
  def test_burn_summarizer(self):
    timestamp_string = '2023-01-09 09:55:39.648000 +00:00'
    timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
    start_hour = timestamp_obj.astimezone(pytz.UTC)

    timestamp_string = '2023-01-12 01:47:19.936000 +00:00'
    timestamp_obj = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f %z')
    end_hour = timestamp_obj.astimezone(pytz.UTC)

    hourly_summarizer = LpHourlySummarizer(start_hour, end_hour)
    df_burn = pd.DataFrame({
      'id': [1, 2, 3, 4],
      'address':      ['cf56e3', 'cf56e3',
                       '800dee', '800dee'],
      'block_number': [1398801, 1398802, 
                       1398803, 1398804],
      'amount0':     [144100081137, 143967281437,
                       1000000000, 59],
      'amount1':     [919041928425877, 910434567551373,
                       919041928425879, 910434567551375]
    })

    expected_success_result = pd.DataFrame({
      'num_burns': [2, 2],
      'burns_0': [Decimal(288067362574), Decimal(1000000059)],
      'burns_1': [Decimal(1829476495977250), Decimal(1829476495977254)]
    }, index=['cf56e3', '800dee'])

    # get summarized data
    df_result = hourly_summarizer.burn_summarizer(df_burn)
    # test result should equal expected result
    self.assertTrue(expected_success_result.equals(df_result))


if __name__ == '__main__':  
  unittest.main()