"""
Test script for Email Service
Run: python test_email.py
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
# Add parent directory to path
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import EmailService



async def test_email():
    """Test sending order confirmation email"""
    
    print("🧪 Testing Email Service...")
    print("=" * 60)
    
    # Check if email is configured
    email_service = EmailService()
    
    if not email_service.smtp_username or not email_service.smtp_password:
        print("❌ Email not configured!")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD in .env file")
        print("\nSee EMAIL_SETUP.md for instructions")
        return
    
    print(f"📧 SMTP Server: {email_service.smtp_server}:{email_service.smtp_port}")
    print(f"📧 From: {email_service.sender_name} <{email_service.sender_email}>")
    print()
    
    # Get recipient email
    recipient = input("Enter test email address (or press Enter to use sender): ").strip()
    if not recipient:
        recipient = email_service.sender_email
    
    print(f"\n📤 Sending test email to: {recipient}")
    print("-" * 60)
    
    # Sample order data
    test_order_data = {
        "to_email": recipient,
        "order_id": 999,
        "customer_name": "Nguyễn Văn Test",
        "order_date": datetime.now(),
        "total_amount": 1500000,
        "items": [
            {
                "name": "iPhone 15 Pro Max",
                "quantity": 1,
                "price": 1200000,
                "subtotal": 1200000
            },
            {
                "name": "AirPods Pro",
                "quantity": 1,
                "price": 300000,
                "subtotal": 300000
            }
        ],
        "shipping_address": {
            "full_name": "Nguyễn Văn Test",
            "phone": "+84 123 456 789",
            "address_line1": "123 Đường ABC",
            "ward": "Phường 1",
            "district": "Quận 1",
            "city": "TP. Hồ Chí Minh"
        }
    }
    
    # Send email
    try:
        success = email_service.send_order_confirmation_email(**test_order_data)
        
        if success:
            print("✅ Email sent successfully!")
            print(f"\nCheck your inbox at: {recipient}")
            print("Note: Email might be in Spam folder")
        else:
            print("❌ Failed to send email")
            print("Check your SMTP credentials in .env file")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check SMTP_USERNAME and SMTP_PASSWORD in .env")
        print("2. For Gmail: Use App Password, not regular password")
        print("3. Check if 2-Factor Authentication is enabled (required for Gmail)")
        print("4. See EMAIL_SETUP.md for detailed instructions")


if __name__ == "__main__":
    asyncio.run(test_email())
