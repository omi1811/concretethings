-- Supabase Migration Script for ConcreteThings
-- Generated from SQLite data on 2025-11-12
-- 
-- INSTRUCTIONS:
-- 1. Open your Supabase project: https://supabase.com/dashboard
-- 2. Navigate to SQL Editor
-- 3. Create a new query
-- 4. Copy and paste this entire file
-- 5. Execute the query
-- 
-- This script will:
-- - Create all tables (if they don't exist)
-- - Insert your data
-- - Set up sequences for auto-increment IDs

-- Disable triggers temporarily for faster insertion
SET session_replication_role = 'replica';

-- ==============================================
-- TABLE: companies
-- ==============================================
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    subscription_plan VARCHAR(50) NOT NULL,
    active_projects_limit INTEGER NOT NULL,
    price_per_project FLOAT NOT NULL,
    billing_status VARCHAR(50) NOT NULL,
    subscription_start_date TIMESTAMP,
    subscription_end_date TIMESTAMP,
    last_payment_date TIMESTAMP,
    next_billing_date TIMESTAMP,
    company_email VARCHAR(255),
    company_phone VARCHAR(20),
    company_address TEXT,
    gstin VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert companies data
INSERT INTO companies (id, name, subscription_plan, active_projects_limit, price_per_project, billing_status, 
    subscription_start_date, subscription_end_date, last_payment_date, next_billing_date, 
    company_email, company_phone, company_address, gstin, is_active, created_at, updated_at)
VALUES 
    (1, 'Test Construction Co.', 'trial', 5, 5000.0, 'active', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, '2025-11-12 07:14:16.605612', '2025-11-12 07:14:16.605617')
ON CONFLICT (id) DO NOTHING;

-- ==============================================
-- TABLE: users
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Note: You'll need to extract the actual user data from sqlite_dump.sql
-- Look for the INSERT INTO users line and copy the values here

-- ==============================================
-- TABLE: projects
-- ==============================================
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    project_type VARCHAR(50) NOT NULL,
    start_date DATE,
    expected_end_date DATE,
    actual_end_date DATE,
    project_manager VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: project_memberships
-- ==============================================
CREATE TABLE IF NOT EXISTS project_memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, project_id)
);

-- ==============================================
-- TABLE: material_categories
-- ==============================================
CREATE TABLE IF NOT EXISTS material_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: rmc_vendors
-- ==============================================
CREATE TABLE IF NOT EXISTS rmc_vendors (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_code VARCHAR(100),
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, vendor_name)
);

-- ==============================================
-- TABLE: mix_designs
-- ==============================================
CREATE TABLE IF NOT EXISTS mix_designs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    grade VARCHAR(50) NOT NULL,
    mix_id VARCHAR(100),
    cement_content FLOAT,
    water_cement_ratio FLOAT,
    aggregate_ratio VARCHAR(100),
    admixture_details TEXT,
    slump_value INTEGER,
    compressive_strength_7day FLOAT,
    compressive_strength_28day FLOAT,
    design_date DATE,
    approved_by VARCHAR(255),
    remarks TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, grade, mix_id)
);

