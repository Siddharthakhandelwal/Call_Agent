from groq import Groq
import datetime
def groq_suum(data,name):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        date = now.strftime("%d-%m-%Y")
        groq_api="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"
        client = Groq(api_key=groq_api)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f"the transcript is {data} and the client name is {name} , currently the time is {current_time} and the date is {date} summarize the transcript and extract the information like booking or something else in a nice format.Summarzi the transcript in a manner that you are a real state bussiness development agent and u want to send a summary of the meeting to the client"
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