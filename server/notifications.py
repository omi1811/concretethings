"""
WhatsApp Notification Service using Twilio API.
Sends automated alerts for test failures, batch rejections, and NCRs.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Twilio Configuration (from environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Twilio Sandbox
WHATSAPP_ENABLED = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"

# Try to import Twilio (optional dependency)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. WhatsApp notifications will be disabled.")


class WhatsAppNotification:
    """WhatsApp notification service using Twilio."""
    
    def __init__(self):
        self.client = None
        self.enabled = WHATSAPP_ENABLED and TWILIO_AVAILABLE
        
        if self.enabled:
            if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
                logger.warning("Twilio credentials not configured. WhatsApp disabled.")
                self.enabled = False
            else:
                try:
                    self.client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                    logger.info("WhatsApp notification service initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Twilio client: {e}")
                    self.enabled = False
        else:
            logger.info("WhatsApp notifications disabled (set WHATSAPP_ENABLED=true to enable)")
    
    def send_message(self, to_phone: str, message: str) -> bool:
        """
        Send WhatsApp message via Twilio.
        
        Args:
            to_phone: Recipient phone number (international format: +1234567890)
            message: Message text
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"WhatsApp disabled. Would send to {to_phone}: {message[:50]}...")
            return False
        
        try:
            # Format phone number for WhatsApp
            if not to_phone.startswith("whatsapp:"):
                to_phone = f"whatsapp:{to_phone}"
            
            message_obj = self.client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                body=message,
                to=to_phone
            )
            
            logger.info(f"WhatsApp sent to {to_phone}, SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {to_phone}: {e}")
            return False
    
    def send_to_multiple(self, phone_numbers: List[str], message: str) -> dict:
        """
        Send WhatsApp message to multiple recipients.
        
        Returns:
            dict: {"success": int, "failed": int, "total": int}
        """
        success = 0
        failed = 0
        
        for phone in phone_numbers:
            if self.send_message(phone, message):
                success += 1
            else:
                failed += 1
        
        return {
            "success": success,
            "failed": failed,
            "total": len(phone_numbers)
        }


# Singleton instance
_whatsapp_service = None

def get_whatsapp_service() -> WhatsAppNotification:
    """Get WhatsApp notification service singleton."""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppNotification()
    return _whatsapp_service


# ============================================================================
# Notification Templates
# ============================================================================

def format_cube_test_failure(data: dict) -> str:
    """
    Format cube test failure notification message.
    
    Args:
        data: Dict containing:
            - project_name: str
            - batch_number: str
            - vendor_name: str
            - test_age_days: int
            - required_strength_mpa: float
            - average_strength_mpa: float
            - strength_ratio_percent: float
            - cube_1_strength_mpa: float
            - cube_2_strength_mpa: float
            - cube_3_strength_mpa: float
            - ncr_number: str
            - test_id: int
            - app_url: str (optional)
    """
    app_url = data.get("app_url", "http://localhost:8000")
    
    message = f"""🚨 *CONCRETE TEST FAILURE ALERT* 🚨

*Project:* {data['project_name']}
*Batch:* {data['batch_number']}
*RMC Vendor:* {data['vendor_name']}

*Test Details:*
• Test Age: {data['test_age_days']} days
• Required Strength: {data['required_strength_mpa']:.2f} MPa
• Achieved Strength: {data['average_strength_mpa']:.2f} MPa
• Strength Ratio: {data['strength_ratio_percent']:.1f}%

*Status:* ❌ FAILED

*NCR:* {data['ncr_number']}

*Cube Strengths:*
1️⃣ {data['cube_1_strength_mpa']:.2f} MPa
2️⃣ {data['cube_2_strength_mpa']:.2f} MPa
3️⃣ {data['cube_3_strength_mpa']:.2f} MPa
*Average:* {data['average_strength_mpa']:.2f} MPa

⚠️ *Action Required:* Immediate investigation

🔗 View Details: {app_url}/cube-test/{data['test_id']}

---
_Automated alert from ConcreteThings QMS_
"""
    return message


def format_batch_rejection(data: dict) -> str:
    """
    Format batch rejection notification message.
    
    Args:
        data: Dict containing:
            - project_name: str
            - batch_number: str
            - vendor_name: str
            - delivery_date: str
            - rejection_reason: str
            - rejected_by_name: str
            - batch_id: int
            - app_url: str (optional)
    """
    app_url = data.get("app_url", "http://localhost:8000")
    
    message = f"""❌ *BATCH REJECTED* ❌

*Project:* {data['project_name']}
*Batch Number:* {data['batch_number']}
*RMC Vendor:* {data['vendor_name']}
*Delivery Date:* {data['delivery_date']}

*Rejected By:* {data['rejected_by_name']}

*Reason for Rejection:*
{data['rejection_reason']}

⚠️ *Action Required:* Contact quality team

🔗 View Batch: {app_url}/batch/{data['batch_id']}

---
_Automated alert from ConcreteThings QMS_
"""
    return message


