-- PostgreSQL Schema converted from SQLite
-- Generated: data.sqlite3
-- 

-- Drop existing tables (CASCADE removes dependent objects)
DROP TABLE IF EXISTS approved_brands CASCADE;
DROP TABLE IF EXISTS audit_checklists CASCADE;
DROP TABLE IF EXISTS batch_registers CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS concrete_nc_issues CASCADE;
DROP TABLE IF EXISTS concrete_nc_notifications CASCADE;
DROP TABLE IF EXISTS concrete_nc_score_reports CASCADE;
DROP TABLE IF EXISTS concrete_nc_tags CASCADE;
DROP TABLE IF EXISTS cube_test_registers CASCADE;
DROP TABLE IF EXISTS geofence_locations CASCADE;
DROP TABLE IF EXISTS incident_reports CASCADE;
DROP TABLE IF EXISTS induction_topics CASCADE;
DROP TABLE IF EXISTS location_verifications CASCADE;
DROP TABLE IF EXISTS material_categories CASCADE;
DROP TABLE IF EXISTS material_test_registers CASCADE;
DROP TABLE IF EXISTS material_vehicle_register CASCADE;
DROP TABLE IF EXISTS mix_designs CASCADE;
DROP TABLE IF EXISTS password_reset_tokens CASCADE;
DROP TABLE IF EXISTS permit_audit_logs CASCADE;
DROP TABLE IF EXISTS permit_checklists CASCADE;
DROP TABLE IF EXISTS permit_extensions CASCADE;
DROP TABLE IF EXISTS permit_signatures CASCADE;
DROP TABLE IF EXISTS permit_types CASCADE;
DROP TABLE IF EXISTS pour_activities CASCADE;
DROP TABLE IF EXISTS ppe_inventory CASCADE;
DROP TABLE IF EXISTS ppe_issuances CASCADE;
DROP TABLE IF EXISTS project_memberships CASCADE;
DROP TABLE IF EXISTS project_settings CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS rmc_vendors CASCADE;
DROP TABLE IF EXISTS safety_actions CASCADE;
DROP TABLE IF EXISTS safety_audits CASCADE;
DROP TABLE IF EXISTS safety_contractor_notifications CASCADE;
DROP TABLE IF EXISTS safety_form_submissions CASCADE;
DROP TABLE IF EXISTS safety_form_templates CASCADE;
DROP TABLE IF EXISTS safety_inductions CASCADE;
DROP TABLE IF EXISTS safety_modules CASCADE;
DROP TABLE IF EXISTS safety_nc_comments CASCADE;
DROP TABLE IF EXISTS safety_nc_score_reports CASCADE;
DROP TABLE IF EXISTS safety_non_conformances CASCADE;
DROP TABLE IF EXISTS safety_worker_attendance CASCADE;
DROP TABLE IF EXISTS safety_workers CASCADE;
DROP TABLE IF EXISTS tbt_attendances CASCADE;
DROP TABLE IF EXISTS tbt_sessions CASCADE;
DROP TABLE IF EXISTS tbt_topics CASCADE;
DROP TABLE IF EXISTS test_reminders CASCADE;
DROP TABLE IF EXISTS third_party_cube_tests CASCADE;
DROP TABLE IF EXISTS third_party_labs CASCADE;
DROP TABLE IF EXISTS training_attendances CASCADE;
DROP TABLE IF EXISTS training_records CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS work_permits CASCADE;


-- Table: companies
CREATE TABLE companies (
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
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	subscribed_modules TEXT DEFAULT '["safety", "concrete"]'
);

-- Table: users (must be created before projects)
CREATE TABLE users (
	id SERIAL PRIMARY KEY, 
	email VARCHAR(255) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	full_name VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	company_id INTEGER, 
	is_support_admin BOOLEAN NOT NULL, 
	is_company_admin BOOLEAN NOT NULL, 
	is_system_admin BOOLEAN NOT NULL, 
	designation VARCHAR(100), 
	profile_photo VARCHAR(500), 
	is_active BOOLEAN NOT NULL, 
	is_email_verified BOOLEAN NOT NULL, 
	is_phone_verified BOOLEAN NOT NULL, 
	failed_login_attempts INTEGER NOT NULL, 
	account_locked_until TIMESTAMP, 
	last_login TIMESTAMP, 
	last_activity TIMESTAMP, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	created_by INTEGER, 
	role VARCHAR(50) DEFAULT 'building_engineer' NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);

-- Table: projects (must be created before rmc_vendors)
CREATE TABLE projects (
	id SERIAL PRIMARY KEY, 
	company_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	project_code VARCHAR(50) UNIQUE, 
	description TEXT, 
	location VARCHAR(255), 
	client_name VARCHAR(255), 
	start_date DATE, 
	end_date DATE, 
	actual_end_date DATE, 
	status VARCHAR(20) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	created_by INTEGER, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);

-- Table: rmc_vendors (must be created before mix_designs)
CREATE TABLE rmc_vendors (
	id SERIAL PRIMARY KEY, 
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	vendor_name VARCHAR(255) NOT NULL, 
	contact_person_name VARCHAR(100), 
	contact_phone VARCHAR(20), 
	contact_email VARCHAR(255), 
	address TEXT, 
	license_number VARCHAR(100), 
	gstin VARCHAR(20), 
	is_active BOOLEAN NOT NULL, 
	is_approved BOOLEAN NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	created_by INTEGER, 
	approved_at TIMESTAMP, 
	approved_by INTEGER, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

-- Table: material_categories
CREATE TABLE material_categories (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	category_name VARCHAR(100) NOT NULL, 
	category_code VARCHAR(20) NOT NULL, 
	description TEXT, 
	applicable_standards TEXT, 
	requires_testing BOOLEAN NOT NULL, 
	test_frequency VARCHAR(100), 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id)
);


