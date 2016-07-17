# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 20:58:55 2016

Plot various metrics on map
@author: jkwong
"""
import pandas as pd
from kmllib import *
import pickle

data = pickle.load(open('saleData.p', 'rb'))

def plotDaysOnMarket():
    doc = newKML()
    doc = addPoints(doc, data, 'LATITUDE', 'LONGITUDE', 'DAYS ON MARKET')
    printKML(doc, 'daysOnMarket.kml')
    
def ratio(x):
    if x[1] == 0:
        return np.nan
    else:
        return x[0] / x[1]
    
    
def plotSaleToListRatio():
    doc = newKML()
    filtered = data.ix[data["STATUS"] == "Sold"]
    
    filtered["Sale To List Ratio"] = filtered["LAST SALE PRICE"]/filtered["ORIGINAL LIST PRICE"]
    filtered = filtered.ix[filtered["Sale To List Ratio"] < 10]

    doc = addPoints(doc, filtered, 'LATITUDE', 'LONGITUDE', 'Sale To List Ratio')
    printKML(doc, 'saleToListRatio.kml')
    return filtered
    
def testCustomColors():
    doc = newKML()
    df = pd.DataFrame(np.abs(np.random.randn(10,3)), columns=['LATITUDE', 'LONGITUDE', 'VALUE'])
    bins = [0, 0.05, 0.15, 0.3, 0.32, 0.4, 0.5, 0.6, 0.78, 0.9]
    doc = addPointsCustom(doc, df, 'LATITUDE', 'LONGITUDE', 'VALUE', bins)
    printKML(doc, 'testCustomColors.kml')