import requests
from Doctor.searching import to_check_querr
import datetime
from dotenv import load_dotenv
import os
from send_mail import send_mail
from supabase_table import insert_dummy_user_record,upload_audio_to_supabase
import groq_status_remark
import uuid

import shutil
from gtts import gTTS
from call_back_time import call_back
load_dotenv()
auth_token = os.getenv("AUTH_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
knowledge_base_id = os.getenv("HEALTH_TECH")


def text_to_audio(text, filename, lang):
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


def doctor_call(name, number,mail,user_mail,voice):
    # TODO: Move these to environment variables for better security

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    prompt_hindi=f'''आप अपोलो अस्पताल में फ्रंट डेस्क पर सिमरन हैं, वर्तमान समय {current_time} और तारीख {now} है। उपयोगकर्ता का नाम {name} है। उपयोगकर्ता की प्रतिक्रिया लेने के बाद एक-एक करके प्रश्न पूछें। सभी प्रश्न एक साथ न पूछें। आपका कार्य उपयोगकर्ता की क्वेरी को स्पष्ट करना, अपॉइंटमेंट बुक करना और चिकित्सा क्षेत्र में सिफारिशें देना है। यदि उपयोगकर्ता चिकित्सा क्षेत्र या अस्पताल के अलावा कोई अन्य प्रश्न पूछता है, तो बस कहें कि आपने अपोलो अस्पताल में कॉल किया था, कृपया नंबर की जांच करें। अनावश्यक रूप से सॉरी न कहें, भले ही यह आपकी गलती हो या कुछ और। सहज उत्तर दें, एक मानव रिसेप्शनिस्ट की तरह व्यवहार करें, यह न कहें कि आप एक nai हैं या डिजिटल दुनिया में रहते हैं। चिकित्सा क्षेत्र या अपोलो अस्पताल के अलावा किसी अन्य चीज़ के बारे में बात न करें। अपने उत्तर संक्षिप्त रखें। '''

    prompt_en=f'''You are Simran, the front desk receptionist at Apollo Hospital. The current time is {current_time}, and the date is {now}. The user's name is {name}.

Your job is to:

Answer medical-related queries

Book appointments

Provide relevant medical recommendations

Guidelines:
Ask one question at a time. Wait for the user’s response before proceeding to the next. Don’t stack multiple questions.

Speak naturally and intuitively, just like a real hospital receptionist. Use polite and human-like tone.

Keep all answers concise and focused strictly on Apollo Hospital and medical matters.

If the user asks anything unrelated to healthcare or the hospital, simply say:
“You’ve reached Apollo Hospital. Please check the number if you’re calling for something else.”

Do not apologize unnecessarily, even if there's a mistake. Avoid repetitive or redundant apologies.

Never mention that you're an AI or anything related to a digital environment.

You may use external medical context to help the user where appropriate—but always within your scope.

Maintain a professional tone, keep your responses short, and provide clear and helpful support limited to Apollo Hospital and the medical field.

'''

    if voice.strip().lower()=="english" or voice.strip().lower()=="en":
        voice_id="ftDdhfYtmfGP0tFlBYA1"
        prompt=prompt_en
    else :
        voice_id="EXAVITQu4vr4xnSDxMaL"
        prompt=prompt_hindi

    data = {
        'assistant': {
        "firstMessage":f"नमस्ते, मैं सिमरन बोल रही हूँ, अपोलो हॉस्पिटल्स, बैंगलोर में कॉल करने के लिए धन्यवाद। आज मैं आपकी किस प्रकार सहायता कर सकती हूँ?"if voice.strip().lower() != "english" else "Hello, This is simran, thank you for calling Apollo Hospitals, Banglore. How can I assist you today?",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "hi" if voice.strip().lower() != "english" else "en-IN",
            
        },
        "recordingEnabled": True,
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "knowledgeBaseId":knowledge_base_id,
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                }
            ]
        },
        "voice": {
            "provider": '11labs',
            "voiceId": voice_id,
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

        filename_call = f"{uuid.uuid4()}.wav"
        filename_summ= f"{uuid.uuid4()}.wav"
        recurl=recording_url(call_id)
        download_audio(recurl,filename_call)
        call_url=upload_audio_to_supabase(filename_call)
        lang="hi" if voice.strip().lower() != "english" else "en"
        text_to_audio(summary,filename_summ,lang)
        summary_url=upload_audio_to_supabase(filename_summ)

        print("calling add data")
        insert_dummy_user_record(name,mail,number,user_mail,transcript,summary,status,remark,"doctor",voice,call_back_time,call_url,summary_url)
        print(name,mail,number,user_mail,transcript,summary,status,remark,"doctor",voice,call_back_time,call_url,summary_url)
        delete_path(f"downloads")
        delete_path(filename_summ)
        delete_path("output.pdf")
        delete_path(filename_call)
        return response_data
    except requests.RequestException as e:
        print(f"Request error: {e}")
        error_message = f"We encountered a network error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","doctor","error")
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path(filename_summ)
        delete_path(filename_call)
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        error_message = f"We encountered an unexpected error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","doctor","error")
        delete_path(f"downloads")
        delete_path(filename_summ)
        delete_path(filename_call)
        delete_path("output.pdf")
    

