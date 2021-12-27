# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 18:25:55 2021

@author: ayubh
"""


import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt 
import pandas as pd
import Generate_Prepayment_Rate

from Pricing_and_Cashflows import Loan_Portfolio 
import create_Loan_Df as cl
loan_df_1=cl.x.loan_df
class MBS_tranches:
    senior_tranch_loans=loan_df_1[loan_df_1['tranch_level']==1]
    junior_tranch_loans=loan_df_1[loan_df_1['tranch_level']==2] 
    def tranches(self,outstanding_bal_tranchwise=loan_df_1.groupby('tranch_level')["Current_Principal_Balance"].sum(),num_of_tranches=None,names=["senior, junior"]):
        self.outstanding_bal_tranchwise=outstanding_bal_tranchwise
        self.num_of_tranches=len(outstanding_bal_tranchwise)
        self.names=names
        #self.tranch_description=pd.DataFrame()
        print(self.num_of_tranches)
        
    
    def tranchwise_flows(self):
         period_list = [0] * (360+ 0)
         tranch_payment=pd.DataFrame()
         tranch_payment['period']=list(range(0,360))
         tranch_payment['senior']=np.zeros(360)
         tranch_payment_senior=0
         tranch_payment_sr=[]
         for i in range(0,360):
            tranch_payment_sr=[]
            last_period = period_list[i - 1]
            outstanding_bal=0
            initial_bal=0
            
            for j, loan in junior_tranch_loans.iterrows():
                start_bal=(loan['Current_Principal_Balance'])
                if start_bal>0:
                   mortgage_payment=-npf.pmt(loan['Current_Interest_Rate']/12,loan['Remaining_Term']-i,loan['Current_Principal_Balance'],when='end')
                   x=Generate_Prepayment_Rate.select_prepayment_method(0)
                   if x=='b':
                      cpr=Generate_Prepayment_Rate.generate_CPR_PSA(i,360)
                   else:
                      cpr=Generate_Prepayment_Rate.a.iloc[i]
                      prepayment = start_bal * cpr/12    
                      outstanding_bal=(start_bal-mortgage_payment-prepayment)
                      loan['Current_Principal_Balance']=outstanding_bal
                
                      tranch_payment_senior+=mortgage_payment+prepayment
                      
                      
                      loan['Remaining_Term']-=i
                else:
                      tranch_payment_senior=tranch_payment_senior
                      
                tranch_payment_sr.append(tranch_payment_senior)
               
            tranch_payment['senior']=tranch_payment_sr
abc=MBS_tranches()
abc.tranchwise_flows()


