import unittest
from scripts.hidden_paid_radar import cash, jobbi, swarmmemo

class TestRadar(unittest.TestCase):
 def test_real_cash_not_platform_credits(self):
  self.assertEqual(cash({"reward":{"currency":"USDC","amount":3}}),3)
  self.assertIsNone(cash({"reward":{"currency":"CREDITS","amount":100}}))
 def test_reject_staking_and_high_prices(self):
  result,count=jobbi({"items":[
    {"title":"Python API repair","reward":{"currency":"USD","amount":4},"url":"https://example.test/1"},
    {"title":"Stake required for Python job","reward":{"currency":"USD","amount":4}},
    {"title":"Python API big job","reward":{"currency":"USD","amount":40}},
  ]})
  self.assertEqual(count,3)
  self.assertEqual(len(result),1)
 def test_closed_seats_excluded(self):
  result,count=swarmmemo({"works":[
    {"title":"API QA","id":"a","reward":{"usdc":"0.20"},"standing":{"open":1}},
    {"title":"API QA","id":"b","reward":{"usdc":"0.30"},"standing":{"open":0}},
  ]})
  self.assertEqual(count,2)
  self.assertEqual(len(result),1)

if __name__=="__main__":unittest.main()
