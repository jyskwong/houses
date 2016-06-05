# -*- coding: utf-8 -*-
"""
Spyder Editor

Read census tract boundaries
Read census tract median income in Santa Clara county
Given GPS coord, return median income
Copyright (c) 2016 Joyce Kwong
All rights reserved
"""

import csv
import xml.etree.ElementTree as ET
import re
import matplotlib.path as mplPath
import numpy as np


## read CSV with median income in SC county
# output: column 0 = GEO.id
#         column 1 = HD01_VD01
def parseMedianIncome(filename):
    KEYCOL = 0
    DATACOL = 3
    csvData = {}
    with open(filename, 'rU') as csvfile:
        dataFile = csv.reader(csvfile, delimiter=',')
        r = 0
        for row in dataFile:
            if r >= 2:
                val = re.sub(r"\+", "", row[DATACOL])
                val = re.sub(r",", "", val)
                csvData[row[KEYCOL]] = {}
                csvData[row[KEYCOL]]['median'] = float(val)
            r += 1
    return csvData
    
def parseCensusBoundaries(kml, medianIncome):    
    tree = ET.parse(kml)
    doc = tree.getroot()
    folder = doc.find('Folder')
    
    for pm in folder.findall('Placemark'):
        tractID = pm.find(".//*[@name='AFFGEOID']").text
        if tractID in medianIncome.keys():
            clist = pm.find("./Polygon/outerBoundaryIs/LinearRing/coordinates").text
            coords = re.split('\s+', clist)
            coordinates = []
            for c in coords:
                if (c):
                    xyz = c.split(',')
                    coordinates.append([xyz[1], xyz[0]])
            medianIncome[tractID]['polygon'] = mplPath.Path(np.array(coordinates))
    return medianIncome


def getCensusData(coord, censusData):
    tract = ""
    medianIncome = 0
    for tractID in censusData.keys():
        if censusData[tractID]['polygon'].contains_point(coord):
            tract = tractID
            medianIncome = censusData[tractID]['median']
            break
    return (tract, medianIncome)

   
def main():
    CSVFILE = 'mapdata/ACS_13_5YR_B19013_with_ann.csv'
    KMLFILE = 'mapdata/cb_2013_06_tract_500k.kml'
    medianIncome = parseMedianIncome(CSVFILE)
    censusData = parseCensusBoundaries(KMLFILE, medianIncome)
    return censusData
    
if __name__ == "__main__":
    censusData = main()
           
            
            

    