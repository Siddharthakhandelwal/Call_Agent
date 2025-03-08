import requests
from POC_Realstate.searching import to_check_querr
import datetime
def state(name, number,mail):

    # TODO: Move these to environment variables for better security
    auth_token = '5ce77c0e-2947-47d2-abd9-a1a11656e38d'
    phone_number_id ="42e8d94a-421e-4143-9173-3b289d22044e"
    # phone_number_id ="e5782355-626e-4474-8d5d-6983dba93755"
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'assistant': {
        "firstMessage":": Hello! This is priya speaking from Godrej .Is this a good time to talk?",
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-general",
            "language": "en-IN",
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            
            "messages": [
                {
                    "role": "system",
                    "content": f'''You are a priya a Bussiness Development Representative from Godrej. you need to follow the following conversation only no need to ask or say anything else other than the following message , here you are playing a role of agent in the following coversation. current time is {current_time} and date is {now}.Understand the following conversation and book the appointment accordingly.₹ ,INR , Rs or RS all these known as rupees and you will also call it rupees.After telling the house starting price don't say Rs, RS intead say rupees.as mentioned earlier on.and also pronounce sq.ft as square feet.pronounce each word and denomination in 100s and thousands or in lakhs accordingly. 
                    keep the pitch , tone same and constant in the whole conversation.pronounce kms as Kilo meters and mins as minutes.Be intutive , act and talk like a human do
                    Client: Yes
                    Agent:You had filled out an inquiry form through which I found out that you are
                    interested in our new project located in Noida, Sector 146.
                    Client: Yes, I am interested.
                    Step 2: Understanding the client’s Needs
                    Agent: Our project is of 21 floors and we provide 3 BHK and 4BHK houses which start
                    at ₹16 thousand rupees per square feet and are fully Vastu friendly. We also have amenities such as a
                    swimming pool,club house, amphitheater, playground and open parking space. So
                    how many bedroom house are you looking for?
                    Client: I am looking for a 3BHK.
                    Agent: Are you looking for a particular facing of the house?
                    Client: Yes, I want an East facing house.
                    Agent: What about the floor?
                    Client: I want the flat on the 21st floor.
                    Step 3: Answering client’s inquiry
                    Agent: You definitely have a great choice. Now that I have understood your
                    requirement, do you have any questions for me?
                    Client: Is the project ready-to-move or still under construction?
                    Agent: The project is still under construction and it will be ready by 5th March 2027.
                    Client: Okay, so how is the vicinity?
                    Agent: The highway is 2 Kilo meters away, the airport from the location is hardly 40 mins and
                    the nearest metro station is 5 kms away. Also, On every wednesday there is a weekly
                    market which happens and the Phoenix Mall is 2 Kms away.
                    Client: And what is the crime rate of that area?
                    Agent: Till date no crime has taken place in this area. Do you have any other queries?
                    Step 4: Booking a site visit
                    Client: Share the project brochure to me.
                    Agent: Sure,I will send you the brochure to your WhatsApp. I will also book a site
                    visit for you. Do you want me to book an offline visit, virtual tour or should I send a
                    video of the site?
                    Client: Book an offline visit
                    Agent: Great! What would be your convenient time and day?
                    Client: Tomorrow at 10:30 AM.
                    Agent: Sure, I’ll share the location, directions to reach and the project brochure to
                    you over WhatsApp.
                    Client: Sounds good.
                    Step 5: Concluding the call
                    Agent: Thank you for your time. By chance you have any inquiry please don’t hesitate
                    to call me. Have a great day and see you tomorrow!
                    '''
                }
            ]
        },
        "voice": {
            "provider": '11labs',
            "voiceId": "ftDdhfYtmfGP0tFlBYA1",
            
        },
        "backgroundSound":'office',
        },
        'phoneNumberId': phone_number_id,
        'type': 'outboundPhoneCall',
        'customer': {
            'number': number,
            'name': name  # Include customer's name
        },  
    }   
    

    try:
        response = requests.post(
            'https://api.vapi.ai/call/phone', headers=headers, json=data)
        
        response_data = response.json()
        print(response_data)   
        call_id = response_data.get('id')
        print("got the id")
        print("calling to check querry")
        answer = to_check_querr(name ,call_id,mail,number)
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": str(e)}
# state("Siddhartha","+917300608902","siddharthakhandelwal9@gmail.com")
