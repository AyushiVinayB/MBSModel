# -*- coding: utf-8 -*--
"""
Created on Fri Nov 26 23:04:10 2021

@author: ayubh
"""
import create_Loan_Df
import Pricing_and_Cashflows as cf
import pandas as pd
import random
import Int_rate_path1 as int_rate
import numpy_financial as npf
import numpy as np
import matplotlib.pyplot as plt

class MBS_pricing:

    def import_MBS_Cashflows(self):  
        loan_cashflows=create_Loan_Df.y
        #loan_tranchwise_cf=create_Loan_Df.z
        
        # senior_tranche_cf=loan_tranchwise_cf[loan_tranchwise_cf['tranche']==1]
        # junior_tranche_cf=loan_tranchwise_cf[loan_tranchwise_cf['tranche']==2]
        
        loan_total_payments_futurevalue=loan_cashflows['total_payments']
        
        
        discounting_rate=int_rate.HW_model_two_factor()
        size=len(loan_total_payments_futurevalue)
        # size2=len(junior_tranche_cf['total_payments'])
        # size3=len(senior_tranche_cf['total_payments'])
       
        self.discounting_rate1=discounting_rate[:size]
        # self.discounting_rate2=discounting_rate[:size2]
        # self.discounting_rate3=discounting_rate[:size3]
        
        loan_cashflows[:size]
        # senior_tranche_cf=senior_tranche_cf[:size]
        # junior_tranche_cf=junior_tranche_cf[:size]

        self.tranch_cashflow=(create_Loan_Df.z)[:-1]
        size4=len(self.tranch_cashflow)
        self.discounting_rate4=discounting_rate[:size4]
        
        
#numpy_financial.pv(rate, nper, pmt, fv=0, when='end')

#MBS total  
    # def calculate_present_value(self): 
    #          discounted_cf=pd.DataFrame()
    #          discounted_cf_senior=pd.DataFrame()
    #          discounted_cf_junior=pd.DataFrame()
    #          for i in self.discounting_rate1:
    #             self.discounted_cf[i]=(npf.pv(self.discounting_rate1[i],self.loan_cashflows['period'],0,-self.loan_total_payments_futurevalue))
    #             #MBS Senior Tranche
    #          for i in self.discounting_rate3:
    #             self.discounted_cf_senior[i]=(npf.pv(self.discounting_rate3[i],self.senior_tranche_cf['period'],0,-(self.senior_tranche_cf['total_payments'])))
    #             #MBS junior Tranche
    #          for i in self.discounting_rate2:
    #             self.discounted_cf_junior[i]=(npf.pv(self.discounting_rate2[i],self.junior_tranche_cf['period'],0,-(self.junior_tranche_cf['total_payments'])))

    
    #          npv_mbs=np.sum(discounted_cf)
    #          npv_mbs_senior=np.sum(discounted_cf_senior)
    #          npv_mbs_junior=np.sum(discounted_cf_junior)
             
    def caculate_tranch_value(self):
            discounted_tranch_senior=pd.DataFrame()
            discounted_tranch_junior=pd.DataFrame()
            discounted_tranch_total=pd.DataFrame()
            for i in self.discounting_rate4:
                discounted_tranch_senior[i]=(npf.pv(self.discounting_rate4[i],self.tranch_cashflow['period'],0,-self.tranch_cashflow['cashflow_senior']))
            for i in self.discounting_rate4:
                discounted_tranch_junior[i]=(npf.pv(self.discounting_rate4[i],self.tranch_cashflow['period'],0,-self.tranch_cashflow['cashflow_junior']))
            for i in self.discounting_rate4:
                discounted_tranch_total[i]=(npf.pv(self.discounting_rate4[i],self.tranch_cashflow['period'],0,-self.tranch_cashflow['total_cashflow']))
            self.npv_mbs_senior=np.sum(discounted_tranch_senior)
            self.npv_mbs_junior=np.sum(discounted_tranch_junior)
            self.npv_mbs_total=np.sum(discounted_tranch_senior)
            
            
    
    def plot_mbs_value(self):        
        x1= np.mean(self.discounting_rate1)
        # x2= np.mean(self.discounting_rate2)
        # x3= np.mean(self.discounting_rate3)
        # plt.scatter(x1,self.npv_mbs)
        # plt.subplot(1,2,1)
        # plt.scatter(x3,self.npv_mbs_senior)
        # plt.subplot(1,2,2)
        # plt.scatter(x2,self.npv_mbs_junior)
        
        x4=np.mean(self.discounting_rate4)
  
        # plt.scatter(x4,self.npv_mbs_senior)
        # plt.title("Price-Yield Relationship - Senior Tranche")
        # plt.xlabel("Interest Rate")
        # plt.ylabel("Value")
        # plt.subplot(1,3,2)
        # plt.scatter(x4,self.npv_mbs_junior)
        # plt.title("Price-Yield Relationship - Junior Tranche")
        # plt.xlabel("Interest Rate")
        # plt.ylabel("Value")
        # plt.subplot(1,3,3)
        plt.scatter(x4,self.npv_mbs_total)
        plt.title("Price-Yield Relationship - Total MBS")
        plt.xlabel("Interest Rate")
        plt.ylabel("Value")
        
price=MBS_pricing()     
price.import_MBS_Cashflows()
price.caculate_tranch_value()
price.plot_mbs_value()
