# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 21:10:33 2021

@author: Ayushi
"""

import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt 
import pandas as pd

class securities(object):
    def __init__(self,WAC, N, principal,rate, PSA):
        
        self.WAC=WAC
        self.N=N
        self.principal=principal
        self.rate=rate
        self.PSA=PSA
        
    def Monthly_CF_table(self):
        
        prepayment_arr=np.zeros(self.N)
        CPR1=[]
        outstanding_bal=self.principal
        for i in range(self.N):
           r=self.WAC
           if self.N<360:
               k=360-self.N+1
           else:
               k=0
           mortgage_payment=-npf.pmt(self.WAC/12,self.N-i,outstanding_bal,when='end')
           #mortgage_payment = outstanding_bal*(r*(1+r)**(N-i-1))/((1+r)**(N-1))
           
               
           if i+k<=30:
              CPR=0.06*(i+k)/30*self.PSA
              SMM=1-(1-CPR)**(1/12)
           else:
               CPR=0.06*self.PSA
               SMM=1-(1-CPR)**(1/12)
               
           CPR1.append(CPR)
               
           net_interest=outstanding_bal*self.rate/12
           gross_interest=self.WAC/12*outstanding_bal
           scheduled_principle=mortgage_payment - gross_interest
           
           prepayments=SMM*(outstanding_bal - scheduled_principle)
           prepayment_arr[i]= float(prepayments)
           
           total_principal = scheduled_principle + prepayments
           
           projected_monthly_CF = net_interest + total_principal
           
          
           
           print(f'{i+1}\t{outstanding_bal:15.2f}\t{SMM:15.6f}\t{mortgage_payment:15.2f}\t{net_interest:15.2f}\t{scheduled_principle:15.2f}\t{prepayments:15.2f}\t{total_principal:15.2f}\t{projected_monthly_CF:15.2f}')
           outstanding_bal-=total_principal
        return prepayment_arr
   
    def tranchwiseflow(self)  :
        h=self.outstanding_bal_tranchwise
        print(h)
        
    
class MBS(securities):
    def __init__(self, num_of_tranches, names, outstanding_bal_tranchwise,WAC, N, principal, rate, PSA):
        super(MBS,self).__init__(WAC, N, principal, rate, PSA)
        self.num_of_tranches=num_of_tranches
        self.names=names
        self.outstanding_bal_tranchwise=outstanding_bal_tranchwise
        self.tranch_description=pd.DataFrame()
        
    
    @staticmethod
    def tranches(self): 
        self.tranch_description=pd.DataFrame(self.outstanding_bal_tranchwise,columns=["Outstanding_Bal"], index=self.names)
        return  self.tranch_description
    
    def tranchwise_flow(self):
        securities.Monthly_CF_table(self)
        prepayment_arr1=securities.Monthly_CF_table(self)
        
        
        for i,bal in enumerate (self.outstanding_bal_tranchwise):
            outstanding_bal_tranch=bal
            tranch_flow=[]
            tranch_flow_df=pd.DataFrame(columns=['0'])
            j=0
            average_age=0
            while j<self.N:
                 net_int_tranch=outstanding_bal_tranch*self.rate/12
                 gross_int_tranch=self.WAC/12*outstanding_bal_tranch
                 mortgage_pay_tranch=-npf.pmt(self.WAC/12,self.N-j,outstanding_bal_tranch,when='end')
                 principal_tranch=mortgage_pay_tranch-gross_int_tranch
                
                 #assuming sequential pay
                 if outstanding_bal_tranch>0 and prepayment_arr1[j]>0:
                     if outstanding_bal_tranch>prepayment_arr1[j]:
                        prepayment_tranchwise=prepayment_arr1[j]
                        prepayment_arr1[j]=prepayment_arr1[j]-prepayment_tranchwise
                     elif outstanding_bal_tranch<prepayment_arr1[j]:
                        prepayment_tranchwise=outstanding_bal_tranch
                        prepayment_arr1[j]=prepayment_arr1[j]-prepayment_tranchwise
                     else:
                        prepayment_tranchwise=0
                 else:
                    prepayment_tranchwise=0
                 total_prin=principal_tranch+prepayment_tranchwise
                
                 outstanding_bal_tranch-=total_prin
                 if outstanding_bal_tranch<0:
                     average_age=(j+1)/12
                     j=self.N
                 else:
                     j+=1
                        
                     
                 tranch_flow.append([net_int_tranch,gross_int_tranch,prepayment_tranchwise])
            tranch_flow_df=pd.DataFrame(tranch_flow,columns=['netint','grossint','prepayment'])
            print("Tranch",chr(ord("A")+i ) )
            print(tranch_flow_df)
            print(f"Average age of this tranche is: {average_age:3.3f} Years")
            
            
                 
         
            


          
        # plt.ylabel('CPR percentage') 
        # plt.title('Graphical depiction of PSA') 
        # plt.grid() 
        
        # plt.plot(CPR1)
        # plt.text(300,CPR,str(PSA*100)+"PSA")
        # plt.xlabel('Age in Months'); 
           
   
def main():
    PSA100=securities(0.06,360,40000,0.055,1)
    PSA100.Monthly_CF_table()
   
    deal1=MBS(2,['A','B','C'],[5000,15000,20000],WAC=0.06,N=360,principal=40000,rate=0.055,PSA=2)
    #print(MBS.tranches(deal1))
    MBS.Monthly_CF_table(deal1)
    print(deal1.outstanding_bal_tranchwise)
    
    deal1.tranchwise_flow()
 
    #PSA165=MBS.Monthly_CF_table(0.06,358,400000000,0.055,1.65)
    #PSA250=MBS.Monthly_CF_table(0.06,358,400000000,0.055,2.50)
    
    
   
    
if __name__ == '__main__':
    main()
