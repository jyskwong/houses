# -*- coding: utf-8 -*-
"""
Spyder Editor

Copyright (c) 2016 Joyce Kwong
All rights reserved
"""
import matplotlib.path as mplPath
import json
import numpy as np
import os
import pandas as pd
import re


""
def parseSchoolDistrictJSON(districtList):

    polygons = []
    for distrID in districtList:
        jsonfile = "mapdata/{}.json".format(distrID)
        pathPoints = []
        if os.path.isfile(jsonfile):
            with open(jsonfile) as jsondata:
                distrBoundaries = json.load(jsondata)
                if 'boundary' in distrBoundaries.keys():
                    for (longit, lat) in distrBoundaries['boundary']['coordinates'][0][0]:
                        pathPoints.append([lat, longit])
                elif 'schools' in distrBoundaries.keys():
                    for (longit, lat) in distrBoundaries['schools'][0]['coordinates']['coordinates'][0][0]:
                        pathPoints.append([lat, longit])
                else:
                    for (longit, lat) in distrBoundaries['districts'][0]['coordinates']['coordinates'][0][0]:
                        pathPoints.append([lat, longit])
            polygons.append(mplPath.Path(np.array(pathPoints)))
        else:
            print("Can't find district map")
            polygons.append(mplPath.Path(np.array([[0, 0]])))
    return polygons
            
## read in available boundaries for school districts in schools.csv
def parseAllSchools():
    schooldf = pd.read_csv('mapdata/schools.csv')
    schoolData = {}
    for schoolType in ['E', 'M', 'H']:
        schoolData[schoolType] = {}
        schools = schooldf.ix[schooldf["Level"] == schoolType]
        for i in schools.index:
            ids = str(schools.loc[i, "ID"])
            ids = re.sub(r'\s+', '', ids)
            districtList = ids.split(',')
            print(schools.loc[i, "Name"])
            schoolData[schoolType][schools.loc[i, "Name"]] = {}
            schoolData[schoolType][schools.loc[i, "Name"]]['boundary'] = parseSchoolDistrictJSON(districtList)
            schoolData[schoolType][schools.loc[i, "Name"]]['rating'] = schools.loc[i, "Rating"]
    return schoolData

## given a GPS coordinate (lat, long), find corresponding school districts and average rating
def getSchoolDistrict(coord, schoolData):
    schools = {}
    sumRating = 0
    numRating = 0
    for schoolType in schoolData.keys():
        schools[schoolType] = {}
        schools[schoolType]['name'] = ""
        schools[schoolType]['rating'] = ""
        found = False
        for name in schoolData[schoolType].keys():
            polygons = schoolData[schoolType][name]['boundary']
            for distr in polygons:
                if distr.contains_point(coord):
                    schools[schoolType]['name'] = name
                    schools[schoolType]['rating'] = schoolData[schoolType][name]['rating']
                    found = True
            if found:
                break

            
    return schools
            

        
    
    
