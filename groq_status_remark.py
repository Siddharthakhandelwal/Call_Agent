import json
from groq import Groq
from dotenv import load_dotenv
import os
import logging

load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def groq_suum(data):
    try:
        client = Groq(api_key=groq_api)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"""The transcript is: {data} 
Analyze the transcript and give a one-line remark and a status (choose one: Hot (Looks Ultra Excited), Warm (Talked normally), Cold (Not Connected), Won (Paid), Lost (Said no)). 
Your output should be in JSON format like this:
{{
  "Remark": "...",
  "Status": "Hot"
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

        # Try to parse JSON from the response
        parsed = json.loads(response)
        remark = parsed.get("Remark", "")
        status = parsed.get("Status", "")
        print(remark,status)
        return remark, status

    except json.JSONDecodeError:
        logger.error("Could not parse response as JSON.")
        return None, None
    except Exception as e:
        logger.error(f"Error in groq_suum: {repr(e)}")
        return None, None
