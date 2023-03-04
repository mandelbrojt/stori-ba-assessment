# Import required libraries and modules
import numpy as np
import math
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def compute_results(loan_feats_a: dict, loan_feats_b: dict):
    """Calculates the financial results of the given loan features during a period of 12 months"""

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

    # Number of delinquency accounts month-over-month of Contigo B
    contigo_b_delinq_accts_mom = contigo_b_accounts_mom * loan_feats_b["delinquency_rate"]

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
        "delinquency_accounts":np.concatenate((np.floor(contigo_a_delinq_accts_mom), np.floor(contigo_b_delinq_accts_mom))),
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

    return income_results

def overall_results(loan_feats_a: dict, loan_feats_b: dict):
    """Returns overall financial results of the given loan features"""
    results = compute_results(loan_feats_a,loan_feats_b)
    
    # Select financial metrics from results
    selected_cols = ["loan_type","interest_revenue","delinquency_loss","operative_costs","net_income"]

    # Group results by loan_type, sum columns, and transpose the result
    results_by_loan_type = results[selected_cols].groupby("loan_type").sum().T

    # Add a new column "Total" by summing results from Contigo A and Contigo B
    results_by_loan_type["Total"] = results_by_loan_type["Contigo A"] + results_by_loan_type["Contigo B"]

    # Format numbers to have commas per thousand and two decimals
    results_by_loan_type = results_by_loan_type.applymap(lambda x: "{:,.2f}".format(x))

    return results_by_loan_type

def quarterly_results(loan_feats_a: dict, loan_feats_b: dict):
    """Returns quearterly financial results of the given loan features"""
    results = compute_results(loan_feats_a,loan_feats_b)

    # Create a column with the quarter number based on the month number
    results["quarter"] = pd.PeriodIndex(pd.to_datetime(results["month"], format="%m"), freq="Q").strftime("Q%q")

    # Select financial metrics from results
    selected_cols = ["loan_type","quarter","interest_revenue","delinquency_loss","operative_costs","net_income"]

    # Group results by "loan_type" and "quarter", sum columns, and transpose the result
    quarterly_results_by_loan_type = results[selected_cols].groupby(["loan_type","quarter"]).sum().T

    # Format numbers to have commas per thousand and two decimals
    quarterly_results_by_loan_type = quarterly_results_by_loan_type.applymap(lambda x: "{:,.2f}".format(x))

    return quarterly_results_by_loan_type

def monthly_results(loan_feats_a: dict, loan_feats_b: dict):
    """Returns monthly financial results of the given loan features"""
    results = compute_results(loan_feats_a,loan_feats_b)

    # Select financial metrics from results
    selected_cols = ["month","loan_type","interest_revenue","delinquency_loss","operative_costs","net_income"]

    # Group results by "loan_type" and "month", sum columns, and transpose the result
    monthly_results_by_loan_type = results[selected_cols].groupby(["loan_type","month"]).sum().T

    # Format numbers to have commas per thousand and two decimals
    monthly_results_by_loan_type = monthly_results_by_loan_type.applymap(lambda x: "{:,.2f}".format(x))

    return monthly_results_by_loan_type

def visualize_results(loan_feats_a: dict, loan_feats_b: dict):
    """Returns a bar plot of net income results of the given loan features"""
    results = compute_results(loan_feats_a,loan_feats_b)
    contigo_a_results = results[results.loan_type == "Contigo A"]
    contigo_b_results = results[results.loan_type == "Contigo B"]

    fig = make_subplots(rows=1, cols=2)

    fig.add_trace(
        go.Bar(x=contigo_a_results.month,
            y=contigo_a_results.net_income,
            name="Contigo A",
            width=0.5,
            marker=dict(
                color="rgb(173,216,230)",
                line=dict(color="rgb(52,73,94)",width=0.5)
            )
            ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=contigo_b_results.month, 
            y=contigo_b_results.net_income, 
            name="Contigo B",
            width=0.5,
            marker=dict(
                color="rgb(170,150,218)",
                line=dict(color="rgb(52,73,94)", width=0.5)
            )
            ),
        row=1, col=2
    )

    fig.update_layout(height=450, width=850, title_text="Net Income by Loan Type")
    fig.update_xaxes(dtick=1)
    fig.update_xaxes(title_text="Month", row=1, col=1)
    fig.update_xaxes(title_text="Month", row=1, col=2)
    fig.update_yaxes(title_text="Net Income (in mexican pesos)", row=1, col=1)

    fig.show("svg")

if __name__ == "__main__":
    compute_results()
    overall_results()
    quarterly_results()
    monthly_results()
    visualize_results()
