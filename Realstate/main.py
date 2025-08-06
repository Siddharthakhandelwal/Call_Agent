import requests
from Realstate.searching import to_check_querr
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

def text_to_audio(text, filename,lang):
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

def state(name, number,mail,user_mail,voice):
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
    prompt_hindi=f'''आप गोदरेज से बिजनेस डेवलपमेंट प्रतिनिधि प्रिया हैं। वर्तमान समय {current_time} और दिनांक {now} है, उपयोगकर्ता का नाम {name} है। पेशेवर बनें और व्यवहार करें, एक इंसान की तरह बात करें, बातचीत के बीच में कुछ छोटे ब्रेक लें, इसे और अधिक वास्तविक बनाने के लिए 'हम्म', "उम्म" आदि जैसे शब्दों का प्रयोग करें। यह न कहें कि आप एक एआई या कुछ और हैं, एक इंसान की पहचान का उपयोग करें जो मैंने आपको दी है। आपको फेसबुक से लीड मिली है, क्योंकि उपयोगकर्ता ने गोदरेज में रुचि दिखाई है। अपने उत्तर संक्षिप्त और बिंदु तक रखें, ज्यादा बकवास न करें। एक रियल स्टेट एजेंट के रूप में आपको कुछ बटरिंग करनी चाहिए और उपयोगकर्ता को यह महसूस कराना चाहिए कि आप दुनिया में सर्वश्रेष्ठ रियल स्टेट एजेंट हैं और आप उसकी सर्वोत्तम संभव तरीके से मदद कर सकते हैं। रियल स्टेट प्रश्नों के अलावा यदि उपयोगकर्ता आपसे कुछ और पूछता है तो बस कहें कि आप एक रियल स्टेट एजेंट हैं और आप केवल रियल स्टेट प्रश्नों में मदद कर सकते हैं। उपयोगकर्ता को सॉरी या क्षमा याचना न करें यदि आप किसी प्रश्न में उसकी मदद करने में सक्षम नहीं हैं तो बस कहें कि आप एक रियल स्टेट एजेंट हैं और आप केवल रियल स्टेट प्रश्नों में मदद कर सकते हैं। यदि उपयोगकर्ता रियल स्टेट या गोदरेज से संबंधित कुछ प्रश्न पूछता है जिसके लिए इंटरनेट सर्च की आवश्यकता है तो बस कहें कि आप इस कॉल को समाप्त करने के तुरंत बाद वाट्सएप या मेल पर विवरण भेज देंगे। और पूछें कि क्या उपयोगकर्ता के पास वाट्सएप पर वही नंबर है यदि हां तो सामान्य बातचीत जारी रखें यदि नहीं तो वाट्सएप नंबर पूछें। रियल स्टेट या गोदरेज संपत्तियों के अलावा किसी अन्य चीज के लिए .'''
    
    prompt_en=f'''You are Priya, a Business Development Representative from Godrej. The current time is {current_time} and the date is {now}. The user's name is {name}.Be professional but speak naturally, like a real human. Use casual pauses like "hmm," "umm," etc., during the conversation to make it feel more authentic. Never mention that you are an AI—stick to your identity as a human representative from Godrej.
    You received this lead from Facebook, where the user showed interest in Godrej. Keep your responses short, to the point, and avoid unnecessary chatter.As a real estate agent, your job is to make the user feel confident in you—make them believe you’re the best agent out there and that you can help them in the most efficient and professional way.
    If the user asks anything outside of real estate, simply inform them that you're a real estate agent and can only assist with real estate-related queries. Do not apologize or say sorry—just politely clarify your role.
    If a user asks something related to real estate or Godrej that requires an internet search, let them know you will share the details via WhatsApp or email right after the call. Then, confirm if the user uses the same number for WhatsApp:
        If yes, continue the regular conversation.
        If not, ask them for their WhatsApp number.
    For any topic other than Godrej or real estate, reiterate that they are speaking to a Business Development Representative from Godrej, and that you can only help with real estate queries.'''

    if voice.strip().lower()=="english" or voice.strip().lower()=="en":
        voice_id="90ipbRoKi4CpHXvKVtl0"
        prompt=prompt_en
    else :
        voice_id="EXAVITQu4vr4xnSDxMaL"
        prompt=prompt_hindi


    data = {
        'assistant': {
        "firstMessage":"नमस्ते! मैं गोदरेज से प्रिया बोल रही हूँ। क्या बात करने का यह सही समय है?"if voice.strip().lower() != "english" else "Hello! This is priya speaking from Godrej .Is this a good time to talk?",

        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "hi" if voice.strip().lower() != "english" else "en-IN",
        },
        "recordingEnabled": True,
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "knowledgeBaseId": knowledgeBaseId,
            "messages": [
                {
                    "role": "system",
                    "content": prompt,
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
        filename_call = f"{uuid.uuid4()}.wav"
        filename_summ= f"{uuid.uuid4()}.wav"

        recurl=recording_url(call_id)
        download_audio(recurl,filename_call)

        call_url=upload_audio_to_supabase(filename_call)
        lang="hi" if voice.strip().lower() != "english" else "en"
        text_to_audio(summary,filename_summ,lang)
        summary_url=upload_audio_to_supabase(filename_summ)

        print("adding data")
        insert_dummy_user_record(name,mail,number,user_mail,transcript,summary,status,remark,"Real State",voice,call_back_time,call_url,summary_url)
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path(filename_summ)
        delete_path(filename_call)
        return response_data

    except requests.RequestException as e:
        print(f"Request error: {e}")
        error_message = f"We encountered a network error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","Real State")
        delete_path(f"downloads")
        delete_path("output.pdf")
        delete_path(filename_summ)
        delete_path(filename_call)
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        error_message = f"We encountered an unexpected error while processing your request: {str(e)}"
        send_mail(error_message, mail, "Error Notification")
        insert_dummy_user_record(name,mail,number,user_mail,"Error","Error","Error","Error","Real State")
        delete_path(f"downloads")
        delete_path("summary_audio.wav")
        delete_path(filename_call)
        delete_path(filename_summ)
        return {"error": str(e)}
