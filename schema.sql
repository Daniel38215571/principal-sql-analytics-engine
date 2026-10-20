-- Principal Level Data Warehouse Schema
-- Star Schema: 1 Fact Table, 3 Dimension Tables
-- Engine: SQLite

PRAGMA foreign_keys = ON;

-- Dimension 1: Accounts
CREATE TABLE dim_accounts (
    account_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    customer_name TEXT,
    account_type TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dimension 2: Merchants
CREATE TABLE dim_merchants (
    merchant_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    merchant_category TEXT,
    risk_tier INTEGER
);

-- Dimension 3: Date
CREATE TABLE dim_date (
    date_sk INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    is_weekend BOOLEAN
);

-- Fact Table: Transactions
CREATE TABLE fact_transactions (
    transaction_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    account_sk INTEGER,
    merchant_sk INTEGER,
    date_sk INTEGER,
    amount REAL,
    status TEXT,
    FOREIGN KEY(account_sk) REFERENCES dim_accounts(account_sk),
    FOREIGN KEY(merchant_sk) REFERENCES dim_merchants(merchant_sk),
    FOREIGN KEY(date_sk) REFERENCES dim_date(date_sk)
);

-- PRINCIPAL LEVEL: Indexing Strategy
CREATE INDEX idx_fact_account ON fact_transactions(account_sk);
CREATE INDEX idx_fact_date ON fact_transactions(date_sk);
CREATE INDEX idx_fact_merchant ON fact_transactions(merchant_sk);
CREATE INDEX idx_fact_composite ON fact_transactions(account_sk, date_sk, status);
