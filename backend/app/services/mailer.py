"""Email delivery service using SendGrid or Resend."""

import logging
from datetime import datetime
from typing import Any

from fastapi import HTTPException

from app.config import get_settings

logger = logging.getLogger(__name__)


def build_html_email(summary: str, data: dict[str, Any]) -> str:
    """Build a branded HTML email template."""
    # Convert markdown to basic HTML (simple conversion)
    html_body = summary.replace("\n", "<br>")
    html_body = html_body.replace("# ", "<h1>").replace("## ", "<h2>").replace("### ", "<h3>")
    html_body = html_body.replace("**", "<strong>").replace("**", "</strong>")
    html_body = html_body.replace("- ", "• ")
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Insight Report</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
        <!-- Header -->
        <tr>
            <td style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">
                    🐰 Rabbitt AI
                </h1>
                <p style="color: #a0a0a0; margin: 10px 0 0 0; font-size: 14px;">
                    Sales Insight Automator
                </p>
            </td>
        </tr>
        
        <!-- Title -->
        <tr>
            <td style="padding: 30px 30px 20px 30px; text-align: center; border-bottom: 1px solid #eee;">
                <h2 style="color: #1a1a2e; margin: 0; font-size: 22px;">
                    📊 Q1 2026 Sales Insight Report
                </h2>
                <p style="color: #666; margin: 10px 0 0 0; font-size: 14px;">
                    Generated: {timestamp}
                </p>
            </td>
        </tr>
        
        <!-- Content -->
        <tr>
            <td style="padding: 30px; color: #333; font-size: 15px; line-height: 1.6;">
                {html_body}
            </td>
        </tr>
        
        <!-- Data Summary -->
        <tr>
            <td style="padding: 0 30px 30px 30px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f8f9fa; border-radius: 8px; padding: 20px;">
                    <tr>
                        <td style="padding: 15px; text-align: center;">
                            <p style="color: #666; margin: 0; font-size: 12px;">DATA POINTS</p>
                            <p style="color: #1a1a2e; margin: 5px 0 0 0; font-size: 24px; font-weight: 700;">
                                {data.get('shape', [0])[0]:,}
                            </p>
                        </td>
                        <td style="padding: 15px; text-align: center; border-left: 1px solid #ddd;">
                            <p style="color: #666; margin: 0; font-size: 12px;">COLUMNS</p>
                            <p style="color: #1a1a2e; margin: 5px 0 0 0; font-size: 24px; font-weight: 700;">
                                {len(data.get('columns', []))}
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background-color: #1a1a2e; padding: 25px; text-align: center;">
                <p style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px;">
                    Powered by <strong>Rabbitt AI Insights Engine</strong>
                </p>
                <p style="color: #888; margin: 0; font-size: 12px;">
                    This report was automatically generated from your uploaded data.
                </p>
                <p style="color: #666; margin: 15px 0 0 0; font-size: 11px;">
                    © 2026 Rabbitt AI • All rights reserved
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html_template


async def send_with_sendgrid(
    recipient: str, subject: str, html_content: str
) -> bool:
    """Send email using SendGrid."""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    settings = get_settings()
    
    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=recipient,
        subject=subject,
        html_content=html_content,
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"SendGrid response status: {response.status_code}")
        return response.status_code in (200, 201, 202)
    except Exception as e:
        logger.error(f"SendGrid error: {e}")
        raise


async def send_with_resend(
    recipient: str, subject: str, html_content: str
) -> bool:
    """Send email using Resend."""
    import resend
    
    settings = get_settings()
    resend.api_key = settings.RESEND_API_KEY
    
    try:
        response = resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [recipient],
            "subject": subject,
            "html": html_content,
        })
        logger.info(f"Resend response: {response}")
        return bool(response.get("id"))
    except Exception as e:
        logger.error(f"Resend error: {e}")
        raise


async def send_summary(
    recipient: str, summary: str, data: dict[str, Any]
) -> bool:
    """
    Send the generated summary via email.
    
    Args:
        recipient: Email address to send the report to
        summary: Markdown-formatted summary content
        data: Parsed data dictionary for additional context
        
    Returns:
        True if email was sent successfully
        
    Raises:
        HTTPException: 500 if email delivery fails
    """
    settings = get_settings()
    
    # Build email content
    subject = "📊 Q1 2026 Sales Insight Report — Generated by Rabbitt AI"
    html_content = build_html_email(summary, data)
    
    # Log safely (only domain, never full email)
    email_domain = recipient.split("@")[1] if "@" in recipient else "unknown"
    logger.info(f"Sending email to domain: {email_domain}")
    
    try:
        if settings.EMAIL_PROVIDER == "sendgrid":
            success = await send_with_sendgrid(recipient, subject, html_content)
        else:  # resend
            success = await send_with_resend(recipient, subject, html_content)
        
        if success:
            logger.info(f"Email dispatched to domain: {email_domain}")
            return True
        else:
            raise HTTPException(
                status_code=500,
                detail="Email delivery failed. Please try again.",
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Email delivery failed")
        raise HTTPException(
            status_code=500,
            detail=f"Email delivery failed: {str(e)}",
        )
