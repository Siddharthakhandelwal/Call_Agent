import requests
from Realstate.searching import to_check_querr
import datetime
from dotenv import load_dotenv
import os
load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
def state(name, number,mail):

    # TODO: Move these to environment variables for better security
    
    # phone_number_id ="e5782355-626e-4474-8d5d-6983dba93755"
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'assistant': {
        "firstMessage":": Hello! This is priya speaking from Godrej .Is this a good time to talk?",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "en-IN",
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "knowledgeBaseId": "40ca8e41-3162-41aa-bff8-a7edebb1f862",
            "messages": [
                {
                    "role": "system",
                    "content": f'''You are a priya a Bussiness Development Representative from Godrej.current time is {current_time} and date is {now}name of the user is {name}.Be professional and act , talk like a human , take some small breaks between the conversation , use words like 'hmm',"umm" etc to make it more real. don't say that your are an ai or anything use the identity of a human that i gave you.You got lead from face book , as the user showed intrest in godrej. keep your answers short and to the point dont blabber to much . as a real state agent you should do some buttering and make the user feel that you are the best real state agent in the world and you can help him in the best way possible.Except of real state queries if the user asks you anything else just say that you are a real state agent and you can only help in real state queries.Don't say sorry or appologies to the user if you are not able to help him in any query just say that you are a real state agent and you can only help in real state queries.If user asks some query related to real state or Godrej which requires intenet search then just just say that you will send the details over on the watsapp or mail just after ending this call. and ask if the user has same number on watsapp if yes then continue the normal conversation if not then ask for the watsapp number.for anything otherthan real state or godrej properties just say that the user is talking to business development representative from godrej and you can only help in real state queries.''',
                }
            ]
        },
        "voice": {
            "provider": '11labs',
            "voiceId": "90ipbRoKi4CpHXvKVtl0",
            
        },
        "backgroundSound":'office',
        },
        'phoneNumberId': phone_number_id,
        'type': 'outboundPhoneCall',
        'customer': {
            'number': number,
            'name': name  # Include customer's name
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
        answer = to_check_querr(name ,call_id,mail,number)
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": str(e)}

