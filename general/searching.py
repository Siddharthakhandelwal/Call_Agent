import requests
from firecrawl import FirecrawlApp
from groq import Groq
import tiktoken
from send_mail import send_mail
from general.groqmodel import groq_suum
# from send_whatsapp import create_pdf, send_image
from general.groq_image import groq_image
from search_and_download import main
from dotenv import load_dotenv
import os
import time

load_dotenv()

groq_api = os.getenv("GROQ_API_KEY")
firecrawl_api = os.getenv("FIRECRAWL_API_KEY")
search_engine = os.getenv("SEARCH_ENGINE_API_KEY")
engine_id = os.getenv("ENGINE_ID")
client = Groq(api_key=groq_api)


def groq_trans_querr(trans):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "you are a helpful assistant."},
                {"role": "user", "content": f"you have this {trans}, analyze the transcript and just return the question or query that user asked and my answer was that I'll send him later on.Just return the querry and nothing with it ( querry which isn't answered or said to be sended late on ). Return 'None' otherwise."}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in groq_trans_querr: {e}")
        return "None"


def crawl_web(query):
    app = FirecrawlApp(api_key=firecrawl_api)
    tokenizer = tiktoken.get_encoding("cl100k_base")

    def summarize(data):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"You have this: {data}. Summarize it and answer the query: {query}. Extract only useful information."}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
            )
            print(chat_completion.choices[0].message.content)
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error in summarize: {e}")
            return "Summary not available."

    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params={
            'q': query,
            'key': search_engine,
            'cx': engine_id,
        })
        results = response.json()

        if 'items' in results:
            for item in results['items']:
                target_url = item['link']
                print("Trying URL:", target_url)
                try:
                    document = app.scrape_url(target_url, formats=['markdown', 'html'])
                    data = document.markdown or document.html
                    print(data)
                    if not data:
                        continue
                    tokens = tokenizer.encode(data)
                    trimmed_text = tokenizer.decode(tokens[:5000])
                    print(trimmed_text)
                    return summarize(trimmed_text)

                except Exception as scrape_error:
                    print(f"Skipping URL due to scrape error: {scrape_error}")
                    continue

        return f"Couldn't find a working page for '{query}'."

    except Exception as e:
        print(f"Error in crawl_web: {e}")
        return f"Encountered an error while searching for '{query}': {str(e)}"


def to_check_querr(name, call_id, mail, number):
    auth_token = os.getenv("AUTH_TOKEN")
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}

    while True:
        try:
            response = requests.get(url, headers=headers)
            trans = response.json()

            if trans.get('status') == 'ended':
                transcript = trans.get('transcript', '')
                data = groq_suum(transcript)
                send_mail(data, mail, "Summary")

                querry = groq_trans_querr(transcript)
                image_querry = groq_image(transcript)
                
                if image_querry != "None":
                    downloaded_files = main(image_querry)
                    file_paths = [file['path'] for file in downloaded_files] if downloaded_files else []
                    send_mail(data, mail, "Documents that you asked for", file_paths if file_paths else None)

                if querry != "None":
                    try:
                        answer = crawl_web(querry)
                        querry_answer = f"You asked me a question on call and I found the answer: {answer}"
                        send_mail(querry_answer, mail, "Query Answer")
                        return data, transcript
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                        return data, transcript
                return data, transcript
            else:
                time.sleep(5)

        except Exception as e:
            print(f"An error occurred: {e}")
            return "Error occurred"
