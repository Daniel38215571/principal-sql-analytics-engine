import sqlite3
import pandas as pd
import numpy as np
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

# 3. Generate 1,000,000 Rows of Synthetic Data
print("Generating 1,000,000 transactions...")
np.random.seed(42)
n_rows = 1000000

# Generate data directly into a DataFrame for fast insertion
df = pd.DataFrame({
    'transaction_id': [f"TX_{i}" for i in range(n_rows)],
    'account_sk': np.random.randint(1, 100000, size=n_rows),
    'merchant_sk': np.random.randint(1, 1000, size=n_rows),
    'date_sk': np.random.randint(20230101, 20231231, size=n_rows),
    'amount': np.random.uniform(10, 5000, size=n_rows),
    'status': np.random.choice(['SETTLED', 'FAILED', 'PENDING'], size=n_rows)
})

# 4. Insert Data in Bulk (Fast)
print("Inserting data into SQLite...")
df.to_sql('fact_transactions', conn, if_exists='append', index=False)

# 5. Benchmark Query: Find top accounts by volume
query = """
SELECT account_sk, SUM(amount) as total_volume
FROM fact_transactions
WHERE status = 'SETTLED'
GROUP BY account_sk
ORDER BY total_volume DESC
LIMIT 10;
"""

# 6. Measure Speed WITHOUT Index (Simulate a bad schema)
print("\nBenchmarking without composite index...")
cursor.execute("DROP INDEX IF EXISTS idx_fact_composite;")
start_time = time.time()
cursor.execute(query)
results_no_index = cursor.fetchall()
time_no_index = time.time() - start_time
print(f"Time without index: {time_no_index:.4f} seconds")

# 7. Measure Speed WITH Index
print("\nBenchmarking with composite index...")
cursor.execute("CREATE INDEX idx_fact_composite ON fact_transactions(account_sk, date_sk, status);")
start_time = time.time()
cursor.execute(query)
results_with_index = cursor.fetchall()
time_with_index = time.time() - start_time
print(f"Time with index: {time_with_index:.4f} seconds")

# 8. Explain Query Plan (The Principal Level Proof)
print("\nEXPLAIN QUERY PLAN (Proof of optimization):")
cursor.execute(f"EXPLAIN QUERY PLAN {query}")
for row in cursor.fetchall():
    print(row)

conn.close()
