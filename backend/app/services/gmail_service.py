import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict, Any, Optional
import logging

from app.utils.resume_parser import extract_text_from_file

logger = logging.getLogger(__name__)

def send_email_via_gmail(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
    gmail_user: Optional[str] = None,
    gmail_password: Optional[str] = None
) -> bool:
    """
    Sends an email via Gmail SMTP with optional file attachments (e.g. Offer Letter PDF).
    """
    user = gmail_user or os.getenv("GMAIL_USER")
    password = gmail_password or os.getenv("GMAIL_APP_PASSWORD")

    if not user or not password or password == "your_gmail_app_password":
        logger.warning("Gmail credentials not fully configured in environment variables.")
        return False

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email successfully sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def fetch_candidate_resumes_from_gmail(
    gmail_user: Optional[str] = None,
    gmail_password: Optional[str] = None,
    max_emails: int = 10
) -> List[Dict[str, Any]]:
    """
    Fetches unread/recent candidate emails with resume attachments from Gmail inbox via IMAP.
    Extracts candidate name, email, subject, resume filename, and resume text.
    """
    user = gmail_user or os.getenv("GMAIL_USER")
    password = gmail_password or os.getenv("GMAIL_APP_PASSWORD")

    if not user or not password or password == "your_gmail_app_password":
        logger.warning("Gmail credentials not fully configured.")
        return []

    results = []
    temp_dir = os.path.join(os.getcwd(), "scratch_resumes")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(user, password)
        mail.select('inbox')

        # Search for unseen emails
        status, response = mail.search(None, 'UNSEEN')
        email_ids = response[0].split()

        if not email_ids:
            # Fallback to ALL emails if no unseen found
            status, response = mail.search(None, 'ALL')
            email_ids = response[0].split()[-max_emails:]
        else:
            email_ids = email_ids[-max_emails:]

        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    candidate_email = email.utils.parseaddr(msg['From'])[1]
                    raw_name = email.utils.parseaddr(msg['From'])[0]
                    candidate_name = raw_name if raw_name else candidate_email.split('@')[0].capitalize()
                    subject = msg['Subject'] or 'Application for Software Developer'

                    resume_text = ""
                    resume_filename = None

                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        
                        filename = part.get_filename()
                        if filename:
                            ext = os.path.splitext(filename)[1].lower()
                            if ext in ['.pdf', '.docx', '.txt']:
                                file_path = os.path.join(temp_dir, f"{candidate_name}_{filename}")
                                with open(file_path, 'wb') as f:
                                    f.write(part.get_payload(decode=True))
                                
                                try:
                                    resume_text = extract_text_from_file(file_path)
                                    resume_filename = filename
                                except Exception as err:
                                    logger.error(f"Error parsing resume file {file_path}: {err}")

                    if not resume_text:
                        # Extract plain text body if no attachment
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                resume_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')

                    if candidate_email and resume_text:
                        results.append({
                            "candidate_name": candidate_name,
                            "candidate_email": candidate_email,
                            "subject": subject,
                            "resume_filename": resume_filename or "resume.txt",
                            "resume_text": resume_text
                        })

        mail.logout()
    except Exception as e:
        logger.error(f"Failed to fetch resumes from Gmail IMAP: {str(e)}")

    return results
