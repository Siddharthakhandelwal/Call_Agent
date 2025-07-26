import requests
from send_mail import send_mail
from Doctor.groqmodel import groq_suum
# from Doctor.whatsapp import create_pdf
from dotenv import load_dotenv
import os
import time

load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")

def to_check_querr(name, call_id, mail, number):
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    data=None
    transcript=None
    while True:
        try:
            response = requests.get(url, headers=headers)
            trans = response.json()
            print(trans.get('status'))
            if trans.get('status') == 'ended':
                transcript = trans.get('transcript')
                if not transcript:
                    print("Transcript not found.")
                    return None, None

                print("Generating summary...")
                data = groq_suum(transcript, name)

                print("Sending mail...")
                send_mail(data, mail, "Your appointment details")

                # print("Creating WhatsApp PDF...")
                # create_pdf(number, data)

                return data, transcript
            else:
                print("Call still in progress... checking again in 5s.")
                time.sleep(5)

        except Exception as e:
            return data,transcript
