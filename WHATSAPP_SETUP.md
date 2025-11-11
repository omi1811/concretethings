# WhatsApp Notification System Setup Guide

## Overview

ConcreteThings QMS uses WhatsApp notifications to alert stakeholders about:
- **Cube Test Failures** - When concrete strength tests fail
- **Batch Rejections** - When batch deliveries are rejected by quality team
- **NCR Generation** - When Non-Conformance Reports are created
- **Batch Deliveries** - Confirmation of concrete deliveries

## Architecture

```
┌─────────────────┐
│  Flask Backend  │
│                 │
│  cube_tests.py  │────┐
│  batches.py     │    │
└─────────────────┘    │
                       ▼
           ┌────────────────────┐
           │ notifications.py   │
           │                    │
           │ - Format messages  │
           │ - Queue sending    │
           │ - Track delivery   │
           └────────────────────┘
                       │
                       ▼
           ┌────────────────────┐
           │   Twilio API       │
           │  (WhatsApp)        │
           └────────────────────┘
                       │
                       ▼
           ┌────────────────────┐
           │  Stakeholder       │
           │  Mobile Phones     │
           │                    │
           │ • Quality Manager  │
           │ • RMC Vendor       │
           │ • Project Manager  │
           └────────────────────┘
```

## Setup Instructions

### Option 1: Twilio WhatsApp Sandbox (Development & Testing)

**Best for:** Development, testing, proof-of-concept

**Limitations:**
- Users must "opt-in" by sending "join <code>" to Twilio number
- Not suitable for production at scale
- Free tier: Limited messages per month

**Steps:**

1. **Sign up for Twilio**
   - Visit: https://www.twilio.com/try-twilio
   - Create free account (credit card required for verification)
   - Get $15 free credit

2. **Get Your Credentials**
   - Login to Twilio Console: https://console.twilio.com/
   - Note your **Account SID** (starts with AC...)
   - Note your **Auth Token** (click "Show" to reveal)

3. **Activate WhatsApp Sandbox**
   - Navigate to: Messaging → Try it out → Send a WhatsApp message
   - URL: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - You'll see a join code like: `join <word>-<word>`
   - Note the sandbox number (usually `+1 415 523 8886`)

4. **Configure Your App**
   
   Edit `.env` file:
   ```bash
   # Twilio WhatsApp Configuration
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_ENABLED=true
   
   # App URL for notification links
   APP_URL=http://localhost:8000
   ```

5. **Opt-in Test Users**
   
   Each phone that will receive notifications must:
   - Open WhatsApp
   - Send message to: `+1 (415) 523-8886`
   - Text content: `join <your-join-code>`
   - Wait for confirmation from Twilio
   
   Example:
   ```
   To: +1 (415) 523-8886
   Message: join concrete-tiger
   ```

6. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   # This installs: twilio==8.11.0
   ```

7. **Test the Integration**
   ```python
   from server.notifications import get_whatsapp_service
   
   whatsapp = get_whatsapp_service()
   result = whatsapp.send_message(
       "+919876543210",  # Your phone (international format)
       "🚨 Test message from ConcreteThings QMS"
   )
   print(f"Sent: {result}")
   ```

### Option 2: WhatsApp Business API (Production)

**Best for:** Production deployment, high volume

**Requirements:**
- Registered business
- Facebook Business Manager account
- WhatsApp Business API approval from Meta
- Dedicated phone number

**Steps:**

1. **Apply for WhatsApp Business API**
   - Visit: https://business.whatsapp.com/
   - Click "Get Started with the API"
   - Apply through Meta or Business Solution Provider (BSP)

2. **Choose Integration Method**
   
   **Method A: Twilio (Recommended)**
   - Easier setup
   - Good documentation
   - Pay-per-message pricing
   - Steps: https://www.twilio.com/docs/whatsapp
   
   **Method B: Direct Meta API**
   - Lower costs at scale
   - More complex setup
   - Requires technical expertise
   - Docs: https://developers.facebook.com/docs/whatsapp

3. **Get Business Number Verified**
   - Submit business documentation
   - Verify phone number ownership
   - Set up display name
   - Configure message templates (optional)

4. **Configure Production Settings**
   ```bash
   TWILIO_ACCOUNT_SID=your_production_sid
   TWILIO_AUTH_TOKEN=your_production_token
   TWILIO_WHATSAPP_FROM=whatsapp:+911234567890  # Your business number
   WHATSAPP_ENABLED=true
   APP_URL=https://yourdomain.com
   ```

5. **Set Up Message Templates** (Optional but Recommended)
   
   WhatsApp Business API requires pre-approved templates for:
   - Messages sent after 24-hour window
   - First message to new contacts
   
   Create templates in Twilio Console:
   - Test Failure Alert Template
   - Batch Rejection Template
   - NCR Notification Template

### Option 3: Alternative Providers

#### MessageBird
- Similar to Twilio
- Good European presence
- https://messagebird.com/whatsapp

#### Vonage (Nexmo)
- Competitive pricing
- Global reach
- https://www.vonage.com/communications-apis/messages/

#### Gupshup
- India-focused
- Good for INR pricing
- https://www.gupshup.io/

## Notification Types

### 1. Cube Test Failure

**Triggered:** When `CubeTestRegister.pass_fail_status == "fail"`

**Recipients:**
- Quality Manager (project role)
- RMC Vendor contact person
- Project Manager (if configured)

**Message Format:**
```
🚨 *CONCRETE TEST FAILURE ALERT* 🚨

*Project:* ABC Tower
*Batch:* BATCH-2024-001
*RMC Vendor:* XYZ Concrete Pvt Ltd

*Test Details:*
• Test Age: 28 days
• Required Strength: 25.00 MPa
• Achieved Strength: 22.50 MPa
• Strength Ratio: 90.0%

*Status:* ❌ FAILED

*NCR:* NCR-2024-001

*Cube Strengths:*
1️⃣ 23.50 MPa
2️⃣ 22.00 MPa
3️⃣ 22.00 MPa
*Average:* 22.50 MPa

⚠️ *Action Required:* Immediate investigation

🔗 View Details: http://localhost:8000/cube-test/1

---
_Automated alert from ConcreteThings QMS_
```

### 2. Batch Rejection

**Triggered:** When `BatchRegister.verification_status == "rejected"`

**Recipients:**
- RMC Vendor contact person
- Project Manager

**Message Format:**
```
❌ *BATCH REJECTED* ❌

*Project:* ABC Tower
*Batch Number:* BATCH-2024-001
*RMC Vendor:* XYZ Concrete Pvt Ltd
*Delivery Date:* 2024-01-15

*Rejected By:* John Doe (Quality Manager)

*Reason for Rejection:*
Incorrect mix design, slump out of specification

⚠️ *Action Required:* Contact quality team

🔗 View Batch: http://localhost:8000/batch/1

---
_Automated alert from ConcreteThings QMS_
```

### 3. NCR Generated

**Triggered:** When NCR is created manually or auto-generated

**Recipients:**
- Quality Manager
- Project Manager
- Company Admin

### 4. Batch Delivered (Optional)

**Triggered:** When new batch is registered

**Recipients:**
- Quality Manager (for verification)

## Implementation Examples

### In Cube Test API Endpoint

```python
from server.notifications import notify_test_failure
from server.models import User, ProjectMembership

