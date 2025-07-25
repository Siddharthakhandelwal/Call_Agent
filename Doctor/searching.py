import requests
from Doctor.send_mail import send_mail
from Doctor.groqmodel import groq_suum
from Doctor.whatsapp import create_pdf
from dotenv import load_dotenv
import os

load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")

def to_check_querr(call_id,mail,number,name):

  url = f"https://api.vapi.ai/call/{call_id}"
  headers = {
      'Authorization': f'Bearer {auth_token}',
      'Content-Type': 'application/json',
  }
  while True:
    response = requests.get(url, headers=headers)
    trans = response.json()
    print(trans[ 'monitor']['listenUrl'])
    print(trans['transport'])
    print(trans['status'])
    if trans['status'] =='ended' :
      try:
        transcript= trans['transcript']
        print("data")
        dat=groq_suum(transcript,name) 
        print("mailing")# for now like hospital data only
        send_mail(dat,mail,"Your appointment details")
        create_pdf(number,dat)
        return "Success"
      except Exception as e:
         print(f"An error occurred: {e}")
         return "Error occurred"
