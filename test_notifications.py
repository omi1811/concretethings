"""
Test WhatsApp notification system.
Run: python test_notifications.py
"""
import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from notifications import (
    get_whatsapp_service,
    format_cube_test_failure,
    format_batch_rejection,
    format_ncr_generated,
    format_batch_delivered
)


def test_service_initialization():
    """Test WhatsApp service initialization."""
    print("=" * 70)
    print("TEST 1: Service Initialization")
    print("=" * 70)
    
    service = get_whatsapp_service()
    
    print(f"Service enabled: {service.enabled}")
    print(f"Twilio available: {service.client is not None}")
    
    if not service.enabled:
        print("\n⚠️  WhatsApp is DISABLED")
        print("To enable, set in .env:")
        print("  TWILIO_ACCOUNT_SID=your_account_sid")
        print("  TWILIO_AUTH_TOKEN=your_auth_token")
        print("  WHATSAPP_ENABLED=true")
    else:
        print("\n✅ WhatsApp is ENABLED and ready")
    
    print()


def test_message_formatting():
    """Test message formatting templates."""
    print("=" * 70)
    print("TEST 2: Message Formatting")
    print("=" * 70)
    
    # Test 1: Cube test failure
    print("\n--- Cube Test Failure Message ---\n")
    
    test_data = {
        "project_name": "ABC Tower - Phase 1",
        "batch_number": "BATCH-2024-001",
        "vendor_name": "XYZ Concrete Pvt Ltd",
        "test_age_days": 28,
        "required_strength_mpa": 25.0,
        "average_strength_mpa": 22.5,
        "strength_ratio_percent": 90.0,
        "cube_1_strength_mpa": 23.5,
        "cube_2_strength_mpa": 22.0,
        "cube_3_strength_mpa": 22.0,
        "ncr_number": "NCR-2024-001",
        "test_id": 1,
        "app_url": "http://localhost:8000"
    }
    
    message = format_cube_test_failure(test_data)
    print(message)
    
    # Test 2: Batch rejection
    print("\n--- Batch Rejection Message ---\n")
    
    batch_data = {
        "project_name": "ABC Tower - Phase 1",
        "batch_number": "BATCH-2024-002",
        "vendor_name": "XYZ Concrete Pvt Ltd",
        "delivery_date": "2024-01-15",
        "rejection_reason": "Slump test failed. Measured: 180mm, Required: 100±25mm",
        "rejected_by_name": "John Doe (Quality Manager)",
        "batch_id": 2,
        "app_url": "http://localhost:8000"
    }
    
    message = format_batch_rejection(batch_data)
    print(message)
    
    # Test 3: NCR generated
    print("\n--- NCR Generated Message ---\n")
    
    ncr_data = {
        "project_name": "ABC Tower - Phase 1",
        "ncr_number": "NCR-2024-003",
        "issue_description": "Concrete strength below required specification. All three cube samples failed to meet minimum strength criteria.",
        "batch_number": "BATCH-2024-001",
        "test_id": 1,
        "generated_by_name": "Jane Smith (Quality Manager)",
        "app_url": "http://localhost:8000"
    }
    
    message = format_ncr_generated(ncr_data)
    print(message)
    
    # Test 4: Batch delivered
    print("\n--- Batch Delivered Message ---\n")
    
    delivery_data = {
        "project_name": "ABC Tower - Phase 1",
        "batch_number": "BATCH-2024-003",
        "vendor_name": "XYZ Concrete Pvt Ltd",
        "quantity_ordered": 6.0,
        "location": "Building A, Floor 3, Grid B2-C3",
        "delivery_date": "2024-01-15 14:30"
    }
    
    message = format_batch_delivered(delivery_data)
    print(message)
    
    print()


def test_send_message():
    """Test sending actual WhatsApp message (if enabled)."""
    print("=" * 70)
    print("TEST 3: Send Test Message")
    print("=" * 70)
    
    service = get_whatsapp_service()
    
    if not service.enabled:
        print("\n⚠️  WhatsApp disabled. Skipping send test.")
        print("Enable WhatsApp in .env to test sending.")
        print()
        return
    
    # Get test phone number from environment or user input
    test_phone = os.getenv("TEST_WHATSAPP_PHONE")
    
    if not test_phone:
        print("\nEnter test phone number (international format, e.g., +919876543210)")
        print("Or set TEST_WHATSAPP_PHONE in .env")
        test_phone = input("Phone number (or press Enter to skip): ").strip()
    
    if not test_phone:
        print("\n⚠️  No phone number provided. Skipping send test.")
        print()
        return
    
    # Validate phone format
    if not test_phone.startswith("+"):
        print(f"\n❌ Invalid phone format: {test_phone}")
        print("Phone must be in international format: +<country><number>")
        print("Example: +919876543210 (India), +12125551234 (USA)")
        print()
        return
    
    print(f"\nSending test message to: {test_phone}")
    print("Note: User must have joined Twilio WhatsApp sandbox first!")
    print()
    
    # Send test message
    test_message = """🧪 *TEST MESSAGE* 🧪

This is a test notification from ConcreteThings QMS.

If you received this message, the WhatsApp integration is working correctly! ✅

---
_Automated test from ConcreteThings QMS_"""
    
    result = service.send_message(test_phone, test_message)
    
    if result:
        print("✅ Message sent successfully!")
        print("Check WhatsApp to confirm delivery.")
    else:
        print("❌ Message failed to send.")
        print("Check logs for error details.")
    
    print()


