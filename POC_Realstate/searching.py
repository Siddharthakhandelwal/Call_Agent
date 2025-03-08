import requests
from POC_Realstate.send_mail import send_mail
from POC_Realstate.groq_summarizer import groq_suum
from POC_Realstate.whatsapp import create_pdf,send_image
from POC_Realstate.groq_image import groq_image
from POC_Realstate.search_and_download import main
def to_check_querr(name,call_id,mail,number):
  auth_token = '5ce77c0e-2947-47d2-abd9-a1a11656e38d'
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
        data=groq_suum(transcript,name) 
        create_pdf(number,data)
        image=groq_image(transcript)
        if image != "None":
          main(image)
          array=send_image(number)
          send_mail(data,mail,"Documents that you asked for",array)
      except Exception as e:
         print(f"An error occurred: {e}")
         return "Error occurred"
      return "Success"
    
