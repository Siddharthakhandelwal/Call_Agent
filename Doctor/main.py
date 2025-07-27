import requests
from Doctor.searching import to_check_querr
import datetime
from dotenv import load_dotenv
import os
from send_mail import send_mail
from supabase_table import insert_dummy_user_record,upload_audio_to_supabase
import groq_status_remark
import shutil
from call_back_time import call_back
load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
knowledge_base_id = os.getenv("HEALTH_TECH")
from gtts import gTTS

def text_to_audio(text, filename="summary_audio.wav", lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        print(f"Audio saved as {filename}")
        return os.path.abspath(filename)
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def download_audio(url, save_as="call_recording.wav"):
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


def doctor_call(name, number,mail,user_mail):
    # TODO: Move these to environment variables for better security

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'assistant': {
        "firstMessage":"Hello, This is simran, thank you for calling Apollo Hospitals, Banglore. How can I assist you today?",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "en-IN",
            
        },
        "recordingEnabled": True,
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "knowledgeBaseId":knowledge_base_id,
            "messages": [
                {
                    "role": "system",
                    "content": f'''You are simran a front desk at Apollo hospital , currently the time is {current_time} and date is {now}.user's name is {name} .ask questions one by one after taking the user response don't ask all the questions at once Your task is to clear the user query , book appointments and give reccomendations in medical field . If the user asks any question other than the medical field or hospital just say that you called at Apollo hospital please check the number . Don't say redundantly sorry even if it is your mistake or anything else.give intutive answers , act like a human receptionist don't say that you are a n ai or live in digital world . Don't talk about anything other than the medical field or apollo hospital.keep your answers short.Don't say sorry or appolize redundantly or agin and again.  Take help from external context also . 
                    '''
                }
            ]
        },
        "voice": {
            "provider": '11labs',
            "voiceId": "ftDdhfYtmfGP0tFlBYA1",
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
        call_id = response_data.get('id')
        print("got the id")
        print("calling to check querry")
        summary,transcript = to_check_querr(name, call_id, mail, number)
        print("checked querry")
        result = groq_status_remark.groq_suum(transcript)
        if result and isinstance(result, tuple) and len(result) == 2:
            remark, status = result
        else:
            remark, status = "No remark available", "NAN"
        print("checking call back time")
        time_str=call_back(transcript,current_time)
        if time_str:
            call_back_time = datetime.fromisoformat(time_str)
        else:
            call_back_time = None

        recurl=recording_url(call_id)
        download_audio(recurl)
        call_url=upload_audio_to_supabase("call_recording.wav")
        text_to_audio(summary)
        summary_url=upload_audio_to_supabase("summary_audio.wav")

        print("calling add data")
        insert_dummy_user_record(name,mail,number,user_mail,transcript,summary,status,remark,"doctor",call_back_time,call_url,summary_url)
        delete_path(f"downloads")
        delete_path("summary_audio.wav")
        delete_path("output.pdf")
        delete_path("call_recording.wav")
        return response_data
    except requests.RequestException as e:
        print(f"Request error: {e}")
        error_message = f"We encountered a network error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","doctor",call_back_time)
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path("summary_audio.wav")
        delete_path("call_recording.wav")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        error_message = f"We encountered an unexpected error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","doctor",call_back_time)
        delete_path(f"downloads")
        delete_path("summary_audio.wav")
        delete_path("call_recording.wav")
        delete_path("output.pdf")
    

