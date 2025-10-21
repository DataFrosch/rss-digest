"""
Email Sender Module
Handles email composition and sending via SendGrid.
"""

import logging
from datetime import datetime
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)


class EmailSender:
    """Sends digest emails via SendGrid."""

    def __init__(self, api_key: str, from_email: str = "digest@economist-digest.com"):
        """
        Initialize email sender.

        Args:
            api_key: SendGrid API key
            from_email: Sender email address
        """
        self.client = SendGridAPIClient(api_key)
        self.from_email = from_email
        logger.info("Email sender initialized")

    def send_digest(
        self,
        recipient_email: str,
        digest_html: str,
        date_range: str,
        article_count: int,
        template_path: Optional[str] = None
    ) -> bool:
        """
        Send weekly digest email.

        Args:
            recipient_email: Recipient email address
            digest_html: HTML content of the digest
            date_range: Date range string for subject line
            article_count: Number of articles in digest
            template_path: Optional path to HTML template file

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Load template if provided
            if template_path:
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = f.read()
                    # Replace placeholder with digest content
                    full_html = template.replace('{{DIGEST_CONTENT}}', digest_html)
                    full_html = full_html.replace('{{DATE_RANGE}}', date_range)
                except Exception as e:
                    logger.warning(f"Failed to load template: {str(e)}. Using plain HTML.")
                    full_html = self._create_simple_template(digest_html, date_range)
            else:
                full_html = self._create_simple_template(digest_html, date_range)

            # Create email
            subject = f"Your Economist Weekly Digest: {date_range} ({article_count} articles)"

            message = Mail(
                from_email=Email(self.from_email, "Economist Digest"),
                to_emails=To(recipient_email),
                subject=subject,
                html_content=Content("text/html", full_html)
            )

            # Send email
            logger.info(f"Sending digest to {recipient_email}")
            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully (status: {response.status_code})")
                return True
            else:
                logger.error(f"Failed to send email (status: {response.status_code})")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def send_test_email(self, recipient_email: str) -> bool:
        """
        Send a test email to verify configuration.

        Args:
            recipient_email: Recipient email address

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            test_content = """
            <h1>Test Email from Economist Digest</h1>
            <p>This is a test email to verify your SendGrid configuration.</p>
            <p>If you received this, your email setup is working correctly!</p>
            <p><small>Sent at: {}</small></p>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            message = Mail(
                from_email=Email(self.from_email, "Economist Digest"),
                to_emails=To(recipient_email),
                subject="Test Email - Economist Digest",
                html_content=Content("text/html", test_content)
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Test email sent successfully")
                return True
            else:
                logger.error(f"Failed to send test email")
                return False

        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return False

    def _create_simple_template(self, digest_html: str, date_range: str) -> str:
        """
        Create a simple HTML email template.

        Args:
            digest_html: The digest content
            date_range: Date range string

        Returns:
            Complete HTML email
        """
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Economist Weekly Digest</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #e3120b;
            border-bottom: 3px solid #e3120b;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 20px;
        }}
        a {{
            color: #e3120b;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #666;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗞️ Your Economist Weekly Digest</h1>
        <p><strong>Week of {date_range}</strong></p>

        {digest_html}

        <div class="footer">
            <p>This digest was automatically generated from The Economist RSS feeds.</p>
            <p><small>Generated with ❤️ by your automated digest system</small></p>
        </div>
    </div>
</body>
</html>
"""

    def save_digest_html(self, digest_html: str, date_range: str, filepath: str) -> bool:
        """
        Save digest as HTML file for backup/review.

        Args:
            digest_html: The digest content
            date_range: Date range string
            filepath: Path to save the file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            full_html = self._create_simple_template(digest_html, date_range)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_html)

            logger.info(f"Digest saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving digest HTML: {str(e)}")
            return False


def test_email_sender(api_key: str, recipient: str) -> None:
    """
    Test email sender functionality.

    Args:
        api_key: SendGrid API key
        recipient: Test recipient email address
    """
    sender = EmailSender(api_key)

    print("\n=== Email Sender Test ===")
    print(f"Sending test email to: {recipient}")

    success = sender.send_test_email(recipient)

    if success:
        print("✅ Test email sent successfully!")
        print("Check your inbox to confirm receipt.")
    else:
        print("❌ Failed to send test email. Check logs for details.")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    load_dotenv()

    api_key = os.getenv("SENDGRID_API_KEY")
    recipient = os.getenv("RECIPIENT_EMAIL")

    if api_key and recipient:
        test_email_sender(api_key, recipient)
    else:
        print("Please set SENDGRID_API_KEY and RECIPIENT_EMAIL in .env file")
