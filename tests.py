import unittest

from thisisthebus.where.location import new_location, figure_out_datetime

global FRONTEND_DIR
FRONTEND_DIR = 'llamas'


# from thisisthebus.iotd.iotd_parser import determine_previous_and_subsequent
#
#
# class DayTests(unittest.TestCase):
#
#     def test_previous_and_subsequent(self):
#         dates = determine_previous_and_subsequent('2015-10-05')
#         self.assertEqual(len(dates), 3)


class LocationTests(unittest.TestCase):

    def test_make_new_location(self):
        figure_out_datetime("2010-05-25", "22:53:10")
        new_location()