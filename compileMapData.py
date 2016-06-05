# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 22:08:00 2016

Copyright (c) 2016 Joyce Kwong
All rights reserved
@author: jkwong
"""
import pickle
import getCensus
import getSchools

def main():
    # read in schools and census data
    print('Reading in school data')
    schoolData = getSchools.parseAllSchools()
    
    pickle.dump(schoolData, open('schoolData.p', "wb"))
    
    print('Reading in census data')
    censusData = getCensus.main()
    
    pickle.dump(censusData, open('censusData.p', "wb"))
    
if __name__ == "__main__":
    main()