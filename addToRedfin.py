# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 22:00:39 2016

taken CSV dumped from redfin
add school district and census info
Copyright (c) 2016 Joyce Kwong
All rights reserved
@author: jkwong
"""


import pandas as pd
import os
import re
import pickle
import getSchools
import getCensus

REDFIN_SOURCE_PATH = './redfin_source'
REDFIN_OUT_PATH = './redfin_data'

def main():
    os.system("mkdir -p {}".format(REDFIN_OUT_PATH))

    #load school and census data
    schoolData = pickle.load(open('schoolData.p', 'rb'))
    censusData = pickle.load(open('censusData.p', 'rb'))
    first = 1
    
    for filename in os.listdir(REDFIN_SOURCE_PATH):
        if re.search(r'.csv$', filename):
            data = pd.read_csv("{}/{}".format(REDFIN_SOURCE_PATH, filename))
            data["Elementary"] = pd.Series([""]*len(data.index), index=data.index)
            data["Elementary Rating"] = pd.Series([""]*len(data.index), index=data.index)
            data["Middle"] = pd.Series([""]*len(data.index), index=data.index)
            data["Middle Rating"] = pd.Series([""]*len(data.index), index=data.index)
            data["High"] = pd.Series([""]*len(data.index), index=data.index)
            data["High Rating"] = pd.Series([""]*len(data.index), index=data.index)
            data["Census Tract"] = pd.Series([""]*len(data.index), index=data.index)
            data["Median Income"] = pd.Series([""]*len(data.index), index=data.index)
            
            for h in data.index:
                if (not pd.isnull(data.loc[h, "LATITUDE"])) and (not pd.isnull(data.loc[h, "LONGITUDE"])):
                    try:                        
                        coord = [float(data.loc[h, "LATITUDE"]), float(data.loc[h, "LONGITUDE"])]
                        schools = getSchools.getSchoolDistrict(coord, schoolData)
                        data.loc[h, "Elementary"] = schools['E']['name']
                        data.loc[h, "Middle"] = schools['M']['name']
                        data.loc[h, "High"] = schools['H']['name']
                        data.loc[h, "Elementary Rating"] = schools['E']['rating']
                        data.loc[h, "Middle Rating"] = schools['M']['rating']
                        data.loc[h, "High Rating"] = schools['H']['rating']
                    except:
                        print(data.loc[h])
                        return
                    (tract, medianIncome) = getCensus.getCensusData(coord, censusData)
                    data.loc[h, "Census Tract"] = tract
                    data.loc[h, "Median Income"] = medianIncome
            
            newFile = re.sub(r'.csv', '_ext.csv', filename)
            data.to_csv("{}/{}".format(REDFIN_OUT_PATH, newFile), ignore_index=True)
            if first:
                allData = data
                first = 0
            else:
                allData = allData.append(data, ignore_index=True)
    allData = allData.drop_duplicates(["LISTING ID", "ADDRESS"])
    pickle.dump(allData, open('saleData.p', "wb"))
    
    
if __name__ == "__main__":
    main()