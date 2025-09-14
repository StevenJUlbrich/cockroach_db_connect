# SQL Directory Structure

## Overview
This directory contains all SQL statements, templates, and migrations for the CockroachDB Connect application.

## Directory Structure

```
sql/
├── queries/              # Reusable SQL queries
│   ├── reconciliation/   # Reconciliation-specific queries
│   ├── reporting/        # Reporting queries
│   └── maintenance/      # Database maintenance queries
├── templates/            # SQL templates with variable substitution
└── migrations/           # Database schema migrations
```

## Usage Guidelines

### 1. Queries Directory (`/queries`)
Store static SQL queries organized by functional area.

**Naming Convention**: `<action>_<entity>.sql`
- Examples: `get_user_transactions.sql`, `update_account_balance.sql`

**File Format**:
```sql
-- Name: get_user_transactions
-- Description: Retrieves all transactions for a specific user
-- Parameters: :user_id (integer)
-- Returns: transaction_id, amount, timestamp, status

SELECT 
    transaction_id,
    amount,
    created_at as timestamp,
    status
FROM transactions
WHERE user_id = :user_id
ORDER BY created_at DESC;
```

### 2. Templates Directory (`/templates`)
Store SQL templates that require dynamic construction.

**Naming Convention**: `<entity>_template.sql`
- Examples: `dynamic_report_template.sql`, `batch_insert_template.sql`

**File Format**:
```sql
-- Template: dynamic_report
-- Description: Flexible reporting template
-- Variables: ${table_name}, ${columns}, ${conditions}

SELECT ${columns}
FROM ${table_name}
WHERE ${conditions}
ORDER BY ${order_by};
```

### 3. Migrations Directory (`/migrations`)
Store database schema migrations in sequential order.

**Naming Convention**: `V<version>__<description>.sql`
- Examples: `V001__initial_schema.sql`, `V002__add_user_table.sql`

**File Format**:
```sql
-- Migration: V001__initial_schema
-- Description: Creates initial database schema
-- Author: Team
-- Date: 2024-01-15

CREATE TABLE IF NOT EXISTS ...
```

## Query Categories

### Reconciliation Queries
- Transaction matching
- Balance verification
- Data consistency checks
- Audit trail queries

### Reporting Queries
- Daily/Monthly reports
- Performance metrics
- User activity reports
- System health reports

### Maintenance Queries
- Index optimization
- Statistics updates
- Cleanup operations
- Performance tuning

## Best Practices

1. **Always include metadata comments** at the top of each SQL file
2. **Use parameter placeholders** (`:param_name`) for dynamic values
3. **Format SQL** for readability (uppercase keywords, proper indentation)
4. **Version control** all changes with meaningful commit messages
5. **Test queries** in development before adding to repository
6. **Document complex logic** with inline comments
7. **Avoid SELECT *** in production queries

## Example Query File

```sql
-- Name: get_reconciliation_report
-- Description: Generates reconciliation report for specified date range
-- Parameters: 
--   :start_date (date) - Start of reporting period
--   :end_date (date) - End of reporting period
--   :account_id (string) - Optional account filter
-- Returns: account_id, transaction_count, total_amount, status
-- Author: Team
-- Created: 2024-01-15
-- Modified: 2024-01-20 - Added account filter

SELECT 
    t.account_id,
    COUNT(*) as transaction_count,
    SUM(t.amount) as total_amount,
    CASE 
        WHEN SUM(t.amount) = a.expected_balance THEN 'MATCHED'
        ELSE 'DISCREPANCY'
    END as status
FROM 
    transactions t
    JOIN accounts a ON t.account_id = a.id
WHERE 
    t.created_at BETWEEN :start_date AND :end_date
    AND (:account_id IS NULL OR t.account_id = :account_id)
GROUP BY 
    t.account_id, a.expected_balance
HAVING 
    COUNT(*) > 0
ORDER BY 
    status DESC, 
    t.account_id;
```

## Loading Queries in Code

```python
from cockroach_db_connect.sql import SQLRepository

# Initialize repository
repo = SQLRepository()

# Load all queries from directory
repo.load_directory("sql/queries")

# Execute named query
result = db.execute_named_query(
    "get_reconciliation_report",
    start_date="2024-01-01",
    end_date="2024-01-31",
    account_id=None
)
```

## Contributing

When adding new SQL files:
1. Follow the naming conventions
2. Include complete metadata headers
3. Test the query against dev database
4. Submit PR with description of use case
5. Update this README if adding new categories