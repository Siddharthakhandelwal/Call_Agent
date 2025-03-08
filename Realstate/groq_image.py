from groq import Groq
def groq_image(data):
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
                    "content": f'''the transcript is {data} , you have the transcript of the call , just return a single prcise line if the user asked for any image or pdf related to some field or place just return that querry in a single in precise manner , meaningful such that it can be searched on the internet otherwise just return "None" .'''
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