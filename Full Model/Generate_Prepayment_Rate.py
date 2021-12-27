# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 13:41:28 2021

@author: ayubh
"""

#create a PSA Assumption model that would determine the Conditional prepayment rate instead of a constant prepayment rate
#prepayment speed assumption that will be linked to the risk model....!
#This is based on
import Int_rate_path1
import numpy as np
import pandas as pd
from pandas import read_csv
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
from mpl_toolkits import mplot3d
from scipy.stats import norm

def select_prepayment_method(q):
    if q==0:
        type=h
    if q==1:
        type=b
    return type

def generate_CPR_PSA( i, N, PSA=2):  
    #N=Maturity
    #i=period
     for i in range(int(N)):
           
           if N<360:
               k=360-N+1
           else:
               k=0
               
     i=i
     k=k
     if i+k<=30:
        CPR=0.06*(i+k)/30*PSA
        SMM=1-(1-CPR)**(1/12)
     else:
         CPR=0.06*PSA
         SMM=1-(1-CPR)**(1/12)
     return CPR

def generate_CPR_HullWhite():
    x=Int_rate_path1.HW_model_two_factor()
    series = read_csv('Dates.csv')
    z=pd.DataFrame()
    z['Date']=(series['Date'])
    
    # plt.plot(x)
    # plt.title("Simulated Interest Rate Paths")
    # plt.xlabel("Time in months")
    # plt.ylabel("Interest Rate")

    mean_rate=np.mean(x, axis=1)
    
    two_year=x.iloc[24]
    ten_year=x.iloc[120]
    HW_mortage_rate=0.024+ 2*two_year+0.6*ten_year
    
    #CPR=RefiIncentive∗SeasoningMultiplier∗SeasonalityMultiplier
    
    G2PP_Refi=[]
    for j in HW_mortage_rate:
        G2PP_Refi.append ( .2406 - .1389 * math.atan(5.952*(1.089 - 0.06/j)))
    
    #plt.plot(G2PP_Refi)
    
    seasoning=np.ones(361)
    for i in range(30):
        seasoning[i]=1/30*i
    
    #mathworks
    #Keys->Months
    
    seasonality={1:.94,2: .76,3: .73,4: 0.96 ,5: .98 ,6:.92 ,7:.99 ,8:1.1 ,9:1.18,10:1.21,11: 1.23 ,12:.97}
    
    #CPR=RefiIncentive∗SeasoningMultiplier∗SeasonalityMultiplier
    CPR=pd.DataFrame()
    for k,path in enumerate(x):
      row=[]
      for j,i in enumerate(series['Date']):
        date_i=i
        mon=((date_i.split("/"))[0])
        row.append( G2PP_Refi[k]* seasoning[j]* seasonality[int(mon)])
      CPR[k]=row
    
    cpr_df=np.mean(CPR, axis=1)
    # plt.plot(CPR)
    # plt.plot(cpr_df)
    # plt.title("Prepayment Path using Hull White Interest Rate Model")
    # plt.xlabel("Time in months")
    # plt.ylabel("Prepayment Rate")
    return cpr_df
       

a=generate_CPR_HullWhite()
b='b'
h='h'