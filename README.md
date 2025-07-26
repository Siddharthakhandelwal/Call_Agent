# General Python Scripts

This repository contains a collection of Python scripts for various automation tasks, including email sending, WhatsApp messaging, web scraping, and AI-powered text processing.

## Features

- **Automated Phone Calls**: Make outbound phone calls using the Vapi.ai API
- **Email Notifications**: Send emails with attachments using Gmail SMTP
- **WhatsApp Messaging**: Send messages and PDFs via WhatsApp
- **Web Scraping**: Search and download relevant content from the web
- **AI Processing**: Use Groq AI models to summarize text and extract queries

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with the following environment variables:
   ```
   # Email Configuration
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   
   # Vapi.ai Configuration
   AUTH_TOKEN=your-vapi-auth-token
   PHONE_NUMBER_ID=your-phone-number-id
   
   # Groq API
   GROQ_API_KEY=your-groq-api-key
   
   # Firecrawl API
   FIRECRAWL_API_KEY=your-firecrawl-api-key
   
   # Google Search API
   SEARCH_ENGINE_API_KEY=your-google-search-api-key
   ENGINE_ID=your-google-search-engine-id
   ```

## Usage

### Making a Call

```python
from main import make_vapi_call

# Make a call to a user
make_vapi_call("User Name", "+1234567890", "user@example.com")
```

### Sending an Email

```python
from general.send_mail import send_mail

# Send a simple email
send_mail("Hello, this is a test email.", "recipient@example.com", "Test Email")

# Send an email with attachments
send_mail("Please find the attached documents.", "recipient@example.com", "Documents", ["/path/to/file1.pdf", "/path/to/file2.jpg"])
```

### Sending WhatsApp Messages

```python
from general.whatsapp import send_message, create_pdf

# Send a file via WhatsApp
send_message("+1234567890", "/path/to/file.pdf")

# Create a PDF and send it via WhatsApp
create_pdf("+1234567890", "This is the content of the PDF.")
```

## Modules

- `main.py`: Main entry point for making calls
- `send_mail.py`: Email sending functionality
- `whatsapp.py`: WhatsApp messaging functionality
- `searching.py`: Handles query extraction and web searching
- `search_and_download.py`: Downloads files from search results
- `groqmodel.py`: Groq AI model for text summarization
- `groq_image.py`: Groq AI model for image query extraction

## Notes

- For WhatsApp messaging, the script uses `mudslide` which should be installed via npm
- For email sending, you need to use an App Password if you're using Gmail
- The Groq API requires a valid API key for AI processing
