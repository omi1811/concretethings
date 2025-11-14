#!/bin/bash
# ProSite Quick Setup Script
# Run this to configure critical settings

set -e

echo "============================================"
echo "ProSite - Quick Configuration Setup"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Keeping existing .env file"
        ENV_EXISTS=true
    fi
fi

if [ -z "$ENV_EXISTS" ]; then
    echo -e "${GREEN}📝 Creating .env file from template...${NC}"
    cp .env.example .env
    echo "✅ .env file created"
fi

echo ""
echo "============================================"
echo "1. Generating Secure Keys"
echo "============================================"

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

echo "✅ Generated SECRET_KEY"
echo "✅ Generated JWT_SECRET_KEY"

# Update .env with keys
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET_KEY|" .env

echo ""
echo "============================================"
echo "2. Email Configuration"
echo "============================================"
echo ""
echo "Choose email provider:"
echo "  1) Gmail (easiest for testing)"
echo "  2) SendGrid (best for production)"
echo "  3) AWS SES (best for scale)"
echo "  4) Skip for now"
echo ""
read -p "Enter choice (1-4): " email_choice

case $email_choice in
    1)
        echo ""
        echo "Gmail Setup:"
        echo "1. Go to https://myaccount.google.com/apppasswords"
        echo "2. Generate an App Password"
        echo "3. Enter details below:"
        echo ""
        read -p "Gmail address: " gmail_address
        read -p "App Password (16 chars): " gmail_password
        
        sed -i "s|SMTP_HOST=.*|SMTP_HOST=smtp.gmail.com|" .env
        sed -i "s|SMTP_PORT=.*|SMTP_PORT=587|" .env
        sed -i "s|SMTP_USER=.*|SMTP_USER=$gmail_address|" .env
        sed -i "s|SMTP_PASSWORD=.*|SMTP_PASSWORD=$gmail_password|" .env
        sed -i "s|SMTP_FROM_EMAIL=.*|SMTP_FROM_EMAIL=$gmail_address|" .env
        sed -i "s|EMAIL_ENABLED=.*|EMAIL_ENABLED=true|" .env
        
        echo "✅ Gmail configured"
        ;;
    2)
        echo ""
        echo "SendGrid Setup:"
        echo "1. Sign up at https://sendgrid.com"
        echo "2. Create API Key"
        echo "3. Enter details below:"
        echo ""
        read -p "Verified sender email: " sendgrid_email
        read -p "API Key: " sendgrid_key
        
        sed -i "s|SMTP_HOST=.*|SMTP_HOST=smtp.sendgrid.net|" .env
        sed -i "s|SMTP_PORT=.*|SMTP_PORT=587|" .env
        sed -i "s|SMTP_USER=.*|SMTP_USER=apikey|" .env
        sed -i "s|SMTP_PASSWORD=.*|SMTP_PASSWORD=$sendgrid_key|" .env
        sed -i "s|SMTP_FROM_EMAIL=.*|SMTP_FROM_EMAIL=$sendgrid_email|" .env
        sed -i "s|EMAIL_ENABLED=.*|EMAIL_ENABLED=true|" .env
        
        echo "✅ SendGrid configured"
        ;;
    3)
        echo ""
        echo "AWS SES Setup:"
        read -p "SMTP Username: " aws_user
        read -p "SMTP Password: " aws_pass
        read -p "Verified email: " aws_email
        read -p "AWS Region (e.g., us-east-1): " aws_region
        
        sed -i "s|SMTP_HOST=.*|SMTP_HOST=email-smtp.$aws_region.amazonaws.com|" .env
        sed -i "s|SMTP_PORT=.*|SMTP_PORT=587|" .env
        sed -i "s|SMTP_USER=.*|SMTP_USER=$aws_user|" .env
        sed -i "s|SMTP_PASSWORD=.*|SMTP_PASSWORD=$aws_pass|" .env
        sed -i "s|SMTP_FROM_EMAIL=.*|SMTP_FROM_EMAIL=$aws_email|" .env
        sed -i "s|EMAIL_ENABLED=.*|EMAIL_ENABLED=true|" .env
        
        echo "✅ AWS SES configured"
        ;;
    4)
        echo "⏭️  Email configuration skipped"
        ;;
esac

echo ""
echo "============================================"
echo "3. Application URL"
echo "============================================"
echo ""
read -p "Enter your domain (or press Enter for localhost:8000): " app_url
if [ -z "$app_url" ]; then
    app_url="http://localhost:8000"
fi
sed -i "s|APP_URL=.*|APP_URL=$app_url|" .env
echo "✅ Application URL set to: $app_url"

echo ""
echo "============================================"
echo "4. Database Backup Setup"
echo "============================================"
echo ""
read -p "Setup automated daily backup? (y/n): " setup_backup

if [ "$setup_backup" = "y" ]; then
    mkdir -p backups
    
    cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d-%H%M%S)
DB_FILE="./data.sqlite3"

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/data-$DATE.sqlite3"

# Keep only last 30 days
find $BACKUP_DIR -name "data-*.sqlite3" -mtime +30 -delete

echo "✅ Backup created: data-$DATE.sqlite3"
EOF
    
    chmod +x backup_db.sh
    echo "✅ Backup script created: backup_db.sh"
    
    # Create first backup
    ./backup_db.sh
    
    echo ""
    echo "To setup daily backups, add to crontab:"
    echo "0 2 * * * cd $(pwd) && ./backup_db.sh"
fi

echo ""
echo "============================================"
echo "5. Test Configuration"
echo "============================================"
echo ""

echo "Testing application startup..."
if python3 -c "from server.app import app; print('✅ App loads successfully')" 2>&1 | grep -q "✅"; then
    echo -e "${GREEN}✅ Application configuration valid${NC}"
else
    echo -e "${RED}❌ Application failed to load${NC}"
    echo "Please check error messages above"
fi

if [ "$email_choice" != "4" ]; then
    echo ""
    read -p "Test email configuration? (y/n): " test_email
    if [ "$test_email" = "y" ]; then
        read -p "Send test email to: " test_email_addr
        python3 -c "
from server.email_notifications import send_email
try:
    send_email(
        to_email='$test_email_addr',
        subject='ProSite Email Test',
        body='If you receive this, email is configured correctly! ✅'
    )
    print('✅ Test email sent to $test_email_addr')
except Exception as e:
    print(f'❌ Email test failed: {e}')
"
    fi
fi

echo ""
echo "============================================"
echo "✅ Configuration Complete!"
echo "============================================"
echo ""
echo "Next Steps:"
echo "  1. Change admin password: shrotrio@gmail.com / Admin@123"
echo "  2. Review .env file and update any other settings"
echo "  3. Start the server: python3 -m server.app"
echo "  4. Check PENDING_TASKS.md for remaining tasks"
echo ""
echo "Documentation:"
echo "  - PENDING_TASKS.md - Complete task list"
echo "  - SUPABASE_VS_CUSTOM_AUTH.md - Auth comparison"
echo "  - MODULE_SYSTEM_AND_AUTH_COMPLETE.md - Auth guide"
echo ""
echo "Admin Login:"
echo "  Email: shrotrio@gmail.com"
echo "  Password: Admin@123 (CHANGE IMMEDIATELY)"
echo ""
echo -e "${GREEN}🚀 ProSite is ready!${NC}"
