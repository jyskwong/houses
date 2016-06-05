# -*- coding: utf-8 -*-
"""
Created on Tue May 31 22:00:00 2016
Module to test school district code

Copyright (c) 2016 Joyce Kwong
All rights reserved
@author: jkwong
"""

import unittest
from getSchools import *
import pandas as pd

class schoolTest(unittest.TestCase):
    def test(self):
        p = parseAllSchools()
        testData = pd.read_csv("mapdata/schools_test.csv")
        for s in testData.index:
            print("Checking address {}".format(testData.loc[s, "ADDRESS"]))
            coord = (testData.loc[s, "LATITUDE"], testData.loc[s, "LONGITUDE"])
            schools = getSchoolDistrict(coord, p)
            if not pd.isnull(testData.loc[s, "Elementary"]):
                self.assertEqual(testData.loc[s, "Elementary"], schools['E']['name'])
            if not pd.isnull(testData.loc[s, "Middle"]):
                self.assertEqual(testData.loc[s, "Middle"], schools['M']['name'])
            if not pd.isnull(testData.loc[s, "High"]):
                self.assertEqual(testData.loc[s, "High"], schools['H']['name'])
                
if __name__ == '__main__':
    unittest.main()
