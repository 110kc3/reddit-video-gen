import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

def get_authenticated_service(client_secrets_file):
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=['https://www.googleapis.com/auth/youtube.upload'])
    credentials = flow.run_console()
    return build('youtube', 'v3', credentials=credentials)

def upload_video(youtube, video_file, title, description, category_id, tags, privacy_status):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if response is not None:
            if 'id' in response:
                print(f"Video uploaded successfully. Video ID: {response['id']}")
            else:
                print("The video upload failed.")
