import unittest

global FRONTEND_DIR
FRONTEND_DIR = 'llamas'


from thisisthebus.iotd.iotd_parser import determine_previous_and_subsequent


class DayTests(unittest.TestCase):

    def test_previous_and_subsequent(self):
        dates = determine_previous_and_subsequent('2015-10-05')
        self.assertEqual(len(dates), 3)
