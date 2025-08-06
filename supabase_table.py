from supabase import create_client, Client
from dotenv import load_dotenv
import os

from datetime import datetime

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Use service role key for inserts

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

SELECT_COLUMNS = (
    "name, email, phone_number, transcript, "
    "summary_transcript,audio_url, "
    "summary_audio_url, summary_transcript, status, "
    "remarks, call_back, voice"
)

def upload_audio_to_supabase(filepath, bucket="audio-files"):
    filename = os.path.basename(filepath)
    try:
        with open(filepath, "rb") as f:
            response = supabase.storage.from_(bucket).upload(
                filename,
                f,
                file_options={"content-type": "audio/wav"}  # ← change here for .wav
            )
            if hasattr(response, "error") and response.error:
                print("Upload error:", response.error)
                return None
            print("Upload successful:", filename)
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    except Exception as e:
        print("Error uploading:", e)
        return None


def insert_dummy_user_record(name,email,phone_number,user_mail,transcript,summary_transcript,status,remarks,model,voice,call_back_time=None,recording_url=None,summary_audio=None):
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
            "audio_url": recording_url,
            "summary_audio_url": summary_audio,
            "summary_transcript": summary_transcript,
            "status": status,
            "call_status": "None",
            "remarks": remarks,
            "model":model,
            "call_back":call_back_time,
            "voice":voice
        }

        response = supabase.table("user_records").insert(dummy_data).execute()

        if response.data:
            print("Record inserted successfully.")
            return response.data[0]
        else:
            print("Insert failed or returned no data.")
            return None

    except Exception as e:
        print(f"Error inserting dummy record: {e}")
        return None


def get_filtered_data(user_email, model):
    try:
        # Perform the filtered query with specific columns
        response = (
            supabase
            .table("user_records")
            .select(SELECT_COLUMNS)
            .eq("user_mail", user_email)
            .eq("model", model)
            .execute()
        )

        print("Data extraction successful.")
        return response.data

    except Exception as e:
        print("Error during data fetch:", e)
        return []


# insert_dummy_user_record("Siddharth","siddharth@example.com","+1234567890","user.siddharth@example.com","This is a dummy transcript.","This is a summary of the dummy transcript.","completed","Test data insert")