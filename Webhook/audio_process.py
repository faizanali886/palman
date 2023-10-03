import requests
import openai
import json
import time
import subprocess
import os
import base64
import tempfile
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from flask import jsonify
import librosa
import soundfile as sf
from pydub import AudioSegment
import replicate

load_dotenv()


CHAT_GPT_API_KEY = os.environ.get('CHAT_GPT_API_KEY')
openai.api_key = CHAT_GPT_API_KEY
TTS_KEY = os.environ.get('TTS_API_KEY')

# AWS S3 credentials
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
os.environ["REPLICATE_API_TOKEN"] = "r8_Si7Gu417uqRwyeT0YbmDIxBuwF5wxzZ0s36Xa"

s3 = boto3.client(
    service_name='s3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)


def get_s3_public_url(object_key):
    # Generate a pre-signed URL for the uploaded object
    public_url = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_key}'
    print("Public Url" + public_url)
    return public_url


def convert_oga_to_wav(filename):
    timestamp = int(time.time())
    dest_filename = f"{timestamp}.wav"
    subprocess.run(['ffmpeg', '-i', filename, dest_filename])
    return dest_filename


def convert_wav_to_oga(filename, dest_filename):
    start_time = time.time()
    sound = AudioSegment.from_file(filename)
    sound.export(dest_filename, format="oga")
    # subprocess.run(['ffmpeg', '-i', filename, dest_filename])
    target_sample_rate = 48000
    y, sr = librosa.load(filename, sr=target_sample_rate)
    # Save the audio with the new sample rate and set the bitrate to None
    sf.write(dest_filename, y, target_sample_rate,
             format='OGG', subtype='OPUS')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time for the audio conversion from wav to oga (OPUS) is: {elapsed_time:.4f} seconds")
    return dest_filename


def generate_replicate_text(file):
    duration = calculate_audio_duration(file)
    output_text = replicate.run(
        "alqasemy2020/whisper-jax:fb09fe931a654f989fffaabdf46b7b5c69f8ace6b89555d84eae6173d49724f1",
        input={"audio": open(file, "rb")}
    )
    print(output_text["transcription"])
    result = output_text["transcription"]
    print(f"Received Audio is: {duration}")
    return result, duration

def send_wav_to_whisper(file, api_key):
    duration = calculate_audio_duration(file)
    url = "https://api.monsterapi.ai/v1/generate/whisper"
    print(file)
    file_format = file
    print(file_format[-3:])
    files = {"file": (file, open(file, "rb"), f"audio/{file_format[-3:]}")}
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.post(url, files=files, headers=headers)

        response_data = json.loads(response.text)
        process_id = response_data.get("process_id")
        print(f"Process ID: {process_id}")

        while True:
            trans_text = get_text_from_whisper(process_id, api_key=api_key, duration=duration)
            text_data = json.loads(trans_text)
            status = text_data.get("status")

            if status == "IN_PROGRESS" or status == "IN_QUEUE":
                print("Processing in progress. Waiting for completion...")
                time.sleep(1)  # Wait for 5 seconds before checking again
            else:
                if status == "COMPLETED":
                    print("Processing completed.")
                else:
                    print(f"Processing status: {status}")

                result = text_data.get("result")
                print(duration)
                return result, duration

    except Exception as e:
        return f"Error on whisper: {str(e)}"


def get_text_from_whisper(process_id, api_key, duration):
    url = f"https://api.monsterapi.ai/v1/status/{process_id}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)

    return response.text
def create_or_load_json_file(userName):
    directory_path = f"chat/{userName}/data"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    file_path = f"{directory_path}/{userName}.json"
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


def gpt_response(input_text, userName):
    ssml_tags_description = """
        You can use only these SSML tags in your responses don't use other than these:
        - <break time='2s' />: for a 2-second pause
        - <emphasis level='moderate'>This is an important announcement</emphasis>: for emphasizing text
        - <emphasis level='reduced'>This is an important announcement</emphasis>: for emphasizing text
        - <emphasis level='strong'>This is an important announcement</emphasis>: for emphasizing text
        """

    message_history_length = 6
    file_path = create_or_load_json_file(userName)
    with open(file_path, "r") as f:
        chat_data = json.load(f)

    chat = chat_data["chat"][-message_history_length:]

    formatted_messages = [f'{userName}: {message[f"{userName}"]}\nyou: {message["you"]}' for message in chat]
    history = '\n\n'.join(formatted_messages)
    print("History :\n", history)
    system_prompt = f"""
        You are a helpful assistant and give me short answer in 50 words in english.
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
    text_message = response['choices'][0]['message']['content']
    save_query_and_response(userName, input_text, response_text)
    # time.sleep(5)
    # messages = [
    #     {"role": "system", "content": f"Add the SSML tags to the text provided {ssml_tags_description}"},
    #     {"role": "user", "content": f"Add the SSML tags in between the following {response_text} not on the start and end."}
    # ]
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    # )

    # assistant_response = response['choices'][0]['message']['content']
    # assistant_response = assistant_response.replace('(', '').replace(')', '')

    return response_text


def send_wa_message(api_key, account_no, recepient, audio_url):
    print(audio_url)

    chat = {
        "secret": api_key,
        "account": account_no,
        "recipient": recepient,
        "type": "media",
        "message": "reply from gpt",
        "media_url": audio_url,
        "media_type": "audio"
    }

    res = requests.post(
        url="https://sendify.app/api/send/whatsapp", params=chat)
    result = res.json()
    return result['status']


def calculate_audio_duration(file_path):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Get the duration in milliseconds
    duration_ms = len(audio)

    # Convert milliseconds to seconds
    duration_sec = duration_ms / 1000.0

    return duration_sec
