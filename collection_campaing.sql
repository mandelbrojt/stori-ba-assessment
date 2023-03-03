select
    round(sum(`recov_debt`) / sum(`total_debt`) * count(`customer_id`)) as recovered_accounts,
    sum(`recov_debt`) as recovered_total_debt,
    sum(`recov_int`) as recovered_interest_revenue,
    sum(`phone_call_cost`) as total_campaign_cost,
    sum(`total_debt` - `recov_debt`) as delinquency_losses,
    sum(`total_recov`) as total_recovery
from
(select *,
	30 as phone_call_cost,
	round(`contactability_score` * 0.75, 4) as payment_score,
    round(`contactability_score` * 0.75 * `total_debt`, 4) as recov_debt,
    round(`contactability_score` * 0.75 * `interest`, 4) as recov_int,
    round((`contactability_score` * 0.75 * `total_debt`) + (`contactability_score` * 0.75 * `interest`), 4) as total_recov
from `contactability_scores`) as campaign_results;