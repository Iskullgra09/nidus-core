-- 1. Enable RLS on core tables
ALTER TABLE organization ENABLE ROW LEVEL SECURITY;
ALTER TABLE member ENABLE ROW LEVEL SECURITY;
-- Note: 'user' is global in NIDUS, so we don't apply RLS to it yet 
-- unless we want users to be invisible to other orgs entirely.

-- 2. Define the "Tenant Isolation" Policy
-- We use a session variable 'app.current_organization_id' which FastAPI will set
CREATE POLICY organization_isolation_policy ON organization
    FOR ALL 
    TO nidus_app_user
    USING (id = NULLIF(current_setting('app.current_organization_id', TRUE), '')::uuid);

CREATE POLICY member_isolation_policy ON member
    FOR ALL 
    TO nidus_app_user
    USING (organization_id = NULLIF(current_setting('app.current_organization_id', TRUE), '')::uuid);

-- 3. Grant DML (Data) permissions to the App User
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nidus_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nidus_app_user;

-- 4. Revoke DDL (Structure) permissions from the App User
-- This ensures the App User cannot DROP tables or TRUNCATE
REVOKE ALL ON SCHEMA public FROM nidus_app_user;
GRANT USAGE ON SCHEMA public TO nidus_app_user;