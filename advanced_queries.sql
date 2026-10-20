-- =====================================================================
-- PRINCIPAL LEVEL ANALYTICS QUERIES
-- =====================================================================

-- 1. NTILE & PERCENTILES
-- Business Value: Find the top 1% of accounts by transaction volume.
-- Principal Level: Uses NTILE to bucket millions of accounts into 100 groups.
WITH account_volumes AS (
    SELECT 
        account_sk,
        SUM(amount) as total_volume
    FROM fact_transactions
    WHERE status = 'SETTLED'
    GROUP BY account_sk
),
percentiles AS (
    SELECT 
        account_sk,
        total_volume,
        NTILE(100) OVER (ORDER BY total_volume DESC) as percentile_bucket
    FROM account_volumes
)
SELECT * FROM percentiles WHERE percentile_bucket = 1;

-- 2. CONSECUTIVE FAILED TRANSACTIONS (Gap & Islands)
-- Business Value: Flag accounts with 3+ consecutive failed transactions.
-- Principal Level: Uses LEAD() to look ahead and group consecutive failures.
WITH failure_sequence AS (
    SELECT 
        account_sk,
        transaction_sk,
        status,
        LEAD(status, 1) OVER (PARTITION BY account_sk ORDER BY transaction_sk) as next_status,
        LEAD(status, 2) OVER (PARTITION BY account_sk ORDER BY transaction_sk) as next_next_status
    FROM fact_transactions
)
SELECT DISTINCT account_sk
FROM failure_sequence
WHERE status = 'FAILED' AND next_status = 'FAILED' AND next_next_status = 'FAILED';

-- 3. ROLLING 30-DAY ACTIVE USERS (Window Function)
-- Business Value: Calculate DAU/MAU ratio for each merchant.
-- Principal Level: Uses subqueries to calculate rolling distinct counts.
SELECT 
    d.full_date,
    COUNT(DISTINCT f.account_sk) as daily_active_users,
    (
        SELECT COUNT(DISTINCT f2.account_sk)
        FROM fact_transactions f2
        JOIN dim_date d2 ON f2.date_sk = d2.date_sk
        WHERE d2.full_date BETWEEN date(d.full_date, '-30 days') AND d.full_date
    ) as rolling_30d_active_users
FROM fact_transactions f
JOIN dim_date d ON f.date_sk = d.date_sk
GROUP BY d.full_date;
