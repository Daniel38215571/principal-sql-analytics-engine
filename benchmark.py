import sqlite3
import time
import os

DB_NAME = "warehouse.db"

# Ensure we start fresh
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

# 1. Connect to SQLite
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 2. Load the Schema
print("Loading Schema...")
with open("schema.sql", "r") as f:
    cursor.executescript(f.read())

# CRITICAL: Turn off foreign keys AFTER schema load to allow synthetic data insertion
cursor.execute("PRAGMA foreign_keys = OFF;")

# 3. Generate 1,000,000 rows natively via Recursive CTE
print("Generating and inserting 1,000,000 transactions via SQL...")
start_insert = time.time()

cursor.execute("""
WITH RECURSIVE
  cnt(x) AS (
     SELECT 1
     UNION ALL
     SELECT x+1 FROM cnt
      LIMIT 1000000
  )
INSERT INTO fact_transactions (transaction_id, account_sk, merchant_sk, date_sk, amount, status)
SELECT
  'TX_' || x,
  (abs(random()) % 10000) + 1,
  (abs(random()) % 1000) + 1,
  20230101 + (abs(random()) % 300),
  (abs(random()) % 5000) + 10.0,
  CASE (abs(random()) % 3)
    WHEN 0 THEN 'SETTLED'
    WHEN 1 THEN 'FAILED'
    ELSE 'PENDING'
  END
FROM cnt;
""")
conn.commit()
print(f"Inserted 1,000,000 rows in {time.time() - start_insert:.2f} seconds.")

# 4. Define the Benchmark Query
query = """
SELECT account_sk, SUM(amount) as total_volume
FROM fact_transactions
WHERE status = 'SETTLED'
GROUP BY account_sk
ORDER BY total_volume DESC
LIMIT 10;
"""

# 5. Benchmark WITHOUT Index
print("\nBenchmarking without composite index...")
cursor.execute("DROP INDEX IF EXISTS idx_fact_composite;")
start_time = time.time()
cursor.execute(query)
cursor.fetchall() # Force execution
time_no_index = time.time() - start_time
print(f"Time without index: {time_no_index:.4f} seconds")

# 6. Benchmark WITH Index
print("\nBenchmarking with composite index...")
cursor.execute("CREATE INDEX idx_fact_composite ON fact_transactions(account_sk, date_sk, status);")
start_time = time.time()
cursor.execute(query)
cursor.fetchall() # Force execution
time_with_index = time.time() - start_time
print(f"Time with index: {time_with_index:.4f} seconds")

# 7. Show Execution Plan
print("\nEXPLAIN QUERY PLAN:")
cursor.execute(f"EXPLAIN QUERY PLAN {query}")
for row in cursor.fetchall():
    print(row)

conn.close()
