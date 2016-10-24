# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 22:58:34 2016

Restrict model to Cumberland and Cherry Chase elementary schools in Sunnyvale

@author: dwei
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import kmllib

#%%
# Read data
df = pd.read_pickle('saleData.p')
# Replace empty strings in derived columns with np.nan
df.iloc[:, -8:] = df.iloc[:, -8:].replace('', np.nan)

#%% Filter rows based on preferences
# Elementary schools
df = df.ix[df['Elementary'].isin(['Cumberland', 'Cherry Chase'])]
# High schools
df = df.ix[df['High'] == 'Homestead']
# Single-family homes
df = df.ix[df['HOME TYPE'] == 'Single Family Residential']
# Number of bedrooms
df = df.ix[df['BEDS'].isin([3, 4])]
# Number of bathrooms
df = df.ix[df['BATHS'] > 1]

#%% Filter rows due to missing values
## Past sales only
#df = df.ix[df['SALE TYPE']=='Past Sale']
## Non-null # bathrooms (excludes multi-family and 4 others)
#df = df.ix[df['BATHS'].notnull()]
## Non-null square feet (excludes 1) 
#df = df.ix[df['SQFT'].notnull()] 
# Non-null lot size (excludes ~400, more condos than SFRs or townhouses)
df = df.ix[df['LOT SIZE'].notnull()]
## Non-null school ratings (excludes few in Campbell Union school district, Palo Alto, San Jose)
#df = df.ix[df['Middle Rating'].notnull() & df['Elementary Rating'].notnull()]

#%% Select columns
#cols = ['HOME TYPE','ADDRESS','CITY','ZIP','BEDS','BATHS','SQFT','LOT SIZE',
#        'YEAR BUILT','LAST SALE DATE','LAST SALE PRICE','LATITUDE','LONGITUDE',
#        'Elementary','Elementary Rating','Middle','Middle Rating','High',
#        'High Rating','Census Tract','Median Income']
colSel = ['BEDS','BATHS','SQFT','LOT SIZE','YEAR BUILT','LAST SALE DATE']
colSel = pd.DataFrame({'binaryCode': False}, index=colSel, columns=['binaryCode','dtype','drop'])
#colSel.at['LAST SALE DATE', 'dtype'] = pd.datetime

# Columns to binary-code
colBin = ['BEDS','BATHS']
colSel.loc[colBin, 'binaryCode'] = True
colSel.loc[colBin,'dtype'] = [int, float]
colSel.loc[colBin,'drop'] = ['mode', 'mode']

#%% Construct features column-by-column
# Upper bound on number of bathrooms
bathsUB = 3.

X = pd.DataFrame()
for col in colSel.index:
    Xnew = df[col].copy()
    if col == 'BATHS':
        # Truncate number of bathrooms
        Xnew[Xnew > bathsUB] = bathsUB
    elif col == 'CITY':
        # Convert all to uppercase
        Xnew = Xnew.str.upper()
    if colSel.at[col, 'binaryCode']:
        # Convert data type
        Xnew = Xnew.astype(colSel.at[col, 'dtype'])
        if colSel.at[col, 'drop'] == 'first':
            # Binary-code column and drop first level
            Xnew = pd.get_dummies(Xnew, prefix=col, prefix_sep='=', drop_first=True)
        elif colSel.at[col, 'drop'] == 'mode':
            # Binary-code column
            Xnew = pd.get_dummies(Xnew, prefix=col, prefix_sep='=')
            # Drop most frequent level
            Xnew.drop(Xnew.sum().argmax(), axis=1, inplace=True)
        if col == 'BATHS':
            # Modify column label to reflect truncation
            colTrunc = Xnew.columns[pd.Series(Xnew.columns).str.partition('=')[2] == str(bathsUB)][0]
            Xnew.rename(columns={colTrunc: colTrunc.replace('=', '>=')}, inplace=True)
    # Concatenate
    X = pd.concat([X, Xnew], axis=1)

#%% Simple feature transformations
# Year built to age in years
X['YEAR BUILT'] = X['LAST SALE DATE'].dt.year - X['YEAR BUILT']
X.rename(columns={'YEAR BUILT': 'Age At Sale'}, inplace=True)
# Sale date to time (in years) since earliest sale date
# Sale date to quarter
dateMin = X['LAST SALE DATE'].min()
#X['LAST SALE DATE'] = (X['LAST SALE DATE'] - dateMin) / np.timedelta64(1, 'Y')
#X.rename(columns={'LAST SALE DATE': 'Years Since {}'.format(dateMin.date())}, inplace=True)
dateMax = X['LAST SALE DATE'].max()
# Quarter boundaries
dateBins = pd.date_range(dateMin, dateMax, freq='91D')
dateBins = dateBins.append(pd.DatetimeIndex([dateMax + pd.Timedelta(1,'D')]))
# Convert sale date to quarter
X['Sale Quarter'] = 0
for q in range(len(dateBins) - 1):
    X.loc[(X['LAST SALE DATE'] >= dateBins[q]) & (X['LAST SALE DATE'] < dateBins[q+1]), 'Sale Quarter'] = q+1
# Binary-code sale quarter
Xnew = pd.get_dummies(X['Sale Quarter'], prefix='Sale Quarter', prefix_sep='=')
Xnew.drop('Sale Quarter={}'.format(len(dateBins)-1), axis=1, inplace=True)
# Concatenate and drop original columns
X = pd.concat([X, Xnew], axis=1)
X.drop(['LAST SALE DATE', 'Sale Quarter'], axis=1, inplace=True)

#%% Feature regressions
# Square feet on number of bedrooms, bathrooms
XBB = X.ix[:, X.columns.str.startswith('BEDS') | X.columns.str.startswith('BATHS')]
XBB = sm.add_constant(XBB)
model = sm.OLS(X['SQFT'], XBB)
results = model.fit()
results.summary()
X['SQFT'] = results.resid
X.rename(columns={'SQFT': 'SQFT Residual'}, inplace=True)

#%% Normalize columns
norms = pd.Series(np.linalg.norm(X, axis=0), index=X.columns)
Xnorm = X / norms

#%% Regress sale price on features
# First add constant column
Xnorm = sm.add_constant(Xnorm)
norms = pd.Series({'const': 1}).append(norms)
model = sm.OLS(df['LAST SALE PRICE'], Xnorm)
results = model.fit()
results.summary()
results.params / norms

#%% Output residuals as KML file
# Concatenate coordinates and residuals into new DataFrame
dfResid = pd.concat([df[['LATITUDE','LONGITUDE']], results.resid], axis=1)
dfResid.rename(columns={0: 'Residual'}, inplace=True)
doc = kmllib.newKML()
binEdges = np.array([2e4, 6e4, 1e5, 1.5e5, 2e5])
binEdges = np.concatenate((-binEdges[::-1], binEdges))
doc = kmllib.addPointsCustom(doc, dfResid, 'LATITUDE', 'LONGITUDE', 'Residual', binEdges)
kmllib.printKML(doc, 'residuals.kml')
