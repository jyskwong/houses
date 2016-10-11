# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 22:19:35 2016

@author: dwei
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt 

#%%
# Read data
df = pd.read_pickle('saleData.p')
# Replace empty strings in derived columns with np.nan
df.iloc[:, -8:] = df.iloc[:, -8:].replace('', np.nan)

#%% Filter by school rating
# Non-null school ratings (excludes few in Campbell Union school district, Palo Alto, San Jose)
df = df.ix[df['Middle Rating'].notnull() & df['Elementary Rating'].notnull()]
# Elementary school rating
df = df.ix[df['Elementary Rating'] > 2]

#%%
# Schools by school ratings
schoolElem = df.groupby('Elementary Rating')['Elementary'].unique()
schoolMid = df.groupby('Middle Rating')['Middle'].unique()
schoolHigh = df.groupby('High Rating')['High'].unique()

#%% Median income vs. school ratings
# Group statistics
df.groupby('Elementary Rating')['Median Income'].agg(['count','mean','median','std'])
df.groupby('Middle Rating')['Median Income'].agg(['count','mean','median','std'])
df.groupby('High Rating')['Median Income'].agg(['count','mean','median','std'])

# Linear regression on elementary school rating only
colSchool = ['Elementary Rating']
X = pd.get_dummies(df[colSchool], columns=colSchool, prefix_sep='=', drop_first=True)
X = sm.add_constant(X)
model = sm.OLS(df['Median Income'], X)
results = model.fit()
#results.summary()
ssr1 = results.ssr
p1 = results.df_model + 1

# Linear regression on all school ratings
colSchool = ['Elementary Rating','Middle Rating','High Rating']
X = pd.get_dummies(df[colSchool], columns=colSchool, prefix_sep='=', drop_first=True)
X = sm.add_constant(X)
model = sm.OLS(df['Median Income'], X)
results = model.fit()
#results.summary()
ssr2 = results.ssr
p2 = results.df_model + 1
# F-statistic between models
F = (ssr1 - ssr2) / (p2 - p1) * (results.nobs - p2) / ssr2

#%% Filter by # bedrooms, bathrooms, square feet
# Non-null # bathrooms (excludes multi-family and 4 others)
df = df.ix[df['BATHS'].notnull()]
# Non-null square feet (excludes 1) 
df = df.ix[df['SQFT'].notnull()] 
# Number of bedrooms
df = df.ix[df['BEDS'].isin([2, 3, 4])]

#%% Square feet vs. # bedrooms and bathrooms
# Group statistics
df.groupby(['BEDS','BATHS'])['SQFT'].agg(['count','mean','median','std'])

# Linear regression
colBB = ['BEDS','BATHS']
X = df[colBB]
X = sm.add_constant(X)
model = sm.OLS(df['SQFT'], X)
results = model.fit()
ssr1 = results.ssr
p1 = results.df_model + 1

# Linear regression with dummy-coding
X = pd.get_dummies(df[colBB], columns=colBB, prefix_sep='=')
X.drop(['BEDS=3.0','BATHS=2.0'], axis=1, inplace=True)
X = sm.add_constant(X)
model = sm.OLS(df['SQFT'], X)
results = model.fit()
ssr2 = results.ssr
p2 = results.df_model + 1
# F-statistic between models with/without dummy-coding
F = (ssr1 - ssr2) / (p2 - p1) * (results.nobs - p2) / ssr2

#%% Non-null lot size (excludes ~400, more condos than SFRs or townhouses)
df = df.ix[df['LOT SIZE'].notnull()]

#%%
# Compute correlation coefficients
colPhys = ['BEDS','BATHS','SQFT','LOT SIZE']
np.corrcoef(df[colPhys], rowvar=0)
colSocEcon = ['Elementary Rating','Middle Rating','High Rating','Median Income']
np.corrcoef(df[colSocEcon], rowvar=0)
np.corrcoef(df[colPhys + colSocEcon], rowvar=0)

#%% Past sales only
df = df.ix[df['SALE TYPE']=='Past Sale']

#%% Univariate relationships with sales price
# Compute correlation coefficients
np.corrcoef(df[colPhys + ['LAST SALE PRICE']], rowvar=0)
np.corrcoef(df[colSocEcon + ['LAST SALE PRICE']], rowvar=0)
np.corrcoef(df[['YEAR BUILT','LAST SALE PRICE']], rowvar=0)

# Group statistics
df.groupby(['BEDS','BATHS'])['LAST SALE PRICE'].agg(['count','mean','median','std'])
df.groupby('Elementary Rating')['LAST SALE PRICE'].agg(['count','mean','median','std'])
df.groupby('Middle Rating')['LAST SALE PRICE'].agg(['count','mean','median','std'])
df.groupby('High Rating')['LAST SALE PRICE'].agg(['count','mean','median','std'])

# Plots
plt.plot(df.loc[df['SQFT']<3500,'SQFT'], df.loc[df['SQFT']<3500,'LAST SALE PRICE'], 'o')
plt.plot(df.loc[df['LOT SIZE']<12000,'LOT SIZE'], df.loc[df['LOT SIZE']<12000,'LAST SALE PRICE'], 'o')
plt.plot(df.loc[df['LAST SALE PRICE']<3.5e6,'Median Income'], df.loc[df['LAST SALE PRICE']<3.5e6,'LAST SALE PRICE'], 'o')
