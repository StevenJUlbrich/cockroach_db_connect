-- Name: get_table_list
-- Description: Retrieves list of tables in specified schema
-- Parameters: 
--   :schema_name (string) - Schema name (default: 'public')
-- Returns: table_name, table_type, row_count_estimate
-- Author: Team
-- Created: 2024-01-15

SELECT 
    t.table_name,
    t.table_type,
    COALESCE(s.n_live_tup, 0) as row_count_estimate
FROM 
    information_schema.tables t
    LEFT JOIN pg_stat_user_tables s 
        ON t.table_name = s.relname 
        AND t.table_schema = s.schemaname
WHERE 
    t.table_schema = COALESCE(:schema_name, 'public')
    AND t.table_type = 'BASE TABLE'
ORDER BY 
    t.table_name;