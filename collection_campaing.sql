select
    round(sum(`recov_debt`) / sum(`total_debt`) * count(`customer_id`)) as total_accounts_recovered,
    sum(`recov_debt`) as total_debt_recovered,
    sum(`recov_int`) as total_interest_recovered,
    sum(`phone_call_cost`) as total_campaign_cost,
    sum(`total_debt`) - sum(`recov_debt`) as total_uncollected_debt,
    sum(`recov_int`) - sum(`phone_call_cost`) + sum(`recov_debt`) as collections_income
from
(select *,
	30 as phone_call_cost,
	round(`contactability_score` * 0.75, 4) as answer_payment_prob,
    round(`contactability_score` * 0.75 * `total_debt`, 4) as recov_debt,
    round(`contactability_score` * 0.75 * `interest`, 4) as recov_int,
    round((`contactability_score` * 0.75 * `total_debt`) + (`contactability_score` * 0.75 * `interest`), 4) as total_recov
from `contactability_scores`) as collections_campaign;