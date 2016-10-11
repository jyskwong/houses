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
import matplotlib.path as mplPath

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
                    id="stylemap_house_{}".format(colorName))
                
        doc.append(style)
        doc.append(styleMap)    
    return doc
    
    
## @fn Add polygon to KML document. 
# polygon defined as a matplotlib.Path object
def addPoly(doc, name, mplPath):
    polyList = KML.MultiGeometry()
     
    coordStr = ""
    for vertex in mplPath.vertices:
        coordStr += "{},{},0 ".format(vertex[1], vertex[0])
    polyList.append(
                KML.Polygon(
                    KML.outerBoundaryIs(
                        KML.LinearRing(
                             KML.coordinates(coordStr)
                        )                            
                    )
                )
            )
    polygons = KML.Placemark(
        KML.name(name),
        polyList
        )
    doc.append(polygons)
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

## @fn Add points in KML document with a custom color scale
# bins = a list with 10 entries
#   a point < bin[0] takes on color0 
#   else a point < bin[1] takes on color1 
#   else a point < bin[9] takes on color9 
#   ... 
#   else color10
def addPointsCustom(doc, dataframe, latLabel, longLabel, valueLabel, bins, skipNull=1):
    if len(dataframe.index) == 0:
        return doc
    
    if (len(bins) != 10):
        raise ValueError("Expected bins to have 10 entries, got {}".format(len(bins)))

    plottedCoord = []
    for i in dataframe.index:
        # get color
        if pd.isnull(dataframe.loc[i, valueLabel]):
            colorName = 0
        else:
            diff = np.array(bins) - dataframe.loc[i, valueLabel]
            colorName = 10
            for (x, d) in enumerate(diff):
                if d > 0:
                    colorName = x
                    break
    
        #add placemark to KML
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
    
    
    
