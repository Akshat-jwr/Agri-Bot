import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

class EmailService:
    @staticmethod
    async def send_verification_email(email: str, verification_token: str):
        """Send verification email to user"""
        try:
            # Create verification URL
            verification_url = f"http://localhost:8000/api/v1/auth/verify/{verification_token}"
            
            # Email content
            subject = "🌾 Verify Your Agricultural Intelligence Account"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2E7D32;">🌾 Welcome to Agricultural Intelligence!</h2>
                    
                    <p>Thank you for registering with our Agricultural Intelligence platform.</p>
                    
                    <p>To complete your registration and start getting personalized farming advice, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                           ✅ Verify My Email
                        </a>
                    </div>
                    
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="background-color: #f5f5f5; padding: 10px; border-radius: 3px; word-break: break-all;">
                        {verification_url}
                    </p>
                    
                    <p><strong>What's next?</strong></p>
                    <ul>
                        <li>✅ Verify your email (this step)</li>
                        <li>🔐 Login to your account</li>
                        <li>🌾 Start asking agricultural questions</li>
                        <li>📍 Set your farming location for personalized advice</li>
                    </ul>
                    
                    <p>If you didn't create this account, please ignore this email.</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #666;">
                        This email was sent by Agricultural Intelligence API<br>
                        Need help? Contact support at support@farmapi.com
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_body = f"""
            Welcome to Agricultural Intelligence!
            
            Please verify your email address by visiting this link:
            {verification_url}
            
            If you didn't create this account, please ignore this email.
            """
            
            # Send email
            if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
                await EmailService._send_email(email, subject, html_body, text_body)
                logging.info(f"📧 Verification email dispatched to {email}")
            else:
                # Development mode - just log the verification URL
                logging.warning("[email] SMTP credentials not set; running in dev logging mode")
                logging.info(f"[email.dev] To: {email} :: {verification_url}")
                print(f"\n--- DEV VERIFICATION EMAIL ---\nTo: {email}\nLink: {verification_url}\n------------------------------\n")
                
        except Exception as e:
            logging.error(f"❌ Failed to send verification email to {email}: {e}")
            # Don't raise exception - registration should still succeed
    
    @staticmethod
    async def _send_email(to_email: str, subject: str, html_body: str, text_body: str):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_USERNAME
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            smtp_server = str(settings.SMTP_SERVER).strip('"').strip()
            smtp_port = int(settings.SMTP_PORT)
            username = str(settings.EMAIL_USERNAME).strip('"').strip()
            password = str(settings.EMAIL_PASSWORD).strip('"').strip()

            server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logging.error(f"SMTP error: {e}")
            raise
