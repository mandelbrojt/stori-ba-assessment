import numpy as np
import math
import pandas as pd
import plotly.express as px

# Contigo A loan features
contigo_a_features = {
    "loan_amt":1000,
    "loan_term":1,
    "interest_rate":0.15,
    "delinquency_rate":0.135,
    "initial_num_accounts":5000,
    "account_growth_mom":0.25,
    "op_cost_per_acct":30
}

# Contigo B loan features
contigo_b_features = {
    "loan_amt":2000,
    "loan_term":1,
    "interest_rate":0.1,
    "delinquency_rate":0.08,
    "initial_num_accounts":10000,
    "account_growth_mom":0.10,
    "op_cost_per_acct":30
}

def compute_accounts(initial_accounts: int, growth_rate: float, num_months=12):
    """Computes the number of accounts during 12 months based on a specific MoM growth rate"""
    return [math.floor(initial_accounts * (1+ growth_rate) ** i) for i in range(num_months)]

# Number of accounts month-over-month of Contigo A
contigo_a_accounts_mom = \
    np.array(compute_accounts(contigo_a_features["initial_num_accounts"], contigo_a_features["account_growth_mom"]))

# Number of accounts month-over-month of Contigo B
contigo_b_accounts_mom = \
    np.array(compute_accounts(contigo_b_features["initial_num_accounts"], contigo_b_features["account_growth_mom"]))

# Number of delinquency accounts month-over-month of Contigo A
contigo_a_delinq_accts_mom = contigo_a_accounts_mom * contigo_a_features["delinquency_rate"]
# Round down every element in the array to the nearest whole number
contigo_a_delinq_accts_mom = np.floor(contigo_a_delinq_accts_mom)

# Number of delinquency accounts month-over-month of Contigo B
contigo_b_delinq_accts_mom = contigo_b_accounts_mom * contigo_b_features["delinquency_rate"]
# Round down every element in the array to the nearest whole number
contigo_b_delinq_accts_mom = np.floor(contigo_b_delinq_accts_mom)

def compute_interest_rev(loan_feats: dict, loan_accounts_mom):
    """Computes the month-over-month interest revenue of a loan type"""
    interest_revenue_per_account = \
        loan_feats["loan_amt"]*loan_feats["interest_rate"]*loan_feats["loan_term"]*(1-loan_feats["delinquency_rate"])
    return loan_accounts_mom * interest_revenue_per_account

# Interest revenue month-over-month of Contigo A
contigo_a_interest_rev_mom = compute_interest_rev(contigo_a_features, contigo_a_accounts_mom)

# Interest revenue month-over-month of Contigo B
contigo_b_interest_rev_mom = compute_interest_rev(contigo_b_features, contigo_b_accounts_mom)

# Delinquency loss month-over-month of Contigo A
contigo_a_delinq_loss_mom = contigo_a_delinq_accts_mom * contigo_a_features["loan_amt"]

# Delinquency loss month-over-month of Contigo B
contigo_b_delinq_loss_mom = contigo_b_delinq_accts_mom * contigo_b_features["loan_amt"]

# Operative cost month-over-month of Contigo A
contigo_a_op_cost_mom = contigo_a_accounts_mom * contigo_a_features["op_cost_per_acct"]

# Operative cost month-over-month of Contigo B
contigo_b_op_cost_mom = contigo_b_accounts_mom * contigo_b_features["op_cost_per_acct"]

# Net income month-over-month of Contigo A
contigo_a_net_income_mom = contigo_a_interest_rev_mom - contigo_a_op_cost_mom - contigo_a_delinq_loss_mom

# Net income month-over-month of Contigo B
contigo_b_net_income_mom = contigo_b_interest_rev_mom - contigo_b_op_cost_mom - contigo_b_delinq_loss_mom

# Maps column names to values
cols_to_values = {
    "month":np.concatenate((np.arange(1,13), np.arange(1,13))),
    "loan_type":["Contigo A"] * 12 + ["Contigo B"] * 12,
    "accounts":np.concatenate((contigo_a_accounts_mom, contigo_b_accounts_mom)),
    "delinquency_accounts":np.concatenate((contigo_a_delinq_accts_mom, contigo_b_delinq_accts_mom)),
    "interest_revenue":np.concatenate((contigo_a_interest_rev_mom, contigo_b_interest_rev_mom)),
    "delinquency_loss":np.concatenate((contigo_a_delinq_loss_mom, contigo_b_delinq_loss_mom)),
    "operative_costs":np.concatenate((contigo_a_op_cost_mom, contigo_b_op_cost_mom)),
    "net_income":np.concatenate((contigo_a_net_income_mom, contigo_b_net_income_mom))
}

# Creates a DataFrame with the results of Contigo loans
collection_results = pd.DataFrame(cols_to_values)

# Converts loan type column to a categorical data type
collection_results["loan_type"] = pd.Categorical(collection_results.loan_type)

# Converts delinquency accounts to an integer data type
collection_results["delinquency_accounts"] = collection_results.delinquency_accounts.astype("int")