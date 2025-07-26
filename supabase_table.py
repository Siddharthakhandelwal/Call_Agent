from supabase import create_client, Client
from dotenv import load_dotenv
import os

from datetime import datetime

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Use service role key for inserts

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_dummy_user_record(name,email,phone_number,user_mail,transcript,summary_transcript,status,remarks,model):
    """
    Inserts a dummy record into the user_records table with placeholder data.
    Returns the inserted record or error.
    """
    try:
        dummy_data = {
            "name": name,
            "email": email,
            "user_mail": user_mail,
            "phone_number": phone_number,
            "transcript": transcript,
            "summary_transcript": summary_transcript,
            "audio_url": "https://example.com/audio.mp3",
            "summary_audio_url": "https://example.com/summary_audio.mp3",
            "summary_transcript": summary_transcript,
            "status": status,
            "call_status": "done",
            "remarks": remarks,
            "model":model
        }

        response = supabase.table("user_records").insert(dummy_data).execute()

        if response.data:
            print("Dummy record inserted successfully.")
            return response.data[0]
        else:
            print("Insert failed or returned no data.")
            return None

    except Exception as e:
        print(f"Error inserting dummy record: {e}")
        return None

# insert_dummy_user_record("Siddharth","siddharth@example.com","+1234567890","user.siddharth@example.com","This is a dummy transcript.","This is a summary of the dummy transcript.","completed","Test data insert")