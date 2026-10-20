# Principal-Level SQL Data Warehouse

A high-performance SQL data warehouse architecture designed to demonstrate advanced schema design, complex query optimization, and advanced analytical SQL at scale. 

This project moves beyond basic CRUD operations to prove competency in handling millions of rows, executing window functions, and optimizing query execution plans for financial analytics.

## Architecture: Star Schema
The warehouse is built on a Star Schema optimized for read-heavy analytical workloads.
- **Fact Table:** `fact_transactions` (1,000,000+ rows) tracking account activity, merchant interactions, dates, amounts, and settlement statuses.
- **Dimension Tables:** `dim_account`, `dim_merchant`, and `dim_date`.
- **Indexing:** Designed with composite indexes `(account_sk, date_sk, status)` to support high-cardinality filtering and fast aggregations.

## Advanced SQL Capabilities
The `advanced_queries.sql` file contains production-grade analytical queries proving the following concepts:
- **Window Functions:** Running totals, moving averages, and ranking (`RANK()`, `DENSE_RANK()`).
- **Segmentation:** Using `NTILE()` to segment customers into quartiles/deciles based on transaction volume.
- **Gap & Islands:** Using `ROW_NUMBER()` and date arithmetic to identify consecutive streaks of transaction activity or detect inactivity periods (churn).

## Benchmark Results & Query Optimization

To validate the architecture, I generated and inserted **1,000,000 synthetic transactions** into the `fact_transactions` table using a native Recursive CTE in SQLite. 

I then benchmarked a high-cardinality aggregation query to compare performance before and after applying the composite index `idx_fact_composite` on `(account_sk, date_sk, status)`.

### The Query
```sql
SELECT account_sk, SUM(amount) as total_volume
FROM fact_transactions
WHERE status = 'SETTLED'
GROUP BY account_sk
ORDER BY total_volume DESC
LIMIT 10;
