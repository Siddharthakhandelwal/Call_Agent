import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication




def send_mail(transcript, recipient_email, subject, attachments=None):
    """
    Send an email with optional attachments.
    
    Args:
        transcript: The transcript to summarize in the email body
        recipient_email: Email address of the recipient
        subject: Email subject line
        attachments: List of file paths to attach (default: None)
    """
    body = transcript
    sender_email = "siddharthakhandelwal789@gmail.com"
    sender_password = "wkrb fiqx fpeq ctmc"  # Use an app password if using Gmail
    
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Attach the body text
        msg.attach(MIMEText(body, 'plain'))
        
        # Process attachments if provided
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        # Get the filename from the path
                        filename = os.path.basename(file_path)
                        
                        # Create the attachment
                        attachment = MIMEApplication(file.read())
                        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(attachment)
                else:
                    print(f"Warning: Attachment file not found: {file_path}")
        
        # Connect to the server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()  # Secure the connection
            server.ehlo()
            
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Authentication error: Ensure you are using an App Password instead of your regular password.")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