def format_ncr_generated(data: dict) -> str:
    """
    Format NCR (Non-Conformance Report) generation notification.
    
    Args:
        data: Dict containing:
            - project_name: str
            - ncr_number: str
            - issue_description: str
            - batch_number: str (optional)
            - test_id: int (optional)
            - generated_by_name: str
            - app_url: str (optional)
    """
    app_url = data.get("app_url", "http://localhost:8000")
    
    batch_info = f"*Batch:* {data['batch_number']}\n" if data.get('batch_number') else ""
    
    message = f"""📋 *NON-CONFORMANCE REPORT GENERATED* 📋

*NCR Number:* {data['ncr_number']}
*Project:* {data['project_name']}
{batch_info}
*Issue Description:*
{data['issue_description']}

*Generated By:* {data['generated_by_name']}
*Date:* {datetime.now().strftime('%Y-%m-%d %H:%M')}

⚠️ *Action Required:* Review and take corrective action

🔗 View NCR: {app_url}/ncr/{data['ncr_number']}

---
_Automated alert from ConcreteThings QMS_
"""
    return message


def format_batch_delivered(data: dict) -> str:
    """
    Format batch delivery confirmation notification.
    
    Args:
        data: Dict containing:
            - project_name: str
            - batch_number: str
            - vendor_name: str
            - quantity_ordered: float
            - location: str
            - delivery_date: str
    """
    message = f"""✅ *BATCH DELIVERED* ✅

*Project:* {data['project_name']}
*Batch Number:* {data['batch_number']}
*RMC Vendor:* {data['vendor_name']}

*Quantity:* {data['quantity_ordered']} m³
*Location:* {data['location']}
*Delivery Date:* {data['delivery_date']}

✓ Entry recorded and pending verification

---
_Automated alert from ConcreteThings QMS_
"""
    return message


# ============================================================================
# High-Level Notification Functions
# ============================================================================

def notify_test_failure(
    cube_test,
    batch_register,
    mix_design,
    vendor,
    project,
    quality_manager_phone: str,
    pm_phone: Optional[str] = None
) -> dict:
    """
    Send test failure notifications to all stakeholders.
    
    Returns:
        dict: Notification results
    """
    whatsapp = get_whatsapp_service()
    
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
        "test_id": cube_test.id,
        "app_url": os.getenv("APP_URL", "http://localhost:8000")
    }
    
    message = format_cube_test_failure(data)
    
    # Collect recipient phone numbers
    recipients = [quality_manager_phone, vendor.contact_phone]
    if pm_phone:
        recipients.append(pm_phone)
    
    # Remove duplicates and None values
    recipients = list(set(filter(None, recipients)))
    
    result = whatsapp.send_to_multiple(recipients, message)
    
    logger.info(f"Test failure notifications sent: {result}")
    return result


def notify_batch_rejection(
    batch_register,
    vendor,
    project,
    rejected_by_name: str,
    vendor_phone: Optional[str] = None,
    pm_phone: Optional[str] = None
) -> dict:
    """
    Send batch rejection notifications.
    
    Returns:
        dict: Notification results
    """
    whatsapp = get_whatsapp_service()
    
    data = {
        "project_name": project.name,
        "batch_number": batch_register.batch_number,
        "vendor_name": vendor.vendor_name,
        "delivery_date": batch_register.delivery_date.strftime("%Y-%m-%d"),
        "rejection_reason": batch_register.rejection_reason or "Not specified",
        "rejected_by_name": rejected_by_name,
        "batch_id": batch_register.id,
        "app_url": os.getenv("APP_URL", "http://localhost:8000")
    }
    
    message = format_batch_rejection(data)
    
    # Notify vendor and PM
    recipients = []
    if vendor_phone:
        recipients.append(vendor_phone)
    if pm_phone:
        recipients.append(pm_phone)
    
    recipients = list(set(filter(None, recipients)))
    
    result = whatsapp.send_to_multiple(recipients, message)
    
    logger.info(f"Batch rejection notifications sent: {result}")
    return result


# ============================================================================
# Setup Instructions
# ============================================================================

def get_setup_instructions() -> str:
    """Get WhatsApp setup instructions."""
    return """
# WhatsApp Notification Setup

## Option 1: Twilio WhatsApp (Recommended for Development)

1. Sign up for Twilio: https://www.twilio.com/try-twilio
2. Get your Account SID and Auth Token
3. Activate WhatsApp Sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
4. Set environment variables in .env:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_ENABLED=true
   ```
5. Join sandbox by sending "join <your-sandbox-code>" to +1 (415) 523-8886 on WhatsApp

## Option 2: WhatsApp Business API (For Production)

1. Apply for WhatsApp Business API access
2. Get approved by Meta/WhatsApp
3. Integrate with Twilio or direct API
4. Update TWILIO_WHATSAPP_FROM with your business number

## Option 3: Alternative Services

- MessageBird
- Vonage (Nexmo)
- Direct WhatsApp Business API
- Gupshup

## Testing

```python
from server.notifications import get_whatsapp_service

whatsapp = get_whatsapp_service()
whatsapp.send_message("+1234567890", "Test message from ConcreteThings QMS")
```

## Install Dependencies

```bash
pip install twilio
```
"""


if __name__ == "__main__":
    # Print setup instructions
    print(get_setup_instructions())
