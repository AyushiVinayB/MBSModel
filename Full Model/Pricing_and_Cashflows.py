# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 17:23:55 2021

@author: ayubh
"""

import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt 
import pandas as pd
import Generate_Prepayment_Rate


from itertools import chain

class Loan_Portfolio:
    
    def __init__(self, discount_rate, loan_df, cashflows_dataframe=None, aggregate_flows_df=None,tranchwise_flow_df=None):
        #Assuming single discount rate at time t0 for NPV calculation/to get price
        self.discount_rate = discount_rate
        #initialize loan dataframe; Current principal bal, interest rate and term from loan database
        self.loan_df = loan_df[['Current_Principal_Balance', 'Current_Interest_Rate', 'Remaining_Term',
            'adjusted_cdr', 'adjusted_cpr', 'adjusted_recovery','Original_Term', 'tranch_level', 'Original_Amount' ]]
        
        #create cashflow dataframe for entire loan portfolio with the following columns 
        if cashflows_dataframe is None:
            self.cashflows_dataframe = self.cash_flows_data_frame_for_portfolio()
            self.cashflows_dataframe['loss'] = self.cashflow_loss()
            self.cashflows_dataframe['total_interest'] = self.total_interests_for_cash_flow()
            self.cashflows_dataframe['total_principal'] = self.total_principals_for_cash_flow()
            self.cashflows_dataframe['total_payments'] = self.total_payments_for_cash_flow()
        else:
            self.cashflows_dataframe = cashflows_dataframe
            
            
        self.aggregate_flows_df = aggregate_flows_df
        self.tranchwise_flow_df=tranchwise_flow_df
        
 
    # create cashflow dataframe for the entire portfolio
    def cash_flows_data_frame_for_portfolio(self):
        #Cashflows for all loans given in a portfolio based on static portfolio real data
        #using apply for row wise application of function on the dataframe; axis=1
        cash_flow_list_list_dicts = self.loan_df.apply(self.generate_loan_cash_flows,axis=1)
        #chain.from_iterable used on terminating iterable sequence of loan cashflows
        cash_flows_list_dicts = list(chain.from_iterable(cash_flow_list_list_dicts))

        cash_flows_data_frame = pd.DataFrame(cash_flows_list_dicts)
        return cash_flows_data_frame
        
    
    @staticmethod
    def generate_loan_cash_flows(loan):
        #individual loan passed as an argument
        loan_pk = int(loan.name)
        orig_bal = float(loan['Current_Principal_Balance'])
        int_rate = float(loan['Current_Interest_Rate'])
        rem_term = int(loan['Remaining_Term'])
        adj_cdr = float(loan['adjusted_cdr'])
        adj_cpr = float(loan['adjusted_cpr'])
        recov_percent = float(loan['adjusted_recovery'])
        original_term= float(loan['Original_Term'])
        tranche=float(loan['tranch_level'])
        principal=float(loan['Current_Principal_Balance'])
        #payment schedule for loan function created later. check
        cash_flows_list_of_dicts = payment_schedule_for_loan(
            loan_df_pk=loan_pk,
            original_balance=orig_bal,
            interest_rate=int_rate,
            maturity=rem_term,
            cdr=adj_cdr,
            cpr=adj_cpr,
            recovery_percentage=recov_percent, 
            N=original_term,
            tranche=tranche,
            principal=principal
            )
        return cash_flows_list_of_dicts
    
    

    @staticmethod
    def tranchwise_flow(self):
        tranchwise_df=pd.DataFrame(  
        columns=('loan_pk_num',
                    'period',
                    'start_balance',
                    'remaining_term',
                    'interest',
                    'payment',
                    'scheduled_principal',
                    'prepayment',
                    'defaults',
                    'recovery',
                    'end_balance',
                    'tranche',
                    'principal'))
      
        for i in range (1, 361):
            total_scheduled_principal_tranchwise=0
            total_interest_tranchwise=0
            total_prepayment_tranchwise=0
            period=i
            period_list_loan=[]
            period_list_tranchwise=[]
            last_period=[]
            for j, loan_row in loan_df.iterrows():
                loan_pk_num= int(loan_row.name)
                orig_bal_t = float(loan_row['Current_Principal_Balance'])
                int_rate_t = float(loan_row['Current_Interest_Rate'])
                rem_term_t = int(loan_row['Remaining_Term'])
                cdr_t = float(loan_row['adjusted_cdr'])
                cpr_t = float(loan_row['adjusted_cpr'])
                recov_percent_t = float(loan_row['adjusted_recovery'])
                N_t= float(loan_row['Original_Term'])
                tranche_t=float(loan_row['tranch_level'])
                principal=float(loan_row['Current_Principal_Balance'])
                period_num_1=int(i)
                
               
                period_0 = dict(
                    loan_df_pk=loan_pk_num,
                    period=0,
                    start_balance=0,
                    remaining_term=rem_term_t + 1,
                    interest=0,
                    payment=0,
                    scheduled_principal=0,
                    prepayment=0,
                    defaults=0,
                    recovery=0,
                    end_balance=orig_bal_t,
                    tranche=tranche_t,
                    principal=principal
                )
                if period_num_1==1:
                    period_list_loan.append(period_0)
                    #period_list_tranchwise.append(period_0)
                    last_period=period_list_loan[j]
                else:
                    last_period=tranchwise_df.loc[(tranchwise_df['period']==(i-1)) &( tranchwise_df['loan_df_pk']==loan_pk_num)]
                   
            
                #last_period=tranchwise_df.loc[(tranchwise_df['loan_pk_num']==j )& (tranchwise_df['period'] == (i+1))]
                if i < rem_term_t:
                      p = create_payment_schedule_period(loan_pk_num, float(last_period['end_balance']), float((last_period['remaining_term']-1)),
                        cdr_t, cpr_t, period_num_1, int_rate_t, recov_percent_t,  N_t , tranche_t, principal)
                      #period_list_loan[j] = p
                      period_list_tranchwise.append(p)
                      
            periodwise_df=pd.DataFrame(period_list_tranchwise)  
            tranchwise_cf_df=periodwise_df.groupby(['period','tranche']).sum(lambda x:tuple(x)).reset_index()
            periodwise_df.loc[(periodwise_df['tranche']==1),'add_prepayment']=0 
            periodwise_df.loc[(periodwise_df['tranche']==2),'add_prepayment']=0 
            senior_tranch=tranchwise_cf_df.loc[tranchwise_cf_df['tranche']==1]
            junior_tranch=tranchwise_cf_df.loc[tranchwise_cf_df['tranche']==2]
            senior_tranch_outstanding_bal=senior_tranch['end_balance']
            senior_tranch_defaults=senior_tranch['defaults']-senior_tranch['recovery']
            junior_tranch_prepayment=junior_tranch['prepayment']
            junior_tranch_outstanding_bal=junior_tranch['end_balance']
            periodwise_df.loc[(periodwise_df['tranche']==1),'add_default']=0
            periodwise_df.loc[(periodwise_df['tranche']==2),'add_default']=0
            
            if (junior_tranch_prepayment.empty==True):
                junior_tranch_prepayment=0
                
            if senior_tranch_outstanding_bal[0]>0 and senior_tranch_outstanding_bal[0]>junior_tranch_prepayment[1]:
                 
                  num_of_loans=((periodwise_df['tranche'])==1).sum()
                  prep_per_loan=junior_tranch_prepayment[1]/num_of_loans
                  def_per_loan= senior_tranch_defaults[0]/num_of_loans
                 
                  if (periodwise_df.loc[(periodwise_df['tranche']==1),'end_balance']>prep_per_loan).all():
                      periodwise_df.loc[(periodwise_df['tranche']==1),'add_prepayment']=prep_per_loan
                      periodwise_df.loc[(periodwise_df['tranche']==2),'add_prepayment']=0
                      periodwise_df.loc[((periodwise_df['tranche']==1) & periodwise_df['end_balance']<0 ,'end_balance')]=0
                      periodwise_df.loc[(periodwise_df['tranche']==2),'prepayment']=0
                      junior_tranch['prepayment']=0
                     
                  elif (periodwise_df.loc[(periodwise_df['tranche']==1),'end_balance']>prep_per_loan).any():
                    num_of_loans=((periodwise_df['tranche'])==1 & (periodwise_df['end_balance']>prep_per_loan)).sum()
                    prep_per_loan=junior_tranch_prepayment[1]/num_of_loans
                    periodwise_df.loc[((periodwise_df['tranche']==1) & periodwise_df['end_balance']<0 ,'end_balance')]=0
                    periodwise_df.loc[((periodwise_df['tranche']==1) & periodwise_df['end_balance']<0 ,'add_prepayment')]=0
                    periodwise_df.loc[((periodwise_df['tranche']==1) & periodwise_df['end_balance']> prep_per_loan ,'add_prepayment')]=prep_per_loan
                    periodwise_df.loc[(periodwise_df['tranche']==2),'add_prepayment']=0
                    periodwise_df.loc[(periodwise_df['tranche']==2),'prepayment']=0
                    junior_tranch['prepayment']=0
                    
                  else:
                    periodwise_df.loc[(periodwise_df['tranche']==1),'add_prepayment']=0 
                    periodwise_df.loc[(periodwise_df['tranche']==2),'add_prepayment']=0 
                    periodwise_df.loc[((periodwise_df['tranche']==1) & periodwise_df['end_balance']<0 ,'end_balance')]=0
            
            if senior_tranch_defaults[0]>junior_tranch_outstanding_bal[1].any():
                num_of_loans=((periodwise_df['tranche'])==1).sum()
                def_per_loan= senior_tranch_defaults[0]/num_of_loans
                if (periodwise_df.loc[(periodwise_df['tranche']==2),'end_balance']>def_per_loan).all(): 
                   periodwise_df.loc[(periodwise_df['tranche']==2),'add_default']=def_per_loan
                   periodwise_df.loc[(periodwise_df['tranche']==1),'defaults']=0
                   periodwise_df.loc[(periodwise_df['tranche']==1),'add_default']=0
                   
                elif (periodwise_df.loc[(periodwise_df['tranche']==2),'end_balance']>def_per_loan).any(): 
                    default_num=((periodwise_df.loc[(periodwise_df['tranche']==2),'end_balance']>def_per_loan)).sum()
                    def_per_loan= senior_tranch_defaults[0]/default_num 
                    periodwise_df.loc[((periodwise_df['tranche']==2) & (periodwise_df['end_balance']> def_per_loan) ,'add_default')]=def_per_loan
                    periodwise_df.loc[((periodwise_df['tranche']==2) & (periodwise_df['end_balance']< def_per_loan) ,'add_default')]=0
                    periodwise_df.loc[(periodwise_df['tranche']==1),'add_default']=0
                else:
                   periodwise_df.loc[((periodwise_df['tranche']==2) & periodwise_df['end_balance']< def_per_loan ,'add_default')]=periodwise_df.loc[(periodwise_df['tranche']==2),'end_balance']
                   #adjust this  in tranch 1
            periodwise_df['prepayment']+=periodwise_df['add_prepayment']
            periodwise_df['end_balance']=periodwise_df['end_balance']-periodwise_df['add_prepayment']-periodwise_df['add_default']
            
        
            if period_num_1==1:
                 tranchwise_df=periodwise_df
            else:
                print("loop complete") 
                tranchwise_df=tranchwise_df.append(periodwise_df)
            
            tranchwise_cf_df=pd.DataFrame()
                
          
            
                # total_scheduled_principal_tranchwise+=p['scheduled_principal']
                # total_interest_tranchwise+=p['interest']
                # total_prepayment_tranchwise+=["prepayment"]
                
                      
         # period = dict(
        # loan_df_pk=loan_df_pk,
        # period=period_num,
        # start_balance=start_balance,
        # remaining_term=remaining_term,
        # interest=interest,
        # payment=payment,
        # scheduled_principal=scheduled_principal,
        # prepayment=prepayment,
        # defaults=defaults,
        # end_balance=end_balance,
        # recovery=recovery,
        # tranche=tranche
        
    
    def cashflow_loss(self):
        #create a column for loss for each cashflow and return that
        self.cashflows_dataframe['loss']= self.cashflows_dataframe['defaults']-self.cashflows_dataframe['recovery']
        return self.cashflows_dataframe['loss']   
    
    
    def total_interests_for_cash_flow(self):
        return self.cashflows_dataframe['interest']
    
    def total_principals_for_cash_flow(self):
        total_principals = self.cashflows_dataframe['scheduled_principal'] + self.cashflows_dataframe['prepayment'] + self.cashflows_dataframe['recovery']
        return total_principals
    
    def total_payments_for_cash_flow(self):
        return self.cashflows_dataframe['total_interest'] + self.cashflows_dataframe['total_principal']

    def current_balance_aggregate_for_portfolio(self):
        #add column
        return float(self.loan_df['Current_Principal_Balance'].sum())
    
    def interest_aggregate_for_portfolio(self):
        print(self.aggregate_flows_df['total_interest'].sum())
        return self.aggregate_flows_df['total_interest'].sum()
        

    def scheduled_principal_aggregate_for_portfolio(self):
       
        return self.aggregate_flows_df['scheduled_principal'].sum()
    
    def unscheduled_principal_aggregate_for_portfolio(self):
       
        return self.aggregate_flows_df['prepayment'].sum()

    def defaults__aggregate_for_portfolio(self):
       
        return self.aggregate_flows_df['defaults'].sum()

    def losses_aggregate_for_portfolio(self):
       
        return self.aggregate_flows_df['loss'].sum()

    def recovery_aggregate_for_portfolio(self):
       
        return self.aggregate_flows_df['recovery'].sum()
    
    #continue from line 160
    def cash_flows_aggregate_for_portfolio(
            self,
            fields_list=(
                'start_balance',
                'scheduled_principal',
                'prepayment',
                'interest',
                'defaults',
                'recovery',
                'loss',
                'total_interest',
                'total_principal',
                'total_payments'
            )
    ):
        """ Generates a portfolio's aggregate cash flows for a given set of fields.
        Args:
            fields_list: The list of fields from a loan cash flows to be aggregated.
        Returns: The portfolio's aggregated cash flows.
        """
        self.aggregate_flows_df = self.cashflows_dataframe.groupby('period')[
            fields_list
        ].sum().reset_index()
        return self.aggregate_flows_df
    
    def cash_flow_tranches(self, field_list=('start_balance',
                'scheduled_principal',
                'prepayment',
                'interest',
                'defaults',
                'recovery',
                'loss',
                'total_interest',
                'total_principal',
                'total_payments'
            )
    ):
        self.tranchwise_flow_df=self.cashflows_dataframe.groupby(['period','tranche'])[
            field_list
        ].sum(lambda x:tuple(x)).reset_index()
        return self.tranchwise_flow_df
    
    def cash_flow_tranchwise(self, loan_df):
        tranch_senior_df=loan_df.loc[loan_df['tranch_level']==1]
        tranch_junior_df=loan_df.loc[loan_df['tranch_level']==2]
        tranch_senior_outstanding_bal=(tranch_senior_df.groupby(['tranch_level'])[
            'Current_Principal_Balance'].sum(lambda x:tuple(x)).reset_index())['Current_Principal_Balance'][0]
        tranch_junior_outstanding_bal=(tranch_junior_df.groupby(['tranch_level'])[
            'Current_Principal_Balance'].sum(lambda x:tuple(x)).reset_index())['Current_Principal_Balance'][0]
        start_senior=tranch_senior_outstanding_bal
        start_junior= tranch_junior_outstanding_bal
        tot_out_bal=tranch_senior_outstanding_bal+tranch_junior_outstanding_bal
        tranch_bal_list, tranch_WAC=[], []
        tranch_bal_list.append(tranch_senior_outstanding_bal)
        tranch_bal_list.append(tranch_junior_outstanding_bal)
        WAC_senior_tranch=((tranch_senior_df['Current_Interest_Rate']*tranch_senior_df['Current_Principal_Balance']).sum())/tranch_senior_outstanding_bal
        WAC_junior_tranch=((tranch_junior_df['Current_Interest_Rate']*tranch_junior_df['Current_Principal_Balance']).sum())/tranch_junior_outstanding_bal
        recovery_senior_rate=((tranch_senior_df['adjusted_recovery']*tranch_senior_df['Current_Principal_Balance']).sum())/tranch_senior_outstanding_bal
        recovery_junior_rate=((tranch_junior_df['adjusted_recovery']*tranch_junior_df['Current_Principal_Balance']).sum())/tranch_junior_outstanding_bal
        tranch_WAC.append(WAC_senior_tranch)
        tranch_WAC.append(WAC_junior_tranch)
        cdr=0.005
        cdr1=0.00005
       ################
        tranch_flow=[]
        tranch_flow_df=pd.DataFrame(columns=['0'])
        j=0
        average_age=0
        N=360
        period_list = []
        period_0 = dict(
        period=0,
        total_balance=tot_out_bal,
        outstanding_bal_junior=tranch_junior_outstanding_bal,
        outstanding_bal_senior=tranch_senior_outstanding_bal,
        tot_interest=0,
        payment_senior_tranch=0,
        payment_junior_tranch=0,
        scheduled_principal_senior=0,
        scheduled_principal_junior=0,
        prepayment_senior=0,
        prepayment_junior=0,
        defaults_senior=0,
        recovery_senior=0,
        defaults_junior=0,
        recovery_junior=0,
        total_cashflow=0,
        cashflow_junior=0,
        cashflow_senior=0)
        period_list.append( period_0)
        senior_prin, junior_prin, net_int_tranch_senior, net_int_tranch_junior= 0,0, 0, 0
        while j<N:
             if tranch_senior_outstanding_bal<0:
                 tranch_senior_outstanding_bal=0
             net_int_tranch_senior=tranch_senior_outstanding_bal*WAC_senior_tranch/12
             net_int_tranch_junior=tranch_junior_outstanding_bal*WAC_junior_tranch/12
             #gross_int_tranch=self.WAC/12*outstanding_bal_tranch
        
             mortgage_pay_tranch_senior=-npf.pmt(WAC_senior_tranch/12,N-j,start_senior,when='end')
             mortgage_pay_tranch_junior=-npf.pmt(WAC_junior_tranch/12,N-j,start_junior,when='end')
             principal_tranch_senior=mortgage_pay_tranch_senior-net_int_tranch_senior
             principal_tranch_junior=mortgage_pay_tranch_junior-net_int_tranch_junior
             x=Generate_Prepayment_Rate.select_prepayment_method(0) 
         
             if x=='b':
               cpr=Generate_Prepayment_Rate.generate_CPR_PSA(j,N)
             else:
               cpr=Generate_Prepayment_Rate.a.iloc[j]
               
             prepayment_senior = tranch_senior_outstanding_bal * cpr/12
             defaults_senior = tranch_senior_outstanding_bal * cdr1 / 12
             recovery_senior= defaults_senior*recovery_senior_rate
             prepayment_junior = tranch_junior_outstanding_bal * cpr/12
             defaults_junior = tranch_junior_outstanding_bal * cdr / 12
             recovery_junior= defaults_junior*recovery_junior_rate
             ###recovery = recovery_percentage * defaults
             #assuming sequential pay and junior tranche is I/O till principal in  tranche 1 is retired
            
             if ((tranch_junior_outstanding_bal-defaults_junior)>defaults_senior and tranch_senior_outstanding_bal>0 \
                and tranch_senior_outstanding_bal > (prepayment_senior + prepayment_junior+ principal_tranch_junior+ principal_tranch_senior)) :
               tranch_junior_outstanding_bal-=defaults_senior
               defaults_senior=0
               #all prepayments and principal in junior tranch goes to senior tranch till its paid off completely
               senior_prin=principal_tranch_senior+prepayment_senior+defaults_senior+prepayment_junior+ principal_tranch_junior
               principal_tranch_junior=0
               prepayment_junior=0
               junior_prin=+prepayment_junior+ principal_tranch_junior
               tranch_junior_outstanding_bal-=(defaults_junior+junior_prin)
               tranch_senior_outstanding_bal-=(defaults_senior+senior_prin)
               
             elif (tranch_junior_outstanding_bal-defaults_junior)<defaults_senior and tranch_senior_outstanding_bal>0:
               #it absorbs all the defaults
               defaults_senior-=tranch_junior_outstanding_bal
               tranch_junior_outstanding_bal=0
               senior_prin=principal_tranch_senior+prepayment_senior+prepayment_junior+ principal_tranch_junior
               junior_prin=0
               junior_prin=+prepayment_junior+ principal_tranch_junior
               tranch_senior_outstanding_bal-=(defaults_senior+senior_prin)
               tranch_junior_outstanding_bal-=(defaults_junior+junior_prin)
               
             elif tranch_senior_outstanding_bal< (mortgage_pay_tranch_senior+prepayment_senior):    
               tranch_senior_outstanding_bal=0
               start_senior=0
               excess_prin=mortgage_pay_tranch_senior+prepayment_senior-tranch_senior_outstanding_bal
               junior_prin=+prepayment_junior + principal_tranch_junior + excess_prin
               tranch_junior_outstanding_bal-=(defaults_junior+junior_prin)
               net_int_tranch_senior=0
               tranch_senior_outstanding_bal-=(defaults_senior+senior_prin)
              
             elif tranch_junior_outstanding_bal>0 and tranch_senior_outstanding_bal==0:
               tranch_senior_outstanding_bal=0
               start_senior=0
               junior_prin=+prepayment_junior+ principal_tranch_junior
               tranch_senior_outstanding_bal=0
               tranch_junior_outstanding_bal-=(defaults_junior+junior_prin)
            
             tot_out_bal=tranch_junior_outstanding_bal+tranch_senior_outstanding_bal
             total_payment=junior_prin+senior_prin+ net_int_tranch_senior+ net_int_tranch_junior
             total_pay_senior=senior_prin+net_int_tranch_senior
             total_pay_junior=junior_prin + net_int_tranch_junior
             if tranch_senior_outstanding_bal<0:
                 tranch_senior_outstanding_bal=0
                 
             if tranch_senior_outstanding_bal>0:
                 average_age_senior=(j+1)/12
             else:
                 average_age_senior=average_age_senior
             if tranch_junior_outstanding_bal>0:
                 average_age_junior=(j+1)/12
             else:
                 average_age_junior=average_age_junior
                 
             if tot_out_bal<0:
                 average_age=(j+1)/12
                 j=N
             else:
                 j+=1
                 
             period_0 = dict(
            period=j,
            total_balance=tot_out_bal,
            outstanding_bal_junior=tranch_junior_outstanding_bal,
            outstanding_bal_senior=tranch_senior_outstanding_bal,
            tot_interest=net_int_tranch_senior+net_int_tranch_junior,
            int_senior=net_int_tranch_senior,
            int_junior=net_int_tranch_junior,
            payment_senior_tranch=mortgage_pay_tranch_senior,
            payment_junior_tranch=mortgage_pay_tranch_junior,
            scheduled_principal_senior=principal_tranch_senior,
            scheduled_principal_junior=principal_tranch_junior,
            prepayment_senior= prepayment_senior,
            prepayment_junior= prepayment_junior,
            defaults_senior=defaults_senior,
            recovery_senior=recovery_senior,
            defaults_junior=defaults_junior,
            recovery_junior=recovery_junior,
            total_cashflow=total_payment,
            cashflow_senior=total_pay_senior,
            cashflow_junior= total_pay_junior)
             period_list.append( period_0)
                        
        cash_flows_list = list(chain.from_iterable(period_list))       
        final_df=pd.DataFrame(period_list)
        ab=final_df['cashflow_junior'].sum()/(tranch_junior_df.groupby(['tranch_level'])[
            'Current_Principal_Balance'].sum(lambda x:tuple(x)).reset_index())['Current_Principal_Balance'][0]
        cd=final_df['cashflow_senior'].sum()/(tranch_senior_df.groupby(['tranch_level'])[
            'Current_Principal_Balance'].sum(lambda x:tuple(x)).reset_index())['Current_Principal_Balance'][0]
        ##
        list_age=[[average_age_senior,average_age_junior, average_age]]
        age_df=pd.DataFrame(list_age, columns=['Senior','Junior','Total'])
        print(age_df)
        return final_df
        
        
        
        
    
def payment_schedule_for_loan(loan_df_pk, original_balance, interest_rate, maturity, cdr, cpr, recovery_percentage, N, tranche, principal):
    """ Creates a payment schedule or cash flows for a loan.
    Payment schedules are presented as a list of "period" dictionaries. Each period representing one period
    of the maturity or term. A O period is created to represent the outflow of acquiring the loan. All
    subsequent periods represent incoming cash flows.
    Args:
        loan_df_pk: The loan primary key.
        original_balance: The original balance of the loan.
        interest_rate: The yearly interest rate of the loan.
        maturity: The maturity or term of the loan.
        cdr: The constant default rate of the loan.
        cpr: The constant prepayment rate of the loan.
        recovery_percentage: The recovery percentage of the loan.
        
    Returns: A payment schedule represented as a list of period dictionaries.
    Examples:
    >>> schedule = payment_schedule_for_loan(1, 100000, 0.04, 120, 0.09, 0.02, 0.95)
    >>> print(schedule)
    [
        {
            loan_df_pk: 1, period: 0, start_balance: 0.000000, remaining_term: 121,
            interest: 0.000000, payment: 0.000000, scheduled_principal: 0.000000,
            unscheduled_principal: 0, defaults: 0.000000, recovery: 0.000000,
            end_balance: 100000.000000
        },
        {
            loan_df_pk: 1, period: 1, start_balance: 100000.000000, remaining_term: 120,
            interest: 333.333333, payment: 1012.451382, scheduled_principal: 679.118048,
            unscheduled_principal: 0, defaults: 750.000000, recovery: 712.500000,
            end_balance: 98404.215285
        },
        .....etc....
    ]
    """
    period_list = [0] * (maturity + 1)
    period_0 = dict(
        loan_df_pk=loan_df_pk,
        period=0,
        start_balance=0,
        remaining_term=maturity + 1,
        interest=0,
        payment=0,
        scheduled_principal=0,
        prepayment=0,
        defaults=0,
        recovery=0,
        end_balance=original_balance,
        tranche=tranche,
        principal=principal
    )
    period_list[0] = period_0

    for i in range(1, maturity + 1):
        last_period = period_list[i - 1]

        period = create_payment_schedule_period(
            loan_df_pk, last_period['end_balance'], last_period['remaining_term'] - 1,
            cdr, cpr, i, interest_rate, recovery_percentage,  N , tranche, principal
        )
        period_list[i] = period

    return period_list


def create_payment_schedule_period(
        loan_df_pk, start_balance, remaining_term,
        cdr, cpr, period_num, interest_rate, recovery_percentage, N, tranche, principal):
    """ Create a period and associated information for a loan's payment schedule or cash flows.
    Args:
        loan_df_pk: The loan primary key.
        start_balance: The balance at the beginning of the period.
        remaining_term: The remaining terms after this period.
        cdr: The constant default rate.
        cpr: The constant prepayment rate.
        period_num: The period number.
        interest_rate: The yearly interest rate.
        recovery_percentage: The recovery percentage.
    
    Returns: A period represented as a dictionary.
    Examples:
    >>> period = create_payment_schedule_period(5, 87745.253381, 112, 0.09, 0.02, 9, 0.04, 0.95)
    >>> print(period)
    {
        loan_df_pk: 5, period: 9, start_balance: 87745.253381, remaining_term: 118,
        interest: 292.484178, payment: 940.050272, scheduled_principal: 647.566094,
        unscheduled_principal: 993.848452, defaults: 658.089400, recovery: 625.184930,
        end_balance: 86293.355798
    }
    """

    interest = interest_rate / 12 * start_balance
   
    #payment = calculate_monthly_payment(start_balance, interest_rate / 12, remaining_term)
    payment=-npf.pmt(interest_rate/12,remaining_term,start_balance,when='end')
    if payment>start_balance:
        payment=start_balance
    scheduled_principal = payment - interest
    
    
   
    
    
    x=Generate_Prepayment_Rate.select_prepayment_method(0)
    if x=='b':
       cpr=Generate_Prepayment_Rate.generate_CPR_PSA(period_num,N)
    else:
      cpr=Generate_Prepayment_Rate.a.iloc[period_num]
    prepayment = start_balance * cpr/12
    defaults = start_balance * cdr / 12
    end_balance = start_balance - scheduled_principal - prepayment - defaults
    
    if end_balance<0 or end_balance==0:
        remaining_term=1
        
    recovery = recovery_percentage * defaults
    
    period = dict(
        loan_df_pk=loan_df_pk,
        period=period_num,
        start_balance=start_balance,
        remaining_term=remaining_term,
        interest=interest,
        payment=payment,
        scheduled_principal=scheduled_principal,
        prepayment=prepayment,
        defaults=defaults,
        end_balance=end_balance,
        recovery=recovery,
        tranche=tranche
    )
    
    return period


def calculate_monthly_payment(start_balance, monthly_interest_rate, term):
    """ Calculates the fixed monthly payment of a loan given a term and without a future value.
    Args:
        start_balance: The starting balance of the loan.
        monthly_interest_rate: The monthly interest rate of the loan.
        term: The term of the loan.
    Returns: The monthly payment.
    Examples:
    >>> pymt = calculate_monthly_payment(100000, 0.003333333, 120)
    >>> print(pymt)
    1012.451382
    """
    numerator = (start_balance * (monthly_interest_rate * ((1 + monthly_interest_rate) ** term)))
    denominator = ((1 + monthly_interest_rate) ** term - 1)
    payment = numerator / denominator * 1.0
    return payment



   
def isfloat(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b 
    

    
    
    
    
        
    
        
        
        
        
        
      

