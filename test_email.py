"""
Test script to verify email notifications for cube test failure.
"""
import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.dirname(__file__))

from server.email_notifications import send_email, get_email_service

def test_email():
    """Test email notification."""
    print("Testing Email Notification System...")
    print("=" * 50)
    
    email_service = get_email_service()
    
    if not email_service.enabled:
        print("\n⚠️  Email service is DISABLED")
        print("\nTo enable email notifications:")
        print("1. Set EMAIL_ENABLED=true in your .env file")
        print("2. Configure SMTP settings:")
        print("   - SMTP_HOST (e.g., smtp.gmail.com)")
        print("   - SMTP_PORT (e.g., 587)")
        print("   - SMTP_USER (your email)")
        print("   - SMTP_PASSWORD (app password)")
        print("\nFor Gmail:")
        print("   - Enable 2FA")
        print("   - Generate App Password at: https://myaccount.google.com/apppasswords")
        return
    
    print(f"\n✅ Email service is ENABLED")
    print(f"   SMTP Host: {email_service.smtp_host}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   From Email: {email_service.from_email}")
    
    # Send test email
    test_recipient = input("\nEnter test recipient email address: ").strip()
    
    if not test_recipient:
        print("❌ No email address provided. Exiting.")
        return
    
    print(f"\n📧 Sending test email to {test_recipient}...")
    
    html_body = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #4CAF50;">✅ ProSite Email Test</h2>
        <p>This is a test email from ProSite Quality Management System.</p>
        <p>Your email notifications are <strong>working correctly</strong>!</p>
        <hr>
        <p style="font-size: 12px; color: #666;">
            This is an automated test notification. 
            Cube test failure notifications will use a similar format.
        </p>
    </body>
    </html>
    """
    
    text_body = """
    ProSite Email Test
    
    This is a test email from ProSite Quality Management System.
    Your email notifications are working correctly!
    
    ---
    This is an automated test notification.
    """
    
    success = send_email(
        test_recipient,
        "🧪 ProSite Email Test - Notification System Working",
        html_body,
        text_body
    )
    
    if success:
        print("\n✅ Test email sent successfully!")
        print("   Check your inbox (and spam folder)")
    else:
        print("\n❌ Failed to send test email")
        print("   Check your SMTP configuration")

if __name__ == "__main__":
    test_email()
