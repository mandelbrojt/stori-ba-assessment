# Import required libraries and modules
import numpy as np
import math
import pandas as pd
import plotly.express as px

def financial_results(loan_feats_a: dict, loan_feats_b: dict):

    def compute_accounts(initial_accounts: int, growth_rate: float, num_months=12):
        """Computes the number of accounts by each month during a period of 12 months given a MoM growth rate"""
        return [math.floor(initial_accounts * (1+ growth_rate) ** i) for i in range(num_months)]    

    def compute_interest_rev(loan_feats: dict, loan_accounts_mom):
        """Computes the interest revenue by each month during a period of 12 months"""
        interest_revenue_per_account = \
            loan_feats["loan_amt"]*loan_feats["interest_rate"]*loan_feats["loan_term"]*(1-loan_feats["delinquency_rate"])
        return loan_accounts_mom * interest_revenue_per_account

    # Number of accounts month-over-month of Contigo A
    contigo_a_accounts_mom = \
        np.array(compute_accounts(loan_feats_a["initial_num_accounts"], loan_feats_a["account_growth_mom"]))

    # Number of accounts month-over-month of Contigo B
    contigo_b_accounts_mom = \
        np.array(compute_accounts(loan_feats_b["initial_num_accounts"], loan_feats_b["account_growth_mom"]))

    # Number of delinquency accounts month-over-month of Contigo A
    contigo_a_delinq_accts_mom = contigo_a_accounts_mom * loan_feats_a["delinquency_rate"]

    # Round down every element in the array to the nearest whole number
    contigo_a_delinq_accts_mom = np.floor(contigo_a_delinq_accts_mom)

    # Number of delinquency accounts month-over-month of Contigo B
    contigo_b_delinq_accts_mom = contigo_b_accounts_mom * loan_feats_b["delinquency_rate"]

    # Round down every element in the array to the nearest whole number
    contigo_b_delinq_accts_mom = np.floor(contigo_b_delinq_accts_mom)

    # Interest revenue month-over-month of Contigo A
    contigo_a_interest_rev_mom = compute_interest_rev(loan_feats_a, contigo_a_accounts_mom)

    # Interest revenue month-over-month of Contigo B
    contigo_b_interest_rev_mom = compute_interest_rev(loan_feats_b, contigo_b_accounts_mom)

    # Delinquency loss month-over-month of Contigo A
    contigo_a_delinq_loss_mom = contigo_a_delinq_accts_mom * loan_feats_a["loan_amt"]

    # Delinquency loss month-over-month of Contigo B
    contigo_b_delinq_loss_mom = contigo_b_delinq_accts_mom * loan_feats_b["loan_amt"]

    # Operative cost month-over-month of Contigo A
    contigo_a_op_cost_mom = contigo_a_accounts_mom * loan_feats_a["op_cost_per_acct"]

    # Operative cost month-over-month of Contigo B
    contigo_b_op_cost_mom = contigo_b_accounts_mom * loan_feats_b["op_cost_per_acct"]

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
    income_results = pd.DataFrame(cols_to_values)

    # Converts loan type column to a categorical data type
    income_results["loan_type"] = pd.Categorical(income_results.loan_type)

    # Converts delinquency accounts to an integer data type
    income_results["delinquency_accounts"] = income_results.delinquency_accounts.astype("int")

    # Create a column with the quarter number based on the month number
    income_results["quarter"] = pd.PeriodIndex(pd.to_datetime(income_results["month"], format="%m"), freq="Q").strftime("Q%q")

    # Select financial metrics from startup results
    selected_cols = ["loan_type","interest_revenue","delinquency_loss","operative_costs","net_income"]

    # Group income_results by loan_type, sum columns, and transpose the result
    results_by_loan_type = income_results[selected_cols].groupby("loan_type").sum().T

    # Add a new column "Total" by summing results from Contigo A and Contigo B
    results_by_loan_type["Total"] = results_by_loan_type["Contigo A"] + results_by_loan_type["Contigo B"]

    # Format numbers to have commas per thousand and two decimals
    results_by_loan_type = results_by_loan_type.applymap(lambda x: "{:,.2f}".format(x))

    return results_by_loan_type

if __name__ == "__main__":
    financial_results()
