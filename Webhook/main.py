import datetime
import os
import time
import openai
import requests
import json
import threading
import replicate
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
from audio_process import send_wav_to_whisper, gpt_response, send_wa_message, generate_replicate_text
from azure_tts import azure_tts
from datetime import datetime, timedelta

app = Flask(__name__)

run_with_ngrok(app)

CORS(app, origins="*")

load_dotenv()

SENDIFY_API_KEY = os.environ.get('SENDIFY_API_KEY')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
CHAT_GPT_API_KEY = os.environ.get('CHAT_GPT_API_KEY')
MONSTER_API_TOKEN = os.environ.get('MONSTER_API_TOKEN')
WA_ACCOUNT_ID = os.environ.get('WA_ACCOUNT_ID')
VOICE = os.environ.get('VOICE')
BACKEND_URL = os.environ.get('BACKEND_URL')

openai.api_key = CHAT_GPT_API_KEY
os.environ["REPLICATE_API_TOKEN"] = "r8_Si7Gu417uqRwyeT0YbmDIxBuwF5wxzZ0s36Xa"
# Set the flag to track whether a request has been received
request_received = False

# Timer duration for the idle period (5 minutes)
IDLE_PERIOD_SECONDS = 2 * 60

def reset_request_flag():
    global request_received
    while True:
        print("IDLE Processing.......")
        # Wait for 5 minutes
        time.sleep(IDLE_PERIOD_SECONDS)

        # Check if a request has been received in the last 5 minutes
        if not request_received:
            output_text = replicate.run(
                "alqasemy2020/whisper-jax:fb09fe931a654f989fffaabdf46b7b5c69f8ace6b89555d84eae6173d49724f1",
                input={"audio": open("./sample.wav", "rb")}
            )
            print(output_text["transcription"])

        # Reset the request_received flag
        request_received = False

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.form.to_dict()
    timestamp = int(time.time())
    global request_received

    if 'secret' in data and data['secret'] == WEBHOOK_SECRET:
        receipent = data.get('data[phone]')
        print(receipent)
        audio_url = data.get('data[attachment]')
        print(audio_url)
        code = data.get('data[message]')
        print(code)
        if(audio_url != "0"):
            response = requests.get(audio_url)
            phone_registered = requests.get(
                f'{BACKEND_URL}/api/verify/{receipent}')
            if phone_registered.status_code == 200:
                # Set the request_received flag to True when a request is received
                request_received = True
                data = phone_registered.json()
                print(data["user_data"]["status"])
                
                if data['exists'] == 'yes' and data["user_data"]["status"] in ['freetrial', 'active']:
                    id = data["user_data"]["id"]
                    userName = data["user_data"]["name"]
                    consumed_credits = data["user_data"]["consumed_credits"]
                    initial_credits = data["user_data"]["initial_credits"]
                    botId = data['user_data']['botid']
                    if response.status_code == 200:
                        local_audio_path = f"{timestamp}.wav"

                    with open(local_audio_path, 'wb') as local_audio_file:
                        local_audio_file.write(response.content)

                    audio_reply, text_message, *_ = generate_audio(
                        attachment=f"{timestamp}.wav", userName=userName, id=id, consumed_credits=consumed_credits, initial_credits=initial_credits, botId=botId)
                    print(audio_reply)
                    print(text_message)
                    if (audio_reply == "Error: Decoding failed. ffmpeg returned error code: 1"):
                        audio_reply, text_message, *_ = generate_audio(
                            attachment=f"{timestamp}.wav", userName=userName, consumed_credits=consumed_credits, initial_credits=initial_credits, botId=botId)
                    os.remove(local_audio_path)
                    print("Audio Reply: " + audio_reply)
                    
                    bot = requests.get(f'{BACKEND_URL}/api/bots/{botId}')
                    result = bot.json()
                    SENDIFY_API = result['apiSecret']
                    send_wa_message(SENDIFY_API, botId,
                                    receipent, audio_reply)
                    
                    send_wa_message_text(SENDIFY_API, botId,
                                    receipent, text_message)
                    return "OK", 200
                
                # If the user is Registered but inactive
                elif data['exists'] == 'yes' and data["user_data"]["status"] == "inactive":
                    send_wa_unregister_text(SENDIFY_API_KEY, WA_ACCOUNT_ID,
                        receipent, "Your credits have been ended 😭.")
                    return "Message send Successfully to Unregistered.", 200
                
                else:
                    return "Unauthorized", 401
        # If the user is Unregistered
        elif code == 'Register Me':
            # name = code[12:]
            body = {
                "number": str(receipent),
                "name": str(receipent),
                "email": "user@gmail.com",
                "initial_credits": "00:00:00",
                "consumed_credits": "00:00:00",
                "remaining_credits": "00:00:00",
                "status" : "inactive",
                "botid": "21"
            }
            user_register = requests.post(f'{BACKEND_URL}/api/users/', data=body)
            if user_register.status_code == 201:
                send_wa_unregister_text(SENDIFY_API_KEY, WA_ACCOUNT_ID,
                                receipent, "Your Request for the your palman have been processed 😊.")
                return "User Registered", 201
            else:
                return "Error in Registering a User", 404
        elif code != "" and audio_url == "0":
            url = "https://audios-response-s3-bucket.s3.amazonaws.com/Codes/code.json"

            # Send a GET request to the URL to retrieve the JSON data
            response = requests.get(url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Load the JSON data into a Python dictionary
                json_data = response.json()

                # Access and print some objects from the JSON data
                print(json_data)
                if code in json_data:
                    print("Processing Request")
                    phone_registered = requests.get(
                        f'{BACKEND_URL}/api/verify/{receipent}')
                    
                    data = phone_registered.json()
                    id = data['user_data']['id']
                    remaining_credits = data["user_data"]["remaining_credits"]
                    parsed_timedelta = datetime.strptime(remaining_credits, "%H:%M:%S") - datetime(1900, 1, 1)
                    additional_timedelta = timedelta(seconds=1200)
                    result_timedelta = parsed_timedelta + additional_timedelta

                    data = {
                        "initial_credits" : result_timedelta,
                        "status" : "freetrial"
                    }
                    print(id)
                    credits_status = requests.patch(f'{BACKEND_URL}/api/users/{id}/', data=data)
                    print(credits_status)
                    if credits_status.status_code // 100 == 2:
                        send_wa_unregister_text(SENDIFY_API_KEY, WA_ACCOUNT_ID,
                                receipent, f"Your Request for the your palman have been processed 😊. You have been granted {json_data[code]} seconds 🎉.") 
                    return "Code Found", 200
                else:
                    send_wa_unregister_text(SENDIFY_API_KEY, WA_ACCOUNT_ID,
                            receipent, f"We don't have {code} in our records 🤷‍♂️. If you are a new User please use *Register Me*")
                    return "Code Not Found in our Records", 404
            else:
                return "Failed to retrieve JSON data. Status code:", response.status_code
        else:
            send_wa_unregister_text(SENDIFY_API_KEY, WA_ACCOUNT_ID,
                            receipent, "You don't have an credits available in your account or you are not registered 😭.")
            return "Unauthorized", 401


def generate_audio(attachment, userName, id, consumed_credits, initial_credits, botId):
    try:
        file = attachment
        voice = VOICE
        if file:
            try:
                # text_response, duration = send_wav_to_whisper(
                #     file, MONSTER_API_TOKEN)


                # Audio to Text generation
                start_time = time.time()
                text_response, duration = generate_replicate_text(
                    file)
                # prompt = text_response["text"]
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Elapsed time for the Audio to Text is: {elapsed_time:.4f} seconds")

                # GPT Response Time
                start_time2 = time.time()    
                response = gpt_response(text_response, userName)
                print("Text Generated is:" + response)
                end_time2 = time.time()
                elapsed_time2 = end_time2 - start_time2
                print(f"Elapsed time for the GPT is: {elapsed_time2:.4f} seconds")

                # Text to Speech generation
                start_time3 = time.time()
                if voice == "":
                    audio = azure_tts(
                        response, duration, id, consumed_credits, initial_credits, botId)
                else:
                    audio = azure_tts(
                        response, duration, id, consumed_credits, initial_credits, botId)
                result = audio
                print(result)
                audio_url = result
                print("Url generated Successfully!!!" + audio_url)
                end_time3 = time.time()
                elapsed_time3 = end_time3 - start_time3
                print(f"Elapsed time for the Text to Audio is: {elapsed_time3:.4f} seconds")
                return audio_url, response
            except Exception as e:
                return f"Error: {str(e)}"
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def send_wa_message(api_key, account_no, recepient, audio_url):
    start_time4 = time.time()
    print("Sent this audio" + audio_url)

    chat = {
        "secret": api_key,
        "account": account_no,
        "recipient": recepient,
        "type": "media",
        "message": "This is a message from the audio response you send.",
        "media_url": audio_url,
        "media_type": "audio",
        "priority": 1
    }

    res = requests.post(
        url="https://sendify.app/api/send/whatsapp", params=chat)
    result = res.json()
    print("success")
    end_time4 = time.time()
    elapsed_time4 = end_time4 - start_time4
    print(f"Elapsed time for the Sendify to send the audio is: {elapsed_time4:.4f} seconds")
    return result['status']

def send_wa_message_text(api_key, account_no, recepient, wa_text):
    start_time5 = time.time()
    chat = {
         "secret": api_key,
        "account": account_no,
        "recipient": recepient,
        "type": "text",
        "message": wa_text,
        "priority": 2
    }
    res = requests.post(
        url="https://sendify.app/api/send/whatsapp", params=chat)
    result = res.json()
    print("success")
    end_time5 = time.time()
    elapsed_time5 = end_time5 - start_time5
    print(f"Elapsed time for the Sendify to send the text message is: {elapsed_time5:.4f} seconds")
    return result['status']

def send_wa_unregister_text(api_key, account_no, recepient, wa_text):
    start_time5 = time.time()
    chat = {
         "secret": api_key,
        "account": account_no,
        "recipient": recepient,
        "type": "text",
        "message": wa_text,
        "priority": 1
    }
    res = requests.post(
        url="https://sendify.app/api/send/whatsapp", params=chat)
    result = res.json()
    print("success")
    end_time5 = time.time()
    elapsed_time5 = end_time5 - start_time5
    print(f"Elapsed time for the Sendify to send the text message is: {elapsed_time5:.4f} seconds")
    return result['status']

if __name__ == '__main__':
    # Start a thread to reset the request_received flag after the idle period
    threading.Thread(target=reset_request_flag).start()
    # app.run(port=8000)
    app.run()
