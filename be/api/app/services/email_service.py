import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from datetime import datetime


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SENDER_EMAIL", self.smtp_username)
        self.sender_name = os.getenv("SENDER_NAME", "E-Commerce Store")
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            plain_content: Plain text fallback (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Add plain text version
            if plain_content:
                part1 = MIMEText(plain_content, "plain")
                message.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_order_confirmation_email(
        self,
        to_email: str,
        order_id: int,
        customer_name: str,
        order_date: datetime,
        total_amount: float,
        items: list,
        shipping_address: dict
    ) -> bool:
        """
        Send order confirmation email after successful payment
        
        Args:
            to_email: Customer email
            order_id: Order ID
            customer_name: Customer full name
            order_date: Order creation date
            total_amount: Total order amount
            items: List of order items
            shipping_address: Shipping address dict
        
        Returns:
            True if sent successfully
        """
        subject = f"Xác nhận đơn hàng #{order_id} - Thanh toán thành công"
        
        # Generate items HTML
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.get('name', 'N/A')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 0)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{item.get('price', 0):,.0f} ₫</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{item.get('subtotal', 0):,.0f} ₫</td>
            </tr>
            """
        
        # Format shipping address
        address_html = f"""
        {shipping_address.get('full_name', '')}<br>
        {shipping_address.get('phone', '')}<br>
        {shipping_address.get('address_line1', '')}<br>
        {shipping_address.get('ward', '')}, {shipping_address.get('district', '')}, {shipping_address.get('city', '')}
        """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="margin: 0; color: #ffffff; font-size: 28px;">✅ Thanh toán thành công!</h1>
                    <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px;">Cảm ơn bạn đã mua hàng tại cửa hàng chúng tôi</p>
                </div>
                
                <!-- Body -->
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333;">Xin chào <strong>{customer_name}</strong>,</p>
                    <p style="font-size: 14px; color: #666; line-height: 1.6;">
                        Đơn hàng của bạn đã được thanh toán thành công và đang được xử lý. 
                        Chúng tôi sẽ giao hàng trong thời gian sớm nhất.
                    </p>
                    
                    <!-- Order Info -->
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin: 0 0 15px 0; color: #333; font-size: 18px;">Thông tin đơn hàng</h3>
                        <table style="width: 100%; font-size: 14px;">
                            <tr>
                                <td style="padding: 5px 0; color: #666;">Mã đơn hàng:</td>
                                <td style="padding: 5px 0; text-align: right; color: #333; font-weight: bold;">#{order_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 5px 0; color: #666;">Ngày đặt hàng:</td>
                                <td style="padding: 5px 0; text-align: right; color: #333;">{order_date.strftime('%d/%m/%Y %H:%M')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 5px 0; color: #666;">Tổng tiền:</td>
                                <td style="padding: 5px 0; text-align: right; color: #667eea; font-weight: bold; font-size: 18px;">{total_amount:,.0f} ₫</td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- Order Items -->
                    <h3 style="margin: 25px 0 15px 0; color: #333; font-size: 18px;">Chi tiết đơn hàng</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <thead>
                            <tr style="background-color: #f8f9fa;">
                                <th style="padding: 10px; text-align: left; color: #666;">Sản phẩm</th>
                                <th style="padding: 10px; text-align: center; color: #666;">SL</th>
                                <th style="padding: 10px; text-align: right; color: #666;">Đơn giá</th>
                                <th style="padding: 10px; text-align: right; color: #666;">Thành tiền</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <!-- Shipping Address -->
                    <h3 style="margin: 25px 0 15px 0; color: #333; font-size: 18px;">Địa chỉ giao hàng</h3>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; font-size: 14px; color: #666; line-height: 1.8;">
                        {address_html}
                    </div>
                    
                    <!-- Footer Note -->
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="font-size: 14px; color: #666; margin: 0 0 10px 0;">
                            📦 Chúng tôi sẽ gửi thông báo khi đơn hàng được giao cho đơn vị vận chuyển.
                        </p>
                        <p style="font-size: 14px; color: #666; margin: 0;">
                            💬 Nếu có bất kỳ thắc mắc nào, vui lòng liên hệ với chúng tôi qua email hoặc hotline.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #999;">
                    <p style="margin: 0 0 5px 0;">© 2025 E-Commerce Store. All rights reserved.</p>
                    <p style="margin: 0;">Email này được gửi tự động, vui lòng không trả lời.</p>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
        Xác nhận đơn hàng #{order_id}
        
        Xin chào {customer_name},
        
        Đơn hàng của bạn đã được thanh toán thành công!
        
        Thông tin đơn hàng:
        - Mã đơn hàng: #{order_id}
        - Ngày đặt: {order_date.strftime('%d/%m/%Y %H:%M')}
        - Tổng tiền: {total_amount:,.0f} ₫
        
        Địa chỉ giao hàng:
        {shipping_address.get('full_name', '')}
        {shipping_address.get('phone', '')}
        {shipping_address.get('address_line1', '')}
        
        Cảm ơn bạn đã mua hàng!
        """
        
        return self.send_email(to_email, subject, html_content, plain_content)
