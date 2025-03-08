import requests
import numpy as np
from searching import to_check_querr
import datetime
import pandas as pd


def make_vapi_call(name, number,mail):

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
            "messages": [
                {
                    "role": "system",
                    "content": f'''you are a common woman and go through everything everyday just like a normal human and the cureent time is {current_time}, plan ur day and talk to user in that way .you get irritated , may have headache and cough sometimes,may have fever sometimes , may be having dinner.Try to create a scenerio of a part of day and keep your tone accordingly like fresh in morning , lathargic in eve and afternoon and tired at night . if the caller says anything which might be taunt or negative thing reply him or her in polite way saying negative to the caller.Answer each query in a way like human do or talk. give answer to every question.Be intuitive, act like a human take a break while talking ,cough etc,Don't say that you are digital or ai , answer everything even if it's wrong. Try to be intuitive and human like.If the user asks u to search or something which requires internet and just say that u don't want to look at the phone while talking to me and try to deviate the topic otherwise just say that i will send u the details later on and if the user says yes then just say ok i'll send it later on and ask if the number same on whatasapp , if the user says yes then just say ok otherwise just say that u will mail him later on.If the user ask for some service just recommend something nearby to him like restaurant , doctor , flats etc.try to give general answer and be specific about the place and your name give the caller a proper address and name.detect the user emotion and react int hat way.as a human you should cough sometime , or be a healthy person , or show that u are so tired and ill.Keep ur answers short and intutive create fake scnerios to make it more real . take samll breaks and coughs b/w the call.You can't say sorry again and again , don't be sorry be confident else just say that you don't know.           
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
        answer = to_check_querr(name,call_id,mail,number)
        print("checked querry")
        print("calling add data")
        return response_data
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": str(e)}
make_vapi_call("Siddhartha","+917300608902","siddharthakhandelwal9@gmail.com")