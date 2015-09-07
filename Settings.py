# -*- coding: utf-8 -*-

# Parameters to load the data
Path = 'C:\\Users\\Stuart\\Dropbox\\data\\final\\' #Must be wrapped in quotes with a trailing slash eg 'home/user/data/'
Prefix = 'OR' #Must be wrapped in quotes and match the prefix used in ER_STAR.cpp
Order = 2 #Basin order used in ER_STAR.cpp to extract the drainage basins. eg 1,2,5

#Options to select data to be plotted
RawFlag = 0 #Use 1 to plot the raw data and 0 to not plot it.
DensityFlag = 0 #Use 0 to not plot the raw data as a density plot and 1 to plot 
                #a density plot. Values greater than 1 will be used the thin the 
                #data. For example 2 will plot every second point. Reccommended!
BinFlag = '' #Use 'raw' to bin the raw data, 'patches' to bin the hilltop patch 
             #data and an empty string, '' to not perform binning. 
             #Note that quotes are needed for all cases.
NumBins = 20 #Number of bins to be generated. Must be an integer. eg 5,11,20 Will be ignored if BinFlag is left blank.
PatchFlag = 0 #Use 1 to plot the patch data and 0 to not plot it.
BasinFlag = 1 #Use 1 to plot the basin data and 0 to not plot it.
LandscapeFlag = 0 #Use 1 to plot the landscape average data and 0 to not plot it.

#Options regarding the fitting of the critical gradient
Sc_Method = 0.8
NumBootsraps = 10000

#Plot style options
ErrorBarFlag = False
Format = 'png'

#Comparison data to be plotted from the other studies
GabilanMesa = False #True to plot the data, False to exclude it.
OregonCoastRange = False #True to plot the data, False to exclude it.
SierraNevada = False #True to plot the data, False to exclude it.