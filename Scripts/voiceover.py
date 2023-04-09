import boto3
from Secrets.aws_secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

voiceoverDir = "Voiceovers"

def create_voice_over(fileName, text):
    polly_client = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
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

