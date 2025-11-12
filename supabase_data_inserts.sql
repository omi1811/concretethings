-- Supabase Data Migration - INSERT Statements
-- Generated from SQLite data on 2025-11-12
-- 
-- INSTRUCTIONS:
-- 1. First run supabase_migration.sql to create the schema
-- 2. Then run this file to insert your data
-- 3. Open Supabase SQL Editor and execute this script

-- ==============================================
-- Insert actual data from SQLite
-- ==============================================

-- Companies
INSERT INTO companies (id, name, subscription_plan, active_projects_limit, price_per_project, 
    billing_status, subscription_start_date, subscription_end_date, last_payment_date, 
    next_billing_date, company_email, company_phone, company_address, gstin, is_active, 
    created_at, updated_at)
VALUES 
    (1, 'Test Construction Co.', 'trial', 5, 5000.0, 'active', NULL, NULL, NULL, NULL, 
     NULL, NULL, NULL, NULL, true, '2025-11-12 07:14:16.605612', '2025-11-12 07:14:16.605617')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    subscription_plan = EXCLUDED.subscription_plan,
    updated_at = EXCLUDED.updated_at;

-- Users
INSERT INTO users (id, email, phone, full_name, password_hash, company_id, role, 
    is_active, last_login, created_at, updated_at)
VALUES 
    (1, 'test@example.com', '+919876543210', 'Test User', 
     'scrypt:32768:8:1$McXlQgks3HIw1SWL$ef5f78f824f80d048a62587f7d883201232320c4c80959e8c87bbe4c378c6e5a4c4d8eec98471660de6a0d31c4f10b6068f5e947cfeb4de577e340e31f6ea422',
     1, 'SuperAdmin', true, '2025-11-12 07:24:26.703478', 
     '2025-11-12 07:14:16.695804', '2025-11-12 07:24:26.703963')
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = EXCLUDED.updated_at;

-- Projects
INSERT INTO projects (id, company_id, name, location, description, 
    project_type, status, is_active, created_at, updated_at)
VALUES 
    (1, 1, 'Test Building Project', 'Mumbai, India',
     'Test project for Material Vehicle Register', 
     'construction', 'active', true, 
     '2025-11-12 07:14:16.698704', '2025-11-12 07:14:16.698707')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    updated_at = EXCLUDED.updated_at;

-- Project Memberships
INSERT INTO project_memberships (id, user_id, project_id, role, joined_at)
VALUES 
    (1, 1, 1, 'QualityEngineer', '2025-11-12 07:14:16.700171')
ON CONFLICT (user_id, project_id) DO UPDATE SET
    role = EXCLUDED.role;

-- RMC Vendors (needed for batch_registers foreign key)
INSERT INTO rmc_vendors (id, project_id, vendor_name, vendor_code, contact_person, 
    phone, email, address, is_active, created_at, updated_at)
VALUES 
    (1, 1, 'ABC Concrete Pvt Ltd', 'ABC-001', NULL, NULL, NULL, NULL, 
     true, '2025-11-12 07:14:16', '2025-11-12 07:14:16')
ON CONFLICT (project_id, vendor_name) DO UPDATE SET
    updated_at = EXCLUDED.updated_at;

-- Mix Designs (needed for batch_registers foreign key)
INSERT INTO mix_designs (id, project_id, grade, mix_id, cement_content, 
    water_cement_ratio, aggregate_ratio, is_active, created_at, updated_at)
VALUES 
    (1, 1, 'M25', 'M25-001', NULL, NULL, NULL, 
     true, '2025-11-12 07:14:16', '2025-11-12 07:14:16')
ON CONFLICT (project_id, grade, mix_id) DO UPDATE SET
    updated_at = EXCLUDED.updated_at;

-- Batch Registers
INSERT INTO batch_registers (id, project_id, batch_number, batch_time, 
    rmc_vendor_id, mix_design_id, quantity, truck_number, challan_number, 
    slump_value, temperature, building_name, floor_level, structural_element_type, 
    remarks, created_by, created_at, updated_at)
VALUES 
    (1, 1, 'BATCH-2025-0001', '2025-11-12 07:24:26.713390', 
     1, 1, 1.0, 'MH-01-1234', NULL, 32, 100.0, 
     'Building A', '5th Floor Slab', 'Slab', NULL, 
     1, '2025-11-12 07:24:26.743814', '2025-11-12 07:24:26.743818')
ON CONFLICT (id) DO UPDATE SET
    batch_number = EXCLUDED.batch_number,
    updated_at = EXCLUDED.updated_at;

-- Material Vehicle Register
INSERT INTO material_vehicle_register (id, project_id, vehicle_number, material_type, 
    supplier_name, driver_name, driver_phone, entry_time, exit_time, purpose, 
    notes, recorded_by, created_at, updated_at)
VALUES 
    (1, 1, 'MH-01-1234', 'Concrete', 'ABC Concrete Pvt Ltd', 
     'John Doe', '+919876543210', '2025-11-12 07:24:26.713390', NULL, 
     'Slab casting - Building A', NULL, 1, 
     '2025-11-12 07:24:26.713885', '2025-11-12 07:24:26.744111'),
    (2, 1, 'MH-02-5678', 'Steel', 'XYZ Steel Suppliers', 
     'Jane Smith', '+919876543211', '2025-11-12 07:24:26.721234', NULL, 
     'Steel delivery', NULL, 1, 
     '2025-11-12 07:24:26.721512', '2025-11-12 07:24:26.721515')
ON CONFLICT (id) DO UPDATE SET
    vehicle_number = EXCLUDED.vehicle_number,
    updated_at = EXCLUDED.updated_at;

-- Link vehicle to batch (update material_vehicle_register)
UPDATE material_vehicle_register 
SET batch_id = 1 
WHERE id = 1;

-- ==============================================
-- Reset sequences to match current max IDs
-- ==============================================
SELECT setval('companies_id_seq', (SELECT COALESCE(MAX(id), 1) FROM companies), true);
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users), true);
SELECT setval('projects_id_seq', (SELECT COALESCE(MAX(id), 1) FROM projects), true);
SELECT setval('project_memberships_id_seq', (SELECT COALESCE(MAX(id), 1) FROM project_memberships), true);
SELECT setval('rmc_vendors_id_seq', (SELECT COALESCE(MAX(id), 1) FROM rmc_vendors), true);
SELECT setval('mix_designs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM mix_designs), true);
SELECT setval('batch_registers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM batch_registers), true);
SELECT setval('material_vehicle_register_id_seq', (SELECT COALESCE(MAX(id), 1) FROM material_vehicle_register), true);

-- ==============================================
-- Verification
-- ==============================================
SELECT '=== Migration Data Summary ===' as status;
SELECT 'companies' as table_name, COUNT(*) as row_count FROM companies
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'project_memberships', COUNT(*) FROM project_memberships
UNION ALL
SELECT 'rmc_vendors', COUNT(*) FROM rmc_vendors
UNION ALL
SELECT 'mix_designs', COUNT(*) FROM mix_designs
UNION ALL
SELECT 'batch_registers', COUNT(*) FROM batch_registers
UNION ALL
SELECT 'material_vehicle_register', COUNT(*) FROM material_vehicle_register;

SELECT '✓ Data migration complete!' as message;
