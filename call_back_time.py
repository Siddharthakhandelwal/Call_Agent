import json
from groq import Groq
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_back(transcript, call_time):
    now = datetime.now()
    try:
        client = Groq(api_key=groq_api)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"""The transcript is: {transcript}.
Please return a time when the user asked to call back or gave a time to call. 
The current time is {now} and the call was made at {call_time}. 
Don't return Tommorow , today etc , analyze and give the exact time.
If timezone is not mentioned, assume IST.

Respond in JSON format as:
{{
  "time": "YYYY-MM-DD HH:MM:SS"   # or null if no time mentioned
}}"""}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
        )

        response = chat_completion.choices[0].message.content.strip()
        logger.info(f"Raw response from Groq: {response}")

        parsed = json.loads(response)
        logger.info(f"Parsed JSON: {parsed}")
        return parsed.get("time", None)

    except json.JSONDecodeError:
        logger.error("Could not parse response as JSON.")
        return None
    except Exception as e:
        logger.error(f"Error in groq_suum: {repr(e)}")
        return None
