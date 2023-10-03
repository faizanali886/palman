import os
import time
import openai
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import boto3
import base64
import tempfile
import json
import re
load_dotenv()

SENDIFY_API_KEY = os.environ.get('SENDIFY_API_KEY')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
CHAT_GPT_API_KEY = os.environ.get('CHAT_GPT_API_KEY')
MONSTER_API_TOKEN = os.environ.get('MONSTER_API_TOKEN')
WA_ACCOUNT_ID = os.environ.get('WA_ACCOUNT_ID')
VOICE = os.environ.get('VOICE')
TTS_KEY = os.environ.get('TTS_API_KEY')
TTS_API_URL = "https://ttsfree.com/api/v1/tts"

openai.api_key = CHAT_GPT_API_KEY

# AWS S3 credentials
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

s3 = boto3.client(
    service_name='s3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)


def get_s3_public_url(object_key):
    # Generate a pre-signed URL for the uploaded object
    public_url = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_key}'
    return public_url


app = Flask(__name__)


def create_or_load_json_file(userName):
    # Define the directory path
    directory_path = f"chat/{userName}/data"
    
    # Ensure the directory exists, including parent directories if needed
    os.makedirs(directory_path, exist_ok=True)

    # Define the file path
    file_path = f"{directory_path}/{userName}.json"

    # Create the JSON file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(json.dumps({"chat": []}))

    return file_path

def save_query_and_response(userName, query, answer):

    file_path = create_or_load_json_file(userName)
    with open(file_path, "r") as f:
        chat_data = json.load(f)

    chat_data["chat"].append({userName: query, "you": answer})
    with open(file_path, "w") as f:
        json.dump(chat_data, f)

def gpt_response(input_text,userName):
    ssml_tags_description = """
        Here are some SSML tags you can use:
        - <break time='2s' />: for a 2-second pause
        - <say-as interpret-as='ordinal'>1</say-as>: for reading a number as an ordinal (1st, 2nd, etc.)
        - <say-as interpret-as='characters'>Hello</say-as>: to spell out characters
        - <say-as interpret-as='fraction'>5+1/2</say-as><say-as interpret-as='unit'>10 foot</say-as>: for fractions and units
        - <say-as interpret-as='verbatim'>abcdefg</say-as>: to speak verbatim
        - <say-as interpret-as='date' format='yyyymmdd' detail='1'>2019-10-10</say-as>: to speak a date in a specific format
        - <say-as interpret-as='date' format='dm'>10-9</say-as>: to speak a date in a specific format
        - <say-as interpret-as='date' format='dmy' detail='2'>10-9-2019</say-as>: to speak a date in a specific format
        - <say-as interpret-as='time' format='hms12'>2:30am</say-as>: to speak a time in a specific format
        - <sub alias='HelloWorld'>HW</sub>: to substitute text with an alias
        - <emphasis level='moderate'>This is an important announcement</emphasis>: for emphasizing text
        - <emphasis level='reduced'>This is an important announcement</emphasis>: for emphasizing text
        - <emphasis level='strong'>This is an important announcement</emphasis>: for emphasizing text
        - <emphasis level='none'>This is an important announcement</emphasis>: for emphasizing text
        """
    message_history_length = 6
    file_path = create_or_load_json_file(userName)
    with open(file_path, "r") as f:
        chat_data = json.load(f)

    chat = chat_data["chat"][-message_history_length:]

    formatted_messages = [f'student: {message[f"{userName}"]}\nyou: {message["you"]}' for message in chat]
    history = '\n\n'.join(formatted_messages)
    print(history)
    system_prompt = f"""
        You are a helpful assistant and give me short answer in 50 words in english and use my name {userName} in begining of every response.
        Below is the chat history with the user, where '{userName}' represents the user's message, and 'you' represent your response:
        {history}
        Use this chat history to engage in a meaningful conversation with the user.
        """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    response_text = response['choices'][0]['message']['content']
    save_query_and_response(userName, input_text, response_text)
    messages = [
        {"role": "system", "content": f"Add the SSML tags to the text provided {ssml_tags_description}"},
        {"role": "user", "content": f"Add the SSML tags to the following {response_text}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    assistant_response = response['choices'][0]['message']['content']

    return assistant_response



@app.route('/generate', methods=['POST'])
def generate():
    text = request.form['text']
    userName = request.form['userName']
    
    response = gpt_response( text,userName)
    print(response)
    return jsonify({"message": f"Text Generated is: {response}"})



if __name__ == "__main__":
    app.run(debug=True)
