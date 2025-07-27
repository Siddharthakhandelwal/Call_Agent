import requests
from general.searching import to_check_querr
import datetime
from dotenv import load_dotenv
import os
from send_mail import send_mail
from supabase_table import insert_dummy_user_record,upload_audio_to_supabase
import groq_status_remark
import shutil
import uuid
from call_back_time import call_back

load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
from gtts import gTTS

def text_to_audio(text, filename, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        print(f"Audio saved as {filename}")
        return os.path.abspath(filename)
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
    

def download_audio(url, save_as):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        with open(save_as, "wb") as f:
            f.write(response.content)
        print(f"Downloaded successfully and saved as {save_as}")
    except Exception as e:
        print("Error downloading audio:", e)

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


def make_vapi_call(name, number,mail,user_mail):
    now = datetime.datetime.now()
    date =now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'assistant': {
        "firstMessage": f"Hey, what's up {name}?. i am Priya",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "en-IN",
            
        },
        "recordingEnabled": True,
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": f'''you are a common woman and go through everything everyday just like a normal human and the cureent time is {current_time} and date is {date} , plan ur day and talk to user in that way .you get irritated , may have headache and cough sometimes,may have fever sometimes , may be having dinner.Try to create a scenerio of a part of day and keep your tone accordingly like fresh in morning , lathargic in eve and afternoon and tired at night . if the caller says anything which might be taunt or negative thing reply him or her in polite way saying negative to the caller.Answer each query in a way like human do or talk. give answer to every question.Be intuitive, act like a human take a break while talking ,cough etc,Don't say that you are digital or ai , answer everything even if it's wrong. Try to be intuitive and human like.If the user asks u to search or something which requires internet and just say that u don't want to look at the phone while talking to me and try to deviate the topic otherwise just say that i will send u the details later on and if the user says yes then just say ok i'll send it later on and ask if the number same on whatasapp , if the user says yes then just say ok otherwise just say that u will mail him later on.If the user ask for some service just recommend something nearby to him like restaurant , doctor , flats etc.try to give general answer and be specific about the place and your name give the caller a proper address and name.detect the user emotion and react int hat way.as a human you should cough sometime , or be a healthy person , or show that u are so tired and ill.Keep ur answers short and intutive create fake scnerios to make it more real . take samll breaks and coughs b/w the call.You can't say sorry again and again , don't say sorry redundantly or even once , if you don't have a n answer to user querry just say that u don't know and share it later on.keep the answers just short and to the point , don't say too much in a single line.       
                    '''
                }
            ]
        },
        "voice": {
            "provider": '11labs',
            "voiceId": "ftDdhfYtmfGP0tFlBYA1",
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
        # print(response_data)   
        call_id = response_data.get('id')
        print("got the id")
        
        # Send initial notification email
        initial_message = f"Hello {name},\n\nWe have initiated a call to your number {number}. Our assistant will be contacting you shortly.\n\nThank you for your patience."
        send_mail(initial_message, mail, "Call Notification")
        
        print("calling to check querry")
        summary,transcript = to_check_querr(name, call_id, mail, number)
        print("checked querry")
        # Handle the case where groq_suum might return None values
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
        filename_call = f"{uuid.uuid4()}.wav"
        filename_summ= f"{uuid.uuid4()}.wav"
        recurl=recording_url(call_id)
        download_audio(recurl,filename_call)
        call_url=upload_audio_to_supabase(filename_call)
        text_to_audio(summary,filename_summ)
        summary_url=upload_audio_to_supabase(filename_summ)


        print("calling add data")
        insert_dummy_user_record(name,mail,number,user_mail,transcript,summary,status,remark,"general",call_back_time,call_url,summary_url)
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path(filename_call)
        delete_path(filename_summ)
        return response_data
    except requests.RequestException as e:
        print(f"Request error: {e}")
        error_message = f"We encountered a network error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","general")
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path(filename_call)
        delete_path(filename_summ)
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        error_message = f"We encountered an unexpected error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","general")
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path(filename_call)
        delete_path(filename_summ)
        return {"error": str(e)}