-- ==============================================
-- TABLE: approved_brands
-- ==============================================
CREATE TABLE IF NOT EXISTS approved_brands (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    material_category_id INTEGER NOT NULL REFERENCES material_categories(id) ON DELETE CASCADE,
    brand_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    specifications TEXT,
    approved_date DATE,
    approved_by VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: project_settings
-- ==============================================
CREATE TABLE IF NOT EXISTS project_settings (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE UNIQUE,
    vehicle_allowed_time_hours FLOAT NOT NULL DEFAULT 3.0,
    enable_material_vehicle_addon BOOLEAN NOT NULL DEFAULT false,
    enable_pour_activity_reminders BOOLEAN NOT NULL DEFAULT true,
    enable_test_reminders BOOLEAN NOT NULL DEFAULT true,
    reminder_hours_before_test INTEGER NOT NULL DEFAULT 24,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: material_vehicle_register
-- ==============================================
CREATE TABLE IF NOT EXISTS material_vehicle_register (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    vehicle_number VARCHAR(50) NOT NULL,
    driver_name VARCHAR(255) NOT NULL,
    driver_phone VARCHAR(20),
    material_type VARCHAR(100) NOT NULL,
    supplier_name VARCHAR(255),
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    purpose TEXT,
    photos JSON,
    notes TEXT,
    recorded_by INTEGER NOT NULL REFERENCES users(id),
    batch_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: pour_activities
-- ==============================================
CREATE TABLE IF NOT EXISTS pour_activities (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    pour_date DATE NOT NULL,
    structural_element VARCHAR(100) NOT NULL,
    location_details TEXT,
    concrete_grade VARCHAR(50),
    quantity_ordered FLOAT,
    quantity_poured FLOAT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    weather_conditions VARCHAR(255),
    temperature FLOAT,
    rmc_vendor_id INTEGER REFERENCES rmc_vendors(id),
    mix_design_id INTEGER REFERENCES mix_designs(id),
    supervised_by VARCHAR(255),
    notes TEXT,
    status VARCHAR(50) NOT NULL,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: batch_registers
-- ==============================================
CREATE TABLE IF NOT EXISTS batch_registers (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    pour_activity_id INTEGER REFERENCES pour_activities(id) ON DELETE SET NULL,
    batch_number VARCHAR(100) NOT NULL,
    batch_time TIMESTAMP NOT NULL,
    rmc_vendor_id INTEGER REFERENCES rmc_vendors(id),
    mix_design_id INTEGER REFERENCES mix_designs(id),
    quantity FLOAT NOT NULL,
    truck_number VARCHAR(50),
    challan_number VARCHAR(100),
    slump_value INTEGER,
    temperature FLOAT,
    building_name VARCHAR(255),
    floor_level VARCHAR(100),
    structural_element_type VARCHAR(100),
    remarks TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: cube_test_registers
-- ==============================================
CREATE TABLE IF NOT EXISTS cube_test_registers (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES batch_registers(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    test_age_days INTEGER NOT NULL,
    number_of_cubes INTEGER NOT NULL DEFAULT 3,
    testing_date DATE,
    test_results JSON,
    average_strength FLOAT,
    test_status VARCHAR(50) NOT NULL,
    tested_by VARCHAR(255),
    lab_name VARCHAR(255),
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: test_reminders
-- ==============================================
CREATE TABLE IF NOT EXISTS test_reminders (
    id SERIAL PRIMARY KEY,
    cube_test_id INTEGER NOT NULL REFERENCES cube_test_registers(id) ON DELETE CASCADE,
    reminder_date DATE NOT NULL,
    reminder_sent BOOLEAN NOT NULL DEFAULT false,
    reminder_sent_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: third_party_labs
-- ==============================================
CREATE TABLE IF NOT EXISTS third_party_labs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    lab_name VARCHAR(255) NOT NULL,
    lab_code VARCHAR(100),
    accreditation_number VARCHAR(100),
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: third_party_cube_tests
-- ==============================================
CREATE TABLE IF NOT EXISTS third_party_cube_tests (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES batch_registers(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    lab_id INTEGER NOT NULL REFERENCES third_party_labs(id),
    test_age_days INTEGER NOT NULL,
    sample_sent_date DATE,
    testing_date DATE,
    report_number VARCHAR(100),
    number_of_cubes INTEGER NOT NULL DEFAULT 3,
    test_results JSON,
    average_strength FLOAT,
    report_file_path VARCHAR(500),
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: material_test_registers
-- ==============================================
CREATE TABLE IF NOT EXISTS material_test_registers (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    material_category_id INTEGER NOT NULL REFERENCES material_categories(id),
    approved_brand_id INTEGER REFERENCES approved_brands(id),
    test_date DATE NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    sample_details TEXT,
    test_results JSON,
    pass_fail_status VARCHAR(50) NOT NULL,
    tested_by VARCHAR(255),
    lab_name VARCHAR(255),
    report_number VARCHAR(100),
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: training_records
-- ==============================================
CREATE TABLE IF NOT EXISTS training_records (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    employee_name VARCHAR(255) NOT NULL,
    employee_id VARCHAR(100),
    designation VARCHAR(100),
    training_topic VARCHAR(255) NOT NULL,
    training_date DATE NOT NULL,
    duration_hours FLOAT,
    trainer_name VARCHAR(255),
    training_type VARCHAR(100),
    attendance_status VARCHAR(50),
    assessment_score FLOAT,
    certification_issued BOOLEAN DEFAULT false,
    certificate_number VARCHAR(100),
    expiry_date DATE,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- Reset sequences to match current max IDs
-- ==============================================
SELECT setval('companies_id_seq', (SELECT COALESCE(MAX(id), 1) FROM companies), true);
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users), true);
SELECT setval('projects_id_seq', (SELECT COALESCE(MAX(id), 1) FROM projects), true);
SELECT setval('project_memberships_id_seq', (SELECT COALESCE(MAX(id), 1) FROM project_memberships), true);
SELECT setval('material_categories_id_seq', (SELECT COALESCE(MAX(id), 1) FROM material_categories), true);
SELECT setval('rmc_vendors_id_seq', (SELECT COALESCE(MAX(id), 1) FROM rmc_vendors), true);
SELECT setval('mix_designs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM mix_designs), true);
SELECT setval('approved_brands_id_seq', (SELECT COALESCE(MAX(id), 1) FROM approved_brands), true);
SELECT setval('project_settings_id_seq', (SELECT COALESCE(MAX(id), 1) FROM project_settings), true);
SELECT setval('material_vehicle_register_id_seq', (SELECT COALESCE(MAX(id), 1) FROM material_vehicle_register), true);
SELECT setval('pour_activities_id_seq', (SELECT COALESCE(MAX(id), 1) FROM pour_activities), true);
SELECT setval('batch_registers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM batch_registers), true);
SELECT setval('cube_test_registers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM cube_test_registers), true);
SELECT setval('test_reminders_id_seq', (SELECT COALESCE(MAX(id), 1) FROM test_reminders), true);
SELECT setval('third_party_labs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM third_party_labs), true);
SELECT setval('third_party_cube_tests_id_seq', (SELECT COALESCE(MAX(id), 1) FROM third_party_cube_tests), true);
SELECT setval('material_test_registers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM material_test_registers), true);
SELECT setval('training_records_id_seq', (SELECT COALESCE(MAX(id), 1) FROM training_records), true);

-- Re-enable triggers
SET session_replication_role = 'origin';

-- Verification queries
SELECT 'Migration Summary' as status;
SELECT 'companies' as table_name, COUNT(*) as row_count FROM companies
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'batch_registers', COUNT(*) FROM batch_registers
UNION ALL
SELECT 'material_vehicle_register', COUNT(*) FROM material_vehicle_register;

-- Success message
SELECT 'Migration base schema created successfully!' as message;
SELECT 'Next: Add your INSERT statements for users, projects, and other data from sqlite_dump.sql' as next_step;
