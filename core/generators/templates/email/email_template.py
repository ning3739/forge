"""Email templategenerategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="email",
    priority=76,
    requires=["EmailServiceGenerator"],
    enabled_when=lambda c: c.get_auth_type() == 'complete',
    description="Generate email templates (app/utils/email_template.py)"
)
class EmailTemplateGenerator(BaseTemplateGenerator):
    """Email templateFile generator"""
    
    def generate(self) -> None:
        """generateemailtemplatefile"""
        # Only generate email template for Complete JWT Auth
        if self.config_reader.get_auth_type() != "complete":
            return
        
        # Create template directory
        template_dir = self.project_path / "static" / "email_template"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate various email templates
        self._create_verification_template()
        self._create_password_reset_template()
        self._create_welcome_template()
        self._create_base_template()
    
    def _create_base_template(self) -> None:
        """Createbaseemailtemplate"""
        content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #8b5cf6;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            margin-bottom: 10px;
        }
        .content {
            margin-bottom: 30px;
        }
        .code-box {
            background-color: #f8f9fa;
            border: 2px dashed #8b5cf6;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .code {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background-color: #8b5cf6;
            color: #ffffff;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }
        .button:hover {
            background-color: #7c3aed;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }
        .warning {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info {
            background-color: #dbeafe;
            border-left: 4px solid #3b82f6;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">{{ app_name }}</div>
        </div>
        
        <div class="content">
            {% block content %}{% endblock %}
        </div>
        
        <div class="footer">
            <p>&copy; {{ year }} {{ app_name }}. All rights reserved.</p>
            <p>This is an automated email, please do not reply.</p>
        </div>
    </div>
</body>
</html>
'''
        
        self.file_ops.create_file(
            file_path="static/email_template/base.html",
            content=content,
            overwrite=True
        )
    
    def _create_verification_template(self) -> None:
        """CreateEmailValidatetemplate"""
        content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #8b5cf6;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            margin-bottom: 10px;
        }
        .content {
            margin-bottom: 30px;
        }
        .code-box {
            background-color: #f8f9fa;
            border: 2px dashed #8b5cf6;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .code {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }
        .warning {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">{{ app_name }}</div>
            <h2>Email Verification</h2>
        </div>
        
        <div class="content">
            <p>Hello {{ recipient }},</p>
            
            <p>Thank you for registering! Please use the verification code below to verify your email address:</p>
            
            <div class="code-box">
                <div class="code">{{ code }}</div>
            </div>
            
            <div class="warning">
                <strong>⚠️ Important:</strong> This code will expire in {{ expiration_minutes }} minutes.
            </div>
            
            <p>If you didn't request this verification, please ignore this email.</p>
        </div>
        
        <div class="footer">
            <p>&copy; {{ year }} {{ app_name }}. All rights reserved.</p>
            <p>This is an automated email, please do not reply.</p>
        </div>
    </div>
</body>
</html>
'''
        
        self.file_ops.create_file(
            file_path="static/email_template/verification.html",
            content=content,
            overwrite=True
        )
    
    def _create_password_reset_template(self) -> None:
        """CreatePasswordresettemplate"""
        content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #8b5cf6;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            margin-bottom: 10px;
        }
        .content {
            margin-bottom: 30px;
        }
        .code-box {
            background-color: #f8f9fa;
            border: 2px dashed #8b5cf6;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .code {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }
        .warning {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info {
            background-color: #dbeafe;
            border-left: 4px solid #3b82f6;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">{{ app_name }}</div>
            <h2>Password Reset Request</h2>
        </div>
        
        <div class="content">
            <p>Hello {{ recipient }},</p>
            
            <p>We received a request to reset your password. Please use the code below to reset your password:</p>
            
            <div class="code-box">
                <div class="code">{{ code }}</div>
            </div>
            
            <div class="warning">
                <strong>⚠️ Important:</strong> This code will expire in {{ expiration_minutes }} minutes.
            </div>
            
            <div class="info">
                <strong>ℹ️ Security Notice:</strong> If you didn't request a password reset, please ignore this email and ensure your account is secure.
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; {{ year }} {{ app_name }}. All rights reserved.</p>
            <p>This is an automated email, please do not reply.</p>
        </div>
    </div>
</body>
</html>
'''
        
        self.file_ops.create_file(
            file_path="static/email_template/password_reset.html",
            content=content,
            overwrite=True
        )
    
    def _create_welcome_template(self) -> None:
        """Create welcome email template"""
        content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #8b5cf6;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #8b5cf6;
            margin-bottom: 10px;
        }
        .content {
            margin-bottom: 30px;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }
        .success {
            background-color: #d1fae5;
            border-left: 4px solid #10b981;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">{{ app_name }}</div>
            <h2>Welcome! 🎉</h2>
        </div>
        
        <div class="content">
            <p>Hello {{ recipient }},</p>
            
            <div class="success">
                <strong>✅ Success!</strong> Your email has been verified successfully.
            </div>
            
            <p>Welcome to {{ app_name }}! We're excited to have you on board.</p>
            
            <p>You can now enjoy all the features of our platform. If you have any questions or need assistance, feel free to reach out to our support team.</p>
            
            <p>Thank you for joining us!</p>
        </div>
        
        <div class="footer">
            <p>&copy; {{ year }} {{ app_name }}. All rights reserved.</p>
            <p>This is an automated email, please do not reply.</p>
        </div>
    </div>
</body>
</html>
'''
        
        self.file_ops.create_file(
            file_path="static/email_template/welcome.html",
            content=content,
            overwrite=True
        )
