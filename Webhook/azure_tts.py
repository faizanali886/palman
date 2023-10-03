import os
import time
import tempfile
import boto3
import requests
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from audio_process import calculate_audio_duration, convert_wav_to_oga

load_dotenv()

# AWS S3 credentials
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
BACKEND_URL = os.environ.get('BACKEND_URL')

# Azure TTS credentials
os.environ['SPEECH_KEY'] = '8e8d5dc8d0d04ca89c3484105984d897'
os.environ['SPEECH_REGION'] = 'eastus'
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))


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

def save_audio_to_wav(audio_data, output_filename):
    with open(output_filename, "wb") as audio_file:
        audio_file.write(audio_data)


def azure_tts(text, duration, id, consumed_credits, initial_credits, botId):
    bot = requests.get(f'{BACKEND_URL}/api/bots/{botId}')
    result = bot.json()
    botLangage = result['botLanguage']
    botSpeaker = result['botSpeaker']
    print(botLangage)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = f"{botLangage}-{botSpeaker}"

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    timestamp = int(time.time())
    audio_output_filename = f"{timestamp}.wav"
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
        audio_data = speech_synthesis_result.audio_data
        save_audio_to_wav(audio_data, audio_output_filename)
        print("Audio saved to", audio_output_filename)
        send_file_name = f"{timestamp}.oga"
        duration = duration + calculate_audio_duration(audio_output_filename)
        print("Done TTS")
        send_file = convert_wav_to_oga(audio_output_filename, send_file_name)
        print(send_file)
        if(send_file == "Error: Decoding failed. ffmpeg returned error code: 1"):
            send_file = convert_wav_to_oga(audio_output_filename, send_file_name)
        # Upload the temporary WAV file to S3
        s3.upload_file(send_file, S3_BUCKET_NAME, send_file_name)

        # Get the public URL of the uploaded file
        public_url = get_s3_public_url(send_file_name)

        # Delete the temporary WAV file
        os.remove(audio_output_filename)
        os.remove(send_file)
        duration = int(round(duration))
        print(duration)
        # Convert the string to a timedelta object
        hours, minutes, seconds = map(int, initial_credits.split(':'))
        initial_seconds = hours * 3600 + minutes * 60 + seconds
        remaining_seconds = initial_seconds - duration
        hours, minutes, seconds = map(int, consumed_credits.split(':'))
        consumed_credits_seconds = hours * 3600 + minutes * 60 + seconds
        consumed_credits_seconds = consumed_credits_seconds + duration
        
        update_data = {
            "consumed_credits" : consumed_credits_seconds,
            "remaining_credits" : remaining_seconds
        }
        # Convert the data to JSON
        
        reset_credits = requests.patch(f'{BACKEND_URL}/api/users/{id}/', data=update_data)
        if reset_credits.status_code // 100 == 2:
            return public_url
        else:
            return "Error"
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")