def test_multiple_recipients():
    """Test sending to multiple recipients."""
    print("=" * 70)
    print("TEST 4: Multiple Recipients")
    print("=" * 70)
    
    service = get_whatsapp_service()
    
    if not service.enabled:
        print("\n⚠️  WhatsApp disabled. Skipping multi-recipient test.")
        print()
        return
    
    # Example recipients (would come from database in real app)
    recipients = [
        "+919876543210",  # Quality Manager
        "+919876543211",  # RMC Vendor
        "+919876543212",  # Project Manager
    ]
    
    print(f"\nWould send to {len(recipients)} recipients:")
    for i, phone in enumerate(recipients, 1):
        print(f"  {i}. {phone}")
    
    # Create test failure message
    test_data = {
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
    
    message = format_cube_test_failure(test_data)
    
    # Test without actually sending
    print("\nMessage preview:")
    print("-" * 70)
    print(message[:200] + "...")
    print("-" * 70)
    
    print("\n✅ Multi-recipient test complete (no messages sent)")
    print()


def test_error_handling():
    """Test error handling scenarios."""
    print("=" * 70)
    print("TEST 5: Error Handling")
    print("=" * 70)
    
    service = get_whatsapp_service()
    
    # Test 1: Invalid phone format
    print("\n--- Test Invalid Phone Format ---")
    invalid_phones = [
        "9876543210",  # Missing country code
        "+91 98765 43210",  # Spaces
        "+91-9876543210",  # Dash
        "invalid",  # Not a number
    ]
    
    for phone in invalid_phones:
        print(f"Testing: {phone}")
        result = service.send_message(phone, "Test")
        print(f"  Result: {'❌ Failed (expected)' if not result else '⚠️  Unexpected success'}")
    
    # Test 2: Empty message
    print("\n--- Test Empty Message ---")
    result = service.send_message("+919876543210", "")
    print(f"Empty message result: {'❌ Failed (expected)' if not result else '⚠️  Unexpected success'}")
    
    # Test 3: Service disabled
    print("\n--- Test Service Disabled ---")
    original_enabled = service.enabled
    service.enabled = False
    result = service.send_message("+919876543210", "Test")
    print(f"Disabled service result: {'❌ Not sent (expected)' if not result else '⚠️  Unexpected success'}")
    service.enabled = original_enabled
    
    print("\n✅ Error handling tests complete")
    print()


def print_setup_guide():
    """Print quick setup guide."""
    print("=" * 70)
    print("QUICK SETUP GUIDE")
    print("=" * 70)
    print("""
1. Sign up for Twilio: https://www.twilio.com/try-twilio

2. Get your credentials:
   - Account SID (starts with AC...)
   - Auth Token

3. Activate WhatsApp Sandbox:
   - Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Note the sandbox number: +1 (415) 523-8886
   - Note your join code: join <word>-<word>

4. Configure .env file:
   
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_ENABLED=true
   APP_URL=http://localhost:8000
   TEST_WHATSAPP_PHONE=+919876543210

5. Opt-in to sandbox:
   - Open WhatsApp
   - Send to: +1 (415) 523-8886
   - Message: join <your-join-code>

6. Test:
   python test_notifications.py

For full documentation, see: WHATSAPP_SETUP.md
""")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "WHATSAPP NOTIFICATION SYSTEM TEST" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Check if .env exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print("⚠️  Warning: .env file not found")
        print("Create .env file with Twilio credentials to enable WhatsApp\n")
    
    # Run tests
    test_service_initialization()
    test_message_formatting()
    test_send_message()
    test_multiple_recipients()
    test_error_handling()
    
    # Print summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    service = get_whatsapp_service()
    
    if service.enabled:
        print("\n✅ WhatsApp is ENABLED and ready to send notifications")
        print("   All message templates are working correctly")
    else:
        print("\n⚠️  WhatsApp is DISABLED")
        print("   Message templates are working, but no messages will be sent")
        print("   Follow the setup guide to enable WhatsApp notifications")
    
    print("\nFor full setup instructions, run:")
    print("  python -c \"from server.notifications import get_setup_instructions; print(get_setup_instructions())\"")
    
    print("\nOr read: WHATSAPP_SETUP.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
