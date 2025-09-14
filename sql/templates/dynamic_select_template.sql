-- Template: dynamic_select
-- Description: Flexible SELECT query template for dynamic query construction
-- Variables: 
--   ${columns} - Comma-separated list of columns
--   ${table_name} - Target table name
--   ${join_clause} - Optional JOIN clause
--   ${where_clause} - Optional WHERE conditions
--   ${group_by} - Optional GROUP BY clause
--   ${having_clause} - Optional HAVING clause
--   ${order_by} - Optional ORDER BY clause
--   ${limit} - Optional LIMIT value
-- Author: Team
-- Created: 2024-01-15

SELECT ${columns}
FROM ${table_name}
${join_clause}
${where_clause}
${group_by}
${having_clause}
${order_by}
${limit};