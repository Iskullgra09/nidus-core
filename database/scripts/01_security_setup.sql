-- NIDUS CORE - GLOBAL SECURITY & RLS SETUP

-- 1. CLEANUP & SCHEMA PERMISSIONS
GRANT USAGE ON SCHEMA public TO nidus_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nidus_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nidus_app_user;

-- 2. ENABLE RLS
ALTER TABLE organization ENABLE ROW LEVEL SECURITY;
ALTER TABLE member ENABLE ROW LEVEL SECURITY;
ALTER TABLE role ENABLE ROW LEVEL SECURITY;
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;

-- 3. POLICIES

-- ORGANIZATION
DROP POLICY IF EXISTS organization_isolation_policy ON organization;
CREATE POLICY organization_isolation_policy ON organization
    AS PERMISSIVE FOR ALL TO nidus_app_user
    USING (
        (id::text = current_setting('app.current_organization_id', TRUE))
        OR 
        (current_setting('app.current_organization_id', TRUE) = '') 
    )
    WITH CHECK (true);

-- MEMBER
DROP POLICY IF EXISTS member_isolation_policy ON member;
CREATE POLICY member_isolation_policy ON member
    AS PERMISSIVE FOR ALL TO nidus_app_user
    USING (
        (organization_id::text = current_setting('app.current_organization_id', TRUE))
        OR 
        (current_setting('app.current_organization_id', TRUE) = '')
    )
    WITH CHECK (true);

-- ROLE
DROP POLICY IF EXISTS role_isolation_policy ON role;
CREATE POLICY role_isolation_policy ON role
    AS PERMISSIVE FOR ALL TO nidus_app_user
    USING (true)
    WITH CHECK (true);

-- USER
DROP POLICY IF EXISTS user_isolation_policy ON "user";
CREATE POLICY user_isolation_policy ON "user"
    AS PERMISSIVE FOR ALL TO nidus_app_user
    USING (
        (id::text = current_setting('app.current_user_id', TRUE))
        OR 
        (current_setting('app.current_organization_id', TRUE) = '')
    )
    WITH CHECK (true);