@cube_tests_bp.route('/<int:test_id>/results', methods=['PUT'])
@jwt_required()
def update_test_results(test_id):
    """Update cube test results and auto-calculate pass/fail."""
    
    # ... update cube strengths ...
    
    # Auto-calculate results
    cube_test.calculate_results()
    db.session.commit()
    
    # If test failed, send notifications
    if cube_test.pass_fail_status == "fail":
        # Get batch and related entities
        batch = BatchRegister.query.get(cube_test.batch_id)
        mix_design = MixDesign.query.get(batch.mix_design_id)
        vendor = RMCVendor.query.get(batch.rmc_vendor_id)
        project = Project.query.get(cube_test.project_id)
        
        # Get Quality Manager phone
        qm_membership = ProjectMembership.query.filter_by(
            project_id=project.id,
            role="QualityManager"
        ).first()
        qm_user = User.query.get(qm_membership.user_id) if qm_membership else None
        qm_phone = qm_user.phone if qm_user else None
        
        # Get PM phone
        pm_membership = ProjectMembership.query.filter_by(
            project_id=project.id,
            role="ProjectManager"
        ).first()
        pm_user = User.query.get(pm_membership.user_id) if pm_membership else None
        pm_phone = pm_user.phone if pm_user else None
        
        # Send WhatsApp notifications
        result = notify_test_failure(
            cube_test=cube_test,
            batch_register=batch,
            mix_design=mix_design,
            vendor=vendor,
            project=project,
            quality_manager_phone=qm_phone,
            pm_phone=pm_phone
        )
        
        # Mark notification as sent
        cube_test.notification_sent = True
        db.session.commit()
        
        logger.info(f"Test failure notifications: {result}")
    
    return jsonify(cube_test.to_dict()), 200
```

### In Batch Verification API Endpoint

```python
from server.notifications import notify_batch_rejection

@batches_bp.route('/<int:batch_id>/verify', methods=['PUT'])
@jwt_required()
@project_access_required(['Quality', 'QualityManager'])
def verify_batch(batch_id, project_id):
    """Verify or reject a batch."""
    
    data = request.get_json()
    batch = BatchRegister.query.get_or_404(batch_id)
    
    status = data.get('verification_status')  # 'approved' or 'rejected'
    
    if status == 'rejected':
        batch.verification_status = 'rejected'
        batch.rejection_reason = data.get('rejection_reason')
        batch.verified_by = get_jwt_identity()
        batch.verified_at = datetime.utcnow()
        db.session.commit()
        
        # Send rejection notifications
        vendor = RMCVendor.query.get(batch.rmc_vendor_id)
        project = Project.query.get(batch.project_id)
        verifier = User.query.get(batch.verified_by)
        
        notify_batch_rejection(
            batch_register=batch,
            vendor=vendor,
            project=project,
            rejected_by_name=verifier.full_name,
            vendor_phone=vendor.contact_phone,
            pm_phone=None  # Get from project memberships
        )
    
    return jsonify(batch.to_dict()), 200
```

## Phone Number Format

**CRITICAL:** Phone numbers must be in international format:

✅ **Correct:**
- `+919876543210` (India)
- `+12125551234` (USA)
- `+447700900123` (UK)

❌ **Wrong:**
- `9876543210` (missing country code)
- `09876543210` (leading zero)
- `+91 98765 43210` (spaces)

**Validation in Code:**
```python
def validate_phone(phone: str) -> bool:
    """Validate international phone format."""
    import re
    # Must start with +, followed by 7-15 digits
    pattern = r'^\+[1-9]\d{6,14}$'
    return bool(re.match(pattern, phone))
```

## Troubleshooting

### Error: "Account not authorized"
- Check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are correct
- Verify credentials haven't expired

### Error: "User not opted in"
- User must send `join <code>` to sandbox number first
- Check user is using correct WhatsApp number

### Error: "Invalid phone number"
- Ensure phone is in international format: `+<country><number>`
- Remove spaces, dashes, parentheses

### Messages not sending (but no error)
- Check `WHATSAPP_ENABLED=true` in `.env`
- Check Twilio has sufficient credit balance
- Verify Twilio account is not suspended

### Rate Limits
- Twilio Free: ~10 messages/second
- WhatsApp Business API: Tiered limits based on quality rating

### Sandbox Limitations
- 24-hour opt-in window expires
- Users may need to re-join sandbox
- Not suitable for production

## Cost Estimation

### Twilio Pricing (USD, as of 2024)

**WhatsApp Sandbox (Free Tier):**
- First $15 credit free
- Then: $0.005 per message

**WhatsApp Business API:**
- Business-Initiated: $0.005 - $0.009 per message (India)
- User-Initiated: Free (within 24-hour window)
- Template messages: $0.005 - $0.009

**Example Monthly Cost:**
- 1000 test failures/month: ~$5 - $9
- 5000 notifications/month: ~$25 - $45
- 20000 notifications/month: ~$100 - $180

## Security Best Practices

1. **Never commit credentials to Git**
   ```bash
   # Add to .gitignore
   .env
   ```

2. **Use environment variables**
   - Store `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`
   - Never hardcode in source code

3. **Rotate tokens periodically**
   - Change Auth Token every 90 days
   - Update immediately if compromised

4. **Limit phone number access**
   - Only store verified phone numbers
   - Implement opt-out mechanism

5. **Rate limiting**
   - Prevent notification spam
   - Batch notifications where possible

## Testing

### Unit Test Example

```python
# test_notifications.py
from server.notifications import get_whatsapp_service, format_cube_test_failure

