import requests
from send_mail import send_mail
from groqmodel import groq_suum
from whatsapp import create_pdf

def to_check_querr(name,call_id,mail,number):
  auth_token = '277f9672-6826-41e2-8774-c193991b06fd'
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
        data=groq_suum(transcript)
        send_mail(data,mail,"Summary")
        create_pdf(number,data)
        break
      except Exception as e:
         print(f"An error occurred: {e}")
         return "Error occurred"
