from groq import Groq
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
groq_api=os.getenv("GROQ_API_KEY")

def groq_suum(data,name):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        date = now.strftime("%d-%m-%Y")
        client = Groq(api_key=groq_api)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f'''Extract the appointment details from the following transcript {data} in a format of
                    {date} , {current_time}
                    Name : "{name}",
                    Doctor :"",
                    date and time (appointment time form the data):""
                    consulation cost:"", 
                    and other information
                    you can choose some other format if you like .
                    if there is no relevant information then just return "None"'''
                }
            ],

            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Print the completion returned by the LLM.
        print(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content