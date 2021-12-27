# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 16:04:12 2021

@author: ayubh
"""

import Pricing_and_Cashflows as cf
import pandas as pd
import random

df = pd.read_csv (r"C:/Users/ayubh/Desktop/MBS MODEL/Loan_Data_1.csv")
df.fillna(0, inplace=True)
loan_df = pd.DataFrame(df)

def pd_data_frame_columns_to_float(data_frame, field_list):
    data_frame[field_list] = data_frame[field_list].astype(float)
    return data_frame

def generate_adjusted_cdr(row):
    change = random_change()
    adjusted_cdr = row['constant_default_rate'] * change / 100

    if adjusted_cdr < 0.005:
        return 0.005
    elif adjusted_cdr > 0.25:
        return 0.25
    return adjusted_cdr


def generate_adjusted_cpr(row):
    adjusted_cpr = row['constant_prepayment_rate'] * random_change(factor_number=5) / 100
    if adjusted_cpr > 0.25:
        return 0.25
    elif adjusted_cpr < 0.05:
        return 0.05
    return adjusted_cpr


def generate_adjusted_recovery(row):
    recovery = row['recovery_percentage'] * random_change(factor_number=1) / 100
    if recovery < 0:
        return 0.0
    elif recovery > 1.0:
        return 1.0
    return recovery

def label_tranche(row):
    if row['Lien_Position']==1:
        tranche_label=1
    else:
        tranche_label=2
    return tranche_label

def random_change(factor_number=3, change_range=5, how_many_chances=5):
    change = 0
    for i in range(factor_number):
        chance = random.randrange(how_many_chances)
        if chance == 1:
            change += random.uniform(-change_range, change_range)
    return 100 + change


# Change pandas dtype of the following fields from object to float64.
field_list = [
        'Current_Principal_Balance',
        'Current_Interest_Rate',
        'Original_Amount'
        # 'current_property_value',
        # 'deferred_balance',
        # 'gross_margin',
        # 'junior_lien_balance'
        # 'original_appraisal_amount',
        # 'original_rate',,
        # 'last_payment_received',
        # 'original_amount',
        # 'reset_index',
        # 'senior_lien_balance'
        
    ]
loan_df = pd_data_frame_columns_to_float(data_frame=loan_df, field_list=field_list)

loan_df['Original_Term'] = loan_df['Original_Term'].astype(int)
loan_df['Lien_Position'] =loan_df ['Lien_Position']. astype(int)
#senior tranche-> Lien position 1
#junior tranche-> lien position 0 or 2

# Add default economic assumptions.
loan_df['constant_default_rate'] = float(0.10) / 100
#override this to account for different prepayment speeds
loan_df['constant_prepayment_rate'] = float(0.08) / 100
loan_df['recovery_percentage'] = float(0.05) / 100

adjusted_cdr_series = loan_df.apply(
    generate_adjusted_cdr,
    axis=1
)

loan_df['adjusted_cdr'] = adjusted_cdr_series

adjusted_cpr_series = loan_df.apply(
    generate_adjusted_cpr,
    axis=1
)

loan_df['adjusted_cpr'] = adjusted_cpr_series

adjusted_recovery_series = loan_df.apply(
    generate_adjusted_recovery,
    axis=1
)

loan_df['adjusted_recovery'] = adjusted_recovery_series

tranch_group = loan_df.apply(label_tranche,axis=1)
loan_df['tranch_level']=tranch_group



#This will go in next code file for pricing
x=cf.Loan_Portfolio(0.10,loan_df)
y=x.cash_flows_aggregate_for_portfolio()
z=x.cash_flow_tranchwise(loan_df)
print(y["total_payments"])



