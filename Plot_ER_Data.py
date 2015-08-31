# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 14:01:05 2015

@author: SWDG

"""
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import container
from matplotlib import collections
import numpy as np
import scipy.optimize as optimize
import bin_data as Bin
from scipy.stats import gaussian_kde
from scipy.stats import sem
from uncertainties import unumpy as unp

def LoadData(Path,Prefix,Order):

    #load the data from the raw file
    #not using genfromtext as I want access to individual elements
    #for debugging, may change in future
    with open(Path+Prefix+'_E_R_Star_Raw_Data.csv','r') as raw:
        no_of_cols = len(raw.readline().split(','))
        rawdata = raw.readlines()

    #want the data in a 2d array to make moving the values about simpler
    #dimensions will be 6Xlen(rawdata) no_of_cols = 6
    #and the row order will follow the header format in the input file:
    #i j LH CHT Relief Slope

    no_of_lines = len(rawdata)

    RawData = np.zeros((no_of_cols,no_of_lines),dtype='float64')

    for i,r in enumerate(rawdata):
        split = r.split(',')
        for a in range(no_of_cols):
            RawData[a][i] = split[a]
    #now we have a transformed 2d array of our raw data

    #Next, repeat the process for the patch data
    with open(Path+Prefix+'_E_R_Star_Patch_Data.csv','r') as patch:
        no_of_cols = len(patch.readline().split(','))
        patchdata = patch.readlines()

    #dimensions will be 18Xlen(patchdata) no_of_cols = 18
    #and the row order will follow the header format in the input file:
    #Final_ID lh_means lh_medians lh_std_devs lh_std_errs cht_means cht_medians cht_std_devs cht_std_errs r_means r_medians r_std_devs r_std_errs s_means s_medians s_std_devs s_std_errs patch_size

    no_of_lines = len(patchdata)

    PatchData = np.zeros((no_of_cols,no_of_lines),dtype='float64')

    for i,p in enumerate(patchdata):
        split = p.split(',')
        for a in range(no_of_cols):
            PatchData[a][i] = split[a]
        
    #Next, repeat the process for the Basin data
    with open(Path+Prefix+'_E_R_Star_Basin_'+str(Order)+'_Data.csv','r') as basin:
        no_of_cols = len(basin.readline().split(','))
        basindata = basin.readlines()

    #dimensions will be 11Xlen(basindata) no_of_cols = 19
    #and the row order will follow the header format in the input file:    
    #Basin_ID,LH_mean,CHT_mean,Relief_mean,Slope_mean,LH_median,CHT_median,Relief_median,Slope_median,LH_StdDev,CHT_StdDev,Relief_StdDev,Slope_StdDev,LH_StdErr,CHT_StdErr,Relief_StdErr,Slope_StdErr,Area,Count
    
    no_of_lines = len(basindata)

    BasinData = np.zeros((no_of_cols,no_of_lines),dtype='float64')
    
    for i,d in enumerate(basindata):
        split = d.split(',')
        for a in range(no_of_cols):
            BasinData[a][i] = split[a]
            
    return RawData,PatchData,BasinData

def PropagateErrors(PatchData,BasinData):
       
    #median, sem
    patchLH = unp.uarray(PatchData[2],PatchData[4])
    patchR = unp.uarray(PatchData[10],PatchData[12])
    patchCHT = unp.uarray(PatchData[6],PatchData[8])

    basinLH = unp.uarray(BasinData[5],BasinData[13])
    basinR = unp.uarray(BasinData[7],BasinData[15])
    basinCHT = unp.uarray(BasinData[6],BasinData[14])
  
    return (patchLH,patchR,patchCHT),(basinLH,basinR,basinCHT)
        
def SetUpPlot():
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = 14

    ax = plt.gca()

    ax.set_yscale('log', nonposy='clip')
    ax.set_xscale('log', nonposx='clip')

    plt.xlabel('Dimensionless Erosion Rate, E*')
    plt.ylabel('Dimensionless Relief, R*')

    plt.ylim(0.05,1.1)
    plt.xlim(0.1,1000)
    
    return ax

def PlotRaw(Sc,RawData):
    plt.plot(E_Star(Sc,RawData[3],RawData[2]),R_Star(Sc,RawData[4],RawData[2]),
    'k.',alpha=0.2,label='Raw Data')
    
def PlotRawDensity(Sc,RawData,Thin):
    #http://stackoverflow.com/a/20107592/1627162
    x = E_Star(Sc,RawData[3],RawData[2])
    y = R_Star(Sc,RawData[4],RawData[2])
    
    if Thin:
        x = x[::Thin]
        y = y[::Thin]  
    
    xy = np.vstack([x,y])
    density = gaussian_kde(xy)(xy)

    #order the points by density so highest density is on top in the plot    
    idx = density.argsort()
    x, y, density = x[idx], y[idx], density[idx]
    
    plt.scatter(x,y,c=density,edgecolor='',cmap=plt.get_cmap("autumn_r"))
    cbar = plt.colorbar()
    cbar.set_label('Probability Distribution Function')

def PlotRawBins(Sc,RawData,NumBins,MinimumBinSize=100,ErrorBars=True):
    E_s = E_Star(Sc, RawData[3], RawData[2])
    R_s = R_Star(Sc, RawData[4], RawData[2])

    bin_x, bin_std_x, bin_y, bin_std_y, std_err_x, std_err_y, count = Bin.bin_data_log10(E_s,R_s,NumBins)

    #filter bins based on the number of data points used in their calculation
    bin_x = np.ma.masked_where(count<MinimumBinSize, bin_x)
    bin_y = np.ma.masked_where(count<MinimumBinSize, bin_y)
    #these lines produce a meaningless warning - don't know how to solve it yet.

    if ErrorBars:
        #only plot errorbars for y as std dev of x is just the bin width == meaningless         
        plt.scatter(bin_x,bin_y,c=count,s=50,edgecolor='',cmap=plt.get_cmap("autumn_r"),label='Binned Raw Data', zorder=100)
        plt.errorbar(bin_x, bin_y, yerr=std_err_y, fmt=None,ecolor='k', zorder=0) 
        cbar = plt.colorbar()
        cbar.set_label('Number of values per bin')
    else:
        plt.errorbar(bin_x, bin_y, fmt='bo',label='Binned Raw Data')

def PlotPatchBins(Sc,PatchData,NumBins,MinimumBinSize=10,ErrorBars=True):
    E_s = E_Star(Sc,PatchData[6],PatchData[2])
    R_s = R_Star(Sc,PatchData[10],PatchData[2])

    bin_x, bin_std_x, bin_y, bin_std_y, std_err_x, std_err_y, count = Bin.bin_data_log10(E_s,R_s,NumBins)

    #filter bins based on the number of data points used in their calculation
    bin_x = np.ma.masked_where(count<MinimumBinSize, bin_x)
    bin_y = np.ma.masked_where(count<MinimumBinSize, bin_y)
    #these lines produce a meaningless warning - don't know how to solve it yet.

    if ErrorBars:
        #only plot errorbars for y as std dev of x is just the bin width == meaningless                  
        plt.scatter(bin_x,bin_y,c=count,s=50,edgecolor='',cmap=plt.get_cmap("autumn_r"),label='Binned Patch Data', zorder=100)
        plt.errorbar(bin_x, bin_y, yerr=std_err_y, fmt=None,ecolor='k', zorder=0) 
        cbar = plt.colorbar()
        cbar.set_label('Number of values per bin')

    else:
        plt.errorbar(bin_x, bin_y, fmt='bo',label='Binned Patch Data')        
    
def PlotPatches(Sc,PatchData,ErrorBars):                     

    e_star = E_Star(Sc,PatchData[2],PatchData[0])
    r_star = R_Star(Sc,PatchData[1],PatchData[0])
    if ErrorBars:
        plt.errorbar(unp.nominal_values(e_star),unp.nominal_values(r_star),yerr=unp.std_devs(r_star),xerr=unp.std_devs(e_star),
                     fmt='ro',label='Hilltop Patch Data')     
    else:
        plt.errorbar(unp.nominal_values(e_star),unp.nominal_values(r_star),
                     fmt='ro',label='Hilltop Patch Data')     

def PlotPatchesArea(Sc,PatchData,thresh,alpha):
    e_star = E_Star(Sc,PatchData[6],PatchData[2])
    r_star = R_Star(Sc,PatchData[10],PatchData[2])
    area = PatchData[17]

    x = []
    y = []
    
    for a,b,s in zip(e_star,r_star,area):
        if s > thresh:
            x.append(a)
            y.append(b)
                    
    plt.plot(x,y,color='k',alpha=alpha,marker='o',linestyle='',label='Min. Patch Area = '+str(thresh))
    
def PlotBasins(Sc,BasinData,ErrorBars):
    e_star = E_Star(Sc,BasinData[2],BasinData[0])
    r_star = R_Star(Sc,BasinData[1],BasinData[0])
    
    if ErrorBars:
        plt.errorbar(unp.nominal_values(e_star),unp.nominal_values(r_star),yerr=unp.std_devs(r_star),xerr=unp.std_devs(e_star),
                     fmt='go',label='Basin Data')
    else:
        plt.errorbar(unp.nominal_values(e_star),unp.nominal_values(r_star),
                     fmt='go',label='Basin Data')

def PlotBasinsArea(Sc,BasinData,thresh,alpha):
    e_star = E_Star(Sc,BasinData[6],BasinData[5])
    r_star = R_Star(Sc,BasinData[7],BasinData[5])
    area = BasinData[18]

    x = []
    y = []
    
    for a,b,s in zip(e_star,r_star,area):
        if s > thresh:
            x.append(a)
            y.append(b)
    
    plt.plot(x,y,color='k',alpha=alpha,marker='o',linestyle='',label='Min. Basin Data Points = '+str(thresh))
            
def PlotLandscapeAverage(Sc,RawData,ErrorBars):
    E_Star_temp = E_Star(Sc,RawData[3],RawData[2])
    R_Star_temp = R_Star(Sc,RawData[4],RawData[2])
    E_Star_avg = np.median(E_Star_temp)
    R_Star_avg = np.median(R_Star_temp)
    
    if ErrorBars:
        E_Star_std = np.std(E_Star_temp)
        R_Star_std = np.std(R_Star_temp)
        E_Star_serr = sem(E_Star_temp)
        R_Star_serr = sem(R_Star_temp)    
        plt.errorbar(E_Star_avg,R_Star_avg,yerr=R_Star_serr,xerr=E_Star_serr,
                     fmt='ko',label='Landscape Average')
    else:
        plt.errorbar(E_Star_avg,R_Star_avg, fmt='ko',label='Landscape Average')

def R_Star_Model(x):    
    return (1./x) * (np.sqrt(1.+(x*x)) - np.log(0.5*(1. + np.sqrt(1.+(x*x)))) - 1.)

def E_Star(Sc,CHT,LH):
    if type(LH[0]) == np.float64:
        return (2.*np.fabs(CHT)*LH)/Sc
    else:
        return (2.*unp.fabs(CHT)*LH)/Sc
   
def R_Star(Sc, R, LH):
    return R/(LH*Sc)

def Residuals(Sc, R, LH, CHT):
    return R_Star_Model(E_Star(Sc,CHT,LH)) - R_Star(Sc, R, LH)

def reduced_chi_square(Residuals,Sc,DataErrs=None):

    #if we are fitting from patches or basins, get the std err and include in the chi squared    
    if DataErrs:
        r_star = R_Star(Sc,DataErrs[1],DataErrs[0])   
        
        #get rid of any divide by zero errors
        temp = ((Residuals/unp.std_devs(r_star))**2)        
        temp[np.isinf(temp)] = 0        
        chi_square = np.sum(temp)        
        
    else:
        chi_square = np.sum(Residuals**2)
    
    # degrees of freedom, as we have 1 free parameter, Sc  
    d_o_f = Residuals.size-2
    
    return chi_square/d_o_f         
    
def r_squared(Sc, R, LH, CHT ,infodict):

    measured = R_Star(Sc, R, LH)   
    mean_measured = np.mean(measured)  
      
    sqr_err_w_line = np.square(infodict['fvec'])
    sqr_err_mean = np.square((measured - mean_measured))
           
    return 1.-(np.sum(sqr_err_w_line)/np.sum(sqr_err_mean))

def DrawCurve():
    #plot the e* r* curve from roering 2007
    x = np.arange(0.01, 1000, 0.1)
    plt.plot(x, R_Star_Model(x), 'k-', linewidth=2, label='Nonlinear Flux Law')
        
def GetBestFitSc(Method, Data, DataErrs=None):

    ScInit = 0.8  # Need to have an initial for the optimizer, any valid Sc value can be used - will not impact the final value
    Fit_Sc = [] #Need to initialize this in case Method is incorrectly defined. Need some error handling!

    if Method.lower() == 'raw':
        Fit_Sc,_,infodict,_,_ = optimize.leastsq(Residuals, ScInit, args=(Data[4], Data[2], Data[3]),full_output=True)
        chi = reduced_chi_square(infodict['fvec'],Fit_Sc[0])         
    elif Method.lower() == 'patches':
        Fit_Sc,_,infodict,_,_ = optimize.leastsq(Residuals, ScInit, args=(Data[10], Data[2], Data[6]),full_output=True)
        chi = reduced_chi_square(infodict['fvec'],Fit_Sc[0],DataErrs)
    elif Method.lower() == 'basins':
        Fit_Sc,_,infodict,_,_ = optimize.leastsq(Residuals, ScInit, args=(Data[7], Data[5], Data[6]),full_output=True)
        chi = reduced_chi_square(infodict['fvec'],Fit_Sc[0],DataErrs)
        
    return Fit_Sc[0],chi

def BootstrapSc(Method, Data, n=1000):
    tmp = []
    #need to convert the LH,R,CHT data into a serial 1D array before bootstrapping    
    if Method == 'patches':
        for i in range(len(Data[0])):
            tmp.append(SerializeData(Data[2][i],Data[10][i],Data[6][i]))
    if Method == 'basins':
        for i in range(len(Data[0])):
            tmp.append(SerializeData(Data[5][i],Data[7][i],Data[6][i]))
   
    ToSample = np.array(tmp)
    
    Scs = []    
    for i in range(n):
        sample = np.random.choice(ToSample,len(ToSample),replace=True)
        LH,R,CHT = UnserializeList(sample)
        sc,_,_,_,_ = optimize.leastsq(Residuals, 0.8, args=(R, LH, CHT),full_output=True)
        
        Scs.append(sc[0])
    #        mean          upper bound                               lower bound    
    return np.mean(Scs),np.percentile(Scs,97.5)-np.mean(Scs), np.mean(Scs)-np.percentile(Scs,2.5)
        
def SerializeData(LH, R, CHT):
    return str([LH, R, CHT])[1:-1]

def UnserializeList(serial_list):
    LH=[]
    R=[]
    CHT=[]
    for s in serial_list:
       lh,r,cht = UnserializeData(s)
       LH.append(lh)
       R.append(r)
       CHT.append(cht)
     
    return np.array(LH),np.array(R),np.array(CHT)

def UnserializeData(serial):
    split = [float(s) for s in serial.split(',')]
    return split[0],split[1],split[2]
    
def Labels(Sc,Method,ax):
    
    #remove errorbars from the legend    
    handles, labels = ax.get_legend_handles_labels()   
    handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]  
    
    #color scatterplot symbols like colormap
    for h in handles:        
        if isinstance(h, collections.PathCollection):            
            h.set_color('r')
            h.set_edgecolor('')
                
    ax.legend(handles, labels, loc=4, numpoints=1,scatterpoints=1)    
    
    #in case Method is invalid
    fit_description = ' = '

    if Method.lower() == 'raw':
        fit_description = ' from raw data = '

    elif Method.lower() == 'patches':
        fit_description = ' from hilltop patches = '

    elif Method.lower() == 'basins':
        fit_description = ' from basin average data = '

    if isinstance(Method,int) or isinstance(Method,float):
        plt.title('$\mathregular{S_c}$ set as = ' + str(round(Sc,2)))        
    else:
        plt.title('Best fit $\mathregular{S_c}$'+fit_description+str(round(Sc,2)))

def SavePlot(Path,Prefix,Format):
    plt.savefig(Path+Prefix+'_E_R_Star.'+Format,dpi=500)
    plt.clf()

def CRHurst():
    #plots the hurst 2012 figure 14 points for testing
    #needs the errorbars
    x = [1.15541793184, 2.96599962747, 5.06753455114, 6.87537359947, 8.86462081724, 10.9425778888, 12.9426702489, 14.9866553641, 16.9785507349, 19.0034609662, 20.9560856862, 22.8577931724, 24.6085876779, 27.3044634219, 28.3873092441, 31.1978149101, 32.8625186998, 35.2335006909, 37.2282499959, 43.8911646306, 45.5936728215]    
    y = [0.379133283693, 0.435531356239, 0.547479389809, 0.588874111323, 0.652649344881, 0.696659574468, 0.824275084903, 0.733856012658, 0.783243670886, 0.836195147679, 0.920291139241, 0.862545710267, 0.953440506329, 0.851824367089, 0.97046835443, 0.909219409283, 0.964772151899, 1.08295780591, 0.904050632911, 1.13525316456, 0.934139240506]
    plt.plot(x,y,'k^',label='Hurst et al. 2012')

def GMRoering():
    #plots the gm datapoints from roering 2007 for testing
    x = [1.68]*2
    y = [0.34,0.43]
    
    xerr = [0.7]*2
    yerr = [0.17,0.2]
        
    plt.errorbar(x,y,yerr,xerr,'k^',label='Roering et al. 2007')
    
def OCRRoering():
    #plots the gm datapoints from roering 2007 for testing
    x = [6.3]*2
    y = [0.57,0.64]
    
    xerr = [2.1]*2
    yerr = [0.23,0.18]
    
    plt.errorbar(x,y,yerr,xerr,'k^',label='Roering et al. 2007')
    
def MakeThePlot(Path,Prefix,Sc_Method,RawFlag,DensityFlag,BinFlag,NumBins,PatchFlag,BasinFlag,LandscapeFlag,Order,ErrorBarFlag=True,Format='png'):

    
    RawData,PatchData,BasinData = LoadData(Path,Prefix,Order)

    PatchDataErrs, BasinDataErrs = PropagateErrors(PatchData,BasinData)
        
    ax = SetUpPlot()
    
    DrawCurve()
    
    if isinstance(Sc_Method,int) or isinstance(Sc_Method,float):
        Sc = Sc_Method
    else:
        if Sc_Method.lower() == 'raw':
            Sc,chi = GetBestFitSc(Sc_Method, RawData)
        if Sc_Method.lower() == 'patches':
            #Sc,chi = GetBestFitSc(Sc_Method, PatchData, PatchDataErrs) 
            Sc,upper,lower = BootstrapSc(Sc_Method, PatchData)
        if Sc_Method.lower() == 'basins':
            #Sc,chi = GetBestFitSc(Sc_Method, BasinData, BasinDataErrs)
            Sc,upper,lower = BootstrapSc(Sc_Method, PatchData)
    
    if RawFlag:
        PlotRaw(Sc,RawData)
    if DensityFlag:        
        PlotRawDensity(Sc,RawData,DensityFlag)
    if PatchFlag:
        PlotPatches(Sc,PatchDataErrs,ErrorBarFlag)
    if BinFlag.lower() == 'patches':
        PlotPatchBins(Sc,PatchData,NumBins,ErrorBars=ErrorBarFlag)
    elif BinFlag.lower() == 'raw':
        PlotRawBins(Sc,RawData,NumBins,ErrorBars=ErrorBarFlag)
    if BasinFlag:
        PlotBasins(Sc,BasinDataErrs,ErrorBarFlag)
    if LandscapeFlag:
        PlotLandscapeAverage(Sc,RawData,ErrorBarFlag)

    #OCRRoering()
    #GMRoering()
    #CRHurst()
    
    Labels(Sc,Sc_Method,ax)
    #plt.show()

    SavePlot(Path,Prefix+'_basin_order',Format)    
    
def IngestSettings():
    import Settings
    import sys
    
    
    #typecheck inputs
    if not isinstance(Settings.Path, str):
        sys.exit('Path=%s \nThis is not a valid string and so cannot be used as a path.\nExiting...' % Settings.Path)
        
    if not isinstance(Settings.Prefix, str):
        sys.exit('Prefix=%s \nThis is not a valid string and so cannot be used as a filename prefix.\nExiting...' % Settings.Prefix)

    if not isinstance(Settings.Sc_Method, str) and not isinstance(Settings.Sc_Method, float):
        sys.exit('Sc_Method=%s \nThis is not a valid string or floating point value.\nExiting...' % Settings.Sc_Method)
    else:
        if Settings.Sc_Method.lower() == 'raw' or Settings.Sc_Method.lower() == 'patches' or Settings.Sc_Method.lower() == 'basins':
            sys.exit('Sc_Method=%s \nThis is not a valid method to fit a critical gradient. Valid options are \'raw\',\'patches\', or \'basins\'.\nExiting...' % Settings.Sc_Method)
        if Settings.Sc_Method <= 0 or Settings.Sc_Method > 3:
            sys.exit('Sc_Method=%s \nThis critical gradient not within a expected range of 0 to 3.\nExiting...' % Settings.Sc_Method)
                
    if not isinstance(Settings.RawFlag, int):
        sys.exit('RawFlag should be set to 1 to plot the raw data or 0 to exclude the raw data. You have entered %s\nExiting...' % Settings.RawFlag)
      
    if not isinstance(Settings.DensityFlag, int):
        sys.exit('DensityFlag should be set to 1 to produce a density plot or 0 to not plot a density plot. Integer values greater than 1 will thin the data before plotting. You have entered %s\nExiting...' % Settings.DensityFlag)
        
    #Settings.BinFlag #2 options
    
    if not isinstance(Settings.NumBins, int):
        sys.exit('NumBins should be set to the number of bins to be generated when binning the data. If no binning is to be performed, set the value to 0. You have entered %s\nExiting...' % Settings.NumBins)            
    
    if not isinstance(Settings.PatchFlag, int):
        sys.exit('PatchFlag should be set to 1 to plot the patch data or 0 to exclude the patch data. You have entered %s\nExiting...' % Settings.PatchFlag)
        
    if not isinstance(Settings.BasinFlag, int):
        sys.exit('BasinFlag should be set to 1 to plot the basin data or 0 to exclude the basin data. You have entered %s\nExiting...' % Settings.BasinFlag)
        
    if not isinstance(Settings.LandscapeFlag, int):
        sys.exit('LandscapeFlag should be set to 1 to plot the landscape average data or 0 to exclude the landscape average data. You have entered %s\nExiting...' % Settings.LandscapeFlag)
        
    if not isinstance(Settings.Order, int):
        sys.exit('Order should be set to an integer (eg 1,2,3, etc) to load the basin average data generated for that order of basin. You have entered %s\nExiting...' % Settings.Order)
    
    if not isinstance(Settings.ErrorBarFlag, bool):
        sys.exit('ErrorBarFlag should be set to either True or False. True will generate plots with errorbars, False will exclude them. You have entered %s\nExiting...' % Settings.Order)
    
    #Settings.Format    #restricted options
    
    
    MakeThePlot(Settings.Path,Settings.Prefix,Settings.Sc_Method,Settings.RawFlag,Settings.DensityFlag,Settings.BinFlag,Settings.NumBins,Settings.PatchFlag,Settings.BasinFlag,Settings.LandscapeFlag,Settings.Order,Settings.ErrorBarFlag,Settings.Format)
    
IngestSettings()    
    
#MakeThePlot('GM','patches',0,0,'',20,0,1,0,2,ErrorBarFlag=False,Format='png')



#for l in ['GM','OR','NC','CR']:
#    for m in ['raw','patches','basins']:
#        print l,m        
#        MakeThePlot('C:\\Users\\Stuart\\Dropbox\\data\\final\\',l,m,0,0,'',20,0,1,0,2,ErrorBarFlag=False,Format='png')


