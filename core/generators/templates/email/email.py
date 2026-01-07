"""Email servicegenerategenerator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="email",
    priority=75,
    requires=["ConfigEmailGenerator"],
    enabled_when=lambda c: c.get_auth_type() == 'complete',
    description="Generate email service (app/utils/email.py)"
)
class EmailServiceGenerator(BaseTemplateGenerator):
    """Email serviceFile generator"""
    
    def generate(self) -> None:
        """generate email.py file"""
        # Only generate email service for Complete JWT Auth
        if self.config_reader.get_auth_type() != "complete":
            return
        
        imports = [
            "import asyncio",
            "import smtplib",
            "import ssl",
            "from abc import ABC, abstractmethod",
            "from asyncio import TimeoutError as AsyncioTimeoutError",
            "from datetime import datetime",
            "from email.mime.multipart import MIMEMultipart",
            "from email.mime.text import MIMEText",
            "from pathlib import Path",
            "from typing import Dict, List, Optional, Union, Any",
            "",
            "from fastapi import HTTPException",
            "from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape",
            "",
            "from app.core.config.settings import settings",
            "from app.core.logger import logger_manager",
        ]
        
        content = '''class EmailBackend(ABC):
    """Abstract base class for email backends."""
    
    @abstractmethod
    async def send_email(self, message: MIMEMultipart) -> None:
        """Send email message asynchronously."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test the email backend connection."""
        pass


