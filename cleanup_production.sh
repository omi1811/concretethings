#!/bin/bash
# ProSite - Production Cleanup Script
# Removes unnecessary files for commercial deployment

echo "🧹 ProSite Production Cleanup Starting..."

# Create archive directory for old files
mkdir -p archive/old_docs
mkdir -p archive/migration_scripts
mkdir -p archive/backups

# Move duplicate/redundant documentation
echo "📄 Archiving redundant documentation..."
mv MIGRATION_SUMMARY.md archive/old_docs/ 2>/dev/null
mv SESSION_SUMMARY.md archive/old_docs/ 2>/dev/null
mv BACKEND_COMPLETE_SUMMARY.md archive/old_docs/ 2>/dev/null
mv COMPLETE_SUMMARY.md archive/old_docs/ 2>/dev/null
mv IMPLEMENTATION_STATUS.md archive/old_docs/ 2>/dev/null
mv IMPLEMENTATION_COMPLETE_STATUS.md archive/old_docs/ 2>/dev/null
mv PHASE_1_COMPLETE.md archive/old_docs/ 2>/dev/null
mv MODULE_SYSTEM_AND_AUTH_COMPLETE.md archive/old_docs/ 2>/dev/null
mv FRONTEND_COMPLETE.md archive/old_docs/ 2>/dev/null
mv SCORING_AND_MODULAR_UPDATE.md archive/old_docs/ 2>/dev/null
mv FEATURE_COMPLETENESS_AUDIT.md archive/old_docs/ 2>/dev/null
mv PENDING_TASKS.md archive/old_docs/ 2>/dev/null
mv CRITICAL_BUGS_REPORT.md archive/old_docs/ 2>/dev/null
mv CRITICAL_FIXES_APPLIED.md archive/old_docs/ 2>/dev/null
mv FIXES.md archive/old_docs/ 2>/dev/null

# Move old migration scripts
echo "🔄 Archiving migration scripts..."
mv migrate_db.py archive/migration_scripts/ 2>/dev/null
mv migrate_auth_modules.py archive/migration_scripts/ 2>/dev/null
mv migrate_new_safety_modules.py archive/migration_scripts/ 2>/dev/null
mv migrate_material_vehicle.py archive/migration_scripts/ 2>/dev/null
mv migrate_pour_activities.py archive/migration_scripts/ 2>/dev/null
mv migrate_qms.py archive/migration_scripts/ 2>/dev/null
mv migrate_concrete_nc.py archive/migration_scripts/ 2>/dev/null
mv migrate_safety_nc_scoring.py archive/migration_scripts/ 2>/dev/null
mv migrate_users.py archive/migration_scripts/ 2>/dev/null
mv migrate_training.py archive/migration_scripts/ 2>/dev/null
mv export_to_postgres.py archive/migration_scripts/ 2>/dev/null

# Move database backups
echo "💾 Archiving database backups..."
mv data.sqlite3.backup-* archive/backups/ 2>/dev/null
mv sqlite_dump.sql archive/backups/ 2>/dev/null
mv supabase_data_inserts.sql archive/backups/ 2>/dev/null

# Move test scripts
echo "🧪 Archiving test scripts..."
mv qa_test_suite.py archive/ 2>/dev/null
mv seed.py archive/ 2>/dev/null
mv seed_safety_data.py archive/ 2>/dev/null
mv create_demo_users.py archive/ 2>/dev/null
mv fix_jwt.py archive/ 2>/dev/null

# Move redundant setup scripts
echo "⚙️ Archiving redundant setup scripts..."
mv restructure_to_modules.py archive/ 2>/dev/null
mv QUICK_MIGRATION_REFERENCE.txt archive/old_docs/ 2>/dev/null

# Keep only essential documentation
echo "📚 Keeping essential documentation:"
echo "  ✅ README.md"
echo "  ✅ QUICK_START.md"
echo "  ✅ USER_ROLES_COMPLETE.md"
echo "  ✅ DEPLOYMENT.md"
echo "  ✅ FRONTEND_OPTIMIZATION_COMPLETE.md"
echo "  ✅ QUICK_PERFORMANCE_GUIDE.md"
echo "  ✅ DEPLOYMENT_CHECKLIST.md"
echo "  ✅ COMMERCIAL_READY.md"

# Count archived files
echo ""
echo "📊 Cleanup Summary:"
echo "  • Documentation archived: $(ls archive/old_docs/ 2>/dev/null | wc -l) files"
echo "  • Migration scripts archived: $(ls archive/migration_scripts/ 2>/dev/null | wc -l) files"
echo "  • Backups archived: $(ls archive/backups/ 2>/dev/null | wc -l) files"

echo ""
echo "✅ Production cleanup complete!"
echo "📦 Archived files moved to ./archive/"
echo "🚀 Application ready for commercial deployment"
