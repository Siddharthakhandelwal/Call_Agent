import requests
from Realstate.searching import to_check_querr
import datetime
from dotenv import load_dotenv
import os
from send_mail import send_mail
from supabase_table import insert_dummy_user_record
import groq_status_remark
import shutil
from call_back_time import call_back

load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")



def recording_url(call_id):
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers).json()
    print(response.get("recordingUrl"))
    return response.get("recordingUrl")

def delete_path(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
            print(f"File deleted: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Folder deleted: {path}")
        else:
            print(f"Unknown type: {path}")
    else:
        print(f"Path not found: {path}")

def state(name, number,mail,user_mail):
    knowledgeBaseId = os.getenv("REAL_STATE")
    # TODO: Move these to environment variables for better security
    
    # phone_number_id ="e5782355-626e-4474-8d5d-6983dba93755"
    now = datetime.datetime.now()
    date =now.strftime("%Y-%m-%d")
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
        "recordingEnabled": True,
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "knowledgeBaseId": knowledgeBaseId,
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
        # print(response_data)   
        call_id = response_data.get('id')
        print("got the id")

        initial_message = f"Hello {name},\n\nWe have initiated a call to your number {number}. Our assistant will be contacting you shortly.\n\nThank you for your patience."
        send_mail(initial_message, mail, "Call Notification")

        print("calling to check querry")
        summary,transcript = to_check_querr(name, call_id, mail, number)
        print("checked querry")

        result = groq_status_remark.groq_suum(transcript)
        if result and isinstance(result, tuple) and len(result) == 2:
            remark, status = result
        else:
            remark, status = "No remark available", "NAN"
        # Send confirmation message via WhatsApp if answer is available
        print("checking call back time")
        time_str=call_back(transcript,current_time)
        if time_str:
            call_back_time = datetime.fromisoformat(time_str)
        else:
            call_back_time = None

        recurl=recording_url(call_id)
        print("calling add data")
        insert_dummy_user_record(name,mail,number,user_mail,transcript,summary,status,remark,"Real State",call_back_time,recurl)
        delete_path(f"downloads")
        delete_path("output.pdf")
        return response_data

    except requests.RequestException as e:
        print(f"Request error: {e}")
        error_message = f"We encountered a network error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","Real State")
        delete_path(f"downloads")
        delete_path("output.pdf")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        error_message = f"We encountered an unexpected error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","Real State")
        delete_path(f"downloads")
        delete_path("output.pdf")
        return {"error": str(e)}