def test_format_cube_test_failure():
    data = {
        "project_name": "Test Project",
        "batch_number": "BATCH-TEST-001",
        "vendor_name": "Test Vendor",
        "test_age_days": 28,
        "required_strength_mpa": 25.0,
        "average_strength_mpa": 22.5,
        "strength_ratio_percent": 90.0,
        "cube_1_strength_mpa": 23.5,
        "cube_2_strength_mpa": 22.0,
        "cube_3_strength_mpa": 22.0,
        "ncr_number": "NCR-TEST-001",
        "test_id": 1,
        "app_url": "http://localhost:8000"
    }
    
    message = format_cube_test_failure(data)
    
    assert "CONCRETE TEST FAILURE ALERT" in message
    assert "Test Project" in message
    assert "22.5 MPa" in message
    assert "NCR-TEST-001" in message

def test_whatsapp_send_disabled():
    """Test that messages are logged when WhatsApp is disabled."""
    import os
    os.environ["WHATSAPP_ENABLED"] = "false"
    
    whatsapp = get_whatsapp_service()
    result = whatsapp.send_message("+919876543210", "Test")
    
    assert result == False  # Disabled, not sent
```

### Integration Test

```bash
# Test with real Twilio sandbox
python -c "
from server.notifications import get_whatsapp_service
whatsapp = get_whatsapp_service()
result = whatsapp.send_message(
    '+YOUR_PHONE',
    '🧪 Test notification from ConcreteThings QMS'
)
print(f'Sent: {result}')
"
```

## Monitoring & Analytics

### Twilio Console Monitoring

1. **Message Logs**
   - View all sent messages: https://console.twilio.com/us1/monitor/logs/messages
   - Filter by status: delivered, failed, undelivered
   - Track delivery rates

2. **Usage Dashboard**
   - Monitor credit balance
   - Track daily/monthly usage
   - Set up billing alerts

3. **Webhooks** (Advanced)
   - Set up delivery status callbacks
   - Track message read receipts
   - Handle failed messages

### Application-Level Logging

```python
# In server/notifications.py
logger.info(f"WhatsApp sent to {phone}, SID: {message_sid}")
logger.error(f"Failed to send WhatsApp to {phone}: {error}")

# In app.py
@app.after_request
def log_response(response):
    if 'whatsapp' in request.path:
        logger.info(f"WhatsApp API: {request.method} {request.path} - {response.status}")
    return response
```

## Future Enhancements

1. **Message Templates**
   - Pre-approved templates for faster delivery
   - Reduced costs with template messages

2. **Rich Media**
   - Send batch sheet photos
   - Attach test certificates (PDF)
   - QR codes for quick access

3. **Interactive Messages**
   - Quick reply buttons (Approve/Reject)
   - List messages for batch selection

4. **Delivery Tracking**
   - Store delivery status in database
   - Retry failed messages
   - Track read receipts

5. **Opt-out Management**
   - Allow users to unsubscribe
   - Preference management (only failures, all alerts)

6. **Multi-language Support**
   - Hindi, Tamil, Telugu templates
   - Auto-detect user language preference

## Support

- **Twilio Docs:** https://www.twilio.com/docs/whatsapp
- **WhatsApp Business API:** https://developers.facebook.com/docs/whatsapp
- **Twilio Support:** support@twilio.com
- **ConcreteThings Issues:** Create issue on GitHub

## License

WhatsApp and Twilio are trademarks of their respective owners. This integration follows their Terms of Service and API usage policies.
