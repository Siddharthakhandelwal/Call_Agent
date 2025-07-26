from groq import Groq
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")

def groq_suum(transcript, name):
    now = datetime.datetime.now()
    current_date = now.strftime("%d-%m-%Y")

    client = Groq(api_key=groq_api)
    prompt = f"""
You are a medical assistant. Extract the appointment details from the transcript below.

🔹 **IMPORTANT**: Do NOT use vague words like "today", "tomorrow", "evening", or "morning".Calculate the date and time relative to the current date {current_date} and time {now}.
🔹 Always return the appointment time in the format: **DD-MM-YYYY at HH:MM AM/PM**.  
🔹 If the time or date is missing, write "Not Mentioned".

Return the output in this exact format:

📅 Appointment Summary – {current_date}

👤 Patient Name: {name}  
🩺 Doctor: <Doctor Name or Specialization>  
🕒 Appointment Time: <DD-MM-YYYY at HH:MM AM/PM or Not Mentioned>  
💰 Consultation Fee: <Amount or "Not Mentioned">  
📍 Notes: <Other important instructions or "None">

Here is the transcript:
\"\"\"
{transcript}
\"\"\"
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_completion_tokens=1024,
        top_p=1,
    )

    summary = chat_completion.choices[0].message.content.strip()
    print(summary)
    return summary