class EmailTemplateLoader:
    """Email template loader using Jinja2 with caching."""
    
    def __init__(self, template_dir: Union[str, Path] = "static/email_template"):
        self.template_dir = Path(template_dir)
        self._template_cache: Dict[str, Any] = {}
        
        # Create directory if not exists
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render template using Jinja2 with caching."""
        try:
            if template_name not in self._template_cache:
                template = self.env.get_template(f"{template_name}.html")
                self._template_cache[template_name] = template
            else:
                template = self._template_cache[template_name]
            
            return template.render(**kwargs)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in '{self.template_dir}'"
            )
        except Exception as e:
            raise ValueError(f"Failed to render template '{template_name}': {str(e)}")
    
    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        return (self.template_dir / f"{template_name}.html").exists()
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        return [f.stem for f in self.template_dir.glob("*.html")]
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self._template_cache.clear()


class SMTPEmailBackend(EmailBackend):
    """SMTP email backend implementation."""
    
    def __init__(self, email_settings):
        self.email_settings = email_settings
        self.logger = logger_manager.get_logger(__name__)
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context based on configuration."""
        ssl_context = ssl.create_default_context()
        
        cert_reqs = getattr(
            self.email_settings, "EMAIL_SSL_CERT_REQS", "required"
        )
        
        if cert_reqs == "required":
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        elif cert_reqs == "optional":
            ssl_context.verify_mode = ssl.CERT_OPTIONAL
        else:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        return ssl_context
    
    def _create_smtp_server(self, ssl_context: ssl.SSLContext) -> smtplib.SMTP:
        """Create and configure SMTP server."""
        use_ssl = getattr(self.email_settings, "EMAIL_USE_SSL", False)
        use_tls = getattr(self.email_settings, "EMAIL_USE_TLS", True)
        timeout = getattr(self.email_settings, "EMAIL_TIMEOUT", 30)
        
        if use_ssl:
            server = smtplib.SMTP_SSL(
                self.email_settings.EMAIL_HOST,
                self.email_settings.EMAIL_PORT,
                timeout=timeout,
                context=ssl_context,
            )
        else:
            server = smtplib.SMTP(
                self.email_settings.EMAIL_HOST,
                self.email_settings.EMAIL_PORT,
                timeout=timeout,
            )
            if use_tls:
                server.starttls(context=ssl_context)
        
        return server
    
    async def send_email(self, message: MIMEMultipart) -> None:
        """Send email using SMTP asynchronously."""
        server = None
        try:
            ssl_context = self._create_ssl_context()
            server = self._create_smtp_server(ssl_context)
            
            # Enable debug mode in development
            if hasattr(settings, "debug") and settings.debug:
                server.set_debuglevel(1)
            
            server.login(
                self.email_settings.EMAIL_HOST_USER,
                self.email_settings.EMAIL_HOST_PASSWORD.get_secret_value(),
            )
            
            server.sendmail(
                self.email_settings.EMAIL_HOST_USER,
                message["To"],
                message.as_string()
            )
            
            self.logger.info(f"Email sent successfully to {message['To']}")
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {e}")
            raise HTTPException(
                status_code=400,
                detail="Email authentication failed"
            )
        except smtplib.SMTPConnectError as e:
            self.logger.error(f"SMTP connection failed: {e}")
            raise HTTPException(
                status_code=400,
                detail="Email connection failed"
            )
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            raise HTTPException(
                status_code=400,
                detail="Email sending failed"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {e}")
            raise HTTPException(
                status_code=400,
                detail="Email sending failed"
            )
        finally:
            if server:
                try:
                    server.quit()
                except Exception as e:
                    self.logger.warning(f"Error closing SMTP connection: {e}")
    
    def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            ssl_context = self._create_ssl_context()
            server = self._create_smtp_server(ssl_context)
            server.login(
                self.email_settings.EMAIL_HOST_USER,
                self.email_settings.EMAIL_HOST_PASSWORD.get_secret_value(),
            )
            server.quit()
            return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False


class EmailMessage:
    """Email message builder class."""
    
    def __init__(self, subject: str, recipient: str, sender: str):
        self.subject = subject
        self.recipient = recipient
        self.sender = sender
        self.html_content: Optional[str] = None
        self.text_content: Optional[str] = None
        self.attachments: List[Dict[str, Any]] = []
    
    def set_html_content(self, content: str) -> "EmailMessage":
        """Set HTML content for the email."""
        self.html_content = content
        return self
    
    def set_text_content(self, content: str) -> "EmailMessage":
        """Set text content for the email."""
        self.text_content = content
        return self
    
    def add_attachment(
        self,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> "EmailMessage":
        """Add attachment to the email."""
        self.attachments.append({
            "filename": filename,
            "content": content,
            "content_type": content_type
        })
        return self
    
    def build(self) -> MIMEMultipart:
        """Build MIMEMultipart message."""
        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg["Subject"] = self.subject
        
        if self.text_content:
            msg.attach(MIMEText(self.text_content, "plain"))
        
        if self.html_content:
            msg.attach(MIMEText(self.html_content, "html"))
        
        # Add attachments if any
        for attachment in self.attachments:
            from email.mime.base import MIMEBase
            from email import encoders
            from email.header import Header
            
            part = MIMEBase(*attachment["content_type"].split("/", 1))
            part.set_payload(attachment["content"])
            encoders.encode_base64(part)
            
            # Properly encode filename to handle non-ASCII characters
            filename = attachment["filename"]
            encoded_filename = Header(filename, "utf-8").encode()
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=encoded_filename
            )
            msg.attach(part)
        
        return msg


class EmailService:
    """Main email service class with comprehensive features."""
    
    def __init__(
        self,
        backend: EmailBackend,
        config_settings,
        template_loader: Optional[EmailTemplateLoader] = None,
    ):
        self.backend = backend
        self.settings = config_settings
        self.template_loader = template_loader or EmailTemplateLoader()
        self.logger = logger_manager.get_logger(__name__)
    
    def _prepare_template_variables(
        self,
        recipient: str,
        code: str = "",
        **extra_vars
    ) -> Dict[str, str]:
        """Prepare variables for template rendering."""
        base_vars = {
            "recipient": recipient,
            "code": code,
            "expiration_minutes": str(
                getattr(self.settings.email, "EMAIL_EXPIRATION", 3600) // 60
            ),
            "year": str(datetime.now().year),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "current_time": datetime.now().strftime("%H:%M:%S"),
            "app_name": getattr(self.settings.app, "APP_NAME", "Our App"),
        }
        
        # Merge with any extra variables provided
        base_vars.update(extra_vars)
        return base_vars
    
    def _create_email_message(
        self,
        subject: str,
        recipient: str,
        template_name: str,
        template_vars: Dict[str, str],
    ) -> EmailMessage:
        """Create email message with rendered template."""
        try:
            # Check if template exists
            if not self.template_loader.template_exists(template_name):
                raise HTTPException(
                    status_code=404,
                    detail="Email template not found"
                )
            
            html_content = self.template_loader.render_template(
                template_name,
                **template_vars
            )
        except (FileNotFoundError, ValueError) as e:
            self.logger.error(f"Error rendering template: {e}")
            raise HTTPException(
                status_code=400,
                detail="Email template error"
            )
        
        return EmailMessage(
            subject,
            recipient,
            self.settings.email.EMAIL_HOST_USER
        ).set_html_content(html_content)
    
    async def send_email(
        self,
        subject: str,
        recipient: str,
        template: str,
        code: str = "",
        retries: int = 3,
        retry_delay: int = 2,
        timeout: Optional[int] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        **template_vars,
    ) -> None:
        """Send email with retry mechanism and timeout."""
        if timeout is None:
            timeout = getattr(self.settings.email, "EMAIL_TIMEOUT", 30)
        
        # Validate inputs
        if not recipient or "@" not in recipient:
            raise ValueError("Invalid email address")
        
        if not subject.strip():
            raise ValueError("Email subject cannot be empty")
        
        # Prepare email variables
        template_variables = self._prepare_template_variables(
            recipient,
            code,
            **template_vars
        )
        
        email_message = self._create_email_message(
            subject,
            recipient,
            template,
            template_variables
        )
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                email_message.add_attachment(
                    filename=attachment["filename"],
                    content=attachment["content"],
                    content_type=attachment.get(
                        "content_type",
                        "application/octet-stream"
                    ),
                )
        
        mime_message = email_message.build()
        
        # Retry mechanism with exponential backoff
        last_exception = None
        for attempt in range(retries):
            try:
                await asyncio.wait_for(
                    self.backend.send_email(mime_message),
                    timeout=timeout
                )
                self.logger.info(
                    f"Email sent successfully to {recipient} "
                    f"using template '{template}'"
                )
                return
            except AsyncioTimeoutError as e:
                last_exception = e
                self.logger.warning(
                    f"Timeout error while sending email to {recipient}, "
                    f"attempt {attempt + 1}/{retries}"
                )
            except HTTPException as e:
                # Re-raise HTTP exceptions immediately
                raise e
            except Exception as e:
                last_exception = e
                self.logger.error(
                    f"Error sending email to {recipient}, "
                    f"attempt {attempt + 1}/{retries}: {e}"
                )
            
            if attempt < retries - 1:
                # Exponential backoff
                delay = retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)
        
        self.logger.error(
            f"Failed to send email to {recipient} after {retries} attempts"
        )
        raise HTTPException(
            status_code=400,
            detail="Email sending failed"
        )
    
    async def send_bulk_email(
        self,
        subject: str,
        recipients: List[str],
        template: str,
        code: str = "",
        batch_size: int = 10,
        **template_vars,
    ) -> Dict[str, Any]:
        """Send bulk emails with batching support."""
        results = {
            "success": [],
            "failed": [],
            "total": len(recipients)
        }
        
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            tasks = []
            
            for recipient in batch:
                task = self.send_email(
                    subject=subject,
                    recipient=recipient,
                    template=template,
                    code=code,
                    **template_vars,
                )
                tasks.append(task)
            
            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for recipient, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results["failed"].append({
                        "recipient": recipient,
                        "error": str(result)
                    })
                else:
                    results["success"].append(recipient)
        
        return results
    
    def test_connection(self) -> bool:
        """Test email backend connection."""
        return self.backend.test_connection()
    
    def get_available_templates(self) -> List[str]:
        """Get list of available email templates."""
        return self.template_loader.list_templates()
    
    def clear_template_cache(self) -> None:
        """Clear template cache."""
        self.template_loader.clear_cache()


# Global email service instance
_email_service_instance = None


def get_email_service() -> EmailService:
    """Get the global email service instance."""
    global _email_service_instance
    
    if _email_service_instance is None:
        from app.core.config.settings import settings
        
        _email_service_instance = EmailService(
            backend=SMTPEmailBackend(settings.email),
            config_settings=settings,
            template_loader=EmailTemplateLoader("static/email_template"),
        )
    
    return _email_service_instance


# For backward compatibility - create a property that accesses the service lazily
class EmailServiceProxy:
    """Proxy class for lazy loading of email service."""
    
    def __getattr__(self, name):
        """Delegate all attribute access to the actual email service."""
        service = get_email_service()
        return getattr(service, name)


email_service = EmailServiceProxy()
'''
        
        self.file_ops.create_python_file(
            file_path="app/utils/email.py",
            docstring="Email service for sending emails with template support",
            imports=imports,
            content=content,
            overwrite=True
        )
