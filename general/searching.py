import requests
from firecrawl import FirecrawlApp
from groq import Groq
import tiktoken
from general.send_mail import send_mail
from general.groqmodel import groq_suum
from general.whatsapp import create_pdf,send_image
from general.groq_image import groq_image   
from general.search_and_download import main
from dotenv import load_dotenv
import os

load_dotenv()
groq_api=os.getenv("GROQ_API_KEY")
firecrawl_api=os.getenv("FIRECRAWL_API_KEY")
def groq_trans_querr(trans):
    
    client = Groq(api_key=groq_api)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"you have this {trans} ,analyze the transcript and just return the question or querry that user asked and my answer was that i'll send hium later on.if there is multiple queries then try to combine them in one querry and then return. you need to just return a question which user asked and required internet connection to answer just return them and if there is no actual querry then return none .",
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
def crawl_web(querry):
    app = FirecrawlApp(api_key=firecrawl_api)
    search_engine=os.getenv("SEARCH_ENGINE_API_KEY")
    engine_id=os.getenv("ENGINE_ID")
    tokenizer = tiktoken.get_encoding("cl100k_base") 
    client = Groq(api_key=groq_api)

    def groq_suum(data,querry):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f"you have this {data} , summarize it according to user querry ,{querry} and try to extract and return the valuable info",
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
    url="https://www.googleapis.com/customsearch/v1"
    para={
        'q':querry,
        'key':search_engine,
        'cx':engine_id,
    }
    response=requests.get(url,params=para)
    results=response.json()
    if 'items' in results:
        target_url = results['items'][0]['link']
        print(f"Found URL: {target_url}")
        scrape_result = app.scrape_url(target_url, params={'formats': ['markdown', 'html']})
        data=scrape_result['markdown']
        tokens = tokenizer.encode(data)

    # Keep only the first 6000 tokens
        trimmed_tokens = tokens[:5000]
        trimmed_text = tokenizer.decode(trimmed_tokens)

        print(f"Original tokens: {len(tokens)}, Trimmed tokens: {len(trimmed_tokens)}")
        data=groq_suum(trimmed_text,querry)
        print(data)
        return data


def to_check_querr(name,call_id,mail,number):
  auth_token = os.getenv("AUTH_TOKEN")
  url = f"https://api.vapi.ai/call/{call_id}"
  headers = {
      'Authorization': f'Bearer {auth_token}',
      'Content-Type': 'application/json',
  }
  while True:
    response = requests.get(url, headers=headers)
    trans = response.json()
    print(trans[ 'monitor']['listenUrl'])
    print(trans['transport'])
    print(trans['status'])
    if trans['status'] =='ended' :
      try:
        transcript= trans['transcript']
        data=groq_suum(transcript) 
        send_mail(data,mail,"Summary")
        create_pdf(number,data)
        querry = groq_trans_querr(transcript)
        image_querry=groq_image(transcript)
       
        print(querry)# type: ignore
        if image_querry != "None":
          main(image_querry)
          array=send_image(number)
          send_mail(data,mail,"Documents that you asked for",array)
        if querry != "None":
            try:
                print("web scrapping")
                answer=crawl_web(querry)
                print(answer)
                querry_answer="You asked me a question on call and i have found the answer for you. The answer is :"+answer
                send_mail(querry_answer,mail,"Querry Answer")
                create_pdf(number,querry_answer)
                return answer
            except Exception as e:
               return None
        return None
      except Exception as e:
         print(f"An error occurred: {e}")
         return "Error occurred"

   