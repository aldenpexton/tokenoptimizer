-- Create a function to execute raw SQL queries safely
CREATE OR REPLACE FUNCTION execute_raw_query(query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN (SELECT json_agg(t) FROM (SELECT * FROM json_to_recordset((query)::json) as t) as subq);
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_array();
END;
$$; 