# chujowe
# import pyttsx3

# voiceoverDir = "Voiceovers"

# def create_voice_over(fileName, text):
#     filePath = f"{voiceoverDir}/{fileName}.mp3"
#     engine = pyttsx3.init()
#     engine.save_to_file(text, filePath)
#     engine.runAndWait()
#     return filePath

# chujowe - może do zmiany
# from gtts import gTTS

# voiceoverDir = "Voiceovers"

# def create_voice_over(fileName, text):
#     filePath = f"{voiceoverDir}/{fileName}.mp3"
#     tts = gTTS(text=text, lang='en')
#     tts.save(filePath)
#     return filePath
# import win32com.client

# voiceoverDir = "Voiceovers"

# def create_voice_over(fileName, text):
#     filePath = f"{voiceoverDir}/{fileName}.mp3"
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")
#     fs = win32com.client.Dispatch("SAPI.SpFileStream")
#     fs.Open(filePath, 3, False)
#     speaker.AudioOutputStream = fs
#     speaker.Speak(text)
#     fs.Close()
#     return filePath
import boto3

voiceoverDir = "Voiceovers"

def create_voice_over(fileName, text):
    polly_client = boto3.Session(
        aws_access_key_id='AKIAYZZGEJODH637J4M4', #arn:aws:iam::605133491078:user/polly-script-bot
        aws_secret_access_key='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',
        region_name='eu-central-1'
    ).client('polly')

    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )

    filePath = f"{voiceoverDir}/{fileName}.mp3"
    with open(filePath, 'wb') as audio_file:
        audio_file.write(response['AudioStream'].read())

    return filePath

