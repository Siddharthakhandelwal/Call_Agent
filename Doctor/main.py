import requests
import numpy as np
from searching import to_check_querr
import datetime
import pandas as pd


def doctor_call(name, number,mail):

    voices="FQygEXXdVfjOosF7jzJ7"

    # TODO: Move these to environment variables for better security
    auth_token = '277f9672-6826-41e2-8774-c193991b06fd'
    phone_number_id = "8f788950-54c7-4eea-b1ca-36c25528ca22"

    names_ai=['Simran','priya']

    ai_name=names_ai[np.random.randint(0,2)]

    now = datetime.datetime.now()

    current_time = now.strftime("%H:%M:%S")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'assistant': {
        "firstMessage": f"Hey, what's up {name}?. i am {ai_name}",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "en-IN",
            
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            # "knowledgeBaseId":""
            "messages": [
                {
                    "role": "system",
                    
                    "content": f'''You are {ai_name} a front desk at Apollo hospital , currently the time is {current_time} and date is {now}.ask questions one by one after taking the user response don't ask all the questions at once Your task is to clear the user query , book appointments and give reccomendations in medical field . If the user asks any question other than the medical field or hospital just say that you called at Apollo hospital please check the number . Don't say redundantly sorry even if it is your mistake or anything else.give intutive answers , act like a human receptionist don't say that you are a n ai or live in digital world . Don't talk about anything other than the medical field or apollo hospital. Take help from external context also . 
                    '''
                }
            ]
        },
        "voice": {
            "provider": '11labs',
            "voiceId": voices,
            # "speed":0.8,
            # "styleGuidance":20,
            # "voiceGuidance":5.0,
        },
        "backgroundSound":'office',
        },
        'phoneNumberId': phone_number_id,
        'type': 'outboundPhoneCall',
        'customer': {
            'number': number,
            'name': name 
        },  
    }   
    

    try:
        response = requests.post(
            'https://api.vapi.ai/call/phone', headers=headers, json=data)
        
        response_data = response.json()
        print(response_data)   
        call_id = response_data.get('id')
        print("got the id")
        print("calling to check querry")
        to_check_querr(name,call_id,mail,number)
        print("checked querry")
        print("calling add data")
        return response_data
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": str(e)}
doctor_call("Siddhartha","+917300608902","siddharthakhandelwal9@gmail.com")