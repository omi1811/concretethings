"""
Email Notification Service for ConcreteThings QMS.
Sends automated emails for test failures, batch rejections, and NCRs.
ISO 9001:2015 - Clause 7.4 (Communication)
"""
from __future__ import annotations

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Email Configuration (from environment variables)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "ConcreteThings QMS")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
APP_URL = os.getenv("APP_URL", "http://localhost:8000")


class EmailService:
    """Email notification service using SMTP."""
    
    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.from_email = SMTP_FROM_EMAIL
        self.from_name = SMTP_FROM_NAME
        
        if self.enabled:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Email disabled.")
                self.enabled = False
            else:
                logger.info("Email notification service initialized")
        else:
            logger.info("Email notifications disabled (set EMAIL_ENABLED=true to enable)")
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send HTML email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_to_multiple(
        self, 
        email_addresses: List[str], 
        subject: str, 
        html_body: str,
        text_body: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Send email to multiple recipients.
        
        Returns:
            dict: {"success": int, "failed": int, "total": int}
        """
        success = 0
        failed = 0
        
        for email in email_addresses:
            if self.send_email(email, subject, html_body, text_body):
                success += 1
            else:
                failed += 1
        
        return {
            "success": success,
            "failed": failed,
            "total": len(email_addresses)
        }


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get email notification service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


# ============================================================================
# HTML Email Templates
# ============================================================================

def _get_email_header() -> str:
    """Common email header with branding."""
    return """
    <div style="background-color: #f44336; color: white; padding: 20px; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">🏗️ ConcreteThings QMS</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px;">Quality Management System</p>
    </div>
    """

def _get_email_footer() -> str:
    """Common email footer."""
    return f"""
    <div style="background-color: #f5f5f5; padding: 20px; margin-top: 30px; text-align: center; font-size: 12px; color: #666;">
        <p style="margin: 0;">This is an automated notification from ConcreteThings QMS</p>
        <p style="margin: 5px 0;">Please do not reply to this email</p>
        <p style="margin: 10px 0 0 0;">
            <a href="{APP_URL}" style="color: #f44336; text-decoration: none;">Visit Dashboard</a>
        </p>
    </div>
    """

def format_cube_test_failure_email(data: dict) -> tuple[str, str]:
    """
    Format cube test failure email (HTML + text).
    
    Args:
        data: Dict containing test failure details
        
    Returns:
        tuple: (html_body, text_body)
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
        {_get_email_header()}
        
        <div style="padding: 30px;">
            <h2 style="color: #f44336; margin-top: 0;">🚨 Concrete Test Failure Alert</h2>
            
            <div style="background-color: #fff3cd; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;">
                <strong>⚠️ Action Required:</strong> Concrete strength test has failed. Immediate investigation needed.
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 40%;">Project</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{data['project_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Batch Number</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{data['batch_number']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">RMC Vendor</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{data['vendor_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Test Age</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{data['test_age_days']} days</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Required Strength</td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>{data['required_strength_mpa']:.2f} MPa</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Achieved Strength</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #f44336;"><strong>{data['average_strength_mpa']:.2f} MPa</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Strength Ratio</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{data['strength_ratio_percent']:.1f}%</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Status</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #f44336;"><strong>❌ FAILED</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">NCR Number</td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>{data['ncr_number']}</strong></td>
                </tr>
            </table>
            
            <h3 style="margin-top: 30px;">Individual Cube Strengths (IS 516:1959)</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f44336; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Cube</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Strength (MPa)</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">% of Required</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">Cube 1</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{data['cube_1_strength_mpa']:.2f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{(data['cube_1_strength_mpa'] / data['required_strength_mpa'] * 100):.1f}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">Cube 2</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{data['cube_2_strength_mpa']:.2f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{(data['cube_2_strength_mpa'] / data['required_strength_mpa'] * 100):.1f}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">Cube 3</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{data['cube_3_strength_mpa']:.2f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{(data['cube_3_strength_mpa'] / data['required_strength_mpa'] * 100):.1f}%</td>
                    </tr>
                    <tr style="background-color: #f5f5f5; font-weight: bold;">
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">Average</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: #f44336;">{data['average_strength_mpa']:.2f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{data['strength_ratio_percent']:.1f}%</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin: 30px 0; padding: 20px; background-color: #f5f5f5; border-radius: 5px;">
                <h3 style="margin-top: 0;">📋 Required Actions (ISO 9001:2015 Clause 8.7)</h3>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    <li>Investigate root cause of failure</li>
                    <li>Review mix design and batching records</li>
                    <li>Verify curing conditions</li>
                    <li>Assess structural implications</li>
                    <li>Implement corrective actions</li>
                    <li>Document findings in NCR</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{APP_URL}/cube-test/{data['test_id']}" 
                   style="display: inline-block; padding: 12px 30px; background-color: #f44336; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    View Full Test Report
                </a>
            </div>
        </div>
        
        {_get_email_footer()}
    </body>
    </html>
    """
    
    # Plain text version
    text = f"""
CONCRETE TEST FAILURE ALERT

Project: {data['project_name']}
Batch: {data['batch_number']}
RMC Vendor: {data['vendor_name']}

Test Details:
- Test Age: {data['test_age_days']} days
- Required Strength: {data['required_strength_mpa']:.2f} MPa
- Achieved Strength: {data['average_strength_mpa']:.2f} MPa
- Strength Ratio: {data['strength_ratio_percent']:.1f}%
- Status: FAILED
- NCR: {data['ncr_number']}

Individual Cube Strengths:
1. Cube 1: {data['cube_1_strength_mpa']:.2f} MPa
2. Cube 2: {data['cube_2_strength_mpa']:.2f} MPa
3. Cube 3: {data['cube_3_strength_mpa']:.2f} MPa
Average: {data['average_strength_mpa']:.2f} MPa

ACTION REQUIRED: Immediate investigation needed.

View Details: {APP_URL}/cube-test/{data['test_id']}

---
This is an automated notification from ConcreteThings QMS
"""
    
    return html, text


# ============================================================================
# High-Level Notification Functions
# ============================================================================

def notify_test_failure_email(
    cube_test,
    batch_register,
    mix_design,
    vendor,
    project,
    quality_manager_email: str,
    pm_email: Optional[str] = None
) -> dict:
    """
    Send test failure email notifications to all stakeholders.
    
    Returns:
        dict: Notification results
    """
    email_service = get_email_service()
    
    data = {
        "project_name": project.name,
        "batch_number": batch_register.batch_number,
        "vendor_name": vendor.vendor_name,
        "test_age_days": cube_test.test_age_days,
        "required_strength_mpa": cube_test.required_strength_mpa,
        "average_strength_mpa": cube_test.average_strength_mpa,
        "strength_ratio_percent": cube_test.strength_ratio_percent,
        "cube_1_strength_mpa": cube_test.cube_1_strength_mpa,
        "cube_2_strength_mpa": cube_test.cube_2_strength_mpa,
        "cube_3_strength_mpa": cube_test.cube_3_strength_mpa,
        "ncr_number": cube_test.ncr_number,
        "test_id": cube_test.id
    }
    
    html_body, text_body = format_cube_test_failure_email(data)
    subject = f"🚨 URGENT: Cube Test Failure - {batch_register.batch_number} - {project.name}"
    
    # Collect recipient emails
    recipients = [quality_manager_email, vendor.contact_email]
    if pm_email:
        recipients.append(pm_email)
    
    # Remove duplicates and None values
    recipients = list(set(filter(None, recipients)))
    
    result = email_service.send_to_multiple(recipients, subject, html_body, text_body)
    
    logger.info(f"Test failure email notifications sent: {result}")
    return result


def get_email_setup_instructions() -> str:
    """Get email setup instructions."""
    return """
# Email Notification Setup

## Gmail (Recommended for Development)

1. Enable 2-Factor Authentication in your Google Account
2. Generate App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. Update .env:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=ConcreteThings QMS
   EMAIL_ENABLED=true
   ```

## Other Providers

### Microsoft 365 / Outlook
```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

### SendGrid (Production)
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### AWS SES (Production)
```
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-iam-access-key
SMTP_PASSWORD=your-iam-secret-key
```

## Testing

```python
from server.email_notifications import get_email_service

email = get_email_service()
email.send_email(
    "test@example.com",
    "Test Email",
    "<h1>Test from ConcreteThings QMS</h1>",
    "Test from ConcreteThings QMS"
)
```
"""


def notify_batch_rejection_email(
    batch_id: int,
    batch_number: str,
    vendor_email: Optional[str],
    vendor_name: str,
    project_name: str,
    delivery_date: str,
    rejection_reason: str,
    verifier_name: str
) -> bool:
    """
    Send email notification for batch rejection.
    
    Args:
        batch_id: ID of the rejected batch
        batch_number: Batch number
        vendor_email: Vendor's email address
        vendor_name: Vendor name
        project_name: Project name
        delivery_date: Delivery date (formatted string)
        rejection_reason: Reason for rejection
        verifier_name: Name of the person who rejected
    
    Returns:
        True if email sent successfully, False otherwise
    """
    email_service = get_email_service()
    
    if not email_service.enabled:
        print("Email service is disabled. Skipping batch rejection notification.")
        return False
    
    # Prepare email data
    subject = f"⚠️ Batch Rejected - {batch_number} | {project_name}"
    
    # HTML body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #dc3545;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .batch-info {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
            .rejection-reason {{
                background-color: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin: 20px 0;
            }}
            .info-row {{
                margin: 10px 0;
            }}
            .label {{
                font-weight: bold;
                color: #555;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 0.9em;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>⚠️ Batch Rejected</h2>
            </div>
            <div class="content">
                <p>Dear {vendor_name},</p>
                
                <p>A concrete batch has been <strong>rejected</strong> by the Quality Team:</p>
                
                <div class="batch-info">
                    <div class="info-row">
                        <span class="label">Batch Number:</span> {batch_number}
                    </div>
                    <div class="info-row">
                        <span class="label">Project:</span> {project_name}
                    </div>
                    <div class="info-row">
                        <span class="label">Delivery Date:</span> {delivery_date}
                    </div>
                    <div class="info-row">
                        <span class="label">Rejected By:</span> {verifier_name}
                    </div>
                </div>
                
                <div class="rejection-reason">
                    <div class="label">Rejection Reason:</div>
                    <p>{rejection_reason if rejection_reason else "No reason provided"}</p>
                </div>
                
                <h3>Required Actions:</h3>
                <ol>
                    <li>Review the rejection reason with your quality control team</li>
                    <li>Take corrective actions to prevent similar issues</li>
                    <li>Contact the project Quality Manager for clarification if needed</li>
                    <li>Ensure all future deliveries meet specified requirements</li>
                </ol>
                
                <div class="footer">
                    <p><strong>This is an automated notification from ConcreteThings Quality Management System.</strong></p>
                    <p>If you have questions, please contact the project Quality Manager.</p>
                    <p style="font-size: 0.8em; color: #999;">
                        Batch ID: {batch_id} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text body
    text_body = f"""
    ⚠️ BATCH REJECTED
    
    Dear {vendor_name},
    
    A concrete batch has been REJECTED by the Quality Team:
    
    BATCH DETAILS:
    - Batch Number: {batch_number}
    - Project: {project_name}
    - Delivery Date: {delivery_date}
    - Rejected By: {verifier_name}
    
    REJECTION REASON:
    {rejection_reason if rejection_reason else "No reason provided"}
    
    REQUIRED ACTIONS:
    1. Review the rejection reason with your quality control team
    2. Take corrective actions to prevent similar issues
    3. Contact the project Quality Manager for clarification if needed
    4. Ensure all future deliveries meet specified requirements
    
    ---
    This is an automated notification from ConcreteThings Quality Management System.
    If you have questions, please contact the project Quality Manager.
    
    Batch ID: {batch_id} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    # Send email
    try:
        if vendor_email:
            success = email_service.send_email(vendor_email, subject, html_body, text_body)
            if success:
                print(f"✅ Batch rejection email sent to {vendor_email}")
                return True
            else:
                print(f"❌ Failed to send batch rejection email to {vendor_email}")
                return False
        else:
            print("⚠️ No vendor email provided. Skipping batch rejection notification.")
            return False
    except Exception as e:
        print(f"❌ Error sending batch rejection email: {str(e)}")
        return False


if __name__ == "__main__":
    print(get_email_setup_instructions())
