# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 21:53:06 2016

@author: jkwong
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May 31 22:00:00 2016
Module to test census data code
@author: jkwong
"""

import unittest
import getCensus
import pandas as pd

class censusTest(unittest.TestCase):
    def test(self):
        censusData = getCensus.main()
        testData = pd.read_csv("mapdata/schools_test.csv")
        for s in testData.index:
            print("Checking address {}".format(testData.loc[s, "ADDRESS"]))
            coord = (testData.loc[s, "LATITUDE"], testData.loc[s, "LONGITUDE"])
            (tract, medianIncome) = getCensus.getCensusData(coord, censusData)
            if not pd.isnull(testData.loc[s, "Median Income"]):
                self.assertEqual(testData.loc[s, "Median Income"], medianIncome)

                
if __name__ == '__main__':
    unittest.main()