-- Table: third_party_labs
CREATE TABLE third_party_labs (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	lab_name VARCHAR(255) NOT NULL, 
	lab_code VARCHAR(50) NOT NULL, 
	contact_person_name VARCHAR(255) NOT NULL, 
	contact_phone VARCHAR(20) NOT NULL, 
	contact_email VARCHAR(255) NOT NULL, 
	address TEXT, 
	city VARCHAR(100), 
	state VARCHAR(100), 
	pincode VARCHAR(10), 
	nabl_accreditation_number VARCHAR(100), 
	nabl_accreditation_valid_till TIMESTAMP, 
	scope_of_accreditation TEXT, 
	is_approved BOOLEAN NOT NULL, 
	approved_by INTEGER, 
	approved_at TIMESTAMP, 
	is_active BOOLEAN NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: project_settings
CREATE TABLE project_settings (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	enable_material_vehicle_addon INTEGER NOT NULL, 
	vehicle_allowed_time_hours FLOAT NOT NULL, 
	send_time_warnings INTEGER NOT NULL, 
	enable_test_reminders INTEGER NOT NULL, 
	reminder_time VARCHAR(10) NOT NULL, 
	notify_project_admins INTEGER NOT NULL, 
	notify_quality_engineers INTEGER NOT NULL, 
	enable_whatsapp_notifications INTEGER NOT NULL, 
	enable_email_notifications INTEGER NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	updated_by INTEGER, 
	UNIQUE (project_id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: project_memberships
CREATE TABLE project_memberships (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	role VARCHAR(64) NOT NULL, 
	can_create_batch INTEGER NOT NULL, 
	can_edit_batch INTEGER NOT NULL, 
	can_delete_batch INTEGER NOT NULL, 
	can_approve_batch INTEGER NOT NULL, 
	can_create_test INTEGER NOT NULL, 
	can_edit_test INTEGER NOT NULL, 
	can_delete_test INTEGER NOT NULL, 
	can_approve_test INTEGER NOT NULL, 
	can_manage_team INTEGER NOT NULL, 
	can_generate_reports INTEGER NOT NULL, 
	can_export_data INTEGER NOT NULL, 
	can_manage_settings INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	joined_at TIMESTAMP NOT NULL, 
	added_by INTEGER, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(added_by) REFERENCES users (id)
);


-- Table: mix_designs
CREATE TABLE mix_designs (
	id SERIAL PRIMARY KEY,
	project_id INTEGER, 
	rmc_vendor_id INTEGER, 
	project_name VARCHAR(255) NOT NULL, 
	mix_design_id VARCHAR(255) NOT NULL, 
	specified_strength_psi INTEGER NOT NULL, 
	concrete_grade VARCHAR(50), 
	is_self_compacting BOOLEAN NOT NULL, 
	is_free_flow BOOLEAN NOT NULL, 
	slump_inches FLOAT, 
	air_content_percent FLOAT, 
	batch_volume FLOAT, 
	volume_unit VARCHAR(32), 
	materials TEXT, 
	notes TEXT, 
	document_name VARCHAR(512), 
	ocr_text TEXT, 
	image_name VARCHAR(512), 
	image_data BYTEA, 
	image_mimetype VARCHAR(100), 
	uploaded_by INTEGER, 
	is_approved BOOLEAN NOT NULL, 
	approved_by INTEGER, 
	approved_at TIMESTAMP, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(rmc_vendor_id) REFERENCES rmc_vendors (id), 
	FOREIGN KEY(uploaded_by) REFERENCES users (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: pour_activities
CREATE TABLE pour_activities (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	pour_id VARCHAR(100) NOT NULL, 
	pour_date TIMESTAMP NOT NULL, 
	building_name VARCHAR(255), 
	floor_level VARCHAR(50), 
	zone VARCHAR(100), 
	grid_reference VARCHAR(100), 
	structural_element_type VARCHAR(50), 
	element_id VARCHAR(100), 
	location_description TEXT, 
	concrete_type VARCHAR(20) NOT NULL, 
	design_grade VARCHAR(50), 
	total_quantity_planned FLOAT NOT NULL, 
	total_quantity_received FLOAT, 
	status VARCHAR(20) NOT NULL, 
	started_at TIMESTAMP, 
	completed_at TIMESTAMP, 
	created_by INTEGER NOT NULL, 
	completed_by INTEGER, 
	remarks TEXT, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(completed_by) REFERENCES users (id)
);


-- Table: approved_brands
CREATE TABLE approved_brands (
	id SERIAL PRIMARY KEY, 
	company_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	brand_name VARCHAR(255) NOT NULL, 
	manufacturer_name VARCHAR(255) NOT NULL, 
	grade_specification VARCHAR(100), 
	compliance_standards TEXT, 
	approved_by INTEGER NOT NULL, 
	approved_at TIMESTAMP NOT NULL, 
	approval_validity TIMESTAMP, 
	type_test_certificate_name VARCHAR(255), 
	type_test_certificate_data BYTEA, 
	type_test_certificate_mimetype VARCHAR(50), 
	is_active BOOLEAN NOT NULL, 
	remarks TEXT, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(category_id) REFERENCES material_categories (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);


-- Table: batch_registers
CREATE TABLE batch_registers (
	id SERIAL PRIMARY KEY, 
	project_id INTEGER NOT NULL, 
	mix_design_id INTEGER NOT NULL, 
	rmc_vendor_id INTEGER NOT NULL, 
	pour_activity_id INTEGER, 
	batch_number VARCHAR(100) NOT NULL, 
	delivery_date TIMESTAMP NOT NULL, 
	delivery_time VARCHAR(10), 
	quantity_ordered FLOAT NOT NULL, 
	quantity_received FLOAT, 
	batch_sheet_photo_name VARCHAR(512), 
	batch_sheet_photo_data BYTEA, 
	batch_sheet_photo_mimetype VARCHAR(100), 
	vehicle_number VARCHAR(50), 
	driver_name VARCHAR(255), 
	temperature_celsius FLOAT, 
	slump_tested FLOAT, 
	building_name VARCHAR(255), 
	floor_level VARCHAR(50), 
	zone VARCHAR(100), 
	grid_reference VARCHAR(100), 
	structural_element_type VARCHAR(50), 
	element_id VARCHAR(100), 
	pour_location_description TEXT, 
	latitude FLOAT, 
	longitude FLOAT, 
	entered_by INTEGER NOT NULL, 
	verification_status VARCHAR(20) NOT NULL, 
	verified_by INTEGER, 
	verified_at TIMESTAMP, 
	rejection_reason TEXT, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	remarks TEXT, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(mix_design_id) REFERENCES mix_designs (id), 
	FOREIGN KEY(rmc_vendor_id) REFERENCES rmc_vendors (id), 
	FOREIGN KEY(pour_activity_id) REFERENCES pour_activities (id), 
	FOREIGN KEY(entered_by) REFERENCES users (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: cube_test_registers
CREATE TABLE cube_test_registers (
	id SERIAL PRIMARY KEY, 
	batch_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	set_number INTEGER NOT NULL, 
	test_age_days INTEGER NOT NULL, 
	cube_identifier VARCHAR(10), 
	pour_activity_id INTEGER, 
	third_party_lab_id INTEGER, 
	sent_to_lab_date TIMESTAMP, 
	expected_result_date TIMESTAMP, 
	casting_date TIMESTAMP NOT NULL, 
	casting_time VARCHAR(10), 
	cast_by INTEGER NOT NULL, 
	structure_type VARCHAR(100), 
	structure_location TEXT, 
	concrete_grade VARCHAR(50), 
	concrete_type VARCHAR(20) NOT NULL, 
	concrete_source VARCHAR(20), 
	number_of_cubes INTEGER NOT NULL, 
	sample_identification VARCHAR(100), 
	curing_method VARCHAR(50), 
	curing_temperature FLOAT, 
	testing_date TIMESTAMP, 
	tested_by INTEGER, 
	testing_machine_id VARCHAR(100), 
	machine_calibration_date TIMESTAMP, 
	cube_1_weight_kg FLOAT, 
	cube_1_length_mm FLOAT, 
	cube_1_width_mm FLOAT, 
	cube_1_height_mm FLOAT, 
	cube_1_load_kn FLOAT, 
	cube_1_strength_mpa FLOAT, 
	cube_2_weight_kg FLOAT, 
	cube_2_length_mm FLOAT, 
	cube_2_width_mm FLOAT, 
	cube_2_height_mm FLOAT, 
	cube_2_load_kn FLOAT, 
	cube_2_strength_mpa FLOAT, 
	cube_3_weight_kg FLOAT, 
	cube_3_length_mm FLOAT, 
	cube_3_width_mm FLOAT, 
	cube_3_height_mm FLOAT, 
	cube_3_load_kn FLOAT, 
	cube_3_strength_mpa FLOAT, 
	average_strength_mpa FLOAT, 
	required_strength_mpa FLOAT, 
	strength_ratio_percent FLOAT, 
	pass_fail_status VARCHAR(20), 
	failure_mode_cube_1 VARCHAR(50), 
	failure_mode_cube_2 VARCHAR(50), 
	failure_mode_cube_3 VARCHAR(50), 
	verified_by INTEGER, 
	verified_at TIMESTAMP, 
	ncr_generated BOOLEAN NOT NULL, 
	ncr_number VARCHAR(100), 
	notification_sent BOOLEAN NOT NULL, 
	tester_signature_data BYTEA, 
	tester_signature_timestamp TIMESTAMP, 
	verifier_signature_data BYTEA, 
	verifier_signature_timestamp TIMESTAMP, 
	remarks TEXT, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(batch_id) REFERENCES batch_registers (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(pour_activity_id) REFERENCES pour_activities (id), 
	FOREIGN KEY(third_party_lab_id) REFERENCES third_party_labs (id), 
	FOREIGN KEY(cast_by) REFERENCES users (id), 
	FOREIGN KEY(tested_by) REFERENCES users (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: third_party_cube_tests
CREATE TABLE third_party_cube_tests (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	batch_id INTEGER NOT NULL, 
	lab_id INTEGER NOT NULL, 
	lab_test_report_number VARCHAR(100) NOT NULL, 
	test_age_days INTEGER NOT NULL, 
	sample_collection_date TIMESTAMP NOT NULL, 
	sample_received_at_lab_date TIMESTAMP NOT NULL, 
	testing_date TIMESTAMP NOT NULL, 
	number_of_cubes_tested INTEGER NOT NULL, 
	cube_1_strength_mpa FLOAT, 
	cube_2_strength_mpa FLOAT, 
	cube_3_strength_mpa FLOAT, 
	average_strength_mpa FLOAT NOT NULL, 
	required_strength_mpa FLOAT NOT NULL, 
	pass_fail_status VARCHAR(20) NOT NULL, 
	certificate_photo_name VARCHAR(255) NOT NULL, 
	certificate_photo_data BYTEA NOT NULL, 
	certificate_photo_mimetype VARCHAR(50) NOT NULL, 
	verified_by INTEGER, 
	verified_at TIMESTAMP, 
	verification_remarks TEXT, 
	ncr_generated BOOLEAN NOT NULL, 
	ncr_number VARCHAR(100), 
	notification_sent BOOLEAN NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	remarks TEXT, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(batch_id) REFERENCES batch_registers (id), 
	FOREIGN KEY(lab_id) REFERENCES third_party_labs (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id), 
	UNIQUE (ncr_number), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: material_vehicle_register
CREATE TABLE material_vehicle_register (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	vehicle_number VARCHAR(50) NOT NULL, 
	vehicle_type VARCHAR(100), 
	material_type VARCHAR(100) NOT NULL, 
	supplier_name VARCHAR(255), 
	challan_number VARCHAR(100), 
	driver_name VARCHAR(255), 
	driver_phone VARCHAR(20), 
	driver_license VARCHAR(50), 
	entry_time TIMESTAMP NOT NULL, 
	exit_time TIMESTAMP, 
	duration_hours FLOAT, 
	allowed_time_hours FLOAT, 
	exceeded_time_limit BOOLEAN NOT NULL, 
	time_warning_sent BOOLEAN NOT NULL, 
	time_warning_sent_at TIMESTAMP, 
	photos TEXT, 
	status VARCHAR(50) NOT NULL, 
	purpose VARCHAR(255), 
	remarks TEXT, 
	linked_batch_id INTEGER, 
	is_linked_to_batch BOOLEAN NOT NULL, 
	created_by INTEGER NOT NULL, 
	updated_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(linked_batch_id) REFERENCES batch_registers (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: material_test_registers
CREATE TABLE material_test_registers (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	brand_id INTEGER, 
	lab_id INTEGER NOT NULL, 
	material_description TEXT NOT NULL, 
	grade_specification VARCHAR(100) NOT NULL, 
	quantity FLOAT NOT NULL, 
	quantity_unit VARCHAR(20) NOT NULL, 
	supplier_name VARCHAR(255) NOT NULL, 
	manufacturer_name VARCHAR(255), 
	batch_lot_number VARCHAR(100) NOT NULL, 
	invoice_number VARCHAR(100) NOT NULL, 
	invoice_date TIMESTAMP NOT NULL, 
	location_description TEXT NOT NULL, 
	lab_test_report_number VARCHAR(100) NOT NULL, 
	sample_collection_date TIMESTAMP NOT NULL, 
	testing_date TIMESTAMP NOT NULL, 
	test_parameters TEXT NOT NULL, 
	test_results TEXT NOT NULL, 
	pass_fail_status VARCHAR(20) NOT NULL, 
	certificate_photo_name VARCHAR(255) NOT NULL, 
	certificate_photo_data BYTEA NOT NULL, 
	certificate_photo_mimetype VARCHAR(50) NOT NULL, 
	entered_by INTEGER NOT NULL, 
	verified_by INTEGER, 
	verified_at TIMESTAMP, 
	verification_status VARCHAR(20) NOT NULL, 
	verification_remarks TEXT, 
	ncr_generated BOOLEAN NOT NULL, 
	ncr_number VARCHAR(100), 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(category_id) REFERENCES material_categories (id), 
	FOREIGN KEY(brand_id) REFERENCES approved_brands (id), 
	FOREIGN KEY(lab_id) REFERENCES third_party_labs (id), 
	FOREIGN KEY(entered_by) REFERENCES users (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id), 
	UNIQUE (ncr_number), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: test_reminders
CREATE TABLE test_reminders (
	id SERIAL PRIMARY KEY,
	cube_test_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	reminder_date TIMESTAMP NOT NULL, 
	test_age_days INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	notification_sent_at TIMESTAMP, 
	notified_user_ids TEXT, 
	test_completed INTEGER NOT NULL, 
	completed_at TIMESTAMP, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(cube_test_id) REFERENCES cube_test_registers (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);


-- Table: safety_modules
CREATE TABLE safety_modules (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER, 
	module_type VARCHAR(50) NOT NULL, 
	module_name VARCHAR(255) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	is_active BOOLEAN NOT NULL, 
	display_order INTEGER NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	created_by INTEGER NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);


-- Table: safety_workers
CREATE TABLE safety_workers (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER, 
	worker_code VARCHAR(50) NOT NULL, 
	full_name VARCHAR(255) NOT NULL, 
	phone VARCHAR(20), 
	email VARCHAR(255), 
	photo VARCHAR(500), 
	contractor VARCHAR(255), 
	skill_category VARCHAR(100), 
	designation VARCHAR(100), 
	training_records JSON, 
	certifications JSON, 
	qr_code VARCHAR(255), 
	nfc_tag VARCHAR(255), 
	is_active BOOLEAN NOT NULL, 
	joined_date TIMESTAMP, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	UNIQUE (worker_code)
);


-- Table: permit_types
CREATE TABLE permit_types (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	permit_type_name VARCHAR(100) NOT NULL, 
	permit_code VARCHAR(20) NOT NULL, 
	description TEXT NOT NULL, 
	risk_level VARCHAR(20) NOT NULL, 
	required_ppe JSON, 
	safety_precautions JSON, 
	required_equipment JSON, 
	requires_site_engineer BOOLEAN NOT NULL, 
	requires_safety_officer BOOLEAN NOT NULL, 
	requires_area_owner BOOLEAN NOT NULL, 
	max_validity_hours INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	created_by INTEGER NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);


-- Table: tbt_sessions
CREATE TABLE tbt_sessions (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	conductor_id INTEGER NOT NULL, 
	conductor_name VARCHAR(255) NOT NULL, 
	conductor_role VARCHAR(100), 
	session_date TIMESTAMP NOT NULL, 
	topic VARCHAR(255) NOT NULL, 
	topic_category VARCHAR(100), 
	location VARCHAR(255) NOT NULL, 
	activity VARCHAR(100) NOT NULL, 
	duration_minutes INTEGER NOT NULL, 
	key_points TEXT, 
	hazards_discussed TEXT, 
	ppe_required TEXT, 
	emergency_contacts TEXT, 
	photo_filename VARCHAR(255), 
	photo_url VARCHAR(500), 
	weather_conditions VARCHAR(255), 
	special_notes TEXT, 
	status VARCHAR(50) NOT NULL, 
	is_completed BOOLEAN NOT NULL, 
	completed_at TIMESTAMP, 
	qr_code_data VARCHAR(500), 
	qr_code_expires_at TIMESTAMP, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(conductor_id) REFERENCES users (id)
);


-- Table: tbt_topics
CREATE TABLE tbt_topics (
	id SERIAL PRIMARY KEY,
	company_id INTEGER, 
	topic_name VARCHAR(255) NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	description TEXT, 
	key_points_template TEXT, 
	hazards_template TEXT, 
	ppe_template TEXT, 
	is_active BOOLEAN NOT NULL, 
	usage_count INTEGER NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id)
);


-- Table: induction_topics
CREATE TABLE induction_topics (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	topic_name VARCHAR(200) NOT NULL, 
	topic_description TEXT, 
	topic_category VARCHAR(100), 
	key_points JSON, 
	dos_and_donts JSON, 
	reference_standards JSON, 
	video_url VARCHAR(500), 
	images JSON, 
	documents JSON, 
	quiz_questions JSON, 
	is_mandatory BOOLEAN, 
	is_active BOOLEAN, 
	display_order INTEGER, 
	created_at TIMESTAMP, 
	updated_at TIMESTAMP, 
	created_by INTEGER, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);


-- Table: incident_reports
CREATE TABLE incident_reports (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	reported_by INTEGER NOT NULL, 
	incident_number VARCHAR(50) NOT NULL, 
	incident_type VARCHAR(17) NOT NULL, 
	incident_date TIMESTAMP NOT NULL, 
	incident_time VARCHAR(10), 
	location VARCHAR(500) NOT NULL, 
	location_latitude NUMERIC(10, 8), 
	location_longitude NUMERIC(11, 8), 
	severity INTEGER NOT NULL, 
	incident_description TEXT NOT NULL, 
	immediate_action_taken TEXT, 
	injured_persons JSON, 
	witnesses JSON, 
	investigation_required BOOLEAN, 
	investigation_team JSON, 
	investigation_start_date TIMESTAMP, 
	investigation_end_date TIMESTAMP, 
	investigation_lead INTEGER, 
	immediate_causes JSON, 
	underlying_causes JSON, 
	root_cause_analysis TEXT, 
	contributing_factors JSON, 
	corrective_actions JSON, 
	preventive_actions JSON, 
	lost_time_hours NUMERIC(10, 2), 
	lost_time_days INTEGER, 
	medical_cost NUMERIC(12, 2), 
	property_damage_cost NUMERIC(12, 2), 
	total_cost NUMERIC(12, 2), 
	property_damage_description TEXT, 
	damaged_equipment JSON, 
	reportable_to_authority BOOLEAN, 
	authority_name VARCHAR(200), 
	authority_notified BOOLEAN, 
	authority_notification_date TIMESTAMP, 
	authority_reference_number VARCHAR(100), 
	authority_report_pdf VARCHAR(500), 
	photos JSON, 
	documents JSON, 
	lessons_learned TEXT, 
	recommendations TEXT, 
	status VARCHAR(19), 
	closed_by INTEGER, 
	closed_date TIMESTAMP, 
	closure_remarks TEXT, 
	created_at TIMESTAMP, 
	updated_at TIMESTAMP, 
	created_by INTEGER, 
	updated_by INTEGER, 
	is_deleted BOOLEAN, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(reported_by) REFERENCES users (id), 
	UNIQUE (incident_number), 
	FOREIGN KEY(investigation_lead) REFERENCES users (id), 
	FOREIGN KEY(closed_by) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: audit_checklists
CREATE TABLE audit_checklists (
	id SERIAL PRIMARY KEY, 
	company_id INTEGER NOT NULL, 
	checklist_name VARCHAR(200) NOT NULL, 
	checklist_code VARCHAR(50), 
	audit_type VARCHAR(22) NOT NULL, 
	checklist_description TEXT, 
	version VARCHAR(20), 
	effective_date TIMESTAMP, 
	revision_date TIMESTAMP, 
	categories JSON NOT NULL, 
	items JSON NOT NULL, 
	total_items INTEGER, 
	total_categories INTEGER, 
	iso_45001_clauses JSON, 
	osha_standards JSON, 
	local_regulations JSON, 
	is_active BOOLEAN, 
	is_default BOOLEAN, 
	is_deleted BOOLEAN, 
	created_by INTEGER, 
	created_at TIMESTAMP, 
	updated_by INTEGER, 
	updated_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: ppe_inventory
CREATE TABLE ppe_inventory (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	ppe_type VARCHAR(17) NOT NULL, 
	ppe_description VARCHAR(200) NOT NULL, 
	ppe_brand VARCHAR(100), 
	ppe_model VARCHAR(100), 
	ppe_size VARCHAR(20), 
	total_stock INTEGER, 
	issued_quantity INTEGER, 
	available_quantity INTEGER, 
	minimum_stock_level INTEGER, 
	last_purchase_date DATE, 
	last_purchase_quantity INTEGER, 
	last_purchase_cost NUMERIC(10, 2), 
	supplier_name VARCHAR(200), 
	supplier_contact VARCHAR(100), 
	storage_location VARCHAR(200), 
	storage_bin VARCHAR(50), 
	isi_marked BOOLEAN, 
	ce_marked BOOLEAN, 
	ansi_compliant BOOLEAN, 
	test_certificate_url VARCHAR(500), 
	typical_lifespan_days INTEGER, 
	low_stock_alert BOOLEAN, 
	expiry_alert BOOLEAN, 
	is_deleted BOOLEAN, 
	created_by INTEGER, 
	created_at TIMESTAMP, 
	updated_by INTEGER, 
	updated_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: geofence_locations
CREATE TABLE geofence_locations (
	id SERIAL PRIMARY KEY, 
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	location_name VARCHAR(200) NOT NULL, 
	location_description TEXT, 
	center_latitude NUMERIC(10, 7) NOT NULL, 
	center_longitude NUMERIC(10, 7) NOT NULL, 
	radius_meters INTEGER NOT NULL, 
	address TEXT, 
	city VARCHAR(100), 
	state VARCHAR(100), 
	pincode VARCHAR(10), 
	is_active BOOLEAN, 
	strict_mode BOOLEAN, 
	tolerance_meters INTEGER, 
	is_deleted BOOLEAN, 
	created_by INTEGER, 
	created_at TIMESTAMP, 
	updated_by INTEGER, 
	updated_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	UNIQUE (project_id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: location_verifications
CREATE TABLE location_verifications (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	submitted_latitude NUMERIC(10, 7) NOT NULL, 
	submitted_longitude NUMERIC(10, 7) NOT NULL, 
	submitted_accuracy NUMERIC(10, 2), 
	is_verified BOOLEAN NOT NULL, 
	distance_from_center NUMERIC(10, 2), 
	allowed_radius INTEGER, 
	action VARCHAR(100), 
	endpoint VARCHAR(200), 
	request_id VARCHAR(100), 
	ip_address VARCHAR(50), 
	user_agent VARCHAR(500), 
	device_info VARCHAR(200), 
	verified_at TIMESTAMP NOT NULL, 
	created_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


-- Table: safety_form_templates
CREATE TABLE safety_form_templates (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER, 
	module_id INTEGER NOT NULL, 
	template_name VARCHAR(255) NOT NULL, 
	template_code VARCHAR(50), 
	description TEXT, 
	category VARCHAR(100), 
	form_fields JSON NOT NULL, 
	has_scoring BOOLEAN NOT NULL, 
	scoring_config JSON, 
	requires_approval BOOLEAN NOT NULL, 
	approval_levels JSON, 
	auto_assign BOOLEAN NOT NULL, 
	assignment_rules JSON, 
	is_recurring BOOLEAN NOT NULL, 
	recurrence_config JSON, 
	version INTEGER NOT NULL, 
	is_latest BOOLEAN NOT NULL, 
	parent_template_id INTEGER, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	created_by INTEGER NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(module_id) REFERENCES safety_modules (id), 
	FOREIGN KEY(parent_template_id) REFERENCES safety_form_templates (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);


-- Table: safety_worker_attendance
CREATE TABLE safety_worker_attendance (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	worker_id INTEGER NOT NULL, 
	date TIMESTAMP NOT NULL, 
	check_in_time TIMESTAMP, 
	check_out_time TIMESTAMP, 
	check_in_method VARCHAR(50), 
	check_in_location JSON, 
	ppe_verified BOOLEAN NOT NULL, 
	ppe_items_checked JSON, 
	ppe_photo VARCHAR(500), 
	induction_completed BOOLEAN NOT NULL, 
	induction_date TIMESTAMP, 
	created_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(worker_id) REFERENCES safety_workers (id)
);


-- Table: work_permits
CREATE TABLE work_permits (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	permit_type_id INTEGER NOT NULL, 
	permit_number VARCHAR(50) NOT NULL, 
	work_description TEXT NOT NULL, 
	work_location VARCHAR(255) NOT NULL, 
	geo_location JSON, 
	contractor_company VARCHAR(255) NOT NULL, 
	contractor_supervisor INTEGER NOT NULL, 
	contractor_phone VARCHAR(20), 
	number_of_workers INTEGER NOT NULL, 
	work_date DATE NOT NULL, 
	start_time TIME NOT NULL, 
	end_time TIME NOT NULL, 
	estimated_duration_hours FLOAT NOT NULL, 
	valid_from TIMESTAMP NOT NULL, 
	valid_until TIMESTAMP NOT NULL, 
	is_expired BOOLEAN NOT NULL, 
	identified_hazards JSON NOT NULL, 
	safety_measures JSON NOT NULL, 
	ppe_required JSON NOT NULL, 
	equipment_checklist JSON, 
	requires_isolation BOOLEAN NOT NULL, 
	isolation_details JSON, 
	emergency_contact_name VARCHAR(100) NOT NULL, 
	emergency_contact_phone VARCHAR(20) NOT NULL, 
	nearest_hospital VARCHAR(255), 
	first_aid_location VARCHAR(255), 
	status VARCHAR(50) NOT NULL, 
	workflow_stage VARCHAR(50) NOT NULL, 
	attachments JSON, 
	photos JSON, 
	created_at TIMESTAMP NOT NULL, 
	submitted_at TIMESTAMP, 
	approved_at TIMESTAMP, 
	work_started_at TIMESTAMP, 
	work_completed_at TIMESTAMP, 
	closed_at TIMESTAMP, 
	is_suspended BOOLEAN NOT NULL, 
	suspension_reason TEXT, 
	suspended_at TIMESTAMP, 
	suspended_by INTEGER, 
	is_cancelled BOOLEAN NOT NULL, 
	cancellation_reason TEXT, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(permit_type_id) REFERENCES permit_types (id), 
	UNIQUE (permit_number), 
	FOREIGN KEY(contractor_supervisor) REFERENCES users (id), 
	FOREIGN KEY(suspended_by) REFERENCES users (id)
);


-- Don't forget to add indexes for foreign keys and frequently queried columns
-- Example:
-- CREATE INDEX idx_users_company_id ON users(company_id);
-- CREATE INDEX idx_projects_company_id ON projects(company_id);

-- Table: tbt_attendances
CREATE TABLE tbt_attendances (
	id SERIAL PRIMARY KEY,
	session_id INTEGER NOT NULL, 
	worker_id INTEGER, 
	worker_name VARCHAR(255) NOT NULL, 
	worker_code VARCHAR(50), 
	worker_company VARCHAR(255), 
	worker_trade VARCHAR(100), 
	check_in_method VARCHAR(50) NOT NULL, 
	check_in_time TIMESTAMP NOT NULL, 
	qr_code_scanned VARCHAR(500), 
	device_info VARCHAR(255), 
	has_signed BOOLEAN NOT NULL, 
	signature_timestamp TIMESTAMP, 
	remarks TEXT, 
	created_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(session_id) REFERENCES tbt_sessions (id), 
	FOREIGN KEY(worker_id) REFERENCES safety_workers (id)
);


-- Table: training_records
CREATE TABLE training_records (
	id SERIAL PRIMARY KEY,
	project_id INTEGER NOT NULL, 
	trainer_id INTEGER NOT NULL, 
	training_date TIMESTAMP NOT NULL, 
	training_topic VARCHAR(255) NOT NULL, 
	trainee_names_json TEXT NOT NULL, 
	building VARCHAR(100) NOT NULL, 
	activity VARCHAR(100) NOT NULL, 
	duration_minutes INTEGER, 
	photo_filename VARCHAR(255) NOT NULL, 
	photo_data BYTEA NOT NULL, 
	photo_mimetype VARCHAR(50) NOT NULL, 
	remarks TEXT, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(trainer_id) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: training_attendances
CREATE TABLE training_attendances (
	id SERIAL PRIMARY KEY,
	training_record_id INTEGER NOT NULL, 
	worker_id INTEGER, 
	worker_name VARCHAR(255) NOT NULL, 
	worker_code VARCHAR(50) NOT NULL, 
	worker_company VARCHAR(255), 
	worker_trade VARCHAR(100), 
	check_in_method VARCHAR(20) NOT NULL, 
	check_in_time TIMESTAMP NOT NULL, 
	qr_code_scanned VARCHAR(100), 
	device_info VARCHAR(255), 
	assessment_score FLOAT, 
	passed_assessment BOOLEAN, 
	certificate_issued BOOLEAN NOT NULL, 
	certificate_number VARCHAR(100), 
	has_signed BOOLEAN NOT NULL, 
	signature_timestamp TIMESTAMP, 
	created_at TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(training_record_id) REFERENCES training_records (id), 
	FOREIGN KEY(worker_id) REFERENCES safety_workers (id)
);


-- Table: safety_inductions
CREATE TABLE safety_inductions (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	worker_id INTEGER NOT NULL, 
	conducted_by INTEGER NOT NULL, 
	induction_number VARCHAR(50) NOT NULL, 
	induction_date TIMESTAMP NOT NULL, 
	induction_topics JSON NOT NULL, 
	video_watched BOOLEAN, 
	video_url VARCHAR(500), 
	video_duration_seconds INTEGER, 
	video_watched_seconds INTEGER, 
	video_completed_at TIMESTAMP, 
	quiz_taken BOOLEAN, 
	quiz_questions JSON, 
	quiz_answers JSON, 
	quiz_score INTEGER, 
	quiz_passing_score INTEGER, 
	quiz_passed BOOLEAN, 
	quiz_attempts INTEGER, 
	quiz_completed_at TIMESTAMP, 
	aadhar_number VARCHAR(12), 
	aadhar_verified BOOLEAN, 
	aadhar_verified_by INTEGER, 
	aadhar_verified_at TIMESTAMP, 
	aadhar_verification_notes TEXT, 
	terms_version VARCHAR(20), 
	terms_accepted BOOLEAN, 
	terms_accepted_at TIMESTAMP, 
	terms_pdf_path VARCHAR(500), 
	worker_signature TEXT, 
	worker_signature_ip VARCHAR(50), 
	worker_signed_at TIMESTAMP, 
	safety_officer_signature TEXT, 
	safety_officer_signed_at TIMESTAMP, 
	witness_name VARCHAR(200), 
	witness_signature TEXT, 
	witness_signed_at TIMESTAMP, 
	certificate_issued BOOLEAN, 
	certificate_number VARCHAR(100), 
	certificate_pdf_path VARCHAR(500), 
	certificate_issued_at TIMESTAMP, 
	valid_from DATE NOT NULL, 
	valid_until DATE NOT NULL, 
	is_expired BOOLEAN, 
	is_reinduction BOOLEAN, 
	previous_induction_id INTEGER, 
	reinduction_reason VARCHAR(500), 
	status VARCHAR(50), 
	remarks TEXT, 
	internal_notes TEXT, 
	created_at TIMESTAMP, 
	updated_at TIMESTAMP, 
	created_by INTEGER, 
	updated_by INTEGER, 
	is_deleted BOOLEAN, 
	deleted_at TIMESTAMP, 
	deleted_by INTEGER, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(worker_id) REFERENCES safety_workers (id), 
	FOREIGN KEY(conducted_by) REFERENCES users (id), 
	UNIQUE (induction_number), 
	FOREIGN KEY(aadhar_verified_by) REFERENCES users (id), 
	FOREIGN KEY(previous_induction_id) REFERENCES safety_inductions (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id), 
	FOREIGN KEY(deleted_by) REFERENCES users (id)
);


-- Table: safety_audits
CREATE TABLE safety_audits (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	audit_number VARCHAR(50) NOT NULL, 
	audit_type VARCHAR(22) NOT NULL, 
	audit_title VARCHAR(200) NOT NULL, 
	audit_description TEXT, 
	scheduled_date TIMESTAMP NOT NULL, 
	scheduled_by_id INTEGER, 
	lead_auditor_id INTEGER NOT NULL, 
	audit_team JSON, 
	actual_start_time TIMESTAMP, 
	actual_end_time TIMESTAMP, 
	audit_duration_minutes INTEGER, 
	audit_location VARCHAR(200), 
	audit_scope TEXT, 
	areas_covered JSON, 
	checklist_id INTEGER, 
	checklist_items JSON, 
	total_items INTEGER, 
	compliant_items INTEGER, 
	non_compliant_items INTEGER, 
	not_applicable_items INTEGER, 
	compliance_percentage NUMERIC(5, 2), 
	audit_grade VARCHAR(12), 
	total_findings INTEGER, 
	observations INTEGER, 
	minor_ncs INTEGER, 
	major_ncs INTEGER, 
	critical_findings INTEGER, 
	findings_details JSON, 
	photos JSON, 
	documents JSON, 
	positive_observations TEXT, 
	areas_of_concern TEXT, 
	immediate_actions_required TEXT, 
	long_term_improvements TEXT, 
	training_recommendations JSON, 
	audit_report_pdf VARCHAR(500), 
	report_generated_at TIMESTAMP, 
	status VARCHAR(16), 
	actions_assigned INTEGER, 
	actions_completed INTEGER, 
	actions_overdue INTEGER, 
	closed_by_id INTEGER, 
	closed_date TIMESTAMP, 
	closure_remarks TEXT, 
	iso_clauses_checked JSON, 
	osha_standards_checked JSON, 
	is_deleted BOOLEAN, 
	created_by INTEGER, 
	created_at TIMESTAMP, 
	updated_by INTEGER, 
	updated_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	UNIQUE (audit_number), 
	FOREIGN KEY(scheduled_by_id) REFERENCES users (id), 
	FOREIGN KEY(lead_auditor_id) REFERENCES users (id), 
	FOREIGN KEY(checklist_id) REFERENCES audit_checklists (id), 
	FOREIGN KEY(closed_by_id) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: ppe_issuances
CREATE TABLE ppe_issuances (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	issuance_number VARCHAR(50) NOT NULL, 
	worker_id INTEGER NOT NULL, 
	ppe_type VARCHAR(17) NOT NULL, 
	ppe_description VARCHAR(200), 
	ppe_brand VARCHAR(100), 
	ppe_model VARCHAR(100), 
	ppe_size VARCHAR(20), 
	serial_number VARCHAR(100), 
	barcode VARCHAR(100), 
	issue_date DATE NOT NULL, 
	issued_by_id INTEGER NOT NULL, 
	issue_remarks TEXT, 
	expected_return_date DATE, 
	expiry_date DATE, 
	return_date DATE, 
	returned_to_id INTEGER, 
	return_condition VARCHAR(7), 
	return_remarks TEXT, 
	damage_reported_date DATE, 
	damage_description TEXT, 
	damage_photos JSON, 
	replacement_required BOOLEAN, 
	replacement_issuance_id INTEGER, 
	loss_reported_date DATE, 
	loss_remarks TEXT, 
	penalty_amount NUMERIC(10, 2), 
	status VARCHAR(8), 
	is_expired BOOLEAN, 
	isi_marked BOOLEAN, 
	ce_marked BOOLEAN, 
	ansi_compliant BOOLEAN, 
	test_certificate_url VARCHAR(500), 
	unit_cost NUMERIC(10, 2), 
	is_deleted BOOLEAN, 
	created_by INTEGER, 
	created_at TIMESTAMP, 
	updated_by INTEGER, 
	updated_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	UNIQUE (issuance_number), 
	FOREIGN KEY(worker_id) REFERENCES safety_workers (id), 
	FOREIGN KEY(issued_by_id) REFERENCES users (id), 
	FOREIGN KEY(returned_to_id) REFERENCES users (id), 
	FOREIGN KEY(replacement_issuance_id) REFERENCES ppe_issuances (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);


-- Table: safety_form_submissions
CREATE TABLE safety_form_submissions (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	template_id INTEGER NOT NULL, 
	submission_number VARCHAR(50) NOT NULL, 
	form_data JSON NOT NULL, 
	location VARCHAR(255), 
	geo_location JSON, 
	photos JSON, 
	videos JSON, 
	documents JSON, 
	score FLOAT, 
	max_score FLOAT, 
	score_percentage FLOAT, 
	status VARCHAR(50) NOT NULL, 
	priority VARCHAR(20), 
	approval_status VARCHAR(50), 
	approvals JSON, 
	due_date TIMESTAMP, 
	closed_date TIMESTAMP, 
	is_overdue BOOLEAN NOT NULL, 
	submitted_at TIMESTAMP NOT NULL, 
	submitted_by INTEGER NOT NULL, 
	updated_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(template_id) REFERENCES safety_form_templates (id), 
	UNIQUE (submission_number), 
	FOREIGN KEY(submitted_by) REFERENCES users (id)
);


-- Table: permit_signatures
CREATE TABLE permit_signatures (
	id SERIAL PRIMARY KEY,
	permit_id INTEGER NOT NULL, 
	signer_role VARCHAR(50) NOT NULL, 
	signer_id INTEGER NOT NULL, 
	signer_name VARCHAR(100) NOT NULL, 
	signer_designation VARCHAR(100) NOT NULL, 
	signature_type VARCHAR(50) NOT NULL, 
	signature_data TEXT, 
	action VARCHAR(50) NOT NULL, 
	comments TEXT, 
	ip_address VARCHAR(50), 
	device_info VARCHAR(255), 
	signed_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(permit_id) REFERENCES work_permits (id), 
	FOREIGN KEY(signer_id) REFERENCES users (id)
);


-- Table: permit_extensions
CREATE TABLE permit_extensions (
	id SERIAL PRIMARY KEY,
	permit_id INTEGER NOT NULL, 
	requested_by INTEGER NOT NULL, 
	extension_reason TEXT NOT NULL, 
	extended_until TIMESTAMP NOT NULL, 
	additional_hours FLOAT NOT NULL, 
	approval_status VARCHAR(50) NOT NULL, 
	approved_by INTEGER, 
	approval_comments TEXT, 
	requested_at TIMESTAMP NOT NULL, 
	approved_at TIMESTAMP, 
	FOREIGN KEY(permit_id) REFERENCES work_permits (id), 
	FOREIGN KEY(requested_by) REFERENCES users (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);


-- Table: permit_checklists
CREATE TABLE permit_checklists (
	id SERIAL PRIMARY KEY,
	permit_id INTEGER NOT NULL, 
	item_description TEXT NOT NULL, 
	is_mandatory BOOLEAN NOT NULL, 
	is_verified BOOLEAN NOT NULL, 
	verified_by INTEGER, 
	verified_at TIMESTAMP, 
	verification_notes TEXT, 
	verification_photo VARCHAR(500), 
	FOREIGN KEY(permit_id) REFERENCES work_permits (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id)
);


-- Table: permit_audit_logs
CREATE TABLE permit_audit_logs (
	id SERIAL PRIMARY KEY,
	permit_id INTEGER NOT NULL, 
	action_type VARCHAR(50) NOT NULL, 
	action_description TEXT NOT NULL, 
	performed_by INTEGER NOT NULL, 
	previous_state JSON, 
	new_state JSON, 
	action_timestamp TIMESTAMP NOT NULL, 
	FOREIGN KEY(permit_id) REFERENCES work_permits (id), 
	FOREIGN KEY(performed_by) REFERENCES users (id)
);


-- Table: safety_actions
CREATE TABLE safety_actions (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	submission_id INTEGER NOT NULL, 
	action_number VARCHAR(50) NOT NULL, 
	action_description TEXT NOT NULL, 
	assigned_to INTEGER NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	due_date TIMESTAMP NOT NULL, 
	status VARCHAR(50) NOT NULL, 
	completion_notes TEXT, 
	completion_photos JSON, 
	is_overdue BOOLEAN NOT NULL, 
	escalation_level INTEGER NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	created_by INTEGER NOT NULL, 
	completed_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(submission_id) REFERENCES safety_form_submissions (id), 
	UNIQUE (action_number), 
	FOREIGN KEY(assigned_to) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);


-- Table: safety_non_conformances
CREATE TABLE safety_non_conformances (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	submission_id INTEGER, 
	nc_number VARCHAR(50) NOT NULL, 
	nc_title VARCHAR(255) NOT NULL, 
	nc_description TEXT NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	category VARCHAR(100), 
	assigned_to_contractor VARCHAR(255), 
	assigned_to_user INTEGER, 
	location VARCHAR(255), 
	geo_location JSON, 
	evidence_photos JSON, 
	evidence_videos JSON, 
	root_cause TEXT, 
	immediate_cause TEXT, 
	proposed_action TEXT, 
	approved_action TEXT, 
	action_taken TEXT, 
	action_photos JSON, 
	action_completion_date TIMESTAMP, 
	verification_status VARCHAR(50) NOT NULL, 
	verification_notes TEXT, 
	verified_by INTEGER, 
	verified_at TIMESTAMP, 
	is_closed BOOLEAN NOT NULL, 
	closed_by INTEGER, 
	closed_at TIMESTAMP, 
	closure_remarks TEXT, 
	due_date TIMESTAMP NOT NULL, 
	is_overdue BOOLEAN NOT NULL, 
	escalation_level INTEGER NOT NULL, 
	notifications_sent JSON, 
	raised_at TIMESTAMP NOT NULL, 
	raised_by INTEGER NOT NULL, 
	updated_at TIMESTAMP NOT NULL, severity_score REAL DEFAULT 0.0, score_month VARCHAR(7), score_year INTEGER, score_week VARCHAR(10), actual_resolution_days INTEGER, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(submission_id) REFERENCES safety_form_submissions (id), 
	UNIQUE (nc_number), 
	FOREIGN KEY(assigned_to_user) REFERENCES users (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id), 
	FOREIGN KEY(closed_by) REFERENCES users (id), 
	FOREIGN KEY(raised_by) REFERENCES users (id)
);


-- Table: safety_nc_comments
CREATE TABLE safety_nc_comments (
	id SERIAL PRIMARY KEY,
	nc_id INTEGER NOT NULL, 
	comment_text TEXT NOT NULL, 
	attachments JSON, 
	created_by INTEGER NOT NULL, 
	created_at TIMESTAMP NOT NULL, 
	FOREIGN KEY(nc_id) REFERENCES safety_non_conformances (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);


-- Table: safety_contractor_notifications
CREATE TABLE safety_contractor_notifications (
	id SERIAL PRIMARY KEY,
	company_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	notification_type VARCHAR(50) NOT NULL, 
	notification_channel VARCHAR(20) NOT NULL, 
	recipient_contractor VARCHAR(255), 
	recipient_user INTEGER, 
	recipient_phone VARCHAR(20), 
	recipient_email VARCHAR(255), 
	nc_id INTEGER, 
	action_id INTEGER, 
	subject VARCHAR(255) NOT NULL, 
	message TEXT NOT NULL, 
	sent_at TIMESTAMP NOT NULL, 
	delivery_status VARCHAR(20) NOT NULL, 
	read_at TIMESTAMP, 
	FOREIGN KEY(company_id) REFERENCES companies (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(recipient_user) REFERENCES users (id), 
	FOREIGN KEY(nc_id) REFERENCES safety_non_conformances (id), 
	FOREIGN KEY(action_id) REFERENCES safety_actions (id)
);


-- Table: concrete_nc_tags
CREATE TABLE concrete_nc_tags (
                id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                level INTEGER NOT NULL,
                parent_tag_id INTEGER,
                color_code VARCHAR(7) DEFAULT '#666666',
                description TEXT,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_tag_id) REFERENCES concrete_nc_tags(id) ON DELETE SET NULL,
                CHECK (level >= 1 AND level <= 4)
            );


-- Table: concrete_nc_issues
CREATE TABLE concrete_nc_issues (
                id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                nc_number VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                photo_urls JSON,
                location_text VARCHAR(200),
                location_latitude REAL,
                location_longitude REAL,
                tag_ids JSON,
                severity VARCHAR(20) NOT NULL,
                severity_score REAL DEFAULT 0.0,
                raised_by_user_id INTEGER NOT NULL,
                raised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contractor_id INTEGER,
                oversight_engineer_id INTEGER,
                status VARCHAR(20) DEFAULT 'raised',
                acknowledged_at TIMESTAMP,
                acknowledged_by_user_id INTEGER,
                contractor_remarks TEXT,
                contractor_response TEXT,
                proposed_deadline TIMESTAMP,
                responded_at TIMESTAMP,
                resolution_description TEXT,
                resolution_photo_urls JSON,
                resolved_at TIMESTAMP,
                resolved_by_user_id INTEGER,
                verified_at TIMESTAMP,
                verified_by_user_id INTEGER,
                verification_remarks TEXT,
                closed_at TIMESTAMP,
                closed_by_user_id INTEGER,
                closure_remarks TEXT,
                actual_resolution_days INTEGER,
                rejection_reason TEXT,
                rejected_at TIMESTAMP,
                rejected_by_user_id INTEGER,
                transfer_history JSON,
                score_month VARCHAR(7),
                score_year INTEGER,
                score_week VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (raised_by_user_id) REFERENCES users(id),
                FOREIGN KEY (contractor_id) REFERENCES rmc_vendors(id),
                FOREIGN KEY (oversight_engineer_id) REFERENCES users(id),
                FOREIGN KEY (acknowledged_by_user_id) REFERENCES users(id),
                FOREIGN KEY (resolved_by_user_id) REFERENCES users(id),
                FOREIGN KEY (verified_by_user_id) REFERENCES users(id),
                FOREIGN KEY (closed_by_user_id) REFERENCES users(id),
                FOREIGN KEY (rejected_by_user_id) REFERENCES users(id),
                CHECK (severity IN ('HIGH', 'MODERATE', 'LOW')),
                CHECK (status IN ('raised', 'acknowledged', 'in_progress', 'resolved', 'verified', 'closed', 'rejected', 'transferred'))
            );


-- Table: concrete_nc_notifications
CREATE TABLE concrete_nc_notifications (
                id SERIAL PRIMARY KEY,
                issue_id INTEGER NOT NULL,
                recipient_user_id INTEGER NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                channel VARCHAR(20) NOT NULL,
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered BOOLEAN DEFAULT FALSE,
                delivery_status VARCHAR(50),
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (issue_id) REFERENCES concrete_nc_issues(id) ON DELETE CASCADE,
                FOREIGN KEY (recipient_user_id) REFERENCES users(id),
                CHECK (channel IN ('whatsapp', 'email', 'in_app'))
            );


-- Table: concrete_nc_score_reports
CREATE TABLE concrete_nc_score_reports (
                id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                contractor_id INTEGER NOT NULL,
                report_type VARCHAR(20) NOT NULL,
                period VARCHAR(20) NOT NULL,
                high_severity_count INTEGER DEFAULT 0,
                moderate_severity_count INTEGER DEFAULT 0,
                low_severity_count INTEGER DEFAULT 0,
                total_issues_count INTEGER DEFAULT 0,
                closed_issues_count INTEGER DEFAULT 0,
                open_issues_count INTEGER DEFAULT 0,
                total_score REAL DEFAULT 0.0,
                closure_rate REAL DEFAULT 0.0,
                avg_resolution_days REAL DEFAULT 0.0,
                performance_grade VARCHAR(2),
                generated_by_user_id INTEGER,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (contractor_id) REFERENCES rmc_vendors(id) ON DELETE CASCADE,
                FOREIGN KEY (generated_by_user_id) REFERENCES users(id),
                CHECK (report_type IN ('monthly', 'weekly')),
                CHECK (performance_grade IN ('A', 'B', 'C', 'D', 'F')),
                UNIQUE (company_id, project_id, contractor_id, report_type, period)
            );


-- Table: password_reset_tokens
CREATE TABLE password_reset_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(64) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );


-- Table: safety_nc_score_reports
CREATE TABLE safety_nc_score_reports (
                id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                contractor_name VARCHAR(255),
                report_type VARCHAR(20) NOT NULL,
                period VARCHAR(20) NOT NULL,
                
                -- Severity counts
                critical_count INTEGER DEFAULT 0,
                major_count INTEGER DEFAULT 0,
                minor_count INTEGER DEFAULT 0,
                
                -- Status counts
                total_issues_count INTEGER DEFAULT 0,
                closed_issues_count INTEGER DEFAULT 0,
                open_issues_count INTEGER DEFAULT 0,
                
                -- Scoring
                total_score REAL DEFAULT 0.0,
                closure_rate REAL DEFAULT 0.0,
                avg_resolution_days REAL DEFAULT 0.0,
                performance_grade VARCHAR(2),
                
                -- Metadata
                generated_by_user_id INTEGER,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (generated_by_user_id) REFERENCES users(id),
                CHECK (report_type IN ('monthly', 'weekly')),
                CHECK (performance_grade IN ('A', 'B', 'C', 'D', 'F')),
                UNIQUE (company_id, project_id, contractor_name, report_type, period)
            );


