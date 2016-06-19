# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 21:37:15 2016

Library for plotting housing data on maps
@author: jkwong
"""

import pykml
from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import os

## @fn new KML document
# returns: handle to KML document
def newKML():
    doc = KML.Document() 
    
    jet = plt.get_cmap('jet')
    
    colorList = {}
    for k in range(11):
        colorList[k] = matplotlib.colors.rgb2hex(jet(k/10.0))[1:]
    
    for (colorName, colorCode) in colorList.iteritems():
        style = KML.Style(
                    KML.IconStyle(
                        KML.color("FF{}".format(colorCode)),
                        KML.scale(0.6)
                    ),
                    KML.LabelStyle(KML.scale(0.5)),
                    id="house_{}".format(colorName)
                )
        styleMap = KML.StyleMap(
                    KML.Pair(
                        KML.key("normal"),
                        KML.styleUrl("house_{}".format(colorName))
                    ),
                    id="stylemap_house_{}".format(colorName)
                )
                
        doc.append(style)
        doc.append(styleMap)    
    return doc

## @fn Add points in KML document
# points come from a pandas dataframe
# longLabel = name of column 
def addPoints(doc, dataframe, latLabel, longLabel, valueLabel, normalize=1, skipNull=1):
    if len(dataframe.index) == 0:
        return doc
        
    if normalize == 1:
        maxval = max(dataframe[valueLabel])
        minval = min(dataframe[valueLabel])
        range_ = maxval - minval
    else:
        maxval = 1
        minval = 1
    
    #TODO plot the colorbar
    for i in range(11):
        print(i*range_/10+minval)
        
    #skip any duplicate entries  
    plottedCoord = []
    for i in dataframe.index:
        if pd.isnull(dataframe.loc[i, valueLabel]):
            colorName = 0
        else:
            if normalize == 1:
                colorName = max(0, min(int((dataframe.loc[i, valueLabel] - minval) / range_ * 10), 10))
            else:
                colorName = dataframe.loc[i, valueLabel]
        if not pd.isnull(dataframe.loc[i, valueLabel]) or skipNull == 0:
            coordStr = "{} {}".format(dataframe.loc[i, longLabel], dataframe.loc[i, latLabel])
            if coordStr not in plottedCoord:
                point = KML.Placemark(
                   KML.description("{:5f}".format(dataframe.loc[i, valueLabel])),
                   KML.styleUrl("stylemap_house_{}".format(colorName)),
                   KML.Point(
                       KML.coordinates("{},{},0".format(dataframe.loc[i, longLabel],dataframe.loc[i, latLabel]))
                        )
                    )
                doc.append(point)
                plottedCoord.append(coordStr)
    return doc
    
def printKML(doc, outfile):
    schema_ogc = Schema("ogckml22.xsd")
    schema_ogc.assertValid(doc)
    
    f = open(outfile, "w")
    f.write(etree.tostring(doc, pretty_print=True))
    f.close()
    
def demo():
    data = pd.read_csv('redfin_data/mv_redfin_2016-06-12-19-28-58_results_ext.csv')
    doc = newKML()
    doc = addPoints(doc, data, 'LATITUDE', 'LONGITUDE', 'Median Income', normalize=1, skipNull=0)
    printKML(doc, 'test.kml')
